"""
RSS Feed Article Fetcher Module

This module handles fetching articles from RSS feeds using the feedparser library.
It retrieves article metadata and prepares it for further processing.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import feedparser
from dateutil import parser as date_parser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RSSFeedFetcher:
    """Class for fetching articles from RSS feeds."""

    def __init__(self, config: Dict):
        """Initialize the RSS feed fetcher with configuration.

        Args:
            config: Dictionary containing fetching configuration settings
        """
        self.feeds = config['rss_feeds']
        self.max_articles_per_feed = config['fetching']['max_articles_per_feed']
        self.max_total_articles = config['fetching']['max_total_articles']
        self.article_age_limit_days = config['fetching']['article_age_limit_days']
        self.timeout = config['fetching']['timeout_seconds']
        self.user_agent = config['fetching']['user_agent']
        
        # Set user agent for feedparser
        feedparser.USER_AGENT = self.user_agent

    def fetch_articles(self) -> List[Dict]:
        """Fetch articles from all configured RSS feeds.

        Returns:
            List of article dictionaries with metadata
        """
        all_articles = []
        
        for feed in self.feeds:
            try:
                logger.info(f"Fetching articles from {feed['name']} ({feed['url']})")
                feed_articles = self._fetch_from_feed(feed)
                all_articles.extend(feed_articles)
                logger.info(f"Retrieved {len(feed_articles)} articles from {feed['name']}")
                
                # Add a small delay between feed requests to be polite
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error fetching from {feed['name']}: {str(e)}")
        
        # Sort articles by published date (newest first) and limit total number
        all_articles.sort(key=lambda x: x['published_date'], reverse=True)
        limited_articles = all_articles[:self.max_total_articles]
        
        logger.info(f"Total articles fetched: {len(limited_articles)}")
        return limited_articles

    def _fetch_from_feed(self, feed: Dict) -> List[Dict]:
        """Fetch articles from a single RSS feed.

        Args:
            feed: Dictionary containing feed information

        Returns:
            List of article dictionaries from the feed
        """
        articles = []
        cutoff_date = datetime.now() - timedelta(days=self.article_age_limit_days)
        
        # Parse the feed (feedparser doesn't support timeout parameter directly)
        parsed_feed = feedparser.parse(feed['url'])
        
        if hasattr(parsed_feed, 'status') and parsed_feed.status != 200:
            logger.warning(f"Feed returned status code {parsed_feed.status}: {feed['url']}")
            return articles
            
        # Process each entry in the feed
        for entry in parsed_feed.entries[:self.max_articles_per_feed]:
            try:
                # Parse the published date
                published_date = self._parse_date(entry)
                
                # Skip articles older than the cutoff date (make sure both dates are comparable)
                if published_date:
                    # Make cutoff_date timezone-aware if published_date is timezone-aware
                    if published_date.tzinfo is not None and cutoff_date.tzinfo is None:
                        from datetime import timezone
                        cutoff_date = cutoff_date.replace(tzinfo=timezone.utc)
                    # Make published_date timezone-naive if cutoff_date is timezone-naive
                    elif published_date.tzinfo is not None and cutoff_date.tzinfo is None:
                        published_date = published_date.replace(tzinfo=None)
                    
                    if published_date < cutoff_date:
                        continue
                
                # Extract article metadata
                article = {
                    'title': entry.get('title', 'No Title'),
                    'url': entry.get('link', ''),
                    'summary': entry.get('summary', ''),
                    'published_date': published_date,
                    'source': feed['name'],
                    'category': feed.get('category', 'general'),
                    'feed_id': feed.get('id', feed['url']),
                }
                
                # Add image URL if available
                article['image_url'] = self._extract_image_url(entry)
                
                articles.append(article)
            except Exception as e:
                logger.error(f"Error processing entry in {feed['name']}: {str(e)}")
        
        return articles

    def _parse_date(self, entry: Dict) -> Optional[datetime]:
        """Parse the published date from a feed entry.

        Args:
            entry: Feed entry dictionary

        Returns:
            Datetime object or None if parsing fails
        """
        date_fields = ['published', 'pubDate', 'updated', 'created', 'date']
        
        for field in date_fields:
            if field in entry:
                try:
                    return date_parser.parse(entry[field])
                except (ValueError, TypeError):
                    pass
        
        # If no date field is found or parsing fails, use current time
        logger.warning("Could not parse date, using current time")
        return datetime.now()

    def _extract_image_url(self, entry: Dict) -> Optional[str]:
        """Extract image URL from a feed entry if available.

        Args:
            entry: Feed entry dictionary

        Returns:
            Image URL string or None if not found
        """
        # Check for media content
        if 'media_content' in entry and entry.media_content:
            for media in entry.media_content:
                if 'url' in media and media.get('type', '').startswith('image/'):
                    return media['url']
        
        # Check for media thumbnail
        if 'media_thumbnail' in entry and entry.media_thumbnail:
            for thumbnail in entry.media_thumbnail:
                if 'url' in thumbnail:
                    return thumbnail['url']
        
        # Check for enclosures
        if 'enclosures' in entry and entry.enclosures:
            for enclosure in entry.enclosures:
                if 'type' in enclosure and enclosure.get('type', '').startswith('image/') and 'href' in enclosure:
                    return enclosure['href']
        
        # Check for image in links
        if 'links' in entry:
            for link in entry.links:
                if link.get('type', '').startswith('image/') and 'href' in link:
                    return link['href']
        
        return None