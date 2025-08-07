"""
User Profile Module

This module handles user profiles, interests, and article filtering based on relevance.
It supports both keyword-based and embedding-based matching for personalization.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UserProfile:
    """Class for managing user profiles and filtering content based on interests."""

    def __init__(self, config: Dict):
        """Initialize the user profile with configuration.

        Args:
            config: Dictionary containing user profile configuration
        """
        self.user_config = config['user']
        self.interests = self.user_config['interests']
        self.matching_method = self.user_config['matching_method']
        self.min_relevance_score = self.user_config['min_relevance_score']
        
        # Initialize embedding model if using embedding-based matching
        self.embedding_model = None
        if self.matching_method == 'embedding':
            try:
                self._initialize_embedding_model()
            except ImportError:
                logger.warning("Sentence transformers not available, falling back to keyword matching")
                self.matching_method = 'keyword'

    def _initialize_embedding_model(self):
        """Initialize the sentence embedding model for semantic matching."""
        try:
            from sentence_transformers import SentenceTransformer
            # Use a smaller model for efficiency
            self.embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
            logger.info("Initialized sentence embedding model for interest matching")
        except ImportError:
            logger.error("Could not import sentence_transformers. Install with: pip install sentence-transformers")
            raise

    def filter_articles(self, articles: List[Dict]) -> List[Dict]:
        """Filter articles based on user interests.

        Args:
            articles: List of article dictionaries

        Returns:
            Filtered list of articles with relevance scores
        """
        if not articles:
            return []
            
        if not self.interests:
            logger.info("No user interests defined, returning all articles")
            return articles
        
        scored_articles = []
        
        for article in articles:
            relevance_score, matched_interests = self._calculate_relevance(article)
            
            # Add relevance information to the article
            article['relevance_score'] = relevance_score
            article['matched_interests'] = matched_interests
            
            # Include articles that meet the minimum relevance threshold
            if relevance_score >= self.min_relevance_score:
                scored_articles.append(article)
        
        # Sort by relevance score (highest first)
        scored_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        logger.info(f"Filtered {len(scored_articles)} relevant articles out of {len(articles)} total")
        return scored_articles

    def _calculate_relevance(self, article: Dict) -> Tuple[float, List[str]]:
        """Calculate relevance score for an article based on user interests.

        Args:
            article: Article dictionary

        Returns:
            Tuple of (relevance_score, list_of_matched_interests)
        """
        if self.matching_method == 'embedding':
            return self._calculate_embedding_relevance(article)
        else:
            return self._calculate_keyword_relevance(article)

    def _calculate_keyword_relevance(self, article: Dict) -> Tuple[float, List[str]]:
        """Calculate relevance using keyword matching.

        Args:
            article: Article dictionary

        Returns:
            Tuple of (relevance_score, list_of_matched_interests)
        """
        # Combine relevant text fields for matching
        text_to_match = ' '.join([
            article.get('title', ''),
            article.get('summary', ''),
            article.get('category', ''),
            ' '.join(article.get('keywords', [])),
            ' '.join(article.get('nlp_keywords', []))
        ]).lower()
        
        # Count matches for each interest
        matched_interests = []
        total_matches = 0
        
        for interest in self.interests:
            interest_lower = interest.lower()
            # Count occurrences of the interest in the text
            count = text_to_match.count(interest_lower)
            
            if count > 0:
                matched_interests.append(interest)
                total_matches += count
        
        # Calculate relevance score (0 to 1)
        # More matches and more matched interests increase the score
        if matched_interests:
            # Base score from percentage of interests matched
            interest_coverage = len(matched_interests) / len(self.interests)
            # Bonus from multiple mentions (capped to avoid extreme values)
            mention_bonus = min(total_matches / 10, 0.5)  
            relevance_score = min(interest_coverage + mention_bonus, 1.0)
        else:
            relevance_score = 0.0
        
        return relevance_score, matched_interests

    def _calculate_embedding_relevance(self, article: Dict) -> Tuple[float, List[str]]:
        """Calculate relevance using embedding-based semantic matching.

        Args:
            article: Article dictionary

        Returns:
            Tuple of (relevance_score, list_of_matched_interests)
        """
        if not self.embedding_model:
            logger.warning("Embedding model not initialized, falling back to keyword matching")
            return self._calculate_keyword_relevance(article)
        
        # Combine relevant text fields for matching
        article_text = ' '.join([
            article.get('title', ''),
            article.get('summary', '')[:500]  # Limit length for efficiency
        ])
        
        if not article_text.strip():
            return 0.0, []
        
        try:
            # Get embeddings
            article_embedding = self.embedding_model.encode(article_text)
            interest_embeddings = self.embedding_model.encode(self.interests)
            
            # Calculate cosine similarity between article and each interest
            from numpy import dot
            from numpy.linalg import norm
            
            similarities = []
            matched_interests = []
            
            for i, interest_embedding in enumerate(interest_embeddings):
                similarity = dot(article_embedding, interest_embedding) / (norm(article_embedding) * norm(interest_embedding))
                similarities.append(similarity)
                
                # Consider an interest matched if similarity is above threshold
                if similarity > 0.5:  # Threshold for considering a match
                    matched_interests.append(self.interests[i])
            
            # Overall relevance is the maximum similarity
            relevance_score = max(similarities) if similarities else 0.0
            
            return relevance_score, matched_interests
            
        except Exception as e:
            logger.error(f"Error in embedding calculation: {str(e)}")
            return self._calculate_keyword_relevance(article)

    def save_user_profile(self):
        """Save the user profile to a file."""
        try:
            # Get the project root directory
            project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            profile_dir = project_root / "data" / "user_profiles"
            profile_dir.mkdir(parents=True, exist_ok=True)
            
            import json
            profile_path = profile_dir / f"{self.user_config['name'].lower().replace(' ', '_')}.json"
            
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_config, f, indent=2)
                
            logger.info(f"Saved user profile to {profile_path}")
            
        except Exception as e:
            logger.error(f"Error saving user profile: {str(e)}")

    @classmethod
    def load_user_profile(cls, config: Dict, profile_name: str) -> 'UserProfile':
        """Load a user profile from a file.

        Args:
            config: Base configuration dictionary
            profile_name: Name of the profile to load

        Returns:
            UserProfile instance with loaded profile
        """
        try:
            # Get the project root directory
            project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            profile_path = project_root / "data" / "user_profiles" / f"{profile_name.lower().replace(' ', '_')}.json"
            
            if not profile_path.exists():
                logger.warning(f"Profile {profile_name} not found, using default profile")
                return cls(config)
            
            import json
            with open(profile_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # Update the config with the loaded user profile
            config_copy = config.copy()
            config_copy['user'] = user_config
            
            logger.info(f"Loaded user profile: {profile_name}")
            return cls(config_copy)
            
        except Exception as e:
            logger.error(f"Error loading user profile: {str(e)}")
            return cls(config)