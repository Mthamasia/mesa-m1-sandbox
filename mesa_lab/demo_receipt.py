"""Demonstração read-only: texto de IA validado sem executar o conteúdo."""
import json
import subprocess
from pathlib import Path

from mesa_lab.proposal_bridge import validate_inert_handoff


def main():
    root = Path(__file__).resolve().parent.parent
    fixture = json.loads(
        (root / "fixtures/m1-4/agent_proposal.json").read_text(encoding="utf-8")
    )
    if fixture["fixture_kind"] != "synthetic_mock_event_not_github_authenticated":
        raise ValueError("Fixture inválida")
    real_sha = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "refs/remotes/origin/main"],
        text=True, timeout=10,
    ).strip()
    receipt = validate_inert_handoff(
        verified_event=fixture["event"],
        observed_base_sha=real_sha,
        provider_name=fixture["provider"]["name"],
        provider_run_id=fixture["provider"]["run_id"],
        proposal_text=fixture["proposal_text"],
        identity_proof="mock_fixture",
    )
    print(json.dumps(receipt, sort_keys=True, ensure_ascii=False))
    if receipt["status"] != "validated_not_executed" or receipt["execution_authorized"]:
        raise RuntimeError("Segurança: proposta não permaneceu inerte")


if __name__ == "__main__":
    main()
