"""
EcoTrip Agent — Testes das Ferramentas
"""

import pytest
from ecotrip_agent.tools import (
    get_emission_factor,
    calculate_carbon_footprint,
    get_transport_alternatives,
    get_distance_between_capitals,
)


class TestGetEmissionFactor:
    def test_modo_valido(self):
        result = get_emission_factor("carro_gasolina")
        assert "factor_kg_co2_per_km" in result
        assert result["factor_kg_co2_per_km"] == 0.192

    def test_modo_invalido(self):
        result = get_emission_factor("foguete")
        assert "error" in result
        assert "modos_validos" in result

    def test_bicicleta_zero_emissao(self):
        result = get_emission_factor("bicicleta")
        assert result["factor_kg_co2_per_km"] == 0.0

    def test_eletrico_menor_que_gasolina(self):
        eletrico = get_emission_factor("carro_eletrico")["factor_kg_co2_per_km"]
        gasolina = get_emission_factor("carro_gasolina")["factor_kg_co2_per_km"]
        assert eletrico < gasolina


class TestCalculateCarbonFootprint:
    def test_calculo_basico(self):
        result = calculate_carbon_footprint(100, "carro_gasolina", 1, False)
        assert result["co2_per_passenger_kg"] == pytest.approx(19.2, abs=0.1)

    def test_ida_e_volta_dobra_distancia(self):
        ida = calculate_carbon_footprint(100, "carro_gasolina", 1, False)
        ida_volta = calculate_carbon_footprint(100, "carro_gasolina", 1, True)
        assert ida_volta["co2_per_passenger_kg"] == pytest.approx(ida["co2_per_passenger_kg"] * 2)

    def test_passageiros_dividem_emissao(self):
        solo = calculate_carbon_footprint(100, "carro_gasolina", 1)
        grupo = calculate_carbon_footprint(100, "carro_gasolina", 4)
        # Emissão por passageiro é a mesma; total quadruplica
        assert solo["co2_per_passenger_kg"] == grupo["co2_per_passenger_kg"]
        assert grupo["co2_total_kg"] == pytest.approx(solo["co2_total_kg"] * 4)

    def test_distancia_zero_retorna_erro(self):
        result = calculate_carbon_footprint(0, "carro_gasolina")
        assert "error" in result

    def test_rating_critico_para_voo_longo(self):
        result = calculate_carbon_footprint(2500, "aviao_domestico", 1, True)
        assert result["rating"] == "crítico"

    def test_rating_baixo_para_metro(self):
        result = calculate_carbon_footprint(10, "metrô")
        assert result["rating"] == "baixo"


class TestGetTransportAlternatives:
    def test_retorna_alternativas_mais_sustentaveis(self):
        result = get_transport_alternatives("aviao_domestico", 500, 1)
        for alt in result["alternatives"]:
            assert alt["co2_kg"] < result["current_co2_per_passenger_kg"]

    def test_filtra_bicicleta_para_longa_distancia(self):
        result = get_transport_alternatives("carro_gasolina", 500, 1)
        modos = [a["transport_mode"] for a in result["alternatives"]]
        assert "bicicleta" not in modos

    def test_modo_mais_limpo_primeiro(self):
        result = get_transport_alternatives("carro_gasolina", 100, 1)
        if len(result["alternatives"]) > 1:
            co2_values = [a["co2_kg"] for a in result["alternatives"]]
            assert co2_values == sorted(co2_values)

    def test_modo_inexistente_retorna_erro(self):
        result = get_transport_alternatives("nave_espacial", 100, 1)
        assert "error" in result


class TestGetDistanceBetweenCapitals:
    def test_calcula_distancia_aerea(self):
        result = get_distance_between_capitals("São Paulo", "Rio de Janeiro", "aviao_domestico")
        assert "distance_km" in result
        # Distância SP-RJ em linha reta é aprox 350-370km
        assert 300 < result["distance_km"] < 450
        assert "linha reta" in result["nota"]

    def test_calcula_distancia_terrestre_com_acrescimo(self):
        result = get_distance_between_capitals("São Paulo", "Rio de Janeiro", "carro_gasolina")
        assert "distance_km" in result
        assert "acréscimo de 20%" in result["nota"]
        
    def test_capital_invalida_retorna_erro(self):
        result = get_distance_between_capitals("Osasco", "Guarulhos")
        assert "error" in result
        assert "capitais_suportadas" in result

