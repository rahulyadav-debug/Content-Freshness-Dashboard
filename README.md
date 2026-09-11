# Content Freshness Dashboard

A modern, interactive SEO analytics dashboard that analyzes content freshness and GA4 traffic data. Identify which pages need updates based on traffic volume and content age.

![Status](https://img.shields.io/badge/status-active-success.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![GitHub](https://img.shields.io/badge/GitHub-rahulyadav--debug-black.svg)

## 🎯 Features

- **Google Analytics 4 Integration** - Connect directly to your GA4 property and pull traffic data (last 90 days)
- **Content Freshness Analysis** - Upload content update dates to track staleness
- **Priority Matrix** - Automatically categorizes URLs into:
  - 🔴 **Act Now** - High traffic + stale content (90+ days)
  - 🟢 **Protect** - High traffic + fresh content
  - 🟡 **Queue** - Low traffic + stale content
  - ⚪ **Monitor** - Low traffic + fresh content
- **Interactive Dashboard** - Search, filter, and sort URLs by priority
- **Traffic Visualization** - View sessions, pageviews, users, and traffic distribution
- **Staleness Breakdown** - Track content age distribution (7, 30, 90, 120+ days)
- **Privacy First** - All data stays local in your browser (no server processing)
- **Responsive Design** - Works seamlessly on desktop and tablet

## 🚀 Quick Start

### 1. Open the Dashboard
Simply open `index.html` in your web browser (no installation required).

```bash
# On Windows
start index.html

# On macOS
open index.html

# On Linux
xdg-open index.html
```

Or deploy to Vercel (see Deployment section).

### 2. Connect Google Analytics

1. **Get OAuth Client ID** (one-time setup):
   - Visit [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Create a new OAuth 2.0 Client ID (Web application)
   - Add `http://localhost:8080` as an Authorized JavaScript Origin
   - For Vercel deployment, add your Vercel domain
   - Copy the Client ID

2. **Enter Client ID** in Step 1 of the dashboard

3. **Authenticate** with Google (requires Viewer access to your GA4 property)

### 3. Pull GA4 Data

1. Get your **GA4 Property ID** from Analytics → Admin → Property Settings
2. Enter the Property ID in Step 2
3. Click "Fetch Traffic" to pull last 90 days of data

### 4. Upload Files

**URL List** (required):
- CSV or TXT format
- CSV: Include a `url` column
- TXT: One URL per line
- Example URLs: `https://example.com/page` or `https://www.example.com/path`

**Freshness Data** (optional):
- CSV export from `extract_dates.py` (or compatible format)
- Columns: `url`, `date`, `days_old`, `method`
- Example:
  ```
  url,date,days_old,method
  https://example.com/page1,2024-06-15,88,Last-Modified
  https://example.com/page2,2024-07-01,72,HTML-Meta
  ```

## 📋 Data Format Examples

### URL List (CSV)
```csv
url
https://example.com/page1
https://example.com/page2
https://example.com/blog/article
```

### URL List (TXT)
```
https://example.com/page1
https://example.com/page2
https://example.com/blog/article
```

### Freshness Data (CSV)
```csv
url,date,days_old,method
https://example.com/page1,2024-06-15,88,Last-Modified
https://example.com/page2,2024-07-01,72,HTML-Meta
https://example.com/page3,2024-08-10,20,Sitemap
```

## 🔄 Priority Algorithm

The dashboard calculates priority scores using:
- **Content Staleness** (60% weight): How old is the content?
- **Traffic Volume** (40% weight): How many people visit this page?

**Priority Levels:**
- **High**: Score > 55% (Act Now - needs update soon)
- **Medium**: Score 30-55% (Queue - update after high priority)
- **Low**: Score < 30% (Monitor - can wait)

## 📊 Dashboard Sections

1. **Priority Matrix** - 4-quadrant view of content performance
2. **Staleness Breakdown** - Distribution of content age
3. **GA4 Traffic Stats** - Total sessions, pageviews, users
4. **URL Table** - Sortable, filterable list with full details

## 🌐 Deployment

### Deploy to Vercel (Recommended)

1. Push to GitHub first:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/Content-Freshness-Dashboard.git
   git push -u origin main
   ```

2. Import to Vercel:
   - Visit [Vercel](https://vercel.com/new)
   - Select "Import Git Repository"
   - Connect your GitHub account and select this repo
   - Click "Deploy"

3. **Update OAuth Client ID**:
   - Add your Vercel domain to Google Cloud Console OAuth settings
   - Update the Client ID in Step 1 of the dashboard

### Self-Hosted Options

- **GitHub Pages**: Push to GitHub and enable Pages in settings
- **Netlify**: Similar to Vercel, connect your GitHub repo
- **Any HTTP Server**: Copy `index.html` to your server

## 🔐 Security & Privacy

- ✅ No backend server (runs 100% in browser)
- ✅ Google OAuth only (secure authentication)
- ✅ Data never leaves your machine
- ✅ Supports private repositories
- ✅ All data is client-side only

## 🛠 Customization

### Change Company Name
Replace `pristyncare.com` references in the `peek()` function and table rendering

### Adjust Time Window
Change `const DAYS_BACK = 90;` to fetch different date ranges

### Customize Color Scheme
Modify CSS variables in `:root` selector (top of `<style>`)

### Add Custom Metrics
Extend the GA4 fetch to include additional metrics from the Analytics Data API

## 📚 Create Freshness Data

If you don't have freshness data yet, create it using a web scraper:

### Python Example
```python
import requests
from datetime import datetime
from bs4 import BeautifulSoup

urls = [
    'https://example.com/page1',
    'https://example.com/page2',
]

results = []
for url in urls:
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Try multiple date sources
        date_meta = soup.find('meta', property='article:published_time')
        date_str = date_meta.get('content') if date_meta else None
        
        if date_str:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            days_old = (datetime.now(date_obj.tzinfo) - date_obj).days
        else:
            days_old = None
        
        results.append({
            'url': url,
            'date': date_str[:10] if date_str else '',
            'days_old': days_old,
            'method': 'article:published_time' if date_str else 'unknown'
        })
    except Exception as e:
        print(f"Error scraping {url}: {e}")

# Save to CSV
import csv
with open('results.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['url', 'date', 'days_old', 'method'])
    writer.writeheader()
    writer.writerows(results)
```

## 🐛 Troubleshooting

### "Invalid Client ID" error
- Make sure you copied the full OAuth Client ID from Google Cloud Console
- Verify the domain is added to Authorized JavaScript Origins

### "No data returned from GA4"
- Check that your URLs exactly match the page paths in GA4 (with protocol and case sensitivity)
- Ensure the Property ID is correct
- Verify you have Viewer access to the GA4 property
- Wait for GA4 to process data (can take 24-48 hours)

### CSV Import failing
- Ensure headers are lowercase (`url`, `date`, `days_old`, `method`)
- Make sure URLs start with `http://` or `https://`
- Check for special characters in CSV (quote them properly)

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs via GitHub Issues
- Suggest features or improvements
- Submit pull requests
- Fork and customize for your needs

## 📧 Support

For issues, questions, or feedback:
- Open a GitHub Issue
- Check existing issues for solutions
- Review the troubleshooting section above

## 🎓 Credits

Built for SEO teams and content managers who want to make data-driven decisions about content updates.

---

**Made with ❤️ for better SEO analytics**
