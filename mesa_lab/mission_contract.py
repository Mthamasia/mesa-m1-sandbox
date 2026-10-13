"""Contratos de missão e proposta, sem execução, I/O ou dependências externas.

Validação estrutural NÃO torna o código proposto seguro para execução.
O executor futuro precisará ser isolado e passar por revisão independente.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

PROTOCOL = "MESA-CODE-V1"
OWNER = "Mthamasia"
REPOSITORY = "Mthamasia/mesa-m1-sandbox"
ISSUE_TITLE = "[MESA-CODE] proposta sintética"
MISSION_PATTERN = re.compile(r"MESA-CODE-([0-9]{4})\Z")
SHA_PATTERN = re.compile(r"[0-9a-f]{40}\Z")
MAX_BODY_BYTES = 4096
MAX_SOURCE_BYTES = 4096


class ContractError(ValueError):
    """Entrada inválida: o pedido deve ser bloqueado, não executado."""


@dataclass(frozen=True)
class Mission:
    mission_id: str
    base_sha: str
    task: str
    wall_seconds: int
    max_files_changed: int
    max_diff_lines: int
    source_sha256: str

    @property
    def stem(self) -> str:
        return "mesa_code_" + self.mission_id[-4:].lower()

    @property
    def allowed_paths(self) -> tuple[str, str]:
        return (f"mesa_sandbox/{self.stem}.py", f"tests/test_{self.stem}.py")


def _strict_json(raw: str) -> dict[str, Any]:
    if not isinstance(raw, str) or len(raw.encode("utf-8")) > MAX_BODY_BYTES:
        raise ContractError("Corpo ausente ou grande demais")

    def pairs_unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        parsed: dict[str, Any] = {}
        for key, value in pairs:
            if key in parsed:
                raise ContractError("Chave duplicada no JSON")
            parsed[key] = value
        return parsed

    try:
        value = json.loads(
            raw, object_pairs_hook=pairs_unique,
            parse_constant=lambda _: (_ for _ in ()).throw(ContractError("Número inválido")),
        )
    except (ValueError, TypeError, UnicodeError) as exc:
        raise ContractError("JSON inválido") from exc
    if type(value) is not dict:
        raise ContractError("É necessário um objeto JSON")
    return value


def _fields(value: dict[str, Any], expected: set[str]) -> None:
    if set(value) != expected:
        raise ContractError("Campos faltando ou desconhecidos")


def _bounded_int(value: Any, lo: int, hi: int) -> int:
    if type(value) is not int or not lo <= value <= hi:
        raise ContractError("Limite inválido")
    return value


def parse_issue(*, repository: str, actor: str, author: str,
                title: str, body: str, event: str = "opened") -> Mission:
    """Metadados de identidade DEVEM vir da API autenticada do GitHub."""
    if (repository, actor, author, title, event) != (
        REPOSITORY, OWNER, OWNER, ISSUE_TITLE, "opened"
    ):
        raise ContractError("Autor, origem ou evento não autorizado")
    if not isinstance(body, str) or not body.startswith(PROTOCOL + "\n"):
        raise ContractError("Versão do contrato ausente")
    obj = _strict_json(body[len(PROTOCOL) + 1:])
    _fields(obj, {"protocol", "mission_id", "project", "base_sha",
                  "task_kind", "task", "test_profile", "limits"})
    if obj["protocol"] != PROTOCOL or obj["project"] != "mesa-m1-sandbox":
        raise ContractError("Projeto ou versão não permitidos")
    if obj["task_kind"] != "synthetic_python_change" or obj["test_profile"] != "stdlib-unittest":
        raise ContractError("Perfil de execução não autorizado")
    mid, sha, task = obj["mission_id"], obj["base_sha"], obj["task"]
    if not isinstance(mid, str) or MISSION_PATTERN.fullmatch(mid) is None:
        raise ContractError("ID de missão inválido")
    if not isinstance(sha, str) or SHA_PATTERN.fullmatch(sha) is None:
        raise ContractError("SHA base inválido")
    if not isinstance(task, str) or not 1 <= len(task) <= 500 or any(ord(c) < 32 and c not in '\n\t' for c in task):
        raise ContractError("Descrição inválida")
    limits = obj["limits"]
    if type(limits) is not dict:
        raise ContractError("Limites inválidos")
    _fields(limits, {"wall_seconds", "max_files_changed", "max_diff_lines"})
    wall = _bounded_int(limits["wall_seconds"], 1, 300)
    count = _bounded_int(limits["max_files_changed"], 2, 2)
    lines = _bounded_int(limits["max_diff_lines"], 1, 200)
    return Mission(mid, sha, task, wall, count, lines,
                   hashlib.sha256(body.encode("utf-8")).hexdigest())


def validate_proposal(mission: Mission, raw: str) -> dict[str, Any]:
    """Valida proposta INERTE e retorna recibo; não executa código recebido."""
    obj = _strict_json(raw)
    _fields(obj, {"protocol", "mission_id", "base_sha", "files", "summary"})
    if (obj["protocol"], obj["mission_id"], obj["base_sha"]) != (
        PROTOCOL, mission.mission_id, mission.base_sha
    ):
        raise ContractError("Proposta não corresponde à missão")
    summary = obj["summary"]
    if type(summary) is not str or not 1 <= len(summary) <= 200:
        raise ContractError("Resumo inválido")
    files = obj["files"]
    if type(files) is not dict or set(files) != set(mission.allowed_paths):
        raise ContractError("Paths não permitidos")
    lines = 0
    for path, content in files.items():
        if type(content) is not str or not content.endswith("\n") or not content.strip():
            raise ContractError("Arquivo vazio/inválido")
        if len(content.encode("utf-8")) > MAX_SOURCE_BYTES:
            raise ContractError("Arquivo grande demais")
        try:
            ast.parse(content, filename=path)
        except SyntaxError as exc:
            raise ContractError("Python sintaticamente inválido") from exc
        lines += len(content.splitlines())
    if lines > mission.max_diff_lines:
        raise ContractError("Orçamento de linhas excedido")
    canonical = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "protocol": PROTOCOL,
        "mission_id": mission.mission_id,
        "mission_sha256": mission.source_sha256,
        "proposal_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "files": sorted(files),
        "file_count": len(files),
        "status": "validated_not_executed",
    }
