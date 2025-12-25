// Set default dates
const today = new Date();
const oneYearAgo = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate());

document.getElementById('start_date').valueAsDate = oneYearAgo;
document.getElementById('end_date').valueAsDate = today;

// Event listeners
document.getElementById('predictBtn').addEventListener('click', handlePredict);
document.getElementById('ticker').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handlePredict();
});

async function handlePredict() {
    const ticker = document.getElementById('ticker').value.toUpperCase();
    const start_date = document.getElementById('start_date').value;
    const end_date = document.getElementById('end_date').value;

    const errorMsg = document.getElementById('errorMsg');
    const successMsg = document.getElementById('successMsg');
    const resultsPanel = document.getElementById('resultsPanel');
    const loading = document.getElementById('loading');
    const resultsContent = document.getElementById('resultsContent');

    // Clear messages
    errorMsg.classList.remove('active');
    successMsg.classList.remove('active');

    // Validate inputs
    if (!ticker || !start_date || !end_date) {
        errorMsg.textContent = '❌ Preencha todos os campos';
        errorMsg.classList.add('active');
        return;
    }

    if (new Date(start_date) >= new Date(end_date)) {
        errorMsg.textContent = '❌ Data inicial deve ser anterior à data final';
        errorMsg.classList.add('active');
        return;
    }

    // Show loading
    resultsPanel.classList.add('active');
    loading.classList.add('active');
    resultsContent.style.display = 'none';

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ticker,
                start_date,
                end_date
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao fazer previsão');
        }

        const data = await response.json();
        displayResults(data);

        loading.classList.remove('active');
        resultsContent.style.display = 'block';
        successMsg.textContent = '✅ Previsão concluída com sucesso!';
        successMsg.classList.add('active');

    } catch (error) {
        loading.classList.remove('active');
        errorMsg.textContent = `❌ ${error.message}`;
        errorMsg.classList.add('active');
    }
}

function displayResults(data) {
    // Update metric cards
    document.getElementById('lastClose').textContent = `R$ ${data.last_close.toFixed(2)}`;
    document.getElementById('nextPrice').textContent = `R$ ${data.next_price.toFixed(2)}`;
    
    const priceChangeDiv = document.getElementById('priceChange');
    const change = data.price_change;
    const changePct = data.price_change_pct;
    priceChangeDiv.textContent = `R$ ${change.toFixed(2)} (${changePct.toFixed(2)}%)`;
    priceChangeDiv.classList.toggle('negative', change < 0);
    
    document.getElementById('dataPoints').textContent = data.data_points;
    document.getElementById('r2Score').textContent = data.metrics.R2.toFixed(4);

    // Update detailed metrics
    document.getElementById('mse').textContent = data.metrics.MSE.toFixed(6);
    document.getElementById('mae').textContent = data.metrics.MAE.toFixed(6);
    document.getElementById('rmse').textContent = data.metrics.RMSE.toFixed(6);

    // Update plot
    document.getElementById('plotImage').src = data.plot;

    // Update summary text
    const summaryHTML = `
        <p><strong>Ação Analisada:</strong> ${data.ticker}</p>
        <p><strong>Período:</strong> ${formatDate(data.start_date)} a ${formatDate(data.end_date)}</p>
        <p><strong>Último preço de fechamento:</strong> R$ ${data.last_close.toFixed(2)}</p>
        <p><strong>Próximo preço previsto:</strong> R$ ${data.next_price.toFixed(2)}</p>
        <p><strong>Variação prevista:</strong> R$ ${data.price_change.toFixed(2)} (${data.price_change_pct.toFixed(2)}%)</p>
        <p><strong>R² Score:</strong> ${data.metrics.R2.toFixed(4)} (quanto mais próximo de 1, melhor)</p>
        <p><strong>Erro Médio Absoluto (MAE):</strong> R$ ${data.metrics.MAE.toFixed(2)}</p>
        <p><strong>Total de dias analisados:</strong> ${data.data_points}</p>
        <p style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 0.85em; color: #999;">
            <em>Modelo: LSTM de 2 camadas com 64 neurônios</em>
        </p>
    `;
    document.getElementById('summaryText').innerHTML = summaryHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString + 'T00:00:00');
    return date.toLocaleDateString('pt-BR');
}
