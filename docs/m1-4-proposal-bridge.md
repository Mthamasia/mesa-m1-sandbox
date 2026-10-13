# M1-4 — Proposta de IA como texto inerte

A entrega liga o contrato MESA-CODE-V1 (PR #9) a um adaptador que valida propostas e emite recibo com SHA-256 e chave de idempotência. NÃO executa, importa nem aplica o Python fornecido pela IA.

## Demonstração reproduzível

- `fixtures/m1-4/agent_proposal.json` contém uma **proposta sintética redigida nesta sessão do ChatGPT** e um envelope de Issue **SIMULADO**. O campo de prova de identidade deve ser `mock_fixture`; não atesta autoria real no GitHub.
- `python3 -m mesa_lab.demo_receipt` lê a fixture em CI e compara o SHA base da missão com o verdadeiro `origin/main` disponível no checkout. Se a base tiver mudado, falha fechado.
- O resultado deve ser `validated_not_executed`, `execution_authorized: false`, com caminhos fixos e hashes auditáveis.
- O provider e o run_id são metadados informados pelo adaptador externo. Não podem ser considerados verificados só porque um modelo os escreveu.
- `ast.parse` no contrato anterior checa somente sintaxe; não garante que o código seja seguro. NÃO rodamos testes do conteúdo gerado por IA nesta fase.

## Próximos gates, ainda bloqueados

Um produtor real de propostas por Claude/Codex requer autenticação e orçamento aprovados; não exportar OAuth Claude.ai da VPS para GitHub Actions. A validação real de autoria GitHub deve ocorrer no adaptador de evento, não na fixture. Código de IA só pode ser aplicado e testado em executor isolado, sem credenciais de escrita ou acesso às VPS. Auditor independente e publicador PR separado antes de permitir entregas reais.

Este PR é de laboratório público, sem secrets, sem API paga, sem alterações na VPS e sem merge/deploy.
