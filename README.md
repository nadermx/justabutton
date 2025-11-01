# JustAButton

> One button. One chance. Forever.

A social experiment exploring human behavior with the simplest possible interface: a button you can only click once.

🔴 **Live Site:** [www.justabutton.org](https://www.justabutton.org)

## What Is This?

It's literally just a button. But there's a catch:

- **You can only click it once**
- **Your click is recorded forever**
- **Everyone sees the same global statistics**
- **You can challenge friends to beat your time**

That's it. No account creation, no complicated features, just pure simplicity and curiosity.

## The Concept

When you land on the page, a timer starts. The question is simple: *how fast will you click?*

Once you click:
- ✅ Your time is recorded permanently (stored in localStorage + database)
- 📊 You see your global ranking among all clickers
- 🌍 Global statistics update in real-time
- 🏆 You can share a challenge link with friends
- 🚫 You can never click again (attempts are tracked as "reclick attempts")

## Stats & Features

### Personal Stats
- **Your Time** - How fast you clicked (in seconds)
- **Your Ranking** - Where you place among all clickers
- **Performance Comparison** - How you compare to the average

### Global Statistics
- **Total Clicks** - All-time button clicks
- **Total Visitors** - People who visited the page
- **Click-Through Rate** - Percentage of visitors who clicked
- **Average Time** - Mean time to click
- **Fastest Click** - The speed record
- **Slowest Click** - The slowest recorded click
- **Bounce Rate** - Visitors who left without clicking
- **Reclick Attempts** - Times people tried to click again
- **Today's Stats** - Visitors and clicks from today
- **Geographic Data** - Clicks by country with flags
- **Browser Stats** - Most popular browsers
- **Referrer Tracking** - Top referring websites

### Friend Challenge Feature
Share a personalized challenge URL with encoded performance data:
- Friends see your time and ranking before they click
- After clicking, they see a head-to-head comparison
- Challenge URLs are compact (6-character base62 encoding)
- Works even if your friend already clicked

## Tech Stack

### Backend
- **Django 5.2.7** - Python web framework
- **SQLite** - Database (PostgreSQL-ready)
- **Gunicorn** - WSGI server
- **IP2Location** - Geographic data lookup

### Frontend
- **Vanilla JavaScript** - No frameworks, pure performance
- **Bootstrap 5.3.2** - Responsive grid and utilities
- **Chart.js** - Data visualizations
- **Canvas Confetti** - Celebration effects

### Infrastructure
- **Nginx** - Reverse proxy with HTTP/2
- **Supervisor** - Process management
- **Ansible** - Automated deployment
- **Let's Encrypt** - SSL/TLS certificates
- **Clicky Analytics** - Privacy-friendly tracking

## Project Structure

```
justabutton/
├── button/                 # Main Django app
│   ├── models.py          # PageSession and ButtonClick models
│   ├── views.py           # API endpoints and page rendering
│   ├── urls.py            # URL routing
│   └── templates/
│       └── button/
│           └── index.html # Single-page application
├── config/                # Django project settings
│   ├── settings.py        # Development settings
│   ├── settings_prod.py   # Production settings
│   └── wsgi.py           # WSGI configuration
├── ansible/               # Deployment automation
│   ├── djangodeployubuntu20.yml
│   ├── update_nginx.yml
│   ├── setup_ssl.yml
│   └── files/            # Config templates
│       ├── nginx.conf.j2
│       └── supervisor.conf.j2
├── static/               # Static assets
├── manage.py            # Django management
└── requirements.txt     # Python dependencies
```

## Key Features Breakdown

### 1. One-Click-Per-Person System
Uses localStorage + session tracking to ensure each person can only click once:
```javascript
const STORAGE_KEY = 'justabutton_clicked';
const clickData = localStorage.getItem(STORAGE_KEY);
```

### 2. Performance Encoding
Friend challenges use bit-packing to encode time, rank, and percentile into a compact URL:
```
Time (16 bits) | Rank (12 bits) | Percentage (12 bits) | Faster flag (1 bit)
Encoded to base62: http://justabutton.org/?c=3zWG1p
```

### 3. Geographic Tracking
IP addresses are resolved to countries using:
- **Local IP2Location database** (primary)
- **ip-api.com fallback** (if local fails)

### 4. Real-Time Stats
All statistics update immediately after each click:
- Django ORM aggregations for efficiency
- JSON API endpoints consumed by frontend JavaScript
- No page reload required

### 5. Security Features
- **Referrer sanitization** - Blocks XSS and template injection
- **Time validation** - Rejects impossible times (< 0.01s or > 999.99s)
- **CSRF protection** - Django's built-in CSRF middleware
- **Rate limiting** - Via nginx configuration

## Setup

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/nadermx/justabutton.git
cd justabutton
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Start development server**
```bash
python manage.py runserver
```

6. **Visit**
```
http://127.0.0.1:8000/
```

## Contributing

This is a simple personal project, but contributions are welcome! Feel free to:
- Report bugs via GitHub Issues
- Suggest features
- Submit pull requests

## Fun Facts

- The entire frontend is a single HTML file (~1800 lines)
- Challenge URLs are only 6 characters long
- The database tracks every click forever
- People have tried to click again over 1000+ times
- The fastest recorded click is under 0.5 seconds
- Over 50 countries have clicked the button

## Why?

Because sometimes the internet is too complicated. This is a reminder that simple things can still be interesting.

What will you do when you can only click once?

## License

MIT License - See LICENSE file for details

## Author

Created by [nadermx](https://john.nader.mx) with curiosity about buttons.

---

**Live Site:** [www.justabutton.org](https://www.justabutton.org)
**Source:** [github.com/nadermx/justabutton](https://github.com/nadermx/justabutton)
