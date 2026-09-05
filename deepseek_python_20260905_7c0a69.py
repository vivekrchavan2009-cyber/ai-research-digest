import openai
from typing import Dict, List
import json

class AISynthesizer:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
    
    def categorize_and_summarize(self, raw_data: Dict) -> Dict:
        """Use GPT-4 to categorize and summarize content"""
        
        # Prepare the prompt
        prompt = self._build_prompt(raw_data)
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": """You are an advanced AI research assistant. 
                Categorize AI news into exactly these 3 categories:
                1. Major Model Releases & Updates
                2. Research Breakthroughs & Technical Papers  
                3. Practical Tooling, Agentic Workflows, & No-Code AI
                
                For each item, provide:
                - What the breakthrough is
                - Why it matters (industry impact)
                - Key metrics/benchmarks mentioned
                
                Include source attribution (video title, channel name, key takeaways).
                Return as JSON with categories as keys and lists of items."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        # Parse JSON response
        try:
            categorized = json.loads(response.choices[0].message.content)
        except:
            # Fallback if JSON parsing fails
            categorized = self._fallback_categorize(raw_data)
        
        return categorized
    
    def _build_prompt(self, raw_data: Dict) -> str:
        """Build the prompt from raw scraped data"""
        prompt = "Here is the raw AI content from the last 7 days:\n\n"
        
        if raw_data.get('videos'):
            prompt += "=== YouTube Videos ===\n"
            for v in raw_data['videos'][:15]:  # Limit to 15
                prompt += f"Title: {v['title']}\n"
                prompt += f"Channel: {v['channel_name']}\n"
                prompt += f"Summary: {v['summary'][:200]}\n\n"
        
        if raw_data.get('papers'):
            prompt += "=== Research Papers ===\n"
            for p in raw_data['papers'][:10]:
                prompt += f"Title: {p['title']}\n"
                prompt += f"Category: {p['category']}\n"
                prompt += f"Summary: {p['summary'][:300]}\n\n"
        
        if raw_data.get('blog_posts'):
            prompt += "=== Blog Posts ===\n"
            for b in raw_data['blog_posts'][:5]:
                prompt += f"Title: {b['title']}\n"
                prompt += f"Summary: {b['summary'][:200]}\n\n"
        
        prompt += "\nPlease categorize and summarize the above content into the 3 specified categories."
        return prompt
    
    def _fallback_categorize(self, raw_data: Dict) -> Dict:
        """Fallback categorization without AI"""
        categories = {
            "Major Model Releases & Updates": [],
            "Research Breakthroughs & Technical Papers": [],
            "Practical Tooling, Agentic Workflows, & No-Code AI": []
        }
        
        # Simple keyword-based categorization
        for video in raw_data.get('videos', []):
            title = video['title'].lower()
            if any(word in title for word in ['release', 'update', 'launch', 'new model']):
                categories["Major Model Releases & Updates"].append({
                    "title": video['title'],
                    "source": f"YouTube: {video['channel_name']}",
                    "summary": video['summary'][:200],
                    "url": video['url']
                })
            elif any(word in title for word in ['paper', 'research', 'breakthrough', 'study']):
                categories["Research Breakthroughs & Technical Papers"].append({
                    "title": video['title'],
                    "source": f"YouTube: {video['channel_name']}",
                    "summary": video['summary'][:200],
                    "url": video['url']
                })
            else:
                categories["Practical Tooling, Agentic Workflows, & No-Code AI"].append({
                    "title": video['title'],
                    "source": f"YouTube: {video['channel_name']}",
                    "summary": video['summary'][:200],
                    "url": video['url']
                })
        
        # Add papers to Research category
        for paper in raw_data.get('papers', []):
            categories["Research Breakthroughs & Technical Papers"].append({
                "title": paper['title'],
                "source": f"arXiv: {paper['category']}",
                "summary": paper['summary'][:200],
                "url": paper['url']
            })
        
        return categories