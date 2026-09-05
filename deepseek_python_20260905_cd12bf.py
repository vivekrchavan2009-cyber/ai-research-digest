from flask import Flask, render_template, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import json
from datetime import datetime
import os

from config import Config
from scraper import ContentScraper
from synthesizer import AISynthesizer

app = Flask(__name__)
app.config.from_object(Config)

# Initialize components
scraper = ContentScraper(
    channels=Config.YOUTUBE_CHANNELS,
    rss_feeds=Config.RSS_FEEDS
)
synthesizer = AISynthesizer(api_key=Config.OPENAI_API_KEY)

# Cache for digest results
cache = {
    'last_update': None,
    'digest': None,
    'raw_data': None
}

def generate_digest():
    """Generate the full AI digest"""
    print(f"[{datetime.now()}] Starting digest generation...")
    
    # Step 1: Scrape all content
    raw_data = scraper.scrape_all(days=7)
    cache['raw_data'] = raw_data
    print(f"Scraped {raw_data['total_items']} items")
    
    # Step 2: AI synthesis
    if Config.OPENAI_API_KEY:
        try:
            digest = synthesizer.categorize_and_summarize(raw_data)
            cache['digest'] = digest
            print("AI synthesis complete")
        except Exception as e:
            print(f"AI synthesis failed: {e}")
            # Use fallback
            digest = synthesizer._fallback_categorize(raw_data)
            cache['digest'] = digest
    else:
        # No API key, use fallback
        digest = synthesizer._fallback_categorize(raw_data)
        cache['digest'] = digest
    
    cache['last_update'] = datetime.now().isoformat()
    print(f"[{datetime.now()}] Digest generation complete")
    
    return digest

# Schedule automatic updates every 24 hours
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=generate_digest,
    trigger=IntervalTrigger(hours=24),
    id='daily_digest',
    replace_existing=True
)
scheduler.start()

# Generate initial digest on startup
with app.app_context():
    generate_digest()

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html', 
                         last_update=cache['last_update'],
                         digest=cache['digest'])

@app.route('/api/digest')
def api_digest():
    """API endpoint for digest data"""
    if cache['digest'] is None:
        return jsonify({'error': 'No digest available yet'}), 404
    
    return jsonify({
        'last_update': cache['last_update'],
        'digest': cache['digest'],
        'total_items': cache['raw_data']['total_items'] if cache['raw_data'] else 0
    })

@app.route('/api/refresh')
def api_refresh():
    """Manually trigger a refresh"""
    digest = generate_digest()
    return jsonify({
        'status': 'success',
        'last_update': cache['last_update']
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'last_update': cache['last_update'],
        'has_digest': cache['digest'] is not None
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)