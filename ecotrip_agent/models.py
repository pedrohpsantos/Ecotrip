"""
EcoTrip Agent — Modelos de Dados (Pydantic)
Structured Outputs para integração Agent-to-Agent e APIs externas.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class EmissionRating(str, Enum):
    BAIXO = "baixo"       # < 20 kg CO2
    MEDIO = "médio"       # 20–80 kg CO2
    ALTO = "alto"         # 80–200 kg CO2
    CRITICO = "crítico"   # > 200 kg CO2


class TransportMode(str, Enum):
    AVIAO_DOMESTICO = "aviao_domestico"
    AVIAO_INTERNACIONAL = "aviao_internacional"
    CARRO_GASOLINA = "carro_gasolina"
    CARRO_HIBRIDO = "carro_hibrido"
    CARRO_ELETRICO = "carro_eletrico"
    ONIBUS_INTERESTADUAL = "onibus_interestadual"
    ONIBUS_URBANO = "onibus_urbano"
    METRO = "metrô"
    TREM = "trem"
    MOTO_GASOLINA = "moto_gasolina"
    BICICLETA = "bicicleta"
    A_PE = "a_pe"


class TripData(BaseModel):
    origem: str = Field(..., description="Cidade ou endereço de origem")
    destino: str = Field(..., description="Cidade ou endereço de destino")
    transporte: str = Field(..., description="Modo de transporte principal")
    distancia_km: float = Field(..., gt=0, description="Distância em km (uma direção)")
    passageiros: int = Field(default=1, ge=1, description="Número de passageiros")
    ida_e_volta: bool = Field(default=False, description="True se for ida e volta")


class Equivalencias(BaseModel):
    smartphones_carregados: int = Field(..., description="Carregamentos completos de smartphone")
    horas_streaming: int = Field(..., description="Horas de streaming de vídeo equivalentes")
    arvores_para_compensar: float = Field(..., description="Árvores necessárias para absorver o CO2 em 1 ano")
    km_carro_equivalente: float = Field(..., description="Km equivalentes em carro a gasolina")


class EmissaoResult(BaseModel):
    co2_por_passageiro_kg: float = Field(..., description="Emissão por passageiro em kg de CO2")
    co2_total_kg: float = Field(..., description="Emissão total (todos os passageiros) em kg de CO2")
    rating: EmissionRating
    equivalencias: Equivalencias
    disclaimer: str = Field(
        default="Valores são estimativas baseadas em médias — não representam medições de veículo ou voo específico.",
        description="Aviso obrigatório sobre precisão dos dados"
    )


class AlternativaTransporte(BaseModel):
    transporte: str
    co2_kg: float = Field(..., description="Emissão por passageiro na alternativa")
    reducao_percent: float = Field(..., description="Redução percentual em relação ao transporte atual")
    viabilidade: str = Field(..., description="Nota sobre viabilidade prática desta alternativa")


class EcoTripReport(BaseModel):
    """Schema principal de saída do EcoGuia Agent."""

    eco_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Score de sustentabilidade (100 = zero emissão, 0 = emissão crítica)"
    )
    viagem: TripData
    emissao: EmissaoResult
    alternativas: list[AlternativaTransporte] = Field(
        default_factory=list,
        description="Até 4 alternativas ordenadas por menor emissão"
    )
    recomendacao: str = Field(
        ...,
        max_length=300,
        description="Recomendação acionável em até 2 frases"
    )
    dicas: list[str] = Field(
        default_factory=list,
        min_length=1,
        max_length=5,
        description="Dicas práticas de sustentabilidade para esta viagem"
    )
    compensacao_sugerida: Optional[str] = Field(
        default=None,
        description="Preenchido quando não há alternativa de transporte viável"
    )
