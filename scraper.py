import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json
import os

def fetch_fuel_prices():
    """Fetch prices from Zigwheels"""
    url = "https://www.zigwheels.ph/fuel-price"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        
        ron100_match = re.search(r'RON\s*100[^\d]*?(\d+\.?\d*)', text, re.IGNORECASE)
        ron95_match = re.search(r'RON\s*95[^\d]*?(\d+\.?\d*)', text, re.IGNORECASE)
        
        if ron100_match and ron95_match:
            return {
                'premium_ron100': float(ron100_match.group(1)),
                'unleaded_ron95': float(ron95_match.group(1)),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'Zigwheels Philippines'
            }
    except Exception as e:
        print(f"Error: {e}")
        return None

def save_prices(prices):
    """Save prices to the correct location for Vercel"""
    if not prices:
        return
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Save to data/fuel_prices.json (relative to project root)
    json_path = os.path.join(current_dir, 'data', 'fuel_prices.json')
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(prices, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved prices to {json_path}")

if __name__ == "__main__":
    print("Fetching prices from Zigwheels...")
    prices = fetch_fuel_prices()
    if prices:
        print(f"RON 100: ₱{prices['premium_ron100']}")
        print(f"RON 95: ₱{prices['unleaded_ron95']}")
        save_prices(prices)
    else:
        print("Failed to fetch prices")
