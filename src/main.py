"""
Auto-Newsletter Generator Main Module

This is the main entry point for the Auto-Newsletter Generator application.
It orchestrates the entire pipeline from fetching articles to generating newsletters.
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import yaml
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"newsletter_generator_{datetime.now().strftime('%Y%m%d')}.log")
    ]
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, str(project_root))

# Import application modules
from src.fetcher import RSSFeedFetcher
from src.parser import ArticleParser
from src.summarizer import ArticleSummarizer
from src.user_profile import UserProfile
from src.generator import NewsletterGenerator

class NewsletterApp:
    """Main application class for the Auto-Newsletter Generator."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the newsletter application.

        Args:
            config_path: Path to the configuration file (optional)
        """
        # Load environment variables
        load_dotenv()
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY environment variable not set. Please set it before running.")
        
        # Initialize components
        self.fetcher = RSSFeedFetcher(self.config)
        self.parser = ArticleParser(self.config)
        self.summarizer = ArticleSummarizer(self.config)
        self.user_profile = UserProfile(self.config)
        self.generator = NewsletterGenerator(self.config)

    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load the application configuration from a YAML file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Configuration dictionary
        """
        if not config_path:
            config_path = project_root / "config" / "config.yaml"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            logger.info("Using default configuration")
            return self._default_config()

    def _default_config(self) -> Dict:
        """Create a default configuration if the config file is not available.

        Returns:
            Default configuration dictionary
        """
        return {
            "api": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.3,
                "max_tokens": 1000
            },
            "rss_feeds": [
                {
                    "name": "BBC News - Technology",
                    "url": "http://feeds.bbci.co.uk/news/technology/rss.xml",
                    "category": "technology"
                }
            ],
            "user": {
                "name": "Default User",
                "interests": ["technology", "python", "ai"],
                "matching_method": "keyword",
                "min_relevance_score": 0.3
            },
            "fetching": {
                "max_articles_per_feed": 5,
                "max_total_articles": 10,
                "article_age_limit_days": 2,
                "timeout_seconds": 10,
                "user_agent": "Auto-Newsletter-Generator/1.0"
            },
            "summarization": {
                "length": "medium",
                "include_quotes": True,
                "extract_key_points": True,
                "num_key_points": 3
            },
            "newsletter": {
                "title": "Daily Tech Digest",
                "subtitle": "Your Personalized News Summary",
                "output_format": "markdown",
                "include_images": True,
                "include_links": True,
                "group_by_category": True,
                "output_dir": "data/output",
                "date_format": "%Y-%m-%d"
            }
        }

    def run(self) -> Dict[str, str]:
        """Run the complete newsletter generation pipeline.

        Returns:
            Dictionary with paths to generated newsletter files
        """
        logger.info("Starting Auto-Newsletter Generator pipeline")
        
        # Step 1: Fetch articles from RSS feeds
        logger.info("Step 1: Fetching articles from RSS feeds")
        articles = self.fetcher.fetch_articles()
        if not articles:
            logger.warning("No articles fetched. Check your RSS feed URLs and internet connection.")
            return {}
        
        # Step 2: Parse and extract full content
        logger.info("Step 2: Parsing articles and extracting content")
        parsed_articles = self.parser.parse_articles(articles)
        if not parsed_articles:
            logger.warning("No articles could be parsed. Check article URLs and parsing settings.")
            return {}
        
        # Step 3: Filter articles based on user interests
        logger.info("Step 3: Filtering articles based on user interests")
        filtered_articles = self.user_profile.filter_articles(parsed_articles)
        if not filtered_articles:
            logger.warning("No articles matched user interests. Consider adjusting interest settings.")
            # Fall back to using all parsed articles if none match interests
            filtered_articles = parsed_articles
        
        # Step 4: Summarize articles
        logger.info("Step 4: Summarizing articles")
        summarized_articles = self.summarizer.summarize_articles(filtered_articles)
        
        # Step 5: Generate introduction
        logger.info("Step 5: Generating newsletter introduction")
        introduction = self.summarizer.generate_introduction(summarized_articles)
        
        # Step 6: Generate newsletter
        logger.info("Step 6: Generating newsletter")
        output_files = self.generator.generate_newsletter(summarized_articles, introduction)
        
        if output_files:
            logger.info("Newsletter generation completed successfully!")
            for format_type, file_path in output_files.items():
                logger.info(f"Generated {format_type} newsletter: {file_path}")
        else:
            logger.error("Newsletter generation failed.")
        
        return output_files

def parse_arguments():
    """Parse command line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(description="Auto-Newsletter Generator")
    parser.add_argument(
        "-c", "--config", 
        help="Path to configuration file", 
        default=None
    )
    parser.add_argument(
        "-p", "--profile", 
        help="User profile name to use", 
        default=None
    )
    parser.add_argument(
        "--schedule", 
        help="Schedule newsletter generation (requires APScheduler)", 
        action="store_true"
    )
    parser.add_argument(
        "--time", 
        help="Time to schedule newsletter generation (HH:MM format)", 
        default="08:00"
    )
    return parser.parse_args()

def setup_scheduler(app: NewsletterApp, schedule_time: str):
    """Set up a scheduler for regular newsletter generation.

    Args:
        app: NewsletterApp instance
        schedule_time: Time to schedule in HH:MM format
    """
    try:
        from apscheduler.schedulers.blocking import BlockingScheduler
        from apscheduler.triggers.cron import CronTrigger
        
        scheduler = BlockingScheduler()
        hour, minute = schedule_time.split(":")
        
        scheduler.add_job(
            app.run,
            trigger=CronTrigger(hour=int(hour), minute=int(minute)),
            id="newsletter_generation",
            name="Daily Newsletter Generation"
        )
        
        logger.info(f"Scheduled newsletter generation for {schedule_time} daily")
        scheduler.start()
        
    except ImportError:
        logger.error("APScheduler not installed. Install with: pip install apscheduler")
        sys.exit(1)

def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Initialize the application
    app = NewsletterApp(args.config)
    
    # Load user profile if specified
    if args.profile:
        app.user_profile = UserProfile.load_user_profile(app.config, args.profile)
    
    # Run scheduler if requested
    if args.schedule:
        setup_scheduler(app, args.time)
    else:
        # Run the pipeline once
        app.run()

if __name__ == "__main__":
    main()