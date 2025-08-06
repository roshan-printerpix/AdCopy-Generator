"""
Phase 2: Data Cleaning Module
Handles noise removal, length limits, and relevance scoring using custom code.
"""

import re
import html
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import json


class DataCleaner:
    """Custom data cleaning implementation for ad creative pipeline."""
    
    def __init__(self, max_tokens: int = 8000, min_relevance_score: float = 7.0):
        self.max_tokens = max_tokens
        self.min_relevance_score = min_relevance_score
        
        # Noise patterns to remove
        self.noise_patterns = [
            r'<[^>]+>',  # HTML tags
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # URLs
            r'@\w+',  # Usernames
            r'#\w+',  # Hashtags (optional - might want to keep some)
            r'\[.*?\]',  # Bracketed content
            r'\(.*?\)',  # Parenthetical content (be careful with this)
            r'^\s*&gt;.*$',  # Quote lines
            r'^\s*\*.*$',  # Bullet points
            r'^\s*-.*$',  # Dash points
        ]
        
        # Relevance keywords for ad context
        self.relevance_keywords = {
            'high': ['buy', 'purchase', 'deal', 'offer', 'discount', 'sale', 'product', 'service', 'brand', 'quality', 'best', 'top', 'review', 'recommend'],
            'medium': ['good', 'great', 'amazing', 'awesome', 'love', 'like', 'use', 'try', 'experience', 'worth', 'value'],
            'low': ['maybe', 'perhaps', 'might', 'could', 'possibly', 'sometimes', 'occasionally']
        }

    def clean_text(self, raw_text: str) -> str:
        """Remove noise from raw text."""
        if not raw_text:
            return ""
            
        # Decode HTML entities
        text = html.unescape(raw_text)
        
        # Remove noise patterns
        for pattern in self.noise_patterns:
            text = re.sub(pattern, ' ', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double
        text = text.strip()
        
        return text

    def enforce_length_limit(self, text: str) -> str:
        """Enforce token length limits (approximating 4 chars = 1 token)."""
        if not text:
            return ""
            
        # Rough token estimation: 4 characters ≈ 1 token
        estimated_tokens = len(text) / 4
        
        if estimated_tokens <= self.max_tokens:
            return text
            
        # Truncate to approximate token limit, try to break at sentence boundaries
        max_chars = int(self.max_tokens * 4)
        
        if len(text) <= max_chars:
            return text
            
        # Try to break at sentence boundary
        truncated = text[:max_chars]
        last_period = truncated.rfind('.')
        last_exclamation = truncated.rfind('!')
        last_question = truncated.rfind('?')
        
        sentence_end = max(last_period, last_exclamation, last_question)
        
        if sentence_end > max_chars * 0.8:  # If sentence break is reasonably close
            return text[:sentence_end + 1]
        else:
            return truncated + "..."

    def calculate_relevance_score(self, text: str) -> float:
        """Calculate relevance score for ad context (0-10 scale)."""
        if not text:
            return 0.0
            
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        if not words:
            return 0.0
            
        # Count keyword matches
        high_matches = sum(1 for word in words if word in self.relevance_keywords['high'])
        medium_matches = sum(1 for word in words if word in self.relevance_keywords['medium'])
        low_matches = sum(1 for word in words if word in self.relevance_keywords['low'])
        
        # Calculate weighted score
        total_words = len(words)
        high_ratio = high_matches / total_words
        medium_ratio = medium_matches / total_words
        low_ratio = low_matches / total_words
        
        # Weighted scoring
        score = (high_ratio * 10) + (medium_ratio * 6) + (low_ratio * 3)
        
        # Boost for longer, more substantial content
        length_boost = min(2.0, len(text) / 1000)
        
        # Penalty for very short content
        if len(text) < 100:
            score *= 0.5
            
        final_score = min(10.0, score + length_boost)
        return round(final_score, 2)

    def extract_story_core(self, text: str) -> str:
        """Extract the core narrative/story from text."""
        if not text:
            return ""
            
        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if len(paragraphs) <= 4:
            return text
            
        # Score paragraphs by story indicators
        story_indicators = ['story', 'experience', 'happened', 'when', 'then', 'after', 'before', 'suddenly', 'realized', 'discovered']
        
        scored_paragraphs = []
        for i, para in enumerate(paragraphs):
            para_lower = para.lower()
            story_score = sum(1 for indicator in story_indicators if indicator in para_lower)
            
            # Boost first and last paragraphs slightly
            if i == 0 or i == len(paragraphs) - 1:
                story_score += 0.5
                
            scored_paragraphs.append((story_score, para))
        
        # Sort by score and take top 4
        scored_paragraphs.sort(key=lambda x: x[0], reverse=True)
        top_paragraphs = [para for _, para in scored_paragraphs[:4]]
        
        return '\n\n'.join(top_paragraphs)

    def process_document(self, raw_data: Dict) -> Optional[Dict]:
        """Process a single document through the cleaning pipeline."""
        try:
            # Extract text content
            raw_text = raw_data.get('content', '') or raw_data.get('text', '') or raw_data.get('body', '')
            
            if not raw_text:
                return None
                
            # Step 1: Clean noise
            cleaned_text = self.clean_text(raw_text)
            
            if not cleaned_text:
                return None
                
            # Step 2: Extract story core
            story_core = self.extract_story_core(cleaned_text)
            
            # Step 3: Enforce length limits
            final_text = self.enforce_length_limit(story_core)
            
            # Step 4: Calculate relevance score
            relevance_score = self.calculate_relevance_score(final_text)
            
            # Step 5: Filter by relevance threshold
            if relevance_score < self.min_relevance_score:
                return None
                
            # Return cleaned document
            cleaned_doc = {
                'source': raw_data.get('source', 'unknown'),
                'url': raw_data.get('url', ''),
                'original_length': len(raw_text),
                'cleaned_length': len(final_text),
                'body': final_text,
                'relevance_score': relevance_score,
                'processed_at': raw_data.get('collected_at', ''),
                'metadata': {
                    'cleaning_applied': True,
                    'noise_removed': len(raw_text) - len(cleaned_text),
                    'length_truncated': len(story_core) > len(final_text)
                }
            }
            
            return cleaned_doc
            
        except Exception as e:
            print(f"Error processing document: {e}")
            return None

    def process_batch(self, raw_documents: List[Dict]) -> List[Dict]:
        """Process a batch of documents."""
        cleaned_docs = []
        
        for doc in raw_documents:
            cleaned_doc = self.process_document(doc)
            if cleaned_doc:
                cleaned_docs.append(cleaned_doc)
                
        return cleaned_docs

    def get_cleaning_stats(self, original_docs: List[Dict], cleaned_docs: List[Dict]) -> Dict:
        """Generate cleaning statistics."""
        return {
            'original_count': len(original_docs),
            'cleaned_count': len(cleaned_docs),
            'filtered_out': len(original_docs) - len(cleaned_docs),
            'retention_rate': len(cleaned_docs) / len(original_docs) if original_docs else 0,
            'avg_relevance_score': sum(doc['relevance_score'] for doc in cleaned_docs) / len(cleaned_docs) if cleaned_docs else 0
        }


# Example usage and testing
if __name__ == "__main__":
    # Test the cleaner
    cleaner = DataCleaner()
    
    # Sample raw data
    sample_data = [
        {
            'source': 'reddit',
            'url': 'https://reddit.com/r/test/123',
            'content': '''<p>This is an amazing product! I bought it last week and it's been great. 
            Check out this link: https://example.com for more info. @username recommended it to me.
            
            The quality is top-notch and the price was a great deal. I'd definitely recommend 
            this to anyone looking for a good purchase. The experience has been awesome so far.
            
            #ProductReview #GreatDeal</p>''',
            'collected_at': '2025-01-08T10:00:00Z'
        }
    ]
    
    cleaned = cleaner.process_batch(sample_data)
    stats = cleaner.get_cleaning_stats(sample_data, cleaned)
    
    print("Cleaned Documents:")
    print(json.dumps(cleaned, indent=2))
    print("\nCleaning Stats:")
    print(json.dumps(stats, indent=2))