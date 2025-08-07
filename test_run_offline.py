"""
Test script to run the newsletter generator without OpenAI API calls.
This is useful for testing the overall pipeline when the API quota is exceeded.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, str(project_root))

from src.main import NewsletterApp

class MockSummarizer:
    """Mock summarizer that doesn't use OpenAI API."""
    
    def __init__(self, config):
        self.config = config
    
    def summarize_articles(self, articles):
        """Create mock summaries for articles."""
        for article in articles:
            article['ai_summary'] = f"This is a mock summary of the article '{article['title']}'. " + \
                                   f"The article from {article['source']} discusses important topics related to " + \
                                   f"{article['category']}. This summary is generated offline for testing purposes."
            article['key_points'] = [
                "First key point from the article",
                "Second important detail",
                "Third significant finding"
            ]
            article['quotes'] = [
                "This is a mock quote from the article",
                "Another important statement"
            ]
        return articles
    
    def generate_introduction(self, articles):
        """Generate a mock introduction."""
        return f"Welcome to today's newsletter featuring {len(articles)} articles " + \
               "covering technology, science, and current events. This introduction " + \
               "is generated offline for testing purposes."

def main():
    """Run the newsletter generator with mock summarizer."""
    
    # Initialize the app
    app = NewsletterApp()
    
    # Replace the summarizer with our mock version
    app.summarizer = MockSummarizer(app.config)
    
    print("Running Auto-Newsletter Generator in offline test mode...")
    print("This will fetch real articles but use mock summaries (no OpenAI API calls).")
    
    # Run the pipeline
    output_files = app.run()
    
    if output_files:
        print("\n✅ Test completed successfully!")
        for format_type, file_path in output_files.items():
            print(f"📄 Generated {format_type} newsletter: {file_path}")
    else:
        print("\n❌ Test failed - no output files generated")

if __name__ == "__main__":
    main()
