"""One-off authoring tool: PGPy0.6.0 required only to regenerate test fixtures.

Generated RSA keys are ephemeral test material; private keys are never saved.
Tests and production use real GPG and do not import PGPy.
"""
import datetime
import base64
import hashlib
import io
import json
from pathlib import Path
import tarfile

from pgpy import PGPKey, PGPMessage, PGPUID
from pgpy.constants import (CompressionAlgorithm, HashAlgorithm, KeyFlags,
                            PubKeyAlgorithm, SymmetricKeyAlgorithm)


ROOT = Path(__file__).with_name("source-auth")
CREATED = datetime.datetime(2026, 10, 1, tzinfo=datetime.timezone.utc)
BASENAME = "buildroot-2026.08.tar.xz"


def key(name):
    result = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048, created=CREATED)
    result.add_uid(PGPUID.new(name, comment="PUBLIC SYNTHETIC TEST FIXTURE"),
                   usage={KeyFlags.Sign}, hashes=[HashAlgorithm.SHA256],
                   ciphers=[SymmetricKeyAlgorithm.AES256],
                   compression=[CompressionAlgorithm.Uncompressed], created=CREATED)
    return result


def main():
    ROOT.mkdir(exist_ok=True)
    archive = ROOT / BASENAME
    with tarfile.open(archive, "w:xz") as stream:
        data = b"SYNTHETIC PUPPF TEST ARCHIVE; NOT A BUILDROOT RELEASE\n"
        item = tarfile.TarInfo("buildroot-2026.08/SYNTHETIC.txt")
        item.size = len(data)
        stream.addfile(item, io.BytesIO(data))
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (ROOT / (BASENAME + ".b64")).write_text(base64.b64encode(archive.read_bytes()).decode() + "\n")
    archive.unlink()
    trusted, other = key("Puppf fixture signer"), key("Puppf other fixture signer")
    (ROOT / "fixture-public-key.asc").write_text(str(trusted.pubkey))
    (ROOT / "other-public-key.asc").write_text(str(other.pubkey))
    line = f"SHA256: {digest}  {BASENAME}\n"
    variants = {
        "valid": line,
        "wrong-hash": f"SHA256: {'0' * 64}  {BASENAME}\n",
        "wrong-name": f"SHA256: {digest}  another.tar.xz\n",
        "missing": "There is no SHA256 entry.\n",
        "duplicate-identical": line + line,
        "duplicate-conflicting": line + f"SHA256: {'0' * 64}  {BASENAME}\n",
        "malformed": f"SHA256: NOT-A-HASH  {BASENAME}\n",
        "path-name": f"SHA256: {digest}  ../{BASENAME}\n",
    }
    for name, text in variants.items():
        message = PGPMessage.new(text, cleartext=True)
        message |= trusted.sign(message, hash=HashAlgorithm.SHA256, created=CREATED)
        (ROOT / (name + ".sign")).write_text(str(message))
    message = PGPMessage.new(line, cleartext=True)
    message |= other.sign(message, hash=HashAlgorithm.SHA256, created=CREATED)
    (ROOT / "wrong-signer.sign").write_text(str(message))
    metadata = dict(kind="synthetic fixtures, not upstream release authentication",
                    generator="PGPy0.6.0; ephemeral RSA2048; no private keys retained",
                    archive_basename=BASENAME, archive_sha256=digest,
                    signer_fingerprint=str(trusted.fingerprint),
                    other_fingerprint=str(other.fingerprint),
                    public_key_sha256=hashlib.sha256((ROOT / "fixture-public-key.asc").read_bytes()).hexdigest(),
                    files={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sorted(ROOT.iterdir()) if p.is_file() and p.name != "metadata.json"})
    (ROOT / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: metadata[k] for k in ("archive_sha256", "signer_fingerprint")}, indent=2))


if __name__ == "__main__":
    main()
