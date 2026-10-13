"""Cenários negativos e positivos do contrato M1-3 (sem IA ou rede)."""
import json
import unittest

from mesa_lab.mission_contract import ContractError, parse_issue, validate_proposal

SHA = "a" * 40
META = {"repository": "Mthamasia/mesa-m1-sandbox", "actor": "Mthamasia",
        "author": "Mthamasia", "title": "[MESA-CODE] proposta sintética"}
BASE = {"protocol": "MESA-CODE-V1", "mission_id": "MESA-CODE-0008",
        "project": "mesa-m1-sandbox", "base_sha": SHA,
        "task_kind": "synthetic_python_change", "task": "Criar módulo sintético com testes",
        "test_profile": "stdlib-unittest",
        "limits": {"wall_seconds": 120, "max_files_changed": 2, "max_diff_lines": 40}}


def issue_body(payload=None):
    return "MESA-CODE-V1\n" + json.dumps(BASE if payload is None else payload)


def proposal(mission):
    return {"protocol": "MESA-CODE-V1", "mission_id": mission.mission_id,
            "base_sha": mission.base_sha, "summary": "Implementação sintética",
            "files": {mission.allowed_paths[0]: "def answer():\n    return 42\n",
                      mission.allowed_paths[1]: "def test_answer():\n    assert 42 == 42\n"}}


class IssueContractTests(unittest.TestCase):
    def test_valid_mission(self):
        m = parse_issue(**META, body=issue_body())
        self.assertEqual(m.allowed_paths, ("mesa_sandbox/mesa_code_0008.py", "tests/test_mesa_code_0008.py"))
        self.assertEqual(m.wall_seconds, 120)

    def test_wrong_actor(self):
        with self.assertRaises(ContractError):
            parse_issue(**{**META, "actor": "stranger"}, body=issue_body())

    def test_wrong_author(self):
        with self.assertRaises(ContractError):
            parse_issue(**{**META, "author": "stranger"}, body=issue_body())

    def test_wrong_repo(self):
        with self.assertRaises(ContractError):
            parse_issue(**{**META, "repository": "Mthamasia/agentproof-bridge"}, body=issue_body())

    def test_wrong_event(self):
        with self.assertRaises(ContractError):
            parse_issue(**META, event="edited", body=issue_body())

    def test_unknown_field(self):
        with self.assertRaises(ContractError):
            parse_issue(**META, body=issue_body({**BASE, "shell": "rm -rf /"}))

    def test_duplicate_json_key(self):
        with self.assertRaises(ContractError):
            parse_issue(**META, body='MESA-CODE-V1\n{"project":"a","project":"b"}')

    def test_bad_sha(self):
        with self.assertRaises(ContractError):
            parse_issue(**META, body=issue_body({**BASE, "base_sha": "main"}))

    def test_bool_as_limit(self):
        b = {**BASE, "limits": {**BASE["limits"], "wall_seconds": True}}
        with self.assertRaises(ContractError):
            parse_issue(**META, body=issue_body(b))

    def test_unbounded_limit(self):
        b = {**BASE, "limits": {**BASE["limits"], "wall_seconds": 9999}}
        with self.assertRaises(ContractError):
            parse_issue(**META, body=issue_body(b))

    def test_unapproved_profile(self):
        with self.assertRaises(ContractError):
            parse_issue(**META, body=issue_body({**BASE, "test_profile": "bash:curl"}))

    def test_non_str_task(self):
        with self.assertRaises(ContractError):
            parse_issue(**META, body=issue_body({**BASE, "task": ["ls", "-la"]}))


class ProposalContractTests(unittest.TestCase):
    def setUp(self):
        self.m = parse_issue(**META, body=issue_body())
        self.p = proposal(self.m)

    def test_valid_proposal_receipt(self):
        r = validate_proposal(self.m, json.dumps(self.p))
        self.assertEqual(r["status"], "validated_not_executed")
        self.assertEqual(r["file_count"], 2)
        self.assertEqual(len(r["proposal_sha256"]), 64)

    def test_same_proposal_same_digest(self):
        a = validate_proposal(self.m, json.dumps(self.p))
        b = validate_proposal(self.m, json.dumps(self.p, sort_keys=True))
        self.assertEqual(a["proposal_sha256"], b["proposal_sha256"])

    def test_disallow_dotgithub_path(self):
        self.p["files"][".github/workflows/backdoor.yml"] = "x: y\n"
        with self.assertRaises(ContractError):
            validate_proposal(self.m, json.dumps(self.p))

    def test_disallow_parent_traversal(self):
        self.p["files"]["../../private.py"] = "hello = True\n"
        with self.assertRaises(ContractError):
            validate_proposal(self.m, json.dumps(self.p))

    def test_disallow_mission_id_mismatch(self):
        self.p["mission_id"] = "MESA-CODE-0009"
        with self.assertRaises(ContractError):
            validate_proposal(self.m, json.dumps(self.p))

    def test_reject_invalid_python(self):
        self.p["files"][self.m.allowed_paths[0]] = "def broken(\n"
        with self.assertRaises(ContractError):
            validate_proposal(self.m, json.dumps(self.p))

    def test_reject_excessive_lines(self):
        self.p["files"][self.m.allowed_paths[0]] = "x = 1\n" * 40
        with self.assertRaises(ContractError):
            validate_proposal(self.m, json.dumps(self.p))

    def test_reject_duplicate_key(self):
        raw = json.dumps(self.p).replace('"summary":', '"summary":"fake", "summary":')
        with self.assertRaises(ContractError):
            validate_proposal(self.m, raw)


if __name__ == "__main__":
    unittest.main()
