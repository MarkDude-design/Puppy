"""Pinned public key -> authenticated clearsigned checksum -> archive bytes.

No keyserver/import daemon, policy bypass, archive extraction, build or boot.
The caller owns command logs and must raise on every nonzero command exit.
"""
import hashlib
from pathlib import Path
import re
import shutil


class SourceVerificationError(RuntimeError):
    pass


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


BAD_STATUS = {"BADSIG", "ERRSIG", "NO_PUBKEY", "EXPSIG", "EXPKEYSIG", "REVKEYSIG",
              "KEYEXPIRED", "SIGEXPIRED", "KEYREVOKED", "NODATA", "FAILURE", "ERROR"}


def signature_record(status, fingerprint):
    if not re.fullmatch(r"[0-9A-F]{40}", fingerprint):
        return None
    rows = [line.split() for line in status.splitlines() if line.startswith("[GNUPG:] ")]
    if any(len(row) >= 2 and row[1] in BAD_STATUS for row in rows):
        return None
    for tag in ("PLAINTEXT", "NEWSIG", "GOODSIG", "VALIDSIG"):
        if sum(len(row) >= 2 and row[1] == tag for row in rows) != 1:
            return None
    row = next(row for row in rows if row[1] == "VALIDSIG")
    if (len(row) != 12 or row[2] != fingerprint or row[11] != fingerprint
            or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row[3])
            or any(not re.fullmatch(r"[0-9]+", row[i]) for i in range(4, 10))
            or row[6] != "4" or row[7] != "0" or row[9] != "8" or row[10] != "01"):
        return None
    return {"signer_fingerprint": row[2], "primary_fingerprint": row[11],
            "signature_creation_date": row[3], "signature_timestamp": int(row[4]),
            "public_key_algorithm": int(row[8]), "digest_algorithm": int(row[9]),
            "signature_class": row[10]}


def valid_signature(status, fingerprint):
    return signature_record(status, fingerprint) is not None


def manifest_digest(plaintext, basename):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", basename):
        raise SourceVerificationError("invalid expected archive basename")
    matches = []
    for line in plaintext.splitlines():
        if line.lstrip().upper().startswith("SHA256"):
            row = re.fullmatch(r"SHA256:[ \t]+([0-9A-Fa-f]{64})[ \t]+([A-Za-z0-9][A-Za-z0-9._-]*)", line)
            if row is None:
                raise SourceVerificationError("malformed signed SHA256 entry")
            if row[2] == basename:
                matches.append(row[1].lower())
    if len(matches) != 1:
        raise SourceVerificationError("need exactly one signed SHA256 for exact archive basename")
    return matches[0]


def check_container(path):
    raw = Path(path).read_bytes()
    if len(raw) > 1_000_000:
        raise SourceVerificationError("manifest exceeds size guard")
    try:
        text = raw.decode("ascii")
    except UnicodeError as error:
        raise SourceVerificationError("manifest armor is not ASCII") from error
    lines = text.splitlines()
    if (not lines or lines[0] != "-----BEGIN PGP SIGNED MESSAGE-----"
            or lines.count("-----BEGIN PGP SIGNED MESSAGE-----") != 1
            or lines.count("-----BEGIN PGP SIGNATURE-----") != 1
            or lines.count("-----END PGP SIGNATURE-----") != 1):
        raise SourceVerificationError("expected one clearsigned checksum manifest")
    end = lines.index("-----END PGP SIGNATURE-----")
    if any(line.strip() for line in lines[end + 1:]):
        raise SourceVerificationError("unsigned data follows checksum signature")


def authenticate_archive(archive, manifest, key, release, evidence, work, command):
    """Verify actual files with actual GPG; parse only successful signed output."""
    archive, manifest, key = map(Path, (archive, manifest, key))
    evidence, work = Path(evidence), Path(work)
    expected_key_hash = release["public_key_sha256"]
    if not re.fullmatch(r"[0-9a-f]{64}", expected_key_hash) or file_sha256(key) != expected_key_hash:
        raise SourceVerificationError("public key bytes do not match reviewed SHA256")
    check_container(manifest)
    home = work / "gnupg"
    home.mkdir(mode=0o700)
    gpg = ["gpg", "--no-options", "--homedir", str(home), "--batch",
           "--no-autostart", "--no-auto-key-retrieve"]
    listing = command(gpg + ["--with-colons", "--import-options", "show-only",
                             "--import", str(key)], "key-inspection.log", blocked=True)
    rows = [line.split(":") for line in listing.splitlines()]
    pubs = [i for i, row in enumerate(rows) if row[0] == "pub"]
    if len(pubs) != 1 or pubs[0] + 1 >= len(rows):
        raise SourceVerificationError("key fixture must contain exactly one primary key")
    pub, fpr = rows[pubs[0]], rows[pubs[0] + 1]
    if len(fpr) < 10 or fpr[0] != "fpr" or fpr[9] != release["signer_fingerprint"]:
        raise SourceVerificationError("primary key does not match pinned manifest signer")
    ring = work / "reviewed-public-keyring.gpg"
    command(gpg + ["--output", str(ring), "--dearmor", str(key)],
            "key-dearmor.log", blocked=True)
    status_path = evidence / "manifest-status.log"
    quarantine = evidence / "checksums.quarantined.txt"
    if status_path.exists() or quarantine.exists():
        raise SourceVerificationError("refusing preexisting verification outputs")
    # Exit-zero enforced by command() BEFORE reading either of these files.
    command(gpg + ["--no-default-keyring", "--keyring", str(ring),
                   "--status-file", str(status_path), "--output", str(quarantine),
                   "--decrypt", str(manifest)], "manifest-verification.log", blocked=True)
    try:
        record = signature_record(status_path.read_text(encoding="ascii"),
                                  release["signer_fingerprint"])
        if record is None:
            raise SourceVerificationError("manifest lacks one acceptable exact-signer VALIDSIG")
        # Never read or grep the raw .sign as an authenticated checksum source.
        digest = manifest_digest(quarantine.read_text(encoding="ascii"), release["archive_basename"])
    except (OSError, UnicodeError) as error:
        raise SourceVerificationError("missing or malformed verified GPG output") from error
    if archive.name != release["archive_basename"]:
        raise SourceVerificationError("downloaded archive basename differs from release lock")
    actual = file_sha256(archive)
    if actual != digest or actual != release["archive_sha256"]:
        raise SourceVerificationError("archive SHA256 differs from authenticated manifest or reviewed lock")
    shutil.copyfile(quarantine, evidence / "verified-checksums.txt")
    return {"status": "VERIFIED", "method": "pinned public key; clearsigned SHA256 manifest; exact archive binding",
            "archive_sha256": actual, "manifest_sha256": file_sha256(manifest),
            "public_key_sha256": expected_key_hash, "authenticated_manifest_digest": digest,
            "public_key_bits": int(pub[2]), **record}
