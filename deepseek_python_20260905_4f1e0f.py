import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    YOUTUBE_CHANNELS = [
        'UCXuqSBlHAE6Xw-yeJA0Tunw',  # AI Explained
        'UCpMqUZv3DqNZMqEj3uSS1OA',  # Matt Wolfe
        'UCIuQSk_1Aq57E5k6XuZtUXA',  # Wes Roth
        'UCbfYPyITQ-7l4upoX8nvctg',  # Two Minute Papers
        'UCZHmQk6T2iE8giJj56nuvJw',  # Yannic Kilcher
    ]
    RSS_FEEDS = [
        'https://arxiv.org/rss/cs.AI',
        'https://feeds.feedburner.com/OpenAI',
        'https://deepmind.com/blog/rss.xml',
    ]