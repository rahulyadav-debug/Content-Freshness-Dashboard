#!/usr/bin/env python3
"""
Content Freshness Extractor
Extracts update dates from web pages and calculates content age.
Outputs results.csv for upload to the Content Intelligence Dashboard.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import sys
import time
from urllib.parse import urlparse

# Headers to mimic browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def extract_date_from_page(url):
    """Extract update date from a web page using multiple methods."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        # Method 1: Check Last-Modified header
        if 'Last-Modified' in response.headers:
            try:
                last_mod = response.headers['Last-Modified']
                date_obj = datetime.strptime(last_mod, '%a, %d %b %Y %H:%M:%S %Z')
                days_old = (datetime.now() - date_obj).days
                return {
                    'date': date_obj.strftime('%Y-%m-%d'),
                    'days_old': days_old,
                    'method': 'Last-Modified Header'
                }
            except:
                pass
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Method 2: article:published_time (common on blogs)
        date_meta = soup.find('meta', property='article:published_time')
        if date_meta and date_meta.get('content'):
            try:
                date_str = date_meta.get('content')
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00').split('+')[0].split('-')[0:3].__str__().replace("['", "").replace("']", "").replace(", ", "-"))
                # Simpler parsing
                date_clean = date_str[:10]
                date_obj = datetime.strptime(date_clean, '%Y-%m-%d')
                days_old = (datetime.now() - date_obj).days
                return {
                    'date': date_clean,
                    'days_old': days_old,
                    'method': 'article:published_time'
                }
            except:
                pass
        
        # Method 3: datePublished (JSON-LD)
        date_meta = soup.find('meta', attrs={'itemprop': 'datePublished'})
        if date_meta and date_meta.get('content'):
            try:
                date_str = date_meta.get('content')
                date_clean = date_str[:10]
                date_obj = datetime.strptime(date_clean, '%Y-%m-%d')
                days_old = (datetime.now() - date_obj).days
                return {
                    'date': date_clean,
                    'days_old': days_old,
                    'method': 'datePublished (JSON-LD)'
                }
            except:
                pass
        
        # Method 4: Updated / Modified meta tag
        for meta_name in ['updated', 'modified', 'date', 'publish_date', 'article:modified_time']:
            date_meta = soup.find('meta', attrs={'property': meta_name}) or \
                       soup.find('meta', attrs={'name': meta_name})
            if date_meta and date_meta.get('content'):
                try:
                    date_str = date_meta.get('content')
                    date_clean = date_str[:10]
                    date_obj = datetime.strptime(date_clean, '%Y-%m-%d')
                    days_old = (datetime.now() - date_obj).days
                    return {
                        'date': date_clean,
                        'days_old': days_old,
                        'method': f'Meta: {meta_name}'
                    }
                except:
                    pass
        
        # Method 5: Look for common date patterns in text
        # Updated: YYYY-MM-DD or Last Updated: YYYY-MM-DD
        import re
        text = soup.get_text()
        date_pattern = r'(\d{4}-\d{2}-\d{2})'
        matches = re.findall(date_pattern, text)
        if matches:
            try:
                # Take the most recent date found
                dates = []
                for match in matches:
                    try:
                        d = datetime.strptime(match, '%Y-%m-%d')
                        if d <= datetime.now():
                            dates.append(d)
                    except:
                        pass
                if dates:
                    date_obj = max(dates)
                    days_old = (datetime.now() - date_obj).days
                    return {
                        'date': date_obj.strftime('%Y-%m-%d'),
                        'days_old': days_old,
                        'method': 'Text Pattern (YYYY-MM-DD)'
                    }
            except:
                pass
        
        # No date found
        return {
            'date': '',
            'days_old': None,
            'method': 'Not Found'
        }
    
    except requests.exceptions.RequestException as e:
        return {
            'date': '',
            'days_old': None,
            'method': f'Error: {str(e)[:30]}'
        }
    except Exception as e:
        return {
            'date': '',
            'days_old': None,
            'method': f'Error: {str(e)[:30]}'
        }

def load_urls(filename):
    """Load URLs from file (CSV or TXT)."""
    urls = []
    try:
        if filename.endswith('.csv'):
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    url = row.get('url', '').strip()
                    if url and url.startswith('http'):
                        urls.append(url)
        else:  # TXT file
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    url = line.strip()
                    if url and url.startswith('http'):
                        urls.append(url)
    except FileNotFoundError:
        print(f"❌ Error: File '{filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)
    
    return urls

def save_results(results, output_file='results.csv'):
    """Save results to CSV."""
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['url', 'date', 'days_old', 'method'])
            writer.writeheader()
            writer.writerows(results)
        print(f"\n✅ Results saved to: {output_file}")
        print(f"📊 Summary:")
        print(f"   Total URLs: {len(results)}")
        found = len([r for r in results if r['date']])
        print(f"   Dates found: {found}")
        print(f"   Dates not found: {len(results) - found}")
    except Exception as e:
        print(f"❌ Error saving results: {e}")
        sys.exit(1)

def main():
    print("\n" + "="*60)
    print("🎯 Content Freshness Extractor")
    print("="*60)
    
    # Get input file
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("\nEnter URL file (urls.txt or urls.csv): ").strip()
        if not input_file:
            print("❌ No file specified")
            sys.exit(1)
    
    # Load URLs
    print(f"\n📂 Loading URLs from: {input_file}")
    urls = load_urls(input_file)
    if not urls:
        print("❌ No URLs found in file")
        sys.exit(1)
    
    print(f"✓ Loaded {len(urls)} URLs")
    
    # Process URLs
    print(f"\n⏳ Extracting dates from pages...")
    print("-" * 60)
    
    results = []
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Processing: {urlparse(url).hostname}...", end=" ")
        result = extract_date_from_page(url)
        result['url'] = url
        results.append(result)
        
        if result['date']:
            print(f"✓ Found: {result['date']} ({result['days_old']}d old) [{result['method']}]")
        else:
            print(f"✗ Not found [{result['method']}]")
        
        # Be respectful to servers - add delay
        time.sleep(0.5)
    
    # Save results
    save_results(results)
    
    print("\n" + "="*60)
    print("✅ Done! Upload results.csv to the dashboard")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
