# Puppy — experimental learning workspace

**Working project name: Puppf.** This public repository is an early, throwaway learning experiment, not a release.

We are practicing a verifiable, low-cost engineering workflow while exploring a small RAM-first Linux environment. Our first separate experiments are:

- **P0a / boot spike:** offline QEMU boot of kernel + compressed initramfs + static BusyBox; serial shell; three genuine 120-second HELLO messages.
- **S0 / diode:** host-side, local-file message exchange with bounded messages, transcript, and STOP. No QEMU or model calls in its initial mock tier.

Each experiment has its own hashed work packet and independent acceptance. A boot is **not** proof of sandbox security. Mock messages are **not** proof that two models communicated.

## Lineage and limits

Puppy Linux, created by **Barry Kauler**, inspires our preference for small, understandable, RAM-oriented systems that users can rebuild and own. We acknowledge that lineage without claiming affiliation, endorsement, compatibility, or a derivative release. **This project is not yet designated a Puppy Linux fork or Fedora distribution.** Buildroot is a provisional tool for the first disposable boot spike, not an adopted long-term distribution architecture.

No binaries, networking, model credentials, device writes, metered services, or releases are authorized merely by the presence of a work packet. Mark retains execution, spending, acceptance, merge, and public-release gates. Codex is the bounded implementation worker; Meraki leads the technical method and evidence review; Z coordinates and independently reviews ordinary outcomes.

## Starting point

The Castle workflow pilot remains in [lightbringers-castle PR #7](https://github.com/MarkDude-design/lightbringers-castle/pull/7), inspected at commit `0229aae61eaa6934c293335f66a0d085415a8c07`. Workflow components will be ported deliberately, with fresh target-repository packet hashes and baseline receipts, rather than copying the old execution packet as authority.

See future draft branches/PRs for work-in-progress files. Nothing in this README claims a successful build or guest boot.
