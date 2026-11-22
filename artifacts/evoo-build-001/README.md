# EVOO build-001 image files

Uploaded by Meraki at Mark's request so Z can download and independently inspect the actual binaries. These are the two exact image members read from the owner's verified local evidence archive, not a new build or a release.

Build checkout: b5fef00ef74ac3a0755da269a0bfce80613e4d77.
Evidence archive SHA256: 9ca48307557faa006c4d27a1330b8bac6388b1f1471697a09b48541dfe0ba31e.
The private/full logs archive is not published here.

Files: bzImage (3286016 bytes), rootfs.cpio.gz (754850 bytes).
Run sha256sum -c SHA256SUMS after downloading both. Both image SHA256 values match accepted build #11.

Build recipes/configuration and pinned upstream source/authentication details are under puppy-p0a/ at the build checkout. Linux6.18.7 and BusyBox1.38.0 were built through authenticated Buildroot2026.08. Upstream sources: https://buildroot.org/downloads/buildroot-2026.08.tar.xz ; https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.18.7.tar.xz ; https://busybox.net/downloads/busybox-1.38.0.tar.bz2 . Existing upstream licenses apply; this upload grants no new license.

Evidence review: docs/workflow/runs/PUPPF-LOCAL-001/EVIDENCE-REVIEW.md on the parent branch. Upload/access is not proof Z has downloaded, verified or booted these files. No merge, release, rebuild or owner acceptance is implied.
