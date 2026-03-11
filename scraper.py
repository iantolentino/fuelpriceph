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
        print("Fetching from Zigwheels...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        
        # Look for RON 100 and RON 95
        ron100_match = re.search(r'RON\s*100[^\d]*?(\d+\.?\d*)', text, re.IGNORECASE)
        ron95_match = re.search(r'RON\s*95[^\d]*?(\d+\.?\d*)', text, re.IGNORECASE)
        
        if ron100_match and ron95_match:
            prices = {
                'premium_ron100': float(ron100_match.group(1)),
                'unleaded_ron95': float(ron95_match.group(1)),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'Zigwheels Philippines'
            }
            print(f"Found: RON 100 = ₱{prices['premium_ron100']}, RON 95 = ₱{prices['unleaded_ron95']}")
            return prices
        
        print("Could not find prices in the page")
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def save_prices(prices):
    """Save prices to JSON file in the data folder"""
    if not prices:
        print("No prices to save")
        return False
    
    # Get the absolute path to the data folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, 'data')
    json_path = os.path.join(data_dir, 'fuel_prices.json')
    
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    # Save the file
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(prices, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved to {json_path}")
    
    # Also print the file content for verification
    with open(json_path, 'r') as f:
        content = f.read()
        print(f"File content: {content}")
    
    return True

if __name__ == "__main__":
    print("\n" + "="*50)
    print("FUEL PRICE SCRAPER")
    print("="*50)
    
    prices = fetch_fuel_prices()
    if prices:
        save_prices(prices)
        print("\n✅ Scraper completed successfully")
    else:
        print("\n❌ Scraper failed")
