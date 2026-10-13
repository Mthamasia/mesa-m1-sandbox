# MESA M1 — Sandbox de testes

Laboratório **público e sintético** da MESA Viva para validar um runner temporário do GitHub Actions.

Este repositório não contém códigos, dados, tokens, credenciais ou configurações de produção dos projetos Alpha Hunter X, Private Match, AgentProof ou MEMNX.

## Piloto M1-0

- O workflow `MESA M1 | Testes sintéticos` só pode ser iniciado manualmente (`workflow_dispatch`).
- A execução usa um runner padrão `ubuntu-24.04`, temporário, hospedado pelo GitHub — **não** uma VPS do proprietário.
- Apenas Python da biblioteca padrão: sem `pip install`, sem chamadas de IA, sem tokens de API personalizados, sem deploy e sem envio de mensagens.
- O `GITHUB_TOKEN` do workflow possui apenas `contents: read`; o checkout não preserva credenciais.
- Limite do job: 5 minutos. Apenas uma execução por vez para esse workflow.
- O código de teste foi escrito exclusivamente para este laboratório público.

### Como validar

Abra **Actions → MESA M1 | Testes sintéticos → Run workflow → Run workflow**, selecionando a branch `main`.

O resultado esperado é um job `synthetic-tests` verde, com seis testes unitários passando. Inspecione os logs e a duração antes de considerar o piloto concluído.

### Limites

Este teste **não** comprova execução autônoma de código por Claude/Codex, segurança de agentes com shell, nem orquestração multiprojetos. A evolução dessas capacidades depende de uma etapa separada, com autenticação, isolamento e testes de segurança próprios.

Acompanhamento de arquitetura: [MESA CORE #26](https://github.com/Mthamasia/agentproof-bridge/issues/26).
