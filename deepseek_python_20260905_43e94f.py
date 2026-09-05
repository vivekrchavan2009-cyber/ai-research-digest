import requests
from bs4 import BeautifulSoup
import feedparser
import re
from datetime import datetime, timedelta
from typing import List, Dict

class ContentScraper:
    def __init__(self, channels, rss_feeds):
        self.channels = channels
        self.rss_feeds = rss_feeds
    
    def fetch_youtube_videos(self, channel_id: str, days: int = 7) -> List[Dict]:
        """Fetch recent videos from a YouTube channel using RSS feed"""
        url = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
        feed = feedparser.parse(url)
        
        cutoff = datetime.now() - timedelta(days=days)
        videos = []
        
        for entry in feed.entries[:20]:  # Limit to 20 per channel
            published = datetime(*entry.published_parsed[:6])
            if published < cutoff:
                continue
                
            video_id = entry.id.split(':')[-1]
            videos.append({
                'title': entry.title,
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'published': published.isoformat(),
                'channel_name': entry.author_detail.get('name', 'Unknown'),
                'summary': entry.get('summary', ''),
                'video_id': video_id
            })
        
        return videos
    
    def fetch_arxiv_papers(self, days: int = 7) -> List[Dict]:
        """Fetch recent arXiv papers in AI"""
        papers = []
        cutoff = datetime.now() - timedelta(days=days)
        
        for feed_url in self.rss_feeds:
            if 'arxiv' not in feed_url:
                continue
                
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:50]:
                published = datetime(*entry.published_parsed[:6])
                if published < cutoff:
                    continue
                    
                # Extract arXiv ID and category
                arxiv_id = entry.id.split('/')[-1]
                category = self._extract_category(entry)
                
                papers.append({
                    'title': entry.title,
                    'url': entry.link,
                    'published': published.isoformat(),
                    'summary': entry.get('summary', ''),
                    'arxiv_id': arxiv_id,
                    'category': category,
                    'source': 'arXiv'
                })
        
        return papers
    
    def _extract_category(self, entry) -> str:
        """Extract arXiv category from entry"""
        if hasattr(entry, 'tags'):
            for tag in entry.tags:
                if 'cs.' in tag.term or 'stat.' in tag.term:
                    return tag.term
        return 'cs.AI'
    
    def scrape_all(self, days: int = 7) -> Dict:
        """Scrape all sources and return combined data"""
        all_videos = []
        for channel in self.channels:
            videos = self.fetch_youtube_videos(channel, days)
            all_videos.extend(videos)
        
        all_papers = self.fetch_arxiv_papers(days)
        
        # Fetch blog posts from RSS
        blog_posts = []
        for feed_url in self.rss_feeds:
            if 'arxiv' not in feed_url and 'youtube' not in feed_url:
                feed = feedparser.parse(feed_url)
                cutoff = datetime.now() - timedelta(days=days)
                for entry in feed.entries[:10]:
                    published = datetime(*entry.published_parsed[:6])
                    if published >= cutoff:
                        blog_posts.append({
                            'title': entry.title,
                            'url': entry.link,
                            'published': published.isoformat(),
                            'summary': entry.get('summary', ''),
                            'source': 'Blog'
                        })
        
        return {
            'videos': all_videos,
            'papers': all_papers,
            'blog_posts': blog_posts,
            'total_items': len(all_videos) + len(all_papers) + len(blog_posts)
        }