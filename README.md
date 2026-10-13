# MESA M1 — Sandbox de testes

Laboratório **público e sintético** da MESA Viva para validar um runner temporário do GitHub Actions.

Este repositório não contém códigos, dados, tokens, credenciais ou configurações de produção dos projetos Alpha Hunter X, Private Match, AgentProof ou MEMNX.

## M1-0 — primeiro teste de infraestrutura

- O workflow `MESA M1 | Testes sintéticos` pode ser iniciado manualmente (`workflow_dispatch`).
- A execução usa um runner padrão `ubuntu-24.04`, temporário, hospedado pelo GitHub — **não** uma VPS do proprietário.
- Apenas Python da biblioteca padrão: sem `pip install`, sem chamadas de IA, sem tokens de API personalizados, sem deploy e sem envio de mensagens.
- O `GITHUB_TOKEN` do workflow possui apenas `contents: read`; o checkout não preserva credenciais.
- Limite do job: 5 minutos; concorrência controlada por referência.

Primeira execução: [run #38434642630](https://github.com/Mthamasia/mesa-m1-sandbox/actions/runs/38434642630), 6/6 testes PASS.

## M1-1 — alteração via Pull Request

- Uma branch isolada acrescenta a função pura `apply_discount_cents`, com validação e arredondamento por aritmética inteira, além de novos testes.
- O mesmo workflow passa a executar automaticamente em `pull_request` para `main` **somente** quando mudarem o código sintético, os testes ou o próprio workflow.
- A alteração fica no PR até revisão; **nenhum merge ou deploy automático**.

### Limites

Este teste **não** comprova execução autônoma de código por Claude/Codex, segurança de agentes com shell, nem orquestração multiprojetos. A evolução dessas capacidades depende de uma etapa separada, com autenticação, isolamento e testes de segurança próprios.

Acompanhamento de arquitetura: [MESA CORE #26](https://github.com/Mthamasia/agentproof-bridge/issues/26).
