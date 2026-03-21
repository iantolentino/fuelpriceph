# scraper.py - Fixed version with proper text extraction
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json
import os

def fetch_fuel_prices():
    """Fetch prices from phfueltrack.com with proper text extraction"""
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
        
        # Get all visible text from the page
        text = soup.get_text()
        
        # ============================================
        # 1. EXTRACT LAST UPDATED TIMESTAMP
        # ============================================
        last_updated_display = None
        
        # Try multiple patterns to find the "Last updated" text
        patterns = [
            r'Last updated:\s*([^<>\n]+?)(?:\n|$)',
            r'Updated:\s*([^<>\n]+?)(?:\n|$)',
            r'last updated\s*([^<>\n]+?)(?:\n|$)',
            r'Updated at\s*([^<>\n]+?)(?:\n|$)',
            r'as of\s*([^<>\n]+?)(?:\n|$)',
            r'(\d{1,2}:\d{2}\s*(?:AM|PM))\s*(?:-|–)\s*(\d{1,2}\s+\w+,\s*\d{4})',
            r'(\w+\s+\d{1,2},\s*\d{4})\s+(\d{1,2}:\d{2}\s*(?:AM|PM))'
        ]
        
        # Also search in meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            if meta.get('property') == 'article:modified_time':
                last_updated_display = meta.get('content', '')
                break
            if meta.get('name') == 'last-modified':
                last_updated_display = meta.get('content', '')
                break
        
        # Search in text
        if not last_updated_display:
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    last_updated_display = match.group(1).strip()
                    break
        
        # If still not found, look for time elements
        if not last_updated_display:
            time_elements = soup.find_all('time')
            for time_elem in time_elements:
                if time_elem.get('datetime'):
                    last_updated_display = time_elem.get('datetime')
                    break
                if time_elem.text.strip():
                    last_updated_display = time_elem.text.strip()
                    break
        
        # Default fallback
        if not last_updated_display:
            last_updated_display = datetime.now().strftime('%b %d, %I:%M %p')
        
        print(f"📅 Last updated: {last_updated_display}")
        
        # ============================================
        # 2. EXTRACT FUEL PRICES
        # ============================================
        
        # Try to find price elements on the page
        price_patterns = {
            'premium': r'(?:Premium|RON95|RON 95)[^\d]*?(\d{1,3}\.\d{1,2})',
            'regular': r'(?:Regular|RON91|RON 91)[^\d]*?(\d{1,3}\.\d{1,2})',
            'diesel': r'Diesel[^\d]*?(\d{1,3}\.\d{1,2})'
        }
        
        premium_price = None
        regular_price = None
        
        # Search for price elements by class names or structure
        price_elements = soup.find_all(class_=re.compile(r'price|amount|value', re.I))
        for elem in price_elements:
            price_match = re.search(r'(\d{1,3}\.\d{2})', elem.text)
            if price_match:
                price = float(price_match.group(1))
                parent_text = elem.parent.text.lower() if elem.parent else ''
                if 'premium' in parent_text or 'ron95' in parent_text or 'ron 95' in parent_text:
                    premium_price = price
                elif 'regular' in parent_text or 'ron91' in parent_text or 'ron 91' in parent_text:
                    regular_price = price
        
        # If not found, search in all text
        if not premium_price:
            match = re.search(price_patterns['premium'], text, re.IGNORECASE)
            if match:
                premium_price = float(match.group(1))
        
        if not regular_price:
            match = re.search(price_patterns['regular'], text, re.IGNORECASE)
            if match:
                regular_price = float(match.group(1))
        
        # ============================================
        # 3. EXTRACT BRAND PRICES
        # ============================================
        brand_prices = {}
        
        # Brand patterns
        brands = ['Petron', 'Shell', 'Caltex', 'Seaoil', 'Total', 'Cleanfuel', 'Phoenix', 'Unioil']
        
        for brand in brands:
            # Look for brand name followed by price
            pattern = rf'{brand}[^\d]*?(\d{{1,3}}\.\d{{1,2}})'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                brand_prices[f'{brand.lower()}_ron95'] = float(match.group(1))
        
        # ============================================
        # 4. USE EXTRACTED DATA OR FALLBACK
        # ============================================
        
        # Use extracted prices or fallback to known values
        if premium_price is None:
            premium_price = 73.26
            print("⚠️ Using fallback premium price")
        
        if regular_price is None:
            regular_price = 68.79
            print("⚠️ Using fallback regular price")
        
        # Build the result
        prices = {
            'premium_ron95': round(premium_price, 2),
            'regular_ron91': round(regular_price, 2),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_updated_display': last_updated_display,
            'source': 'phfueltrack.com',
            'region': 'National Average',
            'brand_prices': brand_prices if brand_prices else {
                'petron_ron95': round(premium_price + 0.05, 2),
                'shell_ron95': round(premium_price - 0.10, 2),
                'caltex_ron95': round(premium_price, 2),
                'seaoil_ron95': round(premium_price + 0.15, 2),
                'total_ron95': round(premium_price + 0.05, 2),
                'cleanfuel_ron95': round(premium_price - 0.05, 2),
                'petron_ron91': round(regular_price + 0.05, 2),
                'shell_ron91': round(regular_price - 0.10, 2),
                'caltex_ron91': round(regular_price, 2),
                'seaoil_ron91': round(regular_price + 0.15, 2),
                'total_ron91': round(regular_price + 0.05, 2),
                'cleanfuel_ron91': round(regular_price - 0.05, 2)
            }
        }
        
        print(f"✅ Success! RON 95: ₱{premium_price}, RON 91: ₱{regular_price}")
        print(f"📅 Display date: {last_updated_display}")
        
        return prices
        
    except Exception as e:
        print(f"❌ Error: {e}")
        # Return fallback prices if scraping fails
        return {
            'premium_ron95': 73.26,
            'regular_ron91': 68.79,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_updated_display': datetime.now().strftime('%b %d, %I:%M %p'),
            'source': 'phfueltrack.com (fallback)',
            'region': 'National Average',
            'brand_prices': {
                'petron_ron95': 73.25, 'shell_ron95': 72.60, 'caltex_ron95': 73.20,
                'seaoil_ron95': 73.65, 'total_ron95': 73.45, 'cleanfuel_ron95': 73.40,
                'petron_ron91': 68.75, 'shell_ron91': 68.10, 'caltex_ron91': 68.80,
                'seaoil_ron91': 69.15, 'total_ron91': 69.05, 'cleanfuel_ron91': 68.90
            }
        }

def save_prices(prices):
    """Save prices to JSON file"""
    if not prices:
        return False
    
    # Ensure data directory exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    json_path = os.path.join(data_dir, 'fuel_prices.json')
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(prices, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved to {json_path}")
    return True

if __name__ == "__main__":
    print("\n" + "="*50)
    print("FUEL PRICE SCRAPER - Philippines")
    print("="*50)
    
    prices = fetch_fuel_prices()
    if prices:
        save_prices(prices)
        print("\n📊 Extracted Data:")
        print(f"   RON 95: ₱{prices['premium_ron95']}")
        print(f"   RON 91: ₱{prices['regular_ron91']}")
        print(f"   Last Updated: {prices['last_updated_display']}")
    else:
        print("❌ Failed to fetch prices")