# M1-3: fronteira entre IA e executor (LABORATÓRIO)

Este contrato é uma **base testável**, não um executor de código nem a integração Claude/Codex pronta. A MESA ativa na VPS permanece report_only. Não foram adicionadas chaves, gastos, acesso aos quatro projetos nem uma API pública de escrita.

## Contrato MESA-CODE-V1

Issue autorizada com título `[MESA-CODE] proposta sintética` e corpo com a primeira linha literal `MESA-CODE-V1` seguida de **um único objeto JSON** contendo:

- `protocol`: `MESA-CODE-V1`
- `mission_id`: `MESA-CODE-0008` (4 dígitos)
- `project`: `mesa-m1-sandbox`
- `base_sha`: SHA Git completo de 40 hexadecimais minúsculos
- `task_kind`: `synthetic_python_change`
- `task`: descrição textual até 500 caracteres, tratada **somente como dados**
- `test_profile`: `stdlib-unittest` (identificador fixo, não comando)
- `limits`: `wall_seconds` 1–300, `max_files_changed` exatamente 2, `max_diff_lines` até 200.

Verifica também metadados do evento GitHub: repositório, autor e ator `Mthamasia`, título e evento `opened`. **O corpo da Issue não é fonte confiável de identidade.** O código não consulta o GitHub: o chamador futuro deve fornecer dados de evento autenticados, não texto inventado.

Uma proposta inerte contém os mesmos IDs e dois arquivos de texto exatamente nos caminhos autorizados `mesa_sandbox/mesa_code_0008.py` e `tests/test_mesa_code_0008.py`. Validamos estrutura, sintaxe e orçamento; emitimos SHA-256 canônico para rastrear a proposta.

**AVISO DE SEGURANÇA:** `ast.parse` apenas verifica sintaxe. Código Python sintaticamente válido pode ser malicioso. O resultado `validated_not_executed` NÃO autoriza escrita em branch, shell nem execução de testes de código de IA. Ainda é obrigatório um executor **isolado de produção**, credenciais mínimas, limites de recursos, checkout em commit fixado e revisão de proveniência. Nenhum workflow dispara a partir destas Issues `[MESA-CODE]` neste estágio.

## Evolução para IA de verdade

1. Integrar um produtor de proposta por modelo com autenticação e orçamento aprovados. A assinatura Claude.ai na VPS não deve ter seus tokens copiados para runners públicos.
2. Checar o `base_sha` contra HEAD do PR/repo, aplicar mudanças unicamente em workspace descartável, sem acesso a secrets e sem token de escrita; testes sob perfil predefinido.
3. Separar auditor independente de executor; registrar hash, custo real, origem do agente, número de tentativas e estado; publicador PR com identidade segregada, sem merge.
4. Para observabilidade ao vivo da VPS, criar telemetria **privada/autenticada** fora do site GitHub Pages público.

Referência de planejamento: https://github.com/Mthamasia/agentproof-bridge/issues/26
