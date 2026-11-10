# Puppf

Puppf is a small, experimental project focused on learning, validation, and disciplined boot testing in a lightweight Linux context.

This repository is not yet a finished distribution, fork, or release artifact. It is a baseline bootstrap and learning environment for packet-based experimentation, evidence tracking, and controlled host-side validation.

## Purpose

- Explore lightweight Linux build and testing workflows
- Practice packet-based validation and acceptance criteria
- Maintain honest evidence before claiming success
- Keep scope bounded and reproducible

## Status

M1 is accepted by Mark after Z's evidence review: [build #11](https://github.com/MarkDude-design/Puppy/actions/runs/41773110103)
compiled successfully and passed two real QEMU serial-shell boots with unchanged
image hashes. The kernel and initramfs total 4,040,866 bytes; QEMU allocated
128 MiB. This establishes the small terminal milestone, not a finished release.

M2 is a review candidate: [launch the accepted image locally](puppy-p0a/LAUNCH.md)
with one Python command and a downloaded evidence ZIP. The wrapper's first-user
interactive QEMU demo remains pending; artifact validation and local process
cleanup tests are separate from the earlier hosted guest boots.

## Notes

Puppf is a working name and educational foundation for experimentation, not a completed operating system distribution.

## Method lineage

This experiment draws inspiration from **Puppy Linux and Barry Kauler's** small, user-directed, rebuildable Linux approach. It is not designated a Puppy fork, derivative distribution, or Fedora distribution, and no affiliation or endorsement is implied.
