import pytest

import no_model_acceptance as acceptance
from no_model_acceptance import (
    AcceptanceError, check_correlated_acks, check_nonce, check_nonce_output, nonce_probe,
)


NONCE = "0123456789abcdef" * 2


@pytest.fixture
def exchange():
    requests = [{"request_id": "r1", "nonce": "a" * 32},
                {"request_id": "r2", "nonce": "b" * 32}]
    acks = [{"type": "ACK", **request} for request in requests]
    return requests, acks


def test_nonce_generation_uses_fresh_random_challenges(monkeypatch):
    values = iter(["a" * 32, "b" * 32])
    monkeypatch.setattr(acceptance.secrets, "token_hex", lambda size: next(values) if size == 16 else None)
    assert acceptance.new_nonce() != acceptance.new_nonce()


def test_matching_nonce():
    assert check_nonce(NONCE, NONCE) is None


@pytest.mark.parametrize("received", ["b" * 32, "", None, True, 42, "x\ny", "é", "x" * 129])
def test_wrong_or_malformed_nonce(received):
    with pytest.raises(AcceptanceError):
        check_nonce(NONCE, received)


def test_probe_command_and_output_are_separate():
    command = nonce_probe(NONCE)
    assert NONCE not in command
    assert command.startswith("printf ")
    assert check_nonce_output(NONCE, command + "\n" + NONCE + "\n")["valid"]


@pytest.mark.parametrize("output", [
    "", NONCE, NONCE + "\n" + NONCE + "\n", "PUPPF# " + NONCE + "\n",
    "printf '%s\\n' '" + NONCE + "'\n", "ACK\n", " " + NONCE + "\n",
    "\v" + NONCE + "\v\n", "\u2028" + NONCE + "\u2028\n",
])
def test_missing_duplicate_truncated_or_echo_only_output(output):
    with pytest.raises(AcceptanceError):
        check_nonce_output(NONCE, output)


def test_crlf_output():
    assert check_nonce_output(NONCE, NONCE + "\r\n")["valid"]


def test_unsuitable_probe_nonce():
    with pytest.raises(AcceptanceError):
        nonce_probe("x")


def test_acks_are_correlated_by_id_not_arrival_order(exchange):
    requests, acks = exchange
    assert check_correlated_acks(requests, list(reversed(acks)))["acknowledgements"] == 2


def test_missing_ack(exchange):
    requests, acks = exchange
    with pytest.raises(AcceptanceError, match="missing ACK"):
        check_correlated_acks(requests, acks[:1])


def test_duplicate_ack(exchange):
    requests, acks = exchange
    with pytest.raises(AcceptanceError, match="duplicate ACK"):
        check_correlated_acks(requests, acks + acks[:1])


def test_unknown_ack(exchange):
    requests, acks = exchange
    acks[0]["request_id"] = "old-run"
    with pytest.raises(AcceptanceError, match="unsolicited or stale"):
        check_correlated_acks(requests, acks)


def test_wrong_nonce_and_crossed_correlations(exchange):
    requests, acks = exchange
    acks[0]["nonce"], acks[1]["nonce"] = acks[1]["nonce"], acks[0]["nonce"]
    with pytest.raises(AcceptanceError, match="nonce mismatch"):
        check_correlated_acks(requests, acks)


def test_unconditional_ack_cannot_pass_two_different_inputs(exchange):
    requests, acks = exchange
    acks[1]["nonce"] = acks[0]["nonce"]
    with pytest.raises(AcceptanceError, match="nonce mismatch"):
        check_correlated_acks(requests, acks)


@pytest.mark.parametrize("ack", ["ACK", {}, {"type": "ACK"},
    {"type": "NAK", "request_id": "r1", "nonce": "a" * 32},
    {"type": "ACK", "request_id": "r1", "nonce": "a" * 32, "success": True}])
def test_malformed_ack_contract(exchange, ack):
    with pytest.raises(AcceptanceError):
        check_correlated_acks(exchange[0], [ack])


@pytest.mark.parametrize("kind", ["duplicate-id", "reused-nonce", "extra-field", "invalid-id"])
def test_invalid_request_batch(exchange, kind):
    requests, acks = exchange
    if kind == "duplicate-id":
        requests[1]["request_id"] = requests[0]["request_id"]
    elif kind == "reused-nonce":
        requests[1]["nonce"] = requests[0]["nonce"]
    elif kind == "extra-field":
        requests[0]["metadata"] = "not in contract"
    else:
        requests[0]["request_id"] = "bad\nid"
    with pytest.raises(AcceptanceError):
        check_correlated_acks(requests, acks)


def test_empty_exchange_is_not_acceptance():
    with pytest.raises(AcceptanceError):
        check_correlated_acks([], [])
