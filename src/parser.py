"""
Article Content Parser Module

This module handles extracting full article content from web pages using the newspaper3k library.
It processes article URLs and extracts text, images, and metadata.
"""

import logging
import time
from typing import Dict, List, Optional

import newspaper
from newspaper import Article
from newspaper.article import ArticleException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ArticleParser:
    """Class for parsing and extracting content from articles."""

    def __init__(self, config: Dict):
        """Initialize the article parser with configuration.

        Args:
            config: Dictionary containing fetching configuration settings
        """
        self.timeout = config['fetching']['timeout_seconds']
        self.user_agent = config['fetching']['user_agent']

    def parse_articles(self, articles: List[Dict]) -> List[Dict]:
        """Parse a list of articles to extract full content.

        Args:
            articles: List of article dictionaries with URLs

        Returns:
            List of article dictionaries with extracted content
        """
        parsed_articles = []
        
        for article in articles:
            try:
                logger.info(f"Parsing article: {article['title']} ({article['url']})")
                parsed_article = self._parse_article(article)
                if parsed_article:
                    parsed_articles.append(parsed_article)
                
                # Add a small delay between requests to be polite
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error parsing article {article['url']}: {str(e)}")
        
        logger.info(f"Successfully parsed {len(parsed_articles)} articles")
        return parsed_articles

    def _parse_article(self, article_data: Dict) -> Optional[Dict]:
        """Parse a single article to extract its content.

        Args:
            article_data: Dictionary containing article metadata

        Returns:
            Updated article dictionary with extracted content or None if parsing fails
        """
        url = article_data['url']
        if not url:
            logger.warning("Article URL is empty, skipping")
            return None
        
        try:
            # Configure and download the article
            article = Article(url)
            article.config.browser_user_agent = self.user_agent
            article.config.request_timeout = self.timeout
            
            article.download()
            article.parse()
            
            # Update article data with extracted content
            article_data['content'] = article.text
            
            # If no content was extracted, use the summary from the feed
            if not article_data['content'] and 'summary' in article_data:
                article_data['content'] = article_data['summary']
                logger.warning(f"No content extracted, using feed summary for {url}")
            
            # If still no content, skip this article
            if not article_data['content']:
                logger.warning(f"No content available for {url}, skipping")
                return None
            
            # Update image URL if not already set and available in parsed article
            if not article_data.get('image_url') and article.top_image:
                article_data['image_url'] = article.top_image
            
            # Extract additional metadata if available
            if article.publish_date:
                article_data['published_date'] = article.publish_date
            
            if article.authors:
                article_data['authors'] = article.authors
            
            if article.keywords:
                article_data['keywords'] = article.keywords
            
            # Try to extract article language
            try:
                article.nlp()
                if article.summary:
                    article_data['extracted_summary'] = article.summary
                if article.keywords:
                    article_data['nlp_keywords'] = article.keywords
            except Exception as e:
                logger.debug(f"NLP processing failed for {url}: {str(e)}")
            
            return article_data
            
        except ArticleException as e:
            logger.error(f"Newspaper3k error for {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing {url}: {str(e)}")
            return None

    def extract_quotes(self, content: str) -> List[str]:
        """Extract quotes from article content.

        This is a simple implementation that looks for text between quotation marks.
        A more sophisticated approach could use NLP techniques.

        Args:
            content: Article content text

        Returns:
            List of extracted quotes
        """
        quotes = []
        in_quote = False
        current_quote = ""
        
        for i, char in enumerate(content):
            if char == '"':
                if in_quote:
                    # End of quote
                    if current_quote and len(current_quote) > 10:  # Minimum quote length
                        quotes.append(current_quote.strip())
                    current_quote = ""
                in_quote = not in_quote
            elif in_quote:
                current_quote += char
        
        # Filter quotes to remove duplicates and very short quotes
        unique_quotes = list(set(quotes))
        filtered_quotes = [q for q in unique_quotes if len(q) > 20 and len(q) < 300]
        
        return filtered_quotes[:3]  # Limit to top 3 quotes