from flask import Flask, jsonify, render_template
from scraper import fetch_fuel_prices, save_prices
import json
import os
from datetime import datetime
import threading
import time

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Global variable to store prices
current_prices = None
last_update = None

def update_prices_background():
    """Background thread to update prices every hour"""
    global current_prices, last_update
    
    while True:
        try:
            print(f"\n[{datetime.now()}] 🔄 Fetching prices from Zigwheels...")
            prices = fetch_fuel_prices()
            if prices:
                current_prices = prices
                last_update = datetime.now()
                print(f"✅ Updated: Premium ₱{prices['premium_ron100']} | Unleaded ₱{prices['unleaded_ron95']}")
            else:
                print("❌ Failed to fetch prices")
        except Exception as e:
            print(f"Error in background update: {e}")
        
        # Wait 1 hour
        print("⏳ Waiting 1 hour until next update...")
        time.sleep(3600)

# Start background thread
thread = threading.Thread(target=update_prices_background, daemon=True)
thread.start()

# Initial fetch
with app.app_context():
    print("\n" + "="*50)
    print("🚀 FUEL PRICE PHILIPPINES")
    print("="*50)
    print("Starting initial price fetch...")
    prices = fetch_fuel_prices()
    if prices:
        current_prices = prices
        last_update = datetime.now()
        print(f"✅ Initial prices loaded:")
        print(f"   RON 100 (Premium): ₱{prices['premium_ron100']}")
        print(f"   RON 95 (Unleaded): ₱{prices['unleaded_ron95']}")
    else:
        print("❌ Could not fetch initial prices")

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/prices')
def get_prices():
    """API endpoint to get current prices"""
    global current_prices, last_update
    
    if current_prices:
        # Add server time to response
        response = current_prices.copy()
        response['server_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if last_update:
            response['last_update'] = last_update.strftime('%Y-%m-%d %H:%M:%S')
        return jsonify(response)
    else:
        # Try to fetch on demand
        prices = fetch_fuel_prices()
        if prices:
            current_prices = prices
            return jsonify(prices)
        return jsonify({'error': 'No price data available'}), 503

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'prices_available': current_prices is not None,
        'last_update': last_update.strftime('%Y-%m-%d %H:%M:%S') if last_update else None
    })

@app.route('/debug')
def debug():
    """Debug endpoint to see current state"""
    return jsonify({
        'current_prices': current_prices,
        'last_update': str(last_update) if last_update else None,
        'thread_alive': thread.is_alive()
    })

if __name__ == '__main__':
    # Local development
    print("\n🌐 Starting web server at http://localhost:5000")
    print("   Press Ctrl+C to stop\n")
    app.run(host='0.0.0.0', port=5000, debug=True)