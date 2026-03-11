import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json
import os

def fetch_fuel_prices():
    """
    Fetch current fuel prices from Zigwheels Philippines
    """
    url = "https://www.zigwheels.ph/fuel-price"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # Fetch the page
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get all text
        text = soup.get_text()
        
        # Find RON 100 and RON 95 prices
        ron100_pattern = r'RON\s*100[^\d]*?(\d+\.?\d*)'
        ron95_pattern = r'RON\s*95[^\d]*?(\d+\.?\d*)'
        
        ron100_match = re.search(ron100_pattern, text, re.IGNORECASE)
        ron95_match = re.search(ron95_pattern, text, re.IGNORECASE)
        
        if ron100_match and ron95_match:
            prices = {
                'premium_ron100': float(ron100_match.group(1)),
                'unleaded_ron95': float(ron95_match.group(1)),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'Zigwheels Philippines'
            }
            
            # Find the last updated date from the site
            date_pattern = r'Last updated on (\d{1,2}\s*[A-Za-z]+\s*\d{4})'
            date_match = re.search(date_pattern, text)
            if date_match:
                prices['last_updated_on_site'] = date_match.group(1)
            
            return prices
        
        # Try looking in tables if regex fails
        tables = soup.find_all('table')
        for table in tables:
            table_text = table.get_text()
            if 'RON 100' in table_text and 'RON 95' in table_text:
                rows = table.find_all('tr')
                price_data = {}
                for row in rows:
                    row_text = row.get_text()
                    if 'RON 100' in row_text:
                        numbers = re.findall(r'(\d+\.?\d*)', row_text)
                        if numbers:
                            price_data['premium_ron100'] = float(numbers[0])
                    if 'RON 95' in row_text:
                        numbers = re.findall(r'(\d+\.?\d*)', row_text)
                        if numbers:
                            price_data['unleaded_ron95'] = float(numbers[0])
                
                if 'premium_ron100' in price_data and 'unleaded_ron95' in price_data:
                    price_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    price_data['source'] = 'Zigwheels Philippines'
                    return price_data
        
        return None
        
    except requests.RequestException as e:
        print(f"Network error: {e}")
        return None
    except Exception as e:
        print(f"Parsing error: {e}")
        return None

def save_prices(prices):
    """Save prices to JSON file (optional)"""
    if not prices:
        return False
    
    try:
        with open('fuel_prices.json', 'w', encoding='utf-8') as f:
            json.dump(prices, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

if __name__ == "__main__":
    # Test the scraper directly
    print("\n" + "="*50)
    print("TESTING SCRAPER DIRECTLY")
    print("="*50)
    prices = fetch_fuel_prices()
    if prices:
        print(f"✅ SUCCESS!")
        print(f"RON 100: ₱{prices['premium_ron100']}")
        print(f"RON 95: ₱{prices['unleaded_ron95']}")
        print(f"Source: {prices['source']}")
    else:
        print("❌ FAILED to fetch prices")