"""Valida texto de IA como proposta INERTE; nunca aplica nem executa código."""
import hashlib
import json
import re
from mesa_lab.mission_contract import ContractError, parse_issue, validate_proposal

PROVIDERS = frozenset({"chatgpt_manual_text", "claude_text", "codex_text"})
RUN_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{2,79}\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")
EVENT_KEYS = {"repository", "actor", "author", "title", "event", "issue_number", "body"}


def validate_inert_handoff(*, verified_event, observed_base_sha, provider_name,
                           provider_run_id, proposal_text, identity_proof):
    """Gera recibo idempotente. Identidade deve vir do chamador, não da IA."""
    # Até existir adapter GitHub autenticado, falhar fechado para qualquer prova real.
    if identity_proof != "mock_fixture":
        raise ContractError("Autenticação real ainda não implementada")
    if type(verified_event) is not dict or set(verified_event) != EVENT_KEYS:
        raise ContractError("Envelope do evento inválido")
    number = verified_event["issue_number"]
    if type(number) is not int or not 1 <= number <= 999999:
        raise ContractError("Número da Issue inválido")
    if type(observed_base_sha) is not str or SHA.fullmatch(observed_base_sha) is None:
        raise ContractError("SHA observada inválida")
    # M1-4 só permite a fixture local; Claude/Codex reais exigem autenticação própria.
    if type(provider_name) is not str or provider_name != "chatgpt_manual_text":
        raise ContractError("Provider real ainda não integrado")
    if type(provider_run_id) is not str or RUN_ID.fullmatch(provider_run_id) is None:
        raise ContractError("Run ID inválido")
    if type(proposal_text) is not str:
        raise ContractError("Proposta não textual")
    mission = parse_issue(
        repository=verified_event["repository"], actor=verified_event["actor"],
        author=verified_event["author"], title=verified_event["title"],
        event=verified_event["event"], body=verified_event["body"],
    )
    if mission.base_sha != observed_base_sha:
        raise ContractError("Revisão base divergiu; interromper")
    checked = validate_proposal(mission, proposal_text)
    stable = json.dumps(
        [verified_event["repository"], number, mission.mission_id,
         mission.source_sha256, checked["proposal_sha256"]],
        ensure_ascii=False, separators=(",", ":"),
    )
    return {
        "protocol": "MESA-PROPOSAL-RECEIPT-V1",
        "mission_id": mission.mission_id, "issue_number": number,
        "base_sha": observed_base_sha, "source_sha256": mission.source_sha256,
        "proposal_sha256": checked["proposal_sha256"],
        "provider": provider_name, "provider_run_id": provider_run_id,
        "identity_proof": identity_proof,
        "idempotency_key": hashlib.sha256(stable.encode()).hexdigest(),
        "file_count": checked["file_count"], "files": checked["files"],
        "status": "validated_not_executed", "execution_authorized": False,
    }
