import json
from pathlib import Path
import subprocess
import sys

from no_model_acceptance import LOG_VERSION, main


def test_cli_nonce_pass_and_echo_failure(tmp_path, capsys):
    nonce = "c" * 32
    output = tmp_path / "serial.log"
    output.write_text(nonce + "\n")
    assert main(["nonce", nonce, str(output)]) == 0
    assert json.loads(capsys.readouterr().out)["valid"]
    output.write_text("printf '%s\\n' '" + nonce + "'\n")
    assert main(["nonce", nonce, str(output)]) == 1
    assert not json.loads(capsys.readouterr().out)["valid"]


def test_cli_ack_and_malformed_input(tmp_path, capsys):
    requests, acks = tmp_path / "requests.json", tmp_path / "acks.json"
    requests.write_text(json.dumps([{"request_id": "r1", "nonce": "a" * 32}]))
    acks.write_text(json.dumps([{"type": "ACK", "request_id": "r1", "nonce": "a" * 32}]))
    assert main(["acks", str(requests), str(acks)]) == 0
    assert json.loads(capsys.readouterr().out)["acknowledgements"] == 1
    acks.write_text('{"type":"ACK","type":"NAK"}')
    assert main(["acks", str(requests), str(acks)]) == 1
    assert not json.loads(capsys.readouterr().out)["valid"]


def test_cli_log_failure_is_valid_format_but_not_success(tmp_path, capsys):
    log = tmp_path / "log.jsonl"
    records = [{"schema_version": LOG_VERSION, "run_id": "r1", "seq": 1, "monotonic_ns": 1, "state": "CREATED"},
               {"schema_version": LOG_VERSION, "run_id": "r1", "seq": 2, "monotonic_ns": 2, "state": "FAILED", "reason": "mock"}]
    log.write_text("".join(json.dumps(r) + "\n" for r in records))
    assert main(["log", str(log)]) == 0
    assert json.loads(capsys.readouterr().out)["successful"] is False
    assert main(["log", str(log), "--require-success"]) == 1
    capsys.readouterr()


def test_script_entrypoint_has_real_exit_status(tmp_path):
    script = Path(__file__).resolve().parents[1] / "no_model_acceptance.py"
    artifact = tmp_path / "artifact"
    artifact.write_bytes(b"mock-image")
    completed = subprocess.run([sys.executable, "-B", str(script), "size", str(artifact)], capture_output=True, text=True)
    assert completed.returncode == 0
    assert json.loads(completed.stdout)["combined_payload_bytes"] == 10
    completed = subprocess.run([sys.executable, "-B", str(script), "size", str(tmp_path / "missing")], capture_output=True, text=True)
    assert completed.returncode == 1
    assert json.loads(completed.stdout)["valid"] is False


def test_cli_new_nonce(capsys):
    assert main(["new-nonce"]) == 0
    assert len(json.loads(capsys.readouterr().out)["nonce"]) == 32
