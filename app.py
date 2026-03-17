<<<<<<< HEAD
# app.py (add this new route)
from flask import Flask, jsonify, render_template, send_from_directory
=======
from flask import Flask, jsonify, render_template
>>>>>>> 02c37ea6322d2b0eba9d024b47d8554d5b7f8958
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
<<<<<<< HEAD
            print(f"\n[{datetime.now()}] 🔄 Fetching prices from phfueltrack.com...")
=======
            print(f"\n[{datetime.now()}] 🔄 Fetching prices from Zigwheels...")
>>>>>>> 02c37ea6322d2b0eba9d024b47d8554d5b7f8958
            prices = fetch_fuel_prices()
            if prices:
                current_prices = prices
                last_update = datetime.now()
<<<<<<< HEAD
                # Also save to file
                save_prices(prices)
                print(f"✅ Updated: Premium RON 95: ₱{prices['premium_ron95']} | Regular RON 91: ₱{prices['regular_ron91']}")
=======
                print(f"✅ Updated: Premium ₱{prices['premium_ron100']} | Unleaded ₱{prices['unleaded_ron95']}")
>>>>>>> 02c37ea6322d2b0eba9d024b47d8554d5b7f8958
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
<<<<<<< HEAD
        # Save initial prices to file
        save_prices(prices)
        print(f"✅ Initial prices loaded:")
        print(f"   RON 95 (Premium): ₱{prices['premium_ron95']}")
        print(f"   RON 91 (Regular): ₱{prices['regular_ron91']}")
        if 'brand_prices' in prices:
            print(f"   Based on data from: Petron, Shell, Caltex, Seaoil, Total, Cleanfuel")
=======
        print(f"✅ Initial prices loaded:")
        print(f"   RON 100 (Premium): ₱{prices['premium_ron100']}")
        print(f"   RON 95 (Unleaded): ₱{prices['unleaded_ron95']}")
>>>>>>> 02c37ea6322d2b0eba9d024b47d8554d5b7f8958
    else:
        print("❌ Could not fetch initial prices")

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

<<<<<<< HEAD
@app.route('/data/fuel_prices.json')
def serve_fuel_prices():
    """Serve the fuel_prices.json file"""
    try:
        # Get the absolute path to the data folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, 'data')
        json_path = os.path.join(data_dir, 'fuel_prices.json')
        
        # Check if file exists
        if os.path.exists(json_path):
            return send_from_directory(data_dir, 'fuel_prices.json')
        else:
            # If file doesn't exist, return current_prices from memory
            if current_prices:
                return jsonify(current_prices)
            else:
                return jsonify({'error': 'No price data available'}), 404
    except Exception as e:
        print(f"Error serving fuel_prices.json: {e}")
        return jsonify({'error': str(e)}), 500

=======
>>>>>>> 02c37ea6322d2b0eba9d024b47d8554d5b7f8958
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
<<<<<<< HEAD
        'last_update': last_update.strftime('%Y-%m-%d %H:%M:%S') if last_update else None,
        'ron95_price': current_prices.get('premium_ron95') if current_prices else None,
        'ron91_price': current_prices.get('regular_ron91') if current_prices else None
=======
        'last_update': last_update.strftime('%Y-%m-%d %H:%M:%S') if last_update else None
>>>>>>> 02c37ea6322d2b0eba9d024b47d8554d5b7f8958
    })

@app.route('/debug')
def debug():
    """Debug endpoint to see current state"""
    return jsonify({
        'current_prices': current_prices,
        'last_update': str(last_update) if last_update else None,
<<<<<<< HEAD
        'thread_alive': thread.is_alive() if 'thread' in locals() else False
=======
        'thread_alive': thread.is_alive()
>>>>>>> 02c37ea6322d2b0eba9d024b47d8554d5b7f8958
    })

if __name__ == '__main__':
    # Local development
    print("\n🌐 Starting web server at http://localhost:5000")
    print("   Press Ctrl+C to stop\n")
    app.run(host='0.0.0.0', port=5000, debug=True)