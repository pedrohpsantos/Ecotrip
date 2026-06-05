"""
EcoTrip Agent — Ferramentas de Cálculo
Seguindo boas práticas de design de ferramentas do Módulo 5:
- Nomes descritivos
- Descrições específicas no docstring (são o "prompt" que o LLM lê)
- Validação de entrada explícita
- Retorno estruturado e previsível
"""

import math

# Fatores de emissão: kg CO2 por km por passageiro
# Fontes: IPCC AR6 (2023), ICAO Carbon Footprint Calculator, CETESB
EMISSION_FACTORS: dict[str, float] = {
    "aviao_domestico":       0.255,
    "aviao_internacional":   0.195,
    "carro_gasolina":        0.192,
    "carro_hibrido":         0.106,
    "carro_eletrico":        0.050,
    "onibus_interestadual":  0.089,
    "onibus_urbano":         0.105,
    "metrô":                 0.041,
    "trem":                  0.035,
    "moto_gasolina":         0.113,
    "bicicleta":             0.000,
    "a_pe":                  0.000,
}

VALID_MODES = list(EMISSION_FACTORS.keys())

# Modos inviáveis para distâncias longas (> 100 km)
SHORT_RANGE_ONLY = {"bicicleta", "a_pe", "onibus_urbano", "metrô"}

# Coordenadas geográficas das capitais brasileiras (Latitude, Longitude)
CAPITAIS_BR = {
    "aracaju": (-10.9472, -37.0731),
    "belém": (-1.4558, -48.5044),
    "belo horizonte": (-19.9208, -43.9378),
    "boa vista": (2.8235, -60.6758),
    "brasília": (-15.7938, -47.8827),
    "campo grande": (-20.4428, -54.6464),
    "cuiabá": (-15.6014, -56.0974),
    "curitiba": (-25.4290, -49.2671),
    "florianópolis": (-27.5969, -48.5495),
    "fortaleza": (-3.7319, -38.5267),
    "goiânia": (-16.6869, -49.2643),
    "joão pessoa": (-7.1150, -34.8631),
    "macapá": (0.0349, -51.0694),
    "maceió": (-9.6658, -35.7353),
    "manaus": (-3.1190, -60.0217),
    "natal": (-5.7945, -35.2110),
    "palmas": (-10.2128, -48.3601),
    "porto alegre": (-30.0346, -51.2177),
    "porto velho": (-8.7612, -63.9039),
    "recife": (-8.0476, -34.8770),
    "rio branco": (-9.9749, -67.8105),
    "rio de Janeiro": (-22.9068, -43.1729),
    "salvador": (-12.9714, -38.5113),
    "são luís": (-2.5307, -44.3068),
    "são paulo": (-23.5505, -46.6333),
    "teresina": (-5.0892, -42.8016),
    "vitória": (-20.3155, -40.3128),
}

def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula a distância em linha reta entre dois pontos na Terra em km."""
    R = 6371.0 # Raio da Terra em km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c



def _calculate_equivalences(co2_kg: float) -> dict:
    """Converte kg de CO2 em equivalências compreensíveis para o usuário."""
    return {
        "smartphones_carregados": max(0, round(co2_kg * 122)),
        "horas_streaming":        max(0, round(co2_kg / 0.036)),
        "arvores_para_compensar": max(0, round(co2_kg / 21.77, 1)),
        "km_carro_equivalente":   max(0, round(co2_kg / 0.192, 1)),
    }


def _emission_rating(co2_kg: float) -> str:
    if co2_kg < 20:   return "baixo"
    if co2_kg < 80:   return "médio"
    if co2_kg < 200:  return "alto"
    return "crítico"


def _eco_score(co2_kg: float) -> int:
    """Score de 0-100 inversamente proporcional à emissão por passageiro."""
    if co2_kg <= 0:    return 100
    if co2_kg >= 500:  return 0
    return max(0, round(100 - (co2_kg / 500) * 100))


# =============================================================================
# FERRAMENTAS PÚBLICAS (expostas ao agente)
# =============================================================================

def get_distance_between_capitals(origem: str, destino: str, transport_mode: str = "aviao_domestico") -> dict:
    """
    Calcula a distância em quilômetros entre duas capitais brasileiras.

    USE esta ferramenta quando o usuário informar a cidade de origem e destino, mas não a distância em km.
    Não é necessário perguntar a distância se ambas as cidades forem capitais do Brasil.

    Args:
        origem: Nome da capital de origem (ex: "São Paulo").
        destino: Nome da capital de destino (ex: "Manaus").
        transport_mode: Modo de transporte. Importante pois rotas terrestres são ~20% mais longas que linha reta.

    Returns:
        dict com distance_km (float).
        Em caso de erro (cidade não encontrada), retorna dict com chave "error" e a lista de capitais válidas.
    """
    import unicodedata
    
    def normalize_str(text: str) -> str:
        text = str(text).strip().lower()
        # Remove acentos para facilitar a busca
        text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
        return text

    origem_norm = normalize_str(origem)
    destino_norm = normalize_str(destino)
    
    # Criar um dict de busca normalizado
    search_dict = {normalize_str(k): v for k, v in CAPITAIS_BR.items()}
    
    if origem_norm not in search_dict:
        return {"error": f"Capital '{origem}' não encontrada na base de dados.", "capitais_suportadas": list(CAPITAIS_BR.keys())}
    if destino_norm not in search_dict:
        return {"error": f"Capital '{destino}' não encontrada na base de dados.", "capitais_suportadas": list(CAPITAIS_BR.keys())}

    lat1, lon1 = search_dict[origem_norm]
    lat2, lon2 = search_dict[destino_norm]
    
    distance = _haversine(lat1, lon1, lat2, lon2)
    
    # Se for terrestre, a estrada não é uma linha reta, adiciona fator de correção (20%)
    if "aviao" not in transport_mode.lower():
        distance = distance * 1.20
        nota = "Distância calculada via coordenadas geográficas com acréscimo de 20% para rotas terrestres/rodoviárias."
    else:
        nota = "Distância em linha reta (rota aérea)."

    return {
        "origem_identificada": origem,
        "destino_identificado": destino,
        "distance_km": round(distance, 1),
        "nota": nota
    }



def get_emission_factor(transport_mode: str) -> dict:
    """
    Retorna o fator de emissão de CO2 em kg por km por passageiro para um meio de transporte.

    USE esta ferramenta ANTES de calculate_carbon_footprint para validar que o modo
    de transporte informado pelo usuário é reconhecido pelo sistema.

    Args:
        transport_mode: Modo de transporte. Valores aceitos:
            aviao_domestico, aviao_internacional, carro_gasolina, carro_hibrido,
            carro_eletrico, onibus_interestadual, onibus_urbano, metrô, trem,
            moto_gasolina, bicicleta, a_pe

    Returns:
        dict com factor_kg_co2_per_km (float) e fonte dos dados.
        Em caso de modo inválido, retorna dict com chave "error" e lista de modos válidos.
    """
    mode = transport_mode.lower().strip()
    factor = EMISSION_FACTORS.get(mode)

    if factor is None:
        return {
            "error": f"Modo de transporte '{mode}' não reconhecido.",
            "modos_validos": VALID_MODES,
            "sugestao": "Verifique a grafia ou pergunte ao usuário para confirmar o meio de transporte."
        }

    return {
        "transport_mode": mode,
        "factor_kg_co2_per_km": factor,
        "fonte": "IPCC AR6 (2023) / ICAO / CETESB — médias para o Brasil",
        "nota": "Valor representa emissão por passageiro por km percorrido."
    }


def calculate_carbon_footprint(
    distance_km: float,
    transport_mode: str,
    passengers: int = 1,
    round_trip: bool = False
) -> dict:
    """
    Calcula a pegada de carbono total de uma viagem com emissão por passageiro e total.

    USE após get_emission_factor. Retorna emissão, rating de impacto e equivalências
    educativas para comunicar o resultado ao usuário de forma compreensível.

    Args:
        distance_km: Distância em km de uma direção (não duplique para ida e volta — use round_trip=True).
        transport_mode: Modo de transporte (mesmo enum de get_emission_factor).
        passengers: Número de passageiros no veículo/aeronave (padrão: 1).
        round_trip: True se a viagem for ida e volta; dobra a distância automaticamente.

    Returns:
        dict com co2_per_passenger_kg, co2_total_kg, rating, eco_score, equivalencias.
        Em caso de erro, retorna dict com chave "error".
    """
    if distance_km <= 0:
        return {"error": "distance_km deve ser maior que zero."}
    if passengers < 1:
        return {"error": "passengers deve ser pelo menos 1."}

    factor_result = get_emission_factor(transport_mode)
    if "error" in factor_result:
        return factor_result

    factor = factor_result["factor_kg_co2_per_km"]
    total_km = distance_km * (2 if round_trip else 1)

    co2_per_passenger = round(total_km * factor, 2)
    co2_total = round(co2_per_passenger * passengers, 2)

    return {
        "transport_mode": transport_mode,
        "distancia_total_km": total_km,
        "passengers": passengers,
        "co2_per_passenger_kg": co2_per_passenger,
        "co2_total_kg": co2_total,
        "rating": _emission_rating(co2_per_passenger),
        "eco_score": _eco_score(co2_per_passenger),
        "equivalencias": _calculate_equivalences(co2_per_passenger),
        "disclaimer": "Valores são estimativas baseadas em médias — não representam medições de veículo ou voo específico."
    }


def get_transport_alternatives(
    current_mode: str,
    distance_km: float,
    passengers: int = 1
) -> dict:
    """
    Sugere alternativas de transporte com menor emissão de CO2 para a mesma viagem.

    USE após calculate_carbon_footprint para enriquecer o relatório com opções
    mais sustentáveis. Filtra automaticamente alternativas inviáveis para a distância.

    Args:
        current_mode: Modo de transporte atual do usuário (para calcular a redução relativa).
        distance_km: Distância da viagem em km (uma direção).
        passengers: Número de passageiros.

    Returns:
        dict com lista de até 4 alternativas ordenadas por menor emissão,
        cada uma com co2_kg, reducao_percent e nota de viabilidade.
    """
    current_result = get_emission_factor(current_mode)
    if "error" in current_result:
        return current_result

    current_co2 = distance_km * current_result["factor_kg_co2_per_km"]

    alternatives = []
    for mode, factor in EMISSION_FACTORS.items():
        if mode == current_mode:
            continue

        # Filtra opções inviáveis para distâncias longas
        if distance_km > 100 and mode in SHORT_RANGE_ONLY:
            continue

        alt_co2 = round(distance_km * factor, 2)

        # Só sugere se for estritamente mais sustentável
        if alt_co2 >= current_co2:
            continue

        reduction_pct = round((1 - alt_co2 / current_co2) * 100, 1) if current_co2 > 0 else 0

        # Nota de viabilidade contextual
        if mode in {"bicicleta", "a_pe"}:
            viabilidade = "Ideal para distâncias curtas urbanas."
        elif mode in {"metrô", "onibus_urbano"}:
            viabilidade = "Disponível conforme cobertura da cidade de origem/destino."
        elif mode == "trem":
            viabilidade = "Verifique disponibilidade de linha para esta rota."
        elif mode == "carro_eletrico":
            viabilidade = "Requer acesso a veículo elétrico e infraestrutura de recarga."
        else:
            viabilidade = "Opção geralmente disponível para esta distância."

        alternatives.append({
            "transport_mode": mode,
            "co2_kg": alt_co2,
            "reducao_percent": reduction_pct,
            "viabilidade": viabilidade
        })

    alternatives.sort(key=lambda x: x["co2_kg"])

    if not alternatives:
        return {
            "current_mode": current_mode,
            "current_co2_per_passenger_kg": round(current_co2, 2),
            "alternatives": [],
            "nota": "Não foram encontradas alternativas mais sustentáveis e viáveis para esta rota e distância. Considere compensação de carbono certificada (Gold Standard ou Verra VCS)."
        }

    return {
        "current_mode": current_mode,
        "current_co2_per_passenger_kg": round(current_co2, 2),
        "alternatives": alternatives[:4],
    }
