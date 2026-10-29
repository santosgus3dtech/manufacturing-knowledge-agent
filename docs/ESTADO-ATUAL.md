# Estado atual — Manufacturing Knowledge Agent

Revisão documental: **13/10/2026**, America/Sao_Paulo. Git inicial limpo em `main`, HEAD `e6263ff`.

## Observado

`backend/pyproject.toml` descreve versão 0.1.0, Python >=3.11, FastAPI, MCP, OpenAI, Pydantic e Uvicorn. `frontend/package.json` declara React/TypeScript/Vite e scripts de lint/build.

`backend/manufacturing_agent/api.py` declara modo `synthetic-demo` no health, endpoints de dashboard, máquinas, conhecimento, perguntas, materiais, estimativas, atividade e avaliações. A API chama serviços compartilhados. `pricing.py` usa Decimal e arredondamento explícito para estimativas, mantendo o cálculo separado da resposta generativa.

Existem testes de API, MCP, pricing e retrieval. O README descreve fixtures fictícias, fallback local e embeddings opcionais. Nenhum dado de runtime foi lido e nenhuma API foi chamada.

## Identidade e fontes anteriores

Esta cópia difere da variante `-live` em HEAD, versão, descrição e integração de máquinas. O demo continua documentado como sintético; não foi assumido o estado da edição privada ou de serviços remotos.

## Operação identificada

O README orienta backend por `uvicorn manufacturing_agent.api:app --reload`, frontend por `pnpm run dev`, MCP por `python -m manufacturing_agent.mcp_server` e Docker por Compose. Verificações existentes: Ruff, `pytest backend/tests`, lint e build frontend. Pré-requisitos Python >=3.11 e ambiente Node/pnpm para frontend.

Todos os comandos/testes: **não executado nesta tarefa**. Dependências não foram instaladas; ambiente real não lido.

## Retomada

Última etapa comprovada: organização e validação documental local, com fontes existentes preservadas. Métricas de retrieval, custos estimados e execução da IA não foram revalidados.

Sugestões não aprovadas:

1. Definir a próxima tarefa na edição correta, mantendo o demo sintético.
2. Em validação autorizada, executar avaliação/testes e registrar o dataset e resultados efetivos.
3. Conferir rótulos de métricas da API/UI antes de alterar a interpretação: `citation_precision` no dashboard recebe `recall_at_3` no trecho observado.

Veja [arquitetura](ARQUITETURA.md) e [índice](INDEX.md).
