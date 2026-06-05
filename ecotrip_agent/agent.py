"""
EcoTrip Agent — Definição do Agente (Google ADK)
Arquitetura: Agente único com 3 ferramentas encadeadas via ReAct.
"""

from google.adk.agents import Agent
from ecotrip_agent.prompts import ECOTRIP_SYSTEM_PROMPT
from ecotrip_agent.tools import (
    get_emission_factor,
    calculate_carbon_footprint,
    get_transport_alternatives,
    get_distance_between_capitals,
)

# =============================================================================
# AGENTE PRINCIPAL
# Regra do ADK: nome do arquivo da pasta deve corresponder EXATAMENTE ao agent.name
# =============================================================================

root_agent = Agent(
    name="ecotrip_agent",
    model="gemini-2.5-flash",
    description=(
        "Especialista em cálculo de impacto ambiental de viagens. "
        "Calcula emissões de CO2, compara alternativas de transporte e gera "
        "relatórios de sustentabilidade estruturados. "
        "USE este agente para qualquer pergunta sobre pegada de carbono em viagens."
    ),
    instruction=ECOTRIP_SYSTEM_PROMPT,
    tools=[
        get_distance_between_capitals,
        get_emission_factor,
        calculate_carbon_footprint,
        get_transport_alternatives,
    ],
)
