# Arquitetura e regras — Manufacturing Knowledge Agent

Fontes: `README.md`, manifests backend/frontend, `backend/manufacturing_agent/api.py` e `pricing.py`.

UI React → FastAPI → serviços compartilhados. O README também descreve MCP sobre os mesmos serviços, com ferramentas de busca, status, estimativa e diagnóstico, recursos e prompt de triagem.

A API acessa `services.retriever`, `services.machines`, `services.agent`, `services.activity` e `services.evaluations`. Conhecimento e fixtures têm diretórios próprios; `evals/` é a base documentada de avaliação. A leitura atual não executou avaliação nem abriu dados de runtime.

## Regras observadas

- Pesquisa exige texto entre 2 e 500 caracteres; `top_k` é limitado entre 1 e 10 no endpoint.
- `estimate_quote` normaliza material e rejeita tipos fora de `MATERIALS`.
- O custo soma material, energia, máquina, trabalho e embalagem; aplica reserva de falha e percentual sobre custo. O parâmetro `margin_percent` é usado como multiplicador sobre custo no código, sem inferir uma decisão comercial.
- Cálculo usa Decimal e retorna valores serializáveis; não depende do texto gerado pelo agente.
- A API marca máquinas como demonstração sintética. Não atribuir a estes dados condição real de impressoras.
- O README prevê OpenAI opcional e modo local; a configuração efetiva permanece desconhecida.

Nenhuma escolha tecnológica foi transformada em justificativa histórica. [Estado atual](ESTADO-ATUAL.md) registra lacunas e sugestões.
