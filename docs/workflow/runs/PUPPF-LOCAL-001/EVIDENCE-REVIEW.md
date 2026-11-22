# EVOO build-001 evidence review

Reviewer: Meraki, current ChatGPT/Codex session. Review of owner-uploaded files,
not a second execution of the build or a separate Z review.

## Disposition

Technical evidence review PASS. Recommend accepting this single native-Linux
source-build/two-boot milestone. Mark acceptance, PR merge and M2 manual-console
acceptance remain separate. No repeat build is needed to establish this result.

## Carrier and provenance

Owner uploaded puppf-evoo-build-001-evidence.tar.gz after pasting the final receipt.
Bundle SHA256: 9ca48307557faa006c4d27a1330b8bac6388b1f1471697a09b48541dfe0ba31e.
Retained owner Library file: libfile_231bd08402308191989d5d341688d849.
52 archive members; 16,550,687 total regular-file bytes.
The archive was read without executing its contents or extracting arbitrary paths.
All 45 entries in evidence/evidence-manifest.json were recomputed: exact sizes
and SHA256 values matched, with no mismatches.

Receipt binds the build to b5fef00ef74ac3a0755da269a0bfce80613e4d77,
one attempt, native-local mode. Start 2026-11-22 00:16:14.913749 UTC;
finish 05:24:44.164458 UTC. Total 18,509.250742102 seconds (5h08m29s).
Recorded compile command took 17,970.721263433 seconds (4h59m31s),
with both -j1 and BR2_JLEVEL=1 in the actual recorded argv. Every recorded
host/config/build/audit command has exit0. Laptop fixture log has64 tests PASS.
This is recorded execution evidence, not authenticated live telemetry.

## Source verification

Recomputed included release-key bytes:
085d1b664bc0a900b2c33aa509a7e4d6fa3b6018009cd9d3f8c62a03d7adfa7a,
matching the previously reviewed pin.
Independently reverified the uploaded upstream clearsigned manifest with local
GnuPG in a fresh isolated temporary home/keyring, no automatic key retrieval:
exit0; exact VALIDSIG signer AB07D806D2CE741FB886EE50B025BA8B59C36319.
The resulting plaintext exactly matched the uploaded verified-checksums.txt.
Signed archive SHA256 and runner-recorded downloaded-archive SHA256 both equal
87aaca4164ea9d5c8085854953018263f7963f07c22e73a2a2185cc98c581c34.

Limit: the full downloaded Buildroot/dependency source archives are not inside
this evidence bundle, so their bytes were not independently rehashed in this
review. Source-download binding beyond the signed manifest rests on the
reviewed runner's recorded checks. No signing-policy override used.

## Actual image bytes

| Artifact | Bytes | Recomputed SHA256 |
| --- | ---: | --- |
| bzImage | 3286016 | 75bb3de22351a5e97c601650210dcbdcbf385ad69c9bd1bfb90b4832a628bfe7 |
| rootfs.cpio.gz | 754850 | 2d51be705deca6b606c6e2de15311d7669576b52d12e83801e670981aa1c089e |

Combined4,040,866 bytes. Both hashes match previously accepted build#11 exactly.
This verifies matching output bytes for these two recorded builds on different
hosts; it is not a general reproducibility guarantee or a minimum-RAM result.

## Two boot records, inspected against raw serial logs

| Observation | Run1 | Run2 |
| --- | --- | --- |
| Result | PASS | PASS |
| HELLO guest uptimes | 1,121,241 | 1,121,242 |
| Host heartbeat gaps seconds | 120.029,120.034 | 120.036,120.026 |
| Shell prompt host seconds | 3.208 | 2.762 |
| Split-token output host seconds | 3.218 | 2.797 |
| Timeout | false | false |
| Host stopped QEMU | true | true |
| QEMU return code | 0 | 0 |

Serials contain distinct fresh exact token output, not just echoed probe input.
Each raw log contains one PUPPF_INIT and three sequential HELLO records.
Recorded before/after artifact hashes match the recomputed images and across boots.
QEMU arguments show TCG, one vCPU,128MiB allocated, no NIC, no attached host
drives/shares, direct kernel/initramfs and no reboot.

Known ACPI table initialization errors precede PUPPF_INIT in both raw logs.
They did not block the recorded checks; no claim of warning-free boot.
Minimum RAM, actual guest resident RAM, physical laptop guest boot, persistence
and broad security containment were not measured.

## Next

Preserve successful evidence and build work. Back up this new bundle separately
from the original accepted ZIP. Z can review this receipt and source candidate;
to claim independent binary inspection Z also needs actual bundle access.
Obtain owner milestone disposition before reporting human acceptance.
M2's Ctrl+C/interactive evidence is related but distinct from these automated boots.
No new build, workflow dispatch, paid call, merge or release in this review.
