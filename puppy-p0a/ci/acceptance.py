"""Acceptance over captured guest lines and host-monotonic arrival times.

Fixture success validates this checker, not a guest. Only the QEMU harness may
label a captured observation as a real boot; human acceptance stays pending.
"""
import math
import re


HELLO = re.compile(r"HELLO seq=([1-9][0-9]*) uptime_s=(0|[1-9][0-9]*)")
PROMPT = b"PUPPF# "


def seconds(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and value >= 0)


def check_run(events, token, prompt_at, token_sent_at, elapsed,
              timed_out=False, qemu_exited=False):
    errors = []
    if not seconds(elapsed) or elapsed > 390 or timed_out:
        errors.append("run watchdog exceeded or invalid elapsed time")
    if qemu_exited:
        errors.append("QEMU exited before host acceptance/termination")
    if not seconds(prompt_at) or prompt_at > 90:
        errors.append("serial shell prompt missing or late")
    if not seconds(token_sent_at) or (seconds(prompt_at) and token_sent_at < prompt_at):
        errors.append("shell token was not sent after prompt")
    if not isinstance(token, str) or not re.fullmatch(r"PUPPF_TOKEN_[0-9a-f]{32}", token):
        errors.append("invalid host-generated shell token")
    hello = []
    token_times = []
    init_count = 0
    previous = 0.0
    for event in events:
        text, at = event.get("text"), event.get("at_s")
        if (not isinstance(text, str) or not seconds(at) or at < previous
                or (seconds(elapsed) and at > elapsed)):
            errors.append("malformed or out-of-order host arrival record")
            continue
        previous = at
        if text == "PUPPF_INIT":
            init_count += 1
        if any(marker in text for marker in
               ("Kernel panic", "reboot: Restarting", "PUPPF_SHELL_RESTART")):
            errors.append("guest panic, reboot or shell restart")
        # Full lines only. A token appearing in a command echo never passes.
        if text == token:
            token_times.append(at)
        if text.startswith("HELLO"):
            match = HELLO.fullmatch(text)
            if not match:
                errors.append("malformed HELLO record")
            else:
                hello.append({"seq": int(match[1]), "uptime_s": int(match[2]), "at_s": at})
    if init_count != 1:
        errors.append("expected exactly one init marker")
    if (len(token_times) != 1 or token_times[0] > 90
            or not seconds(token_sent_at) or token_times[0] < token_sent_at):
        errors.append("fresh shell token output missing, duplicate, early or late")
    if [h["seq"] for h in hello] != [1, 2, 3]:
        errors.append("expected exactly HELLO sequences 1,2,3")
    if hello and hello[0]["uptime_s"] > 15:
        errors.append("first HELLO is later than absolute guest uptime 15")
    guest_gaps, host_gaps = [], []
    for a, b in zip(hello, hello[1:]):
        guest_gaps.append(b["uptime_s"] - a["uptime_s"])
        host_gaps.append(b["at_s"] - a["at_s"])
    if any(not 115 <= gap <= 125 for gap in guest_gaps):
        errors.append("guest uptime interval outside 115..125 seconds")
    if any(not 105 <= gap <= 150 for gap in host_gaps):
        errors.append("host arrival interval outside 105..150 seconds")
    return {"status": "FAIL" if errors else "PASS", "errors": errors,
            "hello": hello, "guest_gaps_s": guest_gaps, "host_gaps_s": host_gaps,
            "shell_prompt_at_s": prompt_at, "shell_token_output_at_s": token_times,
            "elapsed_s": elapsed, "watchdog_s": 390,
            "timed_out": timed_out, "qemu_exited_before_host_stop": qemu_exited}
