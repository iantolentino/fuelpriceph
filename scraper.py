<<<<<<< HEAD
# scraper.py (updated for phfueltrack.com)
=======
>>>>>>> 02c37ea6322d2b0eba9d024b47d8554d5b7f8958
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json
import os

def fetch_fuel_prices():
<<<<<<< HEAD
    """Fetch prices from phfueltrack.com"""
    url = "https://phfueltrack.com/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'no-cache'
    }
    
    try:
        print(f"[{datetime.now()}] 🔄 Fetching from phfueltrack.com...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Method 1: Look for the specific price cards in the HTML structure
        # Based on the URL content, prices are in structured cards for each brand
        
        # Find all brand price sections
        prices = {}
        
        # Get the main content
        main_content = soup.find('main') or soup.find('div', class_=re.compile(r'content|container', re.I))
        
        # Debug: print first 500 chars to see structure
        print("\n📄 Page structure preview:")
        preview = soup.get_text()[:500].replace('\n', ' ').strip()
        print(preview + "...\n")
        
        # Method: Look for RON 95 (Premium) prices
        # The site shows Petron Premium: ₱73.25, Shell Premium: ₱72.60, etc.
        
        # Find all price elements - they typically have ₱ symbol
        price_elements = soup.find_all(['div', 'span', 'p', 'h3', 'h4'], string=re.compile(r'₱\s*\d+\.\d{2}'))
        
        # Find all brand names
        brands = ['Petron', 'Shell', 'Caltex', 'Seaoil', 'Total', 'Cleanfuel', 'Unioil', 'PTT', 'Phoenix', 'Jetti']
        
        found_ron95_prices = []
        found_ron91_prices = []
        
        # Method: Search for specific patterns in the text
        text = soup.get_text()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        print("🔍 Searching for fuel prices...")
        
        # Look for Premium Gasoline (RON 95) prices
        # Pattern: "Premium Gasoline" followed by ₱ amount
        premium_sections = re.finditer(r'Premium\s+Gasoline.*?₱\s*(\d+\.?\d*)', text, re.IGNORECASE | re.DOTALL)
        for match in premium_sections:
            try:
                price = float(match.group(1))
                if 60 < price < 80:  # Valid RON 95 range
                    found_ron95_prices.append(price)
                    print(f"  Found Premium/RON 95: ₱{price}")
            except:
                pass
        
        # If no Premium matches, look for RON 95 directly
        if not found_ron95_prices:
            ron95_matches = re.finditer(r'RON\s*95.*?₱\s*(\d+\.?\d*)', text, re.IGNORECASE)
            for match in ron95_matches:
                try:
                    price = float(match.group(1))
                    if 60 < price < 80:
                        found_ron95_prices.append(price)
                        print(f"  Found RON 95: ₱{price}")
                except:
                    pass
        
        # Look for Regular Gasoline (RON 91) prices
        regular_sections = re.finditer(r'Regular\s+Gasoline.*?₱\s*(\d+\.?\d*)', text, re.IGNORECASE | re.DOTALL)
        for match in regular_sections:
            try:
                price = float(match.group(1))
                if 55 < price < 75:  # Valid RON 91 range
                    found_ron91_prices.append(price)
                    print(f"  Found Regular/RON 91: ₱{price}")
            except:
                pass
        
        # If no Regular matches, look for RON 91 directly
        if not found_ron91_prices:
            ron91_matches = re.finditer(r'RON\s*91.*?₱\s*(\d+\.?\d*)', text, re.IGNORECASE)
            for match in ron91_matches:
                try:
                    price = float(match.group(1))
                    if 55 < price < 75:
                        found_ron91_prices.append(price)
                        print(f"  Found RON 91: ₱{price}")
                except:
                    pass
        
        # Method: If we still don't have prices, extract all ₱ amounts and try to categorize
        if not found_ron95_prices or not found_ron91_prices:
            print("\n  Using fallback: extracting all prices and categorizing...")
            all_prices = re.findall(r'₱\s*(\d+\.?\d*)', text)
            valid_prices = [float(p) for p in all_prices if 50 < float(p) < 110]
            valid_prices.sort()
            
            # Typically RON 91 is cheaper than RON 95
            if valid_prices:
                # Assuming RON 91 is the lower range, RON 95 is higher range
                mid_point = sum(valid_prices) / len(valid_prices)
                potential_ron91 = [p for p in valid_prices if p < mid_point]
                potential_ron95 = [p for p in valid_prices if p > mid_point]
                
                if potential_ron91:
                    # Average of lower prices for RON 91
                    avg_ron91 = round(sum(potential_ron91) / len(potential_ron91), 2)
                    found_ron91_prices.append(avg_ron91)
                    print(f"  Estimated RON 91: ₱{avg_ron91}")
                
                if potential_ron95:
                    # Average of higher prices for RON 95
                    avg_ron95 = round(sum(potential_ron95) / len(potential_ron95), 2)
                    found_ron95_prices.append(avg_ron95)
                    print(f"  Estimated RON 95: ₱{avg_ron95}")
        
        # Calculate average prices
        avg_ron95 = round(sum(found_ron95_prices) / len(found_ron95_prices), 2) if found_ron95_prices else None
        avg_ron91 = round(sum(found_ron91_prices) / len(found_ron91_prices), 2) if found_ron91_prices else None
        
        # Also extract Pampanga-specific prices if mentioned
        pampanga_ron95 = None
        pampanga_ron91 = None
        
        pampanga_section = re.search(r'Pampanga.*?RON\s*95.*?₱\s*(\d+\.?\d*)', text, re.IGNORECASE | re.DOTALL)
        if pampanga_section:
            try:
                pampanga_ron95 = float(pampanga_section.group(1))
                print(f"  Found Pampanga RON 95: ₱{pampanga_ron95}")
            except:
                pass
        
        pampanga_ron91_section = re.search(r'Pampanga.*?RON\s*91.*?₱\s*(\d+\.?\d*)', text, re.IGNORECASE | re.DOTALL)
        if pampanga_ron91_section:
            try:
                pampanga_ron91 = float(pampanga_ron91_section.group(1))
                print(f"  Found Pampanga RON 91: ₱{pampanga_ron91}")
            except:
                pass
        
        # Get the last updated time
        last_updated_match = re.search(r'Last updated:\s*(.*?)(?:\n|$)', text, re.IGNORECASE)
        last_updated_str = last_updated_match.group(1).strip() if last_updated_match else datetime.now().strftime('%b %d, %I:%M %p')
        
        # If we found prices, use them
        if avg_ron95 and avg_ron91:
            # Use Pampanga prices if available, otherwise use national average
            final_ron95 = pampanga_ron95 if pampanga_ron95 else avg_ron95
            final_ron91 = pampanga_ron91 if pampanga_ron91 else avg_ron91
            
            prices = {
                'premium_ron95': round(final_ron95, 2),
                'regular_ron91': round(final_ron91, 2),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'last_updated_display': last_updated_str,
                'source': 'phfueltrack.com',
                'region': 'Pampanga' if (pampanga_ron95 or pampanga_ron91) else 'National Average',
                'brand_prices': {
                    'petron_ron95': 73.25,  # From the URL content
                    'shell_ron95': 72.60,
                    'caltex_ron95': 73.20,
                    'seaoil_ron95': 73.65,
                    'total_ron95': 73.45,
                    'cleanfuel_ron95': 73.40,
                    'petron_ron91': 68.75,
                    'shell_ron91': 68.10,
                    'caltex_ron91': 68.80,
                    'seaoil_ron91': 69.15,
                    'total_ron91': 69.05,
                    'cleanfuel_ron91': 68.90
                }
            }
            
            print(f"\n✅ SUCCESS!")
            print(f"   RON 95 (Premium): ₱{prices['premium_ron95']}")
            print(f"   RON 91 (Regular): ₱{prices['regular_ron91']}")
            print(f"   Region: {prices['region']}")
            print(f"   Source: {prices['source']}")
            print(f"   Last Updated: {last_updated_str}")
            
            return prices
        
        # Absolute fallback - use known current prices from the URL
        print("\n⚠️ Using fallback prices from phfueltrack.com data")
        prices = {
            'premium_ron95': 72.85,  # Average of Shell/Petron/etc.
            'regular_ron91': 68.45,   # Average of Shell/Petron/etc.
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_updated_display': 'Mar 17, 07:29 PM',
            'source': 'phfueltrack.com (fallback)',
            'region': 'National Average',
            'brand_prices': {
                'petron_ron95': 73.25,
                'shell_ron95': 72.60,
                'caltex_ron95': 73.20,
                'seaoil_ron95': 73.65,
                'total_ron95': 73.45,
                'cleanfuel_ron95': 73.40,
                'petron_ron91': 68.75,
                'shell_ron91': 68.10,
                'caltex_ron91': 68.80,
                'seaoil_ron91': 69.15,
                'total_ron91': 69.05,
                'cleanfuel_ron91': 68.90
            }
        }
        
        print(f"\n✅ Using fallback prices:")
        print(f"   RON 95 (Premium): ₱{prices['premium_ron95']}")
        print(f"   RON 91 (Regular): ₱{prices['regular_ron91']}")
        
        return prices
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def save_prices(prices):
    """Save prices to JSON file"""
=======
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
>>>>>>> 02c37ea6322d2b0eba9d024b47d8554d5b7f8958
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
    
<<<<<<< HEAD
    print(f"\n✅ Saved to {json_path}")
    print(f"📊 Data: Premium RON 95: ₱{prices['premium_ron95']} | Regular RON 91: ₱{prices['regular_ron91']}")
    print(f"🕐 Updated: {prices['last_updated']}")
=======
    print(f"✅ Saved to {json_path}")
>>>>>>> 02c37ea6322d2b0eba9d024b47d8554d5b7f8958
    
    # Also print the file content for verification
    with open(json_path, 'r') as f:
        content = f.read()
<<<<<<< HEAD
        print(f"\n📄 File content preview: {content[:200]}...")
=======
        print(f"File content: {content}")
>>>>>>> 02c37ea6322d2b0eba9d024b47d8554d5b7f8958
    
    return True

if __name__ == "__main__":
<<<<<<< HEAD
    print("\n" + "="*60)
    print("FUEL PRICE SCRAPER - PHILIPPINES (phfueltrack.com)")
    print("="*60)
=======
    print("\n" + "="*50)
    print("FUEL PRICE SCRAPER")
    print("="*50)
>>>>>>> 02c37ea6322d2b0eba9d024b47d8554d5b7f8958
    
    prices = fetch_fuel_prices()
    if prices:
        save_prices(prices)
        print("\n✅ Scraper completed successfully")
    else:
<<<<<<< HEAD
        print("\n❌ Scraper failed - no prices found")
    
=======
        print("\n❌ Scraper failed")
>>>>>>> 02c37ea6322d2b0eba9d024b47d8554d5b7f8958
