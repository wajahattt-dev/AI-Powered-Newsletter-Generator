"""
Test the newsletter generation with custom interests
"""
import sys
from pathlib import Path
import yaml

# Add the project root to the Python path  
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.main import NewsletterApp
from src.fetcher import RSSFeedFetcher
from src.parser import ArticleParser
from src.user_profile import UserProfile
from src.generator import NewsletterGenerator

def test_newsletter_with_interests():
    """Test newsletter generation with custom interests."""
    
    print("🧪 Testing Newsletter Generation with Custom Interests")
    print("="*60)
    
    # Load config
    config_path = project_root / "config" / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Set custom interests
    test_interests = [
        'artificial intelligence',
        'machine learning', 
        'space exploration',
        'technology trends',
        'climate science'
    ]
    
    print(f"🎯 Testing with interests: {', '.join(test_interests)}")
    print("-" * 60)
    
    # Update config with test interests
    config["user"]["interests"] = test_interests
    
    try:
        # Initialize components
        print("📡 Fetching articles...")
        fetcher = RSSFeedFetcher(config)
        articles = fetcher.fetch_articles()
        print(f"   ✅ Fetched {len(articles)} articles")
        
        print("📄 Parsing articles...")
        parser = ArticleParser(config)
        parsed_articles = parser.parse_articles(articles[:5])  # Limit for testing
        print(f"   ✅ Parsed {len(parsed_articles)} articles")
        
        print("🎯 Filtering articles by interests...")
        user_profile = UserProfile(config)
        filtered_articles = user_profile.filter_articles(parsed_articles)
        print(f"   ✅ Found {len(filtered_articles)} relevant articles")
        
        # Add mock summaries
        print("📝 Adding mock summaries...")
        for article in filtered_articles:
            article['summary'] = f"Summary of '{article['title'][:50]}...' related to your interests in {', '.join(test_interests[:3])}."
            article['key_points'] = [
                "Key insight related to your interests",
                "Important development in this field", 
                "Future implications for the industry"
            ]
            article['quotes'] = [f"Quote from {article['title'][:30]}..."]
        
        print("📰 Generating newsletter...")
        generator = NewsletterGenerator(config)
        
        intro = f"""Welcome to your personalized newsletter! Based on your interests in {', '.join(test_interests)}, 
        we've found {len(filtered_articles)} relevant articles covering the latest developments in these areas."""
        
        output_files = generator.generate_newsletter(filtered_articles, intro)
        
        print(f"   ✅ Newsletter generated!")
        for format_type, file_path in output_files.items():
            print(f"   📄 {format_type.upper()}: {file_path}")
        
        # Show preview of generated content
        if output_files and "markdown" in output_files:
            print("\n📋 Newsletter Preview:")
            print("-" * 40)
            with open(output_files["markdown"], 'r', encoding='utf-8') as f:
                preview = f.read()[:500]
                print(preview)
                if len(preview) >= 500:
                    print("...")
                    
        print(f"\n🎉 Success! Newsletter generated with {len(filtered_articles)} articles matching your interests!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_newsletter_with_interests()
