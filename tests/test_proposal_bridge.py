"""Confirma que propostas de IA continuam inertes e fail-closed."""
import json
import unittest
from pathlib import Path
from mesa_lab.mission_contract import ContractError
from mesa_lab.proposal_bridge import validate_inert_handoff

ROOT = Path(__file__).resolve().parents[1]
FIX = json.loads((ROOT / "fixtures/m1-4/agent_proposal.json").read_text(encoding="utf-8"))
BASE = "fb9d86d3d11419fcbfb7a470b2feebad6aa3f325"
ARGS = {
    "verified_event": FIX["event"], "observed_base_sha": BASE,
    "provider_name": FIX["provider"]["name"],
    "provider_run_id": FIX["provider"]["run_id"],
    "proposal_text": FIX["proposal_text"], "identity_proof": "mock_fixture",
}


class ProposalBridgeTests(unittest.TestCase):
    def assert_blocked(self, **changes):
        with self.assertRaises(ContractError):
            validate_inert_handoff(**{**ARGS, **changes})

    def test_receipt_never_authorizes_execution(self):
        receipt = validate_inert_handoff(**ARGS)
        self.assertEqual(receipt["status"], "validated_not_executed")
        self.assertIs(receipt["execution_authorized"], False)
        self.assertEqual(receipt["identity_proof"], "mock_fixture")

    def test_stable_idempotency_across_json_order(self):
        first = validate_inert_handoff(**ARGS)
        payload = json.loads(FIX["proposal_text"])
        second = validate_inert_handoff(
            **{**ARGS, "proposal_text": json.dumps(payload, sort_keys=True)}
        )
        self.assertEqual(first["idempotency_key"], second["idempotency_key"])

    def test_changed_base_blocks(self):
        self.assert_blocked(observed_base_sha="a" * 40)

    def test_bad_actor_blocks(self):
        self.assert_blocked(verified_event={**FIX["event"], "actor": "outsider"})

    def test_bad_author_blocks(self):
        self.assert_blocked(verified_event={**FIX["event"], "author": "outsider"})

    def test_unexpected_event_field_blocks(self):
        self.assert_blocked(verified_event={**FIX["event"], "shell": "echo bad"})

    def test_bool_issue_number_blocks(self):
        self.assert_blocked(verified_event={**FIX["event"], "issue_number": True})

    def test_unknown_provider_blocks(self):
        self.assert_blocked(provider_name="unverified_provider")

    def test_pathlike_run_id_blocks(self):
        self.assert_blocked(provider_run_id="../../secret")

    def test_false_identity_proof_blocks(self):
        self.assert_blocked(identity_proof="model_self_attested")

    def test_real_github_proof_fails_closed_until_adapter_exists(self):
        self.assert_blocked(identity_proof="verified_github_event")

    def test_markdown_fences_block(self):
        fence = chr(96) * 3
        self.assert_blocked(proposal_text=fence + "json\n" + FIX["proposal_text"] + "\n" + fence)

    def test_shell_command_blocks(self):
        self.assert_blocked(proposal_text="rm -rf /")

    def test_wrong_mission_id_blocks(self):
        payload = json.loads(FIX["proposal_text"])
        payload["mission_id"] = "MESA-CODE-1111"
        self.assert_blocked(proposal_text=json.dumps(payload))

    def test_forged_execution_status_blocks(self):
        payload = json.loads(FIX["proposal_text"])
        payload["status"] = "executed"
        self.assert_blocked(proposal_text=json.dumps(payload))

    def test_unapproved_file_blocks(self):
        payload = json.loads(FIX["proposal_text"])
        payload["files"][".github/workflows/unsafe.yml"] = "name: unsafe\n"
        self.assert_blocked(proposal_text=json.dumps(payload))

    def test_invalid_python_blocks(self):
        payload = json.loads(FIX["proposal_text"])
        payload["files"]["mesa_sandbox/mesa_code_9001.py"] = "def broken(\n"
        self.assert_blocked(proposal_text=json.dumps(payload))

    def test_json_duplicate_key_blocks(self):
        forged = FIX["proposal_text"].replace('"summary":', '"summary":"fake", "summary":')
        self.assert_blocked(proposal_text=forged)

    def test_bad_run_id_type_blocks(self):
        self.assert_blocked(provider_run_id=123)

    def test_paths_are_exact(self):
        receipt = validate_inert_handoff(**ARGS)
        self.assertEqual(receipt["files"], [
            "mesa_sandbox/mesa_code_9001.py",
            "tests/test_mesa_code_9001.py",
        ])


if __name__ == "__main__":
    unittest.main()
