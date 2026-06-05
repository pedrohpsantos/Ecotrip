# 🌱 EcoTrip Agent

> Agente de IA que estima o impacto ambiental de viagens, compara alternativas sustentáveis
> e gera relatórios estruturados para ajudar o usuário a tomar decisões mais conscientes.

Projeto de conclusão do curso **"Do Prompt ao Agente"** — CI&T Academy / DIO.
Desenvolvido com **Google ADK** e técnicas de **Engenharia de Prompt** aplicadas.

---

## Arquitetura

```
ecotrip/
├── ecotrip_agent/
│   ├── __init__.py        # Exporta root_agent
│   ├── agent.py           # Definição do Agente (Google ADK)
│   ├── prompts.py         # System Prompt (Role + CoT + Few-Shot + Guardrails)
│   ├── tools.py           # Ferramentas: get_emission_factor, calculate_carbon_footprint, get_transport_alternatives
│   └── models.py          # Schemas Pydantic (Structured Outputs)
├── data/
│   └── emission_factors.json  # Fatores de emissão IPCC/ICAO/CETESB
├── tests/
│   ├── __init__.py
│   └── test_tools.py      # Testes unitários das ferramentas
├── .env                   # Chaves de API (NUNCA commitar)
├── .env.example           # Template seguro para onboarding
├── .gitignore
├── requirements.txt
└── README.md
```

### Fluxo ReAct do Agente

```
User Input
    │
    ▼
[Thought] → Identifica origem, destino, transporte e passageiros
    │
    ▼
[Action] → get_emission_factor(transport_mode)
    │
    ▼
[Action] → calculate_carbon_footprint(distance_km, mode, passengers, round_trip)
    │
    ▼
[Action] → get_transport_alternatives(current_mode, distance_km, passengers)
    │
    ▼
[Final Answer] → Resposta conversacional + EcoTripReport (JSON estruturado)
```

---

## Conceitos do Curso Aplicados

| Conceito | Onde | Módulo |
|----------|------|--------|
| System Prompt com Role + CoT + Guardrails | `prompts.py` | 4.1.2 / 5.1.3 |
| Few-Shot Prompting com exemplos ReAct | `prompts.py` | 4.2.3 |
| Chain-of-Thought (Passo 1→5) | `ECOTRIP_SYSTEM_PROMPT` | 4.2.3 |
| Negative Prompting (guardrails) | Seção Guardrails do prompt | 4.2.3 |
| Function Calling com descrições precisas | `tools.py` (docstrings) | 5.1.4 |
| Structured Outputs (Pydantic) | `models.py` | 5.4.1 |
| Validação de ferramentas (anti-alucinação) | `tools.py` (`_emission_rating`, validações) | 5.1.5 |
| Formato de Saída especificado | Seção "Formato de Saída" do prompt | 4.1.2 |
| Arquitetura ADK (name = pasta) | `agent.py` | 5.4.1 |

---

## Setup

### Pré-requisitos
- Python 3.11+
- Conta no [Google AI Studio](https://aistudio.google.com) com API Key ativa

### Instalação

```bash
# Clone e acesse o projeto
git clone https://github.com/seu-usuario/ecotrip-agent
cd ecotrip

# Crie e ative o ambiente virtual
uv init

# Instale as dependências
uv add -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com sua GOOGLE_API_KEY
```

### Variáveis de Ambiente

```env
# .env.example — copie para .env e preencha os valores reais
GOOGLE_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-2.5-flash
```

> ⚠️ **Nunca faça commit do arquivo `.env`.** O `.gitignore` já o exclui — verifique antes de qualquer push.

---

## Uso

### Via Google ADK Web UI

```bash
uv run adk web
```

Acesse `http://localhost:8080` e selecione `ecotrip_agent`.

### Via Terminal (ADK CLI)

```bash
uv run adk run ecotrip_agent
```

### Exemplos de Input

```
"Fui de São Paulo para o Rio de Janeiro de carro sozinho, ida e volta."

"Quanto emite um voo de Fortaleza para Manaus?"

"Viajo de Curitiba para São Paulo toda semana de ônibus. Qual é meu impacto mensal?"

"Comparando carro e trem de SP para Campinas, qual é mais sustentável?"
```

---

## Testes

```bash
uv run pytest tests/ -v
```

---

## Landing Page (Calculadora UI)

O projeto também conta com uma interface gráfica interativa (Landing Page) que recria a lógica de cálculo do agente diretamente no navegador, o que a torna ideal para ser hospedada no **GitHub Pages** sem necessidade de backend.

---

## Fontes dos Dados de Emissão

- **IPCC AR6 (2023)** — Chapter 10: Transport
- **ICAO Carbon Footprint Calculator** — aviação civil
- **CETESB** — Relatório de Emissões Veiculares no Estado de SP (2022)
- **Our World in Data** — CO₂ emissions by transport mode
- **IEA (2023)** — equivalências de consumo energético

---

## Limitações Conhecidas

- Distâncias são estimativas baseadas em rotas típicas, não em trajetos reais.
- Fatores de emissão são médias nacionais — emissões reais variam por veículo, ocupação e rota.
- O agente não acessa APIs de geolocalização em tempo real (escopo atual).
- Compensação de carbono é sugerida por categoria, não calculada com precificação em tempo real.

---

## Licença

MIT — uso livre para fins educacionais e projetos pessoais.
