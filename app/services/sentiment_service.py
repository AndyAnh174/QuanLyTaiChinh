"""
Sentiment analysis service for transaction notes
"""
from typing import Optional, Dict
from .ai_service import ai_service


class SentimentService:
    """
    Service for analyzing sentiment in transaction notes/descriptions
    """
    
    SENTIMENT_PROMPT = """Analyze the sentiment of this transaction note/description.

Classify the sentiment as one of:
- "happy" - User feels good about this spending
- "regretful" - User regrets this spending
- "necessary" - User considers this necessary spending
- "neutral" - No strong emotion

Return only the sentiment word, nothing else."""

    def analyze_sentiment(self, text: str) -> Optional[str]:
        """
        Analyze sentiment of transaction note/description
        
        Args:
            text: Transaction note or description
        
        Returns:
            Sentiment: 'happy', 'regretful', 'necessary', or 'neutral'
        """
        if not text or len(text.strip()) < 5:
            return 'neutral'
        
        try:
            sentiment = ai_service.generate_text(text, self.SENTIMENT_PROMPT).strip().lower()
            
            # Validate sentiment
            valid_sentiments = ['happy', 'regretful', 'necessary', 'neutral']
            if sentiment in valid_sentiments:
                return sentiment
            else:
                return 'neutral'
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return 'neutral'
    
    def get_sentiment_score(self, sentiment: str) -> float:
        """
        Convert sentiment to numeric score (0-1)
        
        Args:
            sentiment: Sentiment string
        
        Returns:
            Score between 0 and 1
        """
        scores = {
            'happy': 1.0,
            'necessary': 0.7,
            'neutral': 0.5,
            'regretful': 0.2,
        }
        return scores.get(sentiment, 0.5)


# Singleton instance
sentiment_service = SentimentService()

