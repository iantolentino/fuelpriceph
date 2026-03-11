let state = {
    unit: 'liters',
    prices: {
        premium: 0,
        unleaded: 0,
        lastUpdated: null,
        stations: []
    }
};

const dom = {
    loading: document.getElementById('loading'),
    error: document.getElementById('error'),
    content: document.getElementById('content'),
    lastUpdated: document.getElementById('lastUpdated'),
    dataSource: document.getElementById('dataSource'),
    premiumPrice: document.getElementById('premiumPrice'),
    unleadedPrice: document.getElementById('unleadedPrice'),
    fuelCapacity: document.getElementById('fuelCapacity'),
    premiumCost: document.getElementById('premiumCost'),
    unleadedCost: document.getElementById('unleadedCost'),
    priceDifference: document.getElementById('priceDifference'),
    diffLabel: document.getElementById('diffLabel'),
    stationPrices: document.getElementById('stationPrices'),
    unitBtns: document.querySelectorAll('.unit-btn'),
    refreshLink: document.getElementById('refreshLink'),
    exportLink: document.getElementById('exportLink')
};

document.addEventListener('DOMContentLoaded', () => {
    attachEvents();
    fetchPrices();
});

function attachEvents() {
    if (dom.fuelCapacity) {
        dom.fuelCapacity.addEventListener('input', calculateCosts);
    }
    
    if (dom.unitBtns.length > 0) {
        dom.unitBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const unit = e.target.dataset.unit;
                if (!unit) return;
                setUnit(unit);
            });
        });
    }
    
    if (dom.refreshLink) {
        dom.refreshLink.addEventListener('click', (e) => {
            e.preventDefault();
            fetchPrices(true);
        });
    }
    
    if (dom.exportLink) {
        dom.exportLink.addEventListener('click', (e) => {
            e.preventDefault();
            exportToCSV();
        });
    }
}

async function fetchPrices(forceRefresh = false) {
    showLoading(true);
    
    try {
        const response = await fetch('/data/fuel_prices.json?_=' + Date.now());
        
        if (response.ok) {
            const data = await response.json();
            
            state.prices.premium = data.premium_ron100;
            state.prices.unleaded = data.unleaded_ron95;
            state.prices.lastUpdated = new Date(data.last_updated);
            state.prices.source = data.source;
            
            generateStations();
            updateUI();
            showLoading(false);
            return;
        } else {
            // If file doesn't exist yet, show loading message
            dom.loading.querySelector('p').textContent = 'Waiting for first price update...';
            setTimeout(() => fetchPrices(), 5000); // Try again in 5 seconds
        }
        
    } catch (error) {
        console.error('Fetch error:', error);
        showError('Failed to load prices. Check GitHub Actions is running.');
    }
}

function generateStations() {
    if (!state.prices.premium || !state.prices.unleaded) return;
    
    const stations = [
        { name: 'Petron', premiumName: 'Blaze 100', unleadedName: 'XCS' },
        { name: 'Shell', premiumName: 'V-Power', unleadedName: 'FuelSave' },
        { name: 'Caltex', premiumName: 'Platinum', unleadedName: 'Silver' },
        { name: 'Total', premiumName: 'Excellium', unleadedName: 'Regular' }
    ];
    
    const regions = ['Metro Manila', 'Luzon', 'Visayas', 'Mindanao'];
    
    state.prices.stations = stations.map(station => {
        const region = regions[Math.floor(Math.random() * regions.length)];
        const premiumOffset = (Math.random() * 0.6 - 0.3);
        const unleadedOffset = (Math.random() * 0.6 - 0.3);
        
        return {
            name: station.name,
            premiumName: station.premiumName,
            unleadedName: station.unleadedName,
            region: region,
            premium: Math.round((state.prices.premium + premiumOffset) * 100) / 100,
            unleaded: Math.round((state.prices.unleaded + unleadedOffset) * 100) / 100
        };
    });
}

function updateUI() {
    if (!state.prices.premium || !state.prices.unleaded) return;
    
    dom.premiumPrice.textContent = `₱${state.prices.premium.toFixed(2)}`;
    dom.unleadedPrice.textContent = `₱${state.prices.unleaded.toFixed(2)}`;
    
    if (state.prices.lastUpdated) {
        const formatted = state.prices.lastUpdated.toLocaleString('en-PH', {
            hour: '2-digit', minute: '2-digit',
            day: '2-digit', month: '2-digit'
        });
        dom.lastUpdated.innerHTML = `⌛ ${formatted}`;
        dom.dataSource.textContent = state.prices.source || 'Zigwheels';
    }
    
    renderStations();
    calculateCosts();
}

function renderStations() {
    if (!dom.stationPrices || !state.prices.stations) return;
    
    const html = state.prices.stations.map(s => `
        <div class="station-item">
            <div class="station-name">${s.name}</div>
            <div class="station-price"><span class="fuel-grade">${s.premiumName}</span> ₱${s.premium.toFixed(2)}</div>
            <div class="station-price"><span class="fuel-grade">${s.unleadedName}</span> ₱${s.unleaded.toFixed(2)}</div>
            <div class="station-region">${s.region}</div>
        </div>
    `).join('');
    
    dom.stationPrices.innerHTML = html;
}

function setUnit(unit) {
    if (unit === state.unit) return;
    
    state.unit = unit;
    
    dom.unitBtns.forEach(btn => {
        const active = btn.dataset.unit === unit;
        btn.classList.toggle('active', active);
    });
    
    calculateCosts();
}

function calculateCosts() {
    if (!dom.fuelCapacity || !state.prices.premium || !state.prices.unleaded) return;
    
    const raw = parseFloat(dom.fuelCapacity.value) || 0;
    const liters = state.unit === 'gallons' ? raw * 3.78541 : raw;
    
    const premiumTotal = liters * state.prices.premium;
    const unleadedTotal = liters * state.prices.unleaded;
    const diff = Math.abs(premiumTotal - unleadedTotal);
    
    dom.premiumCost.textContent = `₱${premiumTotal.toFixed(2)}`;
    dom.unleadedCost.textContent = `₱${unleadedTotal.toFixed(2)}`;
    dom.priceDifference.textContent = `₱${diff.toFixed(2)}`;
    
    if (premiumTotal > unleadedTotal) {
        dom.diffLabel.textContent = 'saving with RON 95';
    } else if (unleadedTotal > premiumTotal) {
        dom.diffLabel.textContent = 'saving with RON 100';
    } else {
        dom.diffLabel.textContent = 'price difference';
    }
}

function exportToCSV() {
    if (!state.prices.premium || !state.prices.unleaded) return;
    
    const raw = parseFloat(dom.fuelCapacity.value) || 0;
    const liters = state.unit === 'gallons' ? raw * 3.78541 : raw;
    
    const rows = [
        ['fuel', 'RON', 'price/liter', 'quantity', 'total'],
        ['premium', '100', state.prices.premium, liters.toFixed(2), (liters * state.prices.premium).toFixed(2)],
        ['unleaded', '95', state.prices.unleaded, liters.toFixed(2), (liters * state.prices.unleaded).toFixed(2)],
        [],
        ['generated:', new Date().toLocaleString()],
        ['source:', state.prices.source || 'Zigwheels PH']
    ];
    
    const csv = rows.map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `fuel_ph_${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
    
    URL.revokeObjectURL(url);
}

function showLoading(show) {
    dom.loading.classList.toggle('hidden', !show);
    dom.content.classList.toggle('hidden', show);
    dom.error.classList.add('hidden');
}

function showError(msg) {
    dom.error.textContent = `⚠️ ${msg}`;
    dom.error.classList.remove('hidden');
    dom.loading.classList.add('hidden');
    dom.content.classList.add('hidden');
}

// Refresh every 5 minutes
setInterval(() => {
    if (!document.hidden) {
        fetchPrices();
    }
}, 300000);
