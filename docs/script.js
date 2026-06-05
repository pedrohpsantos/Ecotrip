// Fatores de emissão: kg CO2 por km por passageiro (Baseado no backend em Python)
const EMISSION_FACTORS = {
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
};

// Modos inviáveis para distâncias longas (> 100 km)
const SHORT_RANGE_ONLY = new Set(["bicicleta", "a_pe", "onibus_urbano", "metrô"]);

// Nomes amigáveis para exibição
const MODE_NAMES = {
    "aviao_domestico": "Avião (Doméstico)",
    "aviao_internacional": "Avião (Internacional)",
    "carro_gasolina": "Carro (Gasolina)",
    "carro_hibrido": "Carro (Híbrido)",
    "carro_eletrico": "Carro (Elétrico)",
    "onibus_interestadual": "Ônibus (Interestadual)",
    "onibus_urbano": "Ônibus (Urbano)",
    "metrô": "Metrô",
    "trem": "Trem",
    "moto_gasolina": "Moto (Gasolina)",
    "bicicleta": "Bicicleta",
    "a_pe": "A Pé",
};

// ==========================================
// Lógica de Negócio (Port do backend Python)
// ==========================================

function calculateEquivalences(co2Kg) {
    return {
        smartphones_carregados: Math.max(0, Math.round(co2Kg * 122)),
        horas_streaming: Math.max(0, Math.round(co2Kg / 0.036)),
        arvores_para_compensar: Math.max(0, parseFloat((co2Kg / 21.77).toFixed(1))),
        km_carro_equivalente: Math.max(0, parseFloat((co2Kg / 0.192).toFixed(1))),
    };
}

function getEmissionRating(co2Kg) {
    if (co2Kg < 20) return "baixo";
    if (co2Kg < 80) return "medio";
    if (co2Kg < 200) return "alto";
    return "critico";
}

function getEcoScore(co2Kg) {
    if (co2Kg <= 0) return 100;
    if (co2Kg >= 500) return 0;
    return Math.max(0, Math.round(100 - (co2Kg / 500) * 100));
}

function calculateCarbonFootprint(distanceKm, transportMode, passengers = 1, roundTrip = false) {
    const factor = EMISSION_FACTORS[transportMode];
    if (factor === undefined) throw new Error("Modo de transporte não reconhecido.");

    const totalKm = distanceKm * (roundTrip ? 2 : 1);
    const co2PerPassenger = totalKm * factor;
    const co2Total = co2PerPassenger * passengers;

    return {
        transportMode,
        distanciaTotalKm: totalKm,
        passengers,
        co2PerPassengerKg: co2PerPassenger,
        co2TotalKg: co2Total,
        rating: getEmissionRating(co2PerPassenger),
        ecoScore: getEcoScore(co2PerPassenger),
        equivalencias: calculateEquivalences(co2PerPassenger),
    };
}

function getTransportAlternatives(currentMode, distanceKm) {
    const currentFactor = EMISSION_FACTORS[currentMode];
    if (currentFactor === undefined) return [];

    const currentCo2 = distanceKm * currentFactor;
    const alternatives = [];

    for (const [mode, factor] of Object.entries(EMISSION_FACTORS)) {
        if (mode === currentMode) continue;
        if (distanceKm > 100 && SHORT_RANGE_ONLY.has(mode)) continue;

        const altCo2 = distanceKm * factor;

        // Apenas alternativas mais eficientes
        if (altCo2 >= currentCo2) continue;

        const reductionPct = currentCo2 > 0 ? ((1 - altCo2 / currentCo2) * 100) : 0;

        let viabilidade = "Opção geralmente disponível para esta distância.";
        if (mode === "bicicleta" || mode === "a_pe") {
            viabilidade = "Ideal para distâncias curtas urbanas.";
        } else if (mode === "metrô" || mode === "onibus_urbano") {
            viabilidade = "Disponível conforme cobertura da cidade de origem/destino.";
        } else if (mode === "trem") {
            viabilidade = "Verifique disponibilidade de linha para esta rota.";
        } else if (mode === "carro_eletrico") {
            viabilidade = "Requer acesso a veículo elétrico e infraestrutura de recarga.";
        }

        alternatives.push({
            transportMode: mode,
            co2Kg: altCo2,
            reducaoPercent: reductionPct,
            viabilidade,
        });
    }

    alternatives.sort((a, b) => a.co2Kg - b.co2Kg);
    return alternatives.slice(0, 4);
}

// ==========================================
// Manipulação da Interface (UI)
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("calc-form");
    const resultsSection = document.getElementById("results");

    form.addEventListener("submit", (e) => {
        e.preventDefault();

        // Coleta de dados
        const mode = document.getElementById("transport_mode").value;
        const distance = parseFloat(document.getElementById("distance_km").value);
        const passengers = parseInt(document.getElementById("passengers").value, 10);
        const roundTrip = document.getElementById("round_trip").checked;

        if (!mode || isNaN(distance) || isNaN(passengers)) return;

        // Cálculos
        const result = calculateCarbonFootprint(distance, mode, passengers, roundTrip);
        const alternatives = getTransportAlternatives(mode, distance * (roundTrip ? 2 : 1));

        // Atualização da UI
        updateResultsUI(result, alternatives);
    });
});

function animateValue(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        // Easing function: easeOutQuart
        const easeProgress = 1 - Math.pow(1 - progress, 4);
        const currentVal = start + easeProgress * (end - start);
        
        // Verifica se é decimal ou inteiro baseado no valor alvo
        if (end % 1 !== 0) {
            element.textContent = currentVal.toFixed(1).replace('.', ',');
        } else {
            element.textContent = Math.round(currentVal).toLocaleString('pt-BR');
        }

        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

function updateResultsUI(result, alternatives) {
    const resultsSection = document.getElementById("results");
    
    // Atualiza Emissão Total
    const totalEl = document.getElementById("co2_total");
    const perPassengerEl = document.getElementById("co2_per_passenger");
    
    animateValue(totalEl, 0, result.co2TotalKg, 1500);
    animateValue(perPassengerEl, 0, result.co2PerPassengerKg, 1500);

    // Atualiza Eco Score
    document.getElementById("eco-score-badge").textContent = `Score de Sustentabilidade: ${result.ecoScore}/100`;

    // Atualiza Barra de Rating
    const ratingBar = document.getElementById("rating-bar");
    const ratingText = document.getElementById("rating-text");
    
    // Reseta as classes
    ratingBar.className = "rating-bar";
    ratingText.className = "rating-label";
    
    // Mapeia rating para largura da barra e classe
    const ratingMap = {
        "baixo": { width: "25%", text: "Impacto Baixo" },
        "medio": { width: "50%", text: "Impacto Médio" },
        "alto": { width: "75%", text: "Impacto Alto" },
        "critico": { width: "100%", text: "Impacto Crítico" }
    };

    const ratingInfo = ratingMap[result.rating] || ratingMap["baixo"];
    
    // Timeout para forçar a animação
    setTimeout(() => {
        ratingBar.style.width = ratingInfo.width;
        ratingBar.classList.add(`rating-${result.rating}`);
        ratingText.classList.add(`rating-${result.rating}`);
        ratingText.textContent = ratingInfo.text;
    }, 100);

    // Atualiza Equivalências
    const eqList = document.getElementById("equivalences-list");
    eqList.innerHTML = `
        <li>
            <span class="eq-icon">📱</span>
            <span class="eq-text">Cargas de smartphone: <strong>${result.equivalencias.smartphones_carregados.toLocaleString('pt-BR')}</strong></span>
        </li>
        <li>
            <span class="eq-icon">🎬</span>
            <span class="eq-text">Horas de streaming de vídeo: <strong>${result.equivalencias.horas_streaming.toLocaleString('pt-BR')}</strong></span>
        </li>
        <li>
            <span class="eq-icon">🌳</span>
            <span class="eq-text">Árvores necessárias para compensar: <strong>${result.equivalencias.arvores_para_compensar.toLocaleString('pt-BR')}</strong></span>
        </li>
    `;

    // Atualiza Alternativas
    const altContainer = document.getElementById("alternatives-list");
    if (alternatives.length > 0) {
        let altHTML = '';
        alternatives.forEach(alt => {
            altHTML += `
                <div class="alt-card">
                    <div class="alt-header">
                        <span class="alt-mode">${MODE_NAMES[alt.transportMode]}</span>
                        <span class="alt-badge">-${alt.reducaoPercent.toFixed(0)}% CO₂</span>
                    </div>
                    <div class="alt-co2">${alt.co2Kg.toFixed(1).replace('.', ',')} <span style="font-size: 0.8rem; font-weight: normal; color: var(--text-muted)">kg CO₂</span></div>
                    <div class="alt-viability">${alt.viabilidade}</div>
                </div>
            `;
        });
        altContainer.innerHTML = altHTML;
        document.getElementById("alternatives-container").style.display = "block";
    } else {
        altContainer.innerHTML = '<p style="color: var(--text-muted); font-size: 0.95rem;">Você já escolheu uma das opções mais eficientes para esta distância! Parabéns! 🎉</p>';
    }

    // Mostra a seção de resultados
    resultsSection.classList.remove("hidden");
    
    // Scroll suave para os resultados
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 100);
}
