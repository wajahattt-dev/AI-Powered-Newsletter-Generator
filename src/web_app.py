"""
Enhanced Streamlit Web Interface for Auto-Newsletter Generator

This module provides an interactive web interface using Streamlit for the Auto-Newsletter Generator.
It allows users to enter interests, analyze them, configure settings, and generate personalized newsletters.
"""

import os
import sys
import re
import json
import uuid
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add the project root to the Python path
project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, str(project_root))

try:
    import streamlit as st
    import yaml
    from dotenv import load_dotenv
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    print("Streamlit not installed. Install with: pip install streamlit")
    sys.exit(1)

from src.main import NewsletterApp
from src.user_profile import UserProfile

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI-Powered Newsletter Generator",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def analyze_interests(interests_text: str) -> Tuple[List[str], Dict[str, any]]:
    """Analyze user-entered interests and extract meaningful keywords.
    
    Args:
        interests_text: Raw text containing user interests
        
    Returns:
        Tuple of (processed_interests, analysis_results)
    """
    if not interests_text.strip():
        return [], {}
    
    # Clean and process the text
    interests_text = interests_text.lower().strip()
    
    # Split by common separators and clean
    separators = [',', ';', '\n', '|', '&', 'and', '+', 'or']
    for sep in separators:
        interests_text = interests_text.replace(sep, '|')
    
    # Extract individual interests and clean them
    raw_interests = [interest.strip() for interest in interests_text.split('|') if interest.strip()]
    
    # Enhanced interest processing
    processed_interests = []
    keyword_mapping = {
        # Technology
        'ai': 'artificial intelligence',
        'ml': 'machine learning', 
        'tech': 'technology',
        'programming': 'software development',
        'coding': 'software development',
        'software': 'software development',
        'blockchain': 'blockchain technology',
        'crypto': 'cryptocurrency',
        'bitcoin': 'cryptocurrency',
        'web dev': 'web development',
        'mobile apps': 'mobile development',
        'cloud': 'cloud computing',
        'cybersecurity': 'cybersecurity',
        'data science': 'data science',
        'big data': 'data analytics',
        
        # Science
        'space': 'space exploration',
        'nasa': 'space exploration',
        'climate': 'climate change',
        'environment': 'environmental science',
        'medicine': 'medical research',
        'health': 'healthcare',
        'biotech': 'biotechnology',
        'physics': 'physics research',
        'chemistry': 'chemistry research',
        
        # Business
        'startup': 'startups',
        'business': 'business news',
        'finance': 'financial news',
        'economy': 'economic news',
        'market': 'stock market',
        'investment': 'investment news',
        
        # Other
        'sports': 'sports news',
        'entertainment': 'entertainment news',
        'politics': 'political news',
        'world news': 'international news'
    }
    
    # Process and expand interests
    for interest in raw_interests:
        cleaned = re.sub(r'[^\w\s]', '', interest).strip()
        if len(cleaned) > 1:
            # Check if we can expand this interest
            expanded = keyword_mapping.get(cleaned, cleaned)
            processed_interests.append(expanded)
            
            # Add related terms for common interests
            if 'ai' in cleaned or 'artificial intelligence' in cleaned:
                if 'machine learning' not in processed_interests:
                    processed_interests.append('machine learning')
            elif 'machine learning' in cleaned or 'ml' in cleaned:
                if 'artificial intelligence' not in processed_interests:
                    processed_interests.append('artificial intelligence')
    
    # Remove duplicates while preserving order
    processed_interests = list(dict.fromkeys(processed_interests))
    
    # Enhanced categorization
    categories = {
        'technology': ['artificial intelligence', 'machine learning', 'technology', 'software development', 
                      'blockchain technology', 'cryptocurrency', 'web development', 'mobile development',
                      'cloud computing', 'cybersecurity', 'data science', 'data analytics', 'programming',
                      'python', 'javascript', 'java', 'react', 'nodejs'],
        'science': ['space exploration', 'climate change', 'environmental science', 'medical research', 
                   'healthcare', 'biotechnology', 'physics research', 'chemistry research', 'biology',
                   'astronomy', 'genetics', 'neuroscience'],
        'business': ['startups', 'business news', 'financial news', 'economic news', 'stock market',
                    'investment news', 'entrepreneurship', 'venture capital', 'fintech'],
        'sports': ['sports news', 'football', 'basketball', 'soccer', 'tennis', 'olympics'],
        'entertainment': ['entertainment news', 'movies', 'music', 'gaming', 'streaming'],
        'politics': ['political news', 'government', 'policy', 'elections'],
        'world': ['international news', 'global affairs', 'current events']
    }
    
    detected_categories = set()
    for interest in processed_interests:
        for category, keywords in categories.items():
            if any(keyword in interest.lower() for keyword in keywords) or interest.lower() in keywords:
                detected_categories.add(category)
    
    # Generate intelligent recommendations based on actual interests
    recommendations = generate_smart_recommendations(processed_interests, detected_categories)
    suggested_feeds = suggest_rss_feeds(detected_categories)
    
    analysis = {
        'total_interests': len(processed_interests),
        'detected_categories': list(detected_categories),
        'recommendations': recommendations,
        'suggested_feeds': suggested_feeds,
        'original_input': interests_text,
        'processed_interests': processed_interests
    }
    
    return processed_interests, analysis

def generate_smart_recommendations(interests: List[str], categories: set) -> List[str]:
    """Generate intelligent recommendations based on actual user interests."""
    recommendations = []
    
    # Technology-specific recommendations
    if 'technology' in categories:
        tech_interests = [i for i in interests if any(term in i.lower() for term in 
                         ['ai', 'machine learning', 'technology', 'software', 'programming', 'data'])]
        
        if any('ai' in i.lower() or 'artificial intelligence' in i.lower() for i in tech_interests):
            recommendations.append("Consider adding 'deep learning', 'neural networks', or 'computer vision' for more AI coverage")
        
        if any('programming' in i.lower() or 'software' in i.lower() for i in tech_interests):
            recommendations.append("Add specific technologies like 'react', 'python frameworks', or 'cloud platforms'")
        
        if any('data' in i.lower() for i in tech_interests):
            recommendations.append("Include 'big data analytics', 'data visualization', or 'business intelligence'")
    
    # Science-specific recommendations  
    if 'science' in categories:
        if any('space' in i.lower() for i in interests):
            recommendations.append("Add 'mars exploration', 'satellite technology', or 'astrophysics' for space news")
        
        if any('climate' in i.lower() or 'environment' in i.lower() for i in interests):
            recommendations.append("Include 'renewable energy', 'carbon capture', or 'sustainable technology'")
    
    # Business-specific recommendations
    if 'business' in categories:
        recommendations.append("Consider adding industry-specific terms like 'fintech', 'e-commerce', or 'supply chain'")
    
    # General recommendations based on breadth
    if len(categories) == 1:
        recommendations.append("Try adding interests from other categories for a more diverse newsletter")
    elif len(interests) < 3:
        recommendations.append("Add more specific interests to get more targeted news coverage")
    
    # If no specific recommendations, provide general ones
    if not recommendations:
        recommendations.extend([
            "Your interests look great! The system will find relevant articles across these topics",
            "Consider adding emerging trends in your areas of interest",
            "You can always refine your interests after seeing the first newsletter"
        ])
    
    return recommendations[:3]  # Limit to 3 recommendations

def suggest_rss_feeds(categories: set) -> List[Dict[str, str]]:
    """Suggest RSS feeds based on detected categories."""
    feed_suggestions = {
        'technology': [
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "category": "technology"},
            {"name": "Ars Technica", "url": "http://feeds.arstechnica.com/arstechnica/index", "category": "technology"},
            {"name": "Hacker News", "url": "https://hnrss.org/frontpage", "category": "technology"}
        ],
        'science': [
            {"name": "Science Daily", "url": "https://www.sciencedaily.com/rss/all.xml", "category": "science"},
            {"name": "Nature News", "url": "https://www.nature.com/nature.rss", "category": "science"},
            {"name": "Scientific American", "url": "http://rss.sciam.com/ScientificAmerican-News", "category": "science"}
        ],
        'business': [
            {"name": "Reuters Business", "url": "https://feeds.reuters.com/reuters/businessNews", "category": "business"},
            {"name": "Bloomberg", "url": "https://feeds.bloomberg.com/markets/news.rss", "category": "business"}
        ],
        'world': [
            {"name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml", "category": "world"},
            {"name": "Reuters World", "url": "https://feeds.reuters.com/Reuters/worldNews", "category": "world"}
        ]
    }
    
    suggested_feeds = []
    for category in categories:
        if category in feed_suggestions:
            suggested_feeds.extend(feed_suggestions[category])
    
    return suggested_feeds[:5]  # Limit to 5 suggestions

def create_user_profile(name: str, interests: List[str], preferences: Dict) -> str:
    """Create a new user profile and save it to file.
    
    Args:
        name: Profile name
        interests: List of user interests
        preferences: Additional preferences
        
    Returns:
        Path to the created profile file
    """
    # Create user profiles directory if it doesn't exist
    profiles_dir = project_root / "data" / "user_profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename from name
    filename = re.sub(r'[^\w\s]', '', name.lower()).replace(' ', '_')
    if not filename:
        filename = f"user_{uuid.uuid4().hex[:8]}"
    
    profile_data = {
        "name": name,
        "interests": interests,
        "matching_method": preferences.get("matching_method", "keyword"),
        "min_relevance_score": preferences.get("min_relevance_score", 0.3),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    profile_path = profiles_dir / f"{filename}.json"
    with open(profile_path, 'w', encoding='utf-8') as f:
        json.dump(profile_data, f, indent=2, ensure_ascii=False)
    
    return str(profile_path)

def load_config() -> Dict:
    """Load the application configuration.

    Returns:
        Configuration dictionary
    """
    config_path = project_root / "config" / "config.yaml"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        st.error(f"Error loading configuration: {str(e)}")
        return {}

def load_user_profiles() -> List[str]:
    """Load available user profiles.

    Returns:
        List of profile names
    """
    profiles_dir = project_root / "data" / "user_profiles"
    if not profiles_dir.exists():
        return ["Default"]
    
    profiles = ["Default"]
    for file in profiles_dir.glob("*.json"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
                profile_name = profile_data.get("name", file.stem.replace('_', ' ').title())
                if profile_name.lower() != "default":
                    profiles.append(profile_name)
        except Exception:
            # Skip invalid profile files
            continue
    
    return profiles

def display_newsletter(file_path: str):
    """Display a newsletter file in the Streamlit interface.

    Args:
        file_path: Path to the newsletter file
    """
    if not os.path.exists(file_path):
        st.error(f"File not found: {file_path}")
        return
    
    if file_path.endswith(".md"):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        st.markdown(content)
    elif file_path.endswith(".pdf"):
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
        
        # PDF Preview and Download Section
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.download_button(
                label="📄 Download PDF",
                data=pdf_bytes,
                file_name=os.path.basename(file_path),
                mime="application/pdf",
                use_container_width=True
            )
        
        with col2:
            # Create a base64 encoded version for preview
            import base64
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # PDF Preview button that opens in new tab
            pdf_display = f"""
            <a href="data:application/pdf;base64,{base64_pdf}" target="_blank">
                <button style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 0.75rem 1.5rem;
                    font-size: 1rem;
                    font-weight: 600;
                    cursor: pointer;
                    width: 100%;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                ">
                    👁️ Preview PDF
                </button>
            </a>
            """
            st.markdown(pdf_display, unsafe_allow_html=True)
        
        # Show PDF info
        file_size = len(pdf_bytes) / 1024  # KB
        st.info(f"📄 PDF Document • {file_size:.1f} KB • Click 'Preview PDF' to view in new tab")

def run_newsletter_generation_offline(config: Dict, interests: List[str], profile_name: str = None) -> Dict[str, str]:
    """Run the newsletter generation process in offline mode (no AI API).
    
    Args:
        config: Configuration dictionary
        interests: List of user interests
        profile_name: Optional profile name
        
    Returns:
        Dictionary with paths to generated files
    """
    # Update config with user interests
    config["user"]["interests"] = interests
    
    # Create a simple offline version
    try:
        # Initialize app with the updated config
        app = NewsletterApp(config_path=None)
        app.config = config  # Override the loaded config with our updated one
        
        # Reinitialize components with new config
        from src.fetcher import RSSFeedFetcher
        from src.parser import ArticleParser  
        from src.user_profile import UserProfile
        from src.generator import NewsletterGenerator
        
        app.fetcher = RSSFeedFetcher(config)
        app.parser = ArticleParser(config)
        app.user_profile = UserProfile(config)
        app.generator = NewsletterGenerator(config)
        
        # Update the user profile with the new interests
        app.user_profile.interests = interests
        app.user_profile.user_config["interests"] = interests
        
        # Run just the fetching and parsing parts
        with st.spinner("📡 Fetching articles from RSS feeds..."):
            articles = app.fetcher.fetch_articles()
            if not articles:
                st.warning("⚠️ No articles fetched. This might be due to RSS feed issues or network problems.")
                return {}
            st.success(f"✅ Fetched {len(articles)} articles")
        
        with st.spinner("📄 Parsing article content..."):
            parsed_articles = app.parser.parse_articles(articles)
            if not parsed_articles:
                st.warning("⚠️ No articles could be parsed. The websites might be blocking access.")
                return {}
            st.success(f"✅ Successfully parsed {len(parsed_articles)} articles")
        
        with st.spinner(f"🎯 Filtering articles based on your interests: {', '.join(interests[:3])}{'...' if len(interests) > 3 else ''}"):
            filtered_articles = app.user_profile.filter_articles(parsed_articles)
            if not filtered_articles:
                st.warning(f"⚠️ No articles matched your interests. Try broadening your interests or check if the topics are covered in current news.")
                # Use all articles if none match interests
                filtered_articles = parsed_articles[:10]  # Limit to 10 for demo
                st.info(f"📰 Using {len(filtered_articles)} recent articles for your newsletter")
            else:
                st.success(f"✅ Found {len(filtered_articles)} articles matching your interests!")
        
        # Add enhanced mock summaries for offline mode
        with st.spinner("📝 Generating article summaries (offline mode)..."):
            for i, article in enumerate(filtered_articles):
                # Create more realistic summaries based on the actual article content
                content_preview = article.get('content', article.get('summary', ''))[:300]
                
                article['summary'] = f"This article discusses {article['title'].lower()}. {content_preview}... [This is a mock summary generated in offline mode. Enable AI mode with Gemini API for real summaries.]"
                
                # Generate relevant key points based on article title and content
                title_words = article['title'].lower().split()
                key_points = []
                
                if any(word in title_words for word in ['ai', 'artificial', 'intelligence', 'machine', 'learning']):
                    key_points = ["AI technology advancement discussed", "Impact on industry analyzed", "Future implications explored"]
                elif any(word in title_words for word in ['space', 'nasa', 'rocket', 'mars', 'moon']):
                    key_points = ["Space exploration milestone reached", "Technology breakthrough achieved", "Future mission plans revealed"]
                elif any(word in title_words for word in ['climate', 'environment', 'carbon', 'energy']):
                    key_points = ["Environmental impact assessed", "New sustainability measures proposed", "Climate change implications discussed"]
                else:
                    key_points = [
                        f"Key development in {article.get('category', 'news')}",
                        "Important implications for the industry", 
                        "Expert opinions and analysis provided"
                    ]
                
                article['key_points'] = key_points
                article['quotes'] = [f"Key insight from the {article['title'][:50]}... article"]
                
                # Show progress
                if (i + 1) % 3 == 0:
                    st.write(f"📝 Processed {i + 1}/{len(filtered_articles)} articles...")
        
        with st.spinner("📊 Generating newsletter introduction..."):
            # Create a personalized introduction based on user interests
            intro_topics = ", ".join(interests[:5])
            if len(interests) > 5:
                intro_topics += f" and {len(interests) - 5} other topics"
            
            introduction = f"""Welcome to your personalized newsletter! Based on your interests in {intro_topics}, 
            we've curated {len(filtered_articles)} articles that should capture your attention. 
            
            Today's newsletter covers the latest developments across your areas of interest, 
            bringing you up-to-date with the most relevant news and insights.
            
            *Note: This newsletter was generated in offline mode. For AI-powered summaries and analysis, 
            enable the full AI mode with a Gemini API key.*"""
        
        with st.spinner("📰 Generating your personalized newsletter..."):
            output_files = app.generator.generate_newsletter(filtered_articles, introduction)
        
        return output_files
    
    except Exception as e:
        st.error(f"❌ Error generating newsletter: {str(e)}")
        import traceback
        st.text(f"Debug info: {traceback.format_exc()}")
        return {}

def run_newsletter_generation_gemini(config: Dict, interests: List[str], profile_name: str = None) -> Dict[str, str]:
    """Run the newsletter generation process with Gemini AI capabilities.

    Args:
        config: Configuration dictionary
        interests: List of user interests
        profile_name: Optional profile name

    Returns:
        Dictionary with paths to generated files
    """
    # Update config with user interests
    config["user"]["interests"] = interests
    
    # Initialize the application with the updated config
    try:
        app = NewsletterApp(config_path=None)
        app.config = config  # Override with our updated config
        
        # Reinitialize components with new config
        from src.fetcher import RSSFeedFetcher
        from src.parser import ArticleParser  
        from src.user_profile import UserProfile
        from src.generator import NewsletterGenerator
        from src.gemini_summarizer import GeminiArticleSummarizer
        
        app.fetcher = RSSFeedFetcher(config)
        app.parser = ArticleParser(config)
        app.user_profile = UserProfile(config)
        app.generator = NewsletterGenerator(config)
        app.summarizer = GeminiArticleSummarizer(config)
        
        # Update the user profile with the new interests
        app.user_profile.interests = interests
        app.user_profile.user_config["interests"] = interests
        
        # Load user profile if specified
        if profile_name and profile_name.lower() != "default":
            try:
                app.user_profile = UserProfile.load_user_profile(config, profile_name)
                # Still override interests with current ones
                app.user_profile.interests = interests
            except Exception:
                st.warning(f"Could not load profile '{profile_name}', using default settings")
        
        # Run the pipeline with progress tracking
        with st.spinner("📡 Fetching articles from RSS feeds..."):
            articles = app.fetcher.fetch_articles()
            if not articles:
                st.warning("⚠️ No articles fetched. Check RSS feed URLs and internet connection.")
                return {}
            st.success(f"✅ Fetched {len(articles)} articles")
        
        with st.spinner("📄 Parsing article content..."):
            parsed_articles = app.parser.parse_articles(articles)
            if not parsed_articles:
                st.warning("⚠️ No articles could be parsed. Check article URLs and parsing settings.")
                return {}
            st.success(f"✅ Successfully parsed {len(parsed_articles)} articles")
        
        with st.spinner(f"🎯 Filtering articles based on your interests: {', '.join(interests[:3])}{'...' if len(interests) > 3 else ''}"):
            filtered_articles = app.user_profile.filter_articles(parsed_articles)
            if not filtered_articles:
                st.warning(f"⚠️ No articles matched your interests. Consider adjusting interest settings.")
                # Fall back to using all parsed articles if none match interests
                filtered_articles = parsed_articles
            st.success(f"✅ Found {len(filtered_articles)} articles matching your interests!")
        
        with st.spinner("🤖 Generating AI summaries using Gemini..."):
            summarized_articles = app.summarizer.summarize_articles(filtered_articles)
            st.success(f"✅ Generated AI summaries for {len(summarized_articles)} articles")
        
        with st.spinner("📝 Generating newsletter introduction..."):
            introduction = app.summarizer.generate_introduction(summarized_articles)
        
        with st.spinner("📰 Creating your personalized newsletter..."):
            output_files = app.generator.generate_newsletter(summarized_articles, introduction)
        
        return output_files
                
    except Exception as e:
        st.error(f"❌ Error during Gemini AI generation: {str(e)}")
        # Fallback to offline mode
        st.info("🔄 Falling back to offline mode...")
        return run_newsletter_generation_offline(config, interests, profile_name)
    """Load the application configuration.

    Returns:
        Configuration dictionary
    """
    config_path = project_root / "config" / "config.yaml"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        st.error(f"Error loading configuration: {str(e)}")
        return {}

def load_user_profiles() -> List[str]:
    """Load available user profiles.

    Returns:
        List of profile names
    """
    profiles_dir = project_root / "data" / "user_profiles"
    if not profiles_dir.exists():
        return []
    
    profiles = ["Default"]
    for file in profiles_dir.glob("*.json"):
        profile_name = file.stem.replace('_', ' ').title()
        if profile_name.lower() != "default":
            profiles.append(profile_name)
    
    return profiles

def display_newsletter(file_path: str):
    """Display a newsletter file in the Streamlit interface.

    Args:
        file_path: Path to the newsletter file
    """
    if not os.path.exists(file_path):
        st.error(f"File not found: {file_path}")
        return
    
    if file_path.endswith(".md"):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        st.markdown(content)
    elif file_path.endswith(".pdf"):
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=os.path.basename(file_path),
            mime="application/pdf"
        )
        st.warning("PDF preview not available in Streamlit. Please download the file.")

def run_newsletter_generation(config: Dict, profile_name: str) -> Dict[str, str]:
    """Run the newsletter generation process.

    Args:
        config: Configuration dictionary
        profile_name: Name of the user profile to use

    Returns:
        Dictionary with paths to generated files
    """
    # Initialize the application
    app = NewsletterApp()
    app.config = config
    
    # Load user profile if specified
    if profile_name and profile_name.lower() != "default":
        app.user_profile = UserProfile.load_user_profile(config, profile_name)
    
    # Run the pipeline
    with st.spinner("Generating newsletter... This may take a few minutes."):
        output_files = app.run()
    
    return output_files

def main():
    """Next-level amazing Streamlit web interface with dark/light mode toggle."""
    
    # Initialize dark mode state
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    
    # Dark mode toggle in top right corner
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        if st.button("🌙" if not st.session_state.dark_mode else "☀️", 
                    help="Toggle Dark/Light Mode",
                    key="theme_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    
    # Dynamic CSS based on theme
    if st.session_state.dark_mode:
        # Luxurious Dark Mode CSS
        st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        
        /* Enhanced Dark Mode Global Styles */
        .stApp {
            background: linear-gradient(135deg, #000000 0%, #0d1117 25%, #161b22 50%, #0d1117 75%, #000000 100%);
            font-family: 'Inter', sans-serif;
            color: #ffffff;
        }
        
        /* Main Container */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        
        /* Enhanced Professional Dark Header */
        .main-header {
            background: linear-gradient(135deg, #0d1117 0%, #161b22 25%, #21262d 50%, #161b22 75%, #0d1117 100%);
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 3rem;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.8), 
                        0 0 50px rgba(255, 255, 255, 0.02),
                        inset 0 1px 0 rgba(255, 255, 255, 0.05);
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        .main-header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.02) 0%, transparent 70%);
            animation: rotate 30s linear infinite;
        }
        
        .main-header h1 {
            color: #ffffff;
            margin: 0;
            text-align: center;
            font-size: 3.5rem;
            font-weight: 700;
            text-shadow: 0 2px 20px rgba(255, 255, 255, 0.1), 0 0 40px rgba(255, 255, 255, 0.05);
            position: relative;
            z-index: 1;
            letter-spacing: -0.025em;
            line-height: 1.1;
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .main-header p {
            color: rgba(255,255,255,0.8);
            text-align: center;
            margin: 1rem 0 0 0;
            font-size: 1.2rem;
            font-weight: 400;
            position: relative;
            z-index: 1;
            opacity: 0.9;
        }
        
        /* Enhanced Luxurious Dark Cards */
        .feature-card {
            background: linear-gradient(145deg, #0d1117 0%, #161b22 25%, #21262d 50%, #161b22 75%, #0d1117 100%);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.8),
                        0 0 30px rgba(255, 255, 255, 0.02),
                        inset 0 1px 0 rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
        }
        
        .feature-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 35px 70px rgba(0, 0, 0, 0.9),
                        0 0 40px rgba(255, 255, 255, 0.04),
                        inset 0 1px 0 rgba(255, 255, 255, 0.06);
        }
        
        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.02), transparent);
            transition: left 0.6s;
        }
        
        .feature-card:hover::before {
            left: 100%;
        }
        
        /* Enhanced Dark Interest Cards */
        .interest-card {
            background: linear-gradient(145deg, #0d1117 0%, #161b22 50%, #21262d 100%);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            border-left: 5px solid #58a6ff;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.6),
                        0 0 20px rgba(88, 166, 255, 0.08);
            transition: all 0.3s ease;
        }
        
        .interest-card:hover {
            transform: translateX(10px);
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8),
                        0 0 30px rgba(88, 166, 255, 0.15);
        }
        
        /* Enhanced Dark Metrics */
        .metric-container {
            background: linear-gradient(145deg, #0d1117 0%, #161b22 50%, #21262d 100%);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 20px 45px rgba(0, 0, 0, 0.7),
                        0 0 25px rgba(255, 255, 255, 0.02),
                        inset 0 1px 0 rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            transition: all 0.3s ease;
        }
        
        .metric-container:hover {
            transform: scale(1.05);
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.9),
                        0 0 35px rgba(255, 255, 255, 0.04);
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #58a6ff;
            margin: 0;
            text-shadow: 0 0 20px rgba(88, 166, 255, 0.3);
        }
        
        .metric-label {
            color: #f0f6fc;
            font-weight: 500;
            margin-top: 0.5rem;
            opacity: 0.8;
        }
        
        /* Dark Status Indicators */
        .status-success {
            background: linear-gradient(135deg, #065f46 0%, #047857 50%, #059669 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            box-shadow: 0 15px 35px rgba(5, 150, 105, 0.4),
                        0 0 20px rgba(16, 185, 129, 0.3);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        
        .status-warning {
            background: linear-gradient(135deg, #92400e 0%, #b45309 50%, #d97706 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            box-shadow: 0 15px 35px rgba(217, 119, 6, 0.4),
                        0 0 20px rgba(245, 158, 11, 0.3);
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        
        .status-info {
            background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 50%, #3b82f6 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            box-shadow: 0 15px 35px rgba(59, 130, 246, 0.4),
                        0 0 20px rgba(59, 130, 246, 0.3);
            border: 1px solid rgba(59, 130, 246, 0.3);
        }
        
        /* Enhanced Dark Mode Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #21262d 0%, #30363d 25%, #484f58 50%, #30363d 75%, #21262d 100%);
            color: #f0f6fc;
            border: none;
            border-radius: 50px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.5),
                        0 0 25px rgba(88, 166, 255, 0.08),
                        inset 0 1px 0 rgba(255, 255, 255, 0.03);
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(88, 166, 255, 0.2);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            background: linear-gradient(135deg, #30363d 0%, #484f58 50%, #58a6ff 100%);
            box-shadow: 0 18px 45px rgba(0, 0, 0, 0.7),
                        0 0 35px rgba(88, 166, 255, 0.2);
        }
        
        /* Enhanced Dark Progress */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #21262d 0%, #58a6ff 50%, #79c0ff 100%);
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(88, 166, 255, 0.3);
        }
        
        /* Enhanced Dark Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: rgba(13, 17, 23, 0.8);
            border-radius: 15px;
            padding: 0.5rem;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            justify-content: center;
            display: flex;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border-radius: 10px;
            color: rgba(240, 246, 252, 0.7);
            font-weight: 500;
            transition: all 0.3s ease;
            padding: 1rem 2rem;
            font-size: 1.2rem;
            text-align: center;
            min-width: 150px;
        }
        
        .stTabs [aria-selected="true"] {
            background: rgba(88, 166, 255, 0.15);
            color: #f0f6fc;
            box-shadow: 0 5px 20px rgba(88, 166, 255, 0.2);
            transform: translateY(-2px);
        }
        
        /* Enhanced Dark Inputs */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            border: 2px solid rgba(88, 166, 255, 0.3);
            border-radius: 15px;
            padding: 1rem;
            font-size: 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
            background: rgba(21, 32, 43, 0.95);
            color: #ffffff;
            backdrop-filter: blur(10px);
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .stTextInput > div > div > input::placeholder,
        .stTextArea > div > div > textarea::placeholder {
            color: rgba(255, 255, 255, 0.6);
            font-weight: 400;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #58a6ff;
            color: #ffffff;
            background: rgba(30, 41, 59, 0.98);
            box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.15),
                        0 0 25px rgba(88, 166, 255, 0.2),
                        inset 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        /* Dark Glass Effect */
        .glass-effect {
            background: rgba(0, 0, 0, 0.4);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6),
                        0 0 20px rgba(139, 92, 246, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid rgba(139, 92, 246, 0.2);
        }
        
        /* Enhanced Dark Theme Toggle Button */
        #theme_toggle {
            background: linear-gradient(135deg, #21262d 0%, #30363d 100%) !important;
            border: 2px solid rgba(88, 166, 255, 0.2) !important;
            border-radius: 50px !important;
            padding: 0.5rem 1rem !important;
            font-size: 1.2rem !important;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.3s ease !important;
            color: #f0f6fc !important;
        }
        
        #theme_toggle:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 12px 30px rgba(88, 166, 255, 0.3) !important;
            background: linear-gradient(135deg, #30363d 0%, #58a6ff 100%) !important;
        }
        
        /* Dark Text Colors */
        .stMarkdown, .stText, p, span, div {
            color: #ffffff !important;
        }
        
        /* Dark Sidebar */
        .css-1d391kg {
            background: linear-gradient(180deg, rgba(0, 0, 0, 0.6) 0%, rgba(26, 26, 26, 0.8) 100%);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(139, 92, 246, 0.2);
        }
        
        /* Enhanced Dark Scrollbar */
        ::-webkit-scrollbar {
            width: 12px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(13, 17, 23, 0.5);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #21262d 0%, #58a6ff 50%, #79c0ff 100%);
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(88, 166, 255, 0.3);
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 50%, #a5f3fc 100%);
            box-shadow: 0 0 20px rgba(88, 166, 255, 0.5);
        }
        
        /* Hide Streamlit Elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        </style>
        """, unsafe_allow_html=True)
    else:
        # Light Mode CSS (Original)
        st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        
        /* Global Styles */
        .stApp {
            background: linear-gradient(135deg, #0f4c75 0%, #3282b8 50%, #0f4c75 100%);
            font-family: 'Inter', sans-serif;
        }
        
        /* Main Container */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        
        /* Elegant Professional Header */
        .main-header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 25%, #1abc9c 50%, #34495e 75%, #2c3e50 100%);
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 3rem;
            box-shadow: 0 20px 40px rgba(44, 62, 80, 0.3);
            position: relative;
            overflow: hidden;
            animation: headerGlow 3s ease-in-out infinite alternate;
        }
        
        @keyframes headerGlow {
            0% { box-shadow: 0 20px 40px rgba(44, 62, 80, 0.3); }
            100% { box-shadow: 0 25px 50px rgba(26, 188, 156, 0.4); }
        }
        
        .main-header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(26, 188, 156, 0.1) 0%, transparent 70%);
            animation: rotate 20s linear infinite;
        }
        
        @keyframes rotate {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .main-header h1 {
            color: white;
            margin: 0;
            text-align: center;
            font-size: 3.5rem;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            position: relative;
            z-index: 1;
            animation: titleFloat 4s ease-in-out infinite;
        }
        
        @keyframes titleFloat {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        
        .main-header p {
            color: rgba(255,255,255,0.9);
            text-align: center;
            margin: 1rem 0 0 0;
            font-size: 1.2rem;
            font-weight: 400;
            position: relative;
            z-index: 1;
        }
        
        /* Enhanced Cards */
        .feature-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
        }
        
        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(26, 188, 156, 0.1), transparent);
            transition: left 0.5s;
        }
        
        .feature-card:hover::before {
            left: 100%;
        }
        
        /* Interest Analysis Cards */
        .interest-card {
            background: linear-gradient(145deg, #ecf8f5 0%, #d5f4e6 100%);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            border-left: 5px solid #1abc9c;
            box-shadow: 0 8px 25px rgba(26, 188, 156, 0.15);
            transition: all 0.3s ease;
        }
        
        .interest-card:hover {
            transform: translateX(10px);
            box-shadow: 0 12px 35px rgba(26, 188, 156, 0.25);
        }
        
        /* Metrics Enhancement */
        .metric-container {
            background: linear-gradient(145deg, #ffffff 0%, #f8fcff 100%);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 10px 30px rgba(15, 76, 117, 0.12);
            border: 1px solid rgba(50, 130, 184, 0.15);
            transition: all 0.3s ease;
        }
        
        .metric-container:hover {
            transform: scale(1.05);
            box-shadow: 0 15px 40px rgba(26, 188, 156, 0.2);
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #0f4c75;
            margin: 0;
        }
        
        .metric-label {
            color: #5a6c7d;
            font-weight: 500;
            margin-top: 0.5rem;
        }
        
        /* Status Indicators */
        .status-success {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
        }
        
        .status-warning {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            box-shadow: 0 8px 25px rgba(245, 158, 11, 0.3);
        }
        
        .status-info {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
        }
        
        /* Enhanced Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #0f4c75 0%, #3282b8 50%, #1abc9c 100%);
            color: white;
            border: none;
            border-radius: 50px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 8px 25px rgba(15, 76, 117, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(26, 188, 156, 0.4);
        }
        
        .stButton > button:active {
            transform: translateY(-1px);
        }
        
        /* Progress Enhancement */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #0f4c75 0%, #1abc9c 100%);
            border-radius: 10px;
        }
        
        /* Tabs Enhancement */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 0.5rem;
            backdrop-filter: blur(10px);
            justify-content: center;
            display: flex;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border-radius: 10px;
            color: rgba(255, 255, 255, 0.8);
            font-weight: 500;
            transition: all 0.3s ease;
            padding: 1rem 2rem;
            font-size: 1.2rem;
            text-align: center;
            min-width: 150px;
        }
        
        .stTabs [aria-selected="true"] {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }
        
        /* Input Enhancement */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            border: 2px solid rgba(26, 188, 156, 0.3);
            border-radius: 15px;
            padding: 1rem;
            font-size: 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.98);
            color: #2c3e50;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .stTextInput > div > div > input::placeholder,
        .stTextArea > div > div > textarea::placeholder {
            color: rgba(44, 62, 80, 0.6);
            font-weight: 400;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #1abc9c;
            color: #2c3e50;
            background: rgba(255, 255, 255, 1);
            box-shadow: 0 0 0 3px rgba(26, 188, 156, 0.15),
                        inset 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        /* Sidebar Enhancement */
        .css-1d391kg {
            background: linear-gradient(180deg, rgba(15, 76, 117, 0.1) 0%, rgba(26, 188, 156, 0.1) 100%);
            backdrop-filter: blur(10px);
        }
        
        /* Loading Animation */
        .loading-container {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
        }
        
        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 5px solid rgba(15, 76, 117, 0.3);
            border-top: 5px solid #1abc9c;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Success Animation */
        .success-checkmark {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: block;
            stroke-width: 3;
            stroke: #10b981;
            stroke-miterlimit: 10;
            margin: 0 auto;
            box-shadow: inset 0px 0px 0px #10b981;
            animation: fill 0.4s ease-in-out 0.4s forwards, scale 0.3s ease-in-out 0.9s both;
        }
        
        @keyframes scale {
            0%, 100% { transform: none; }
            50% { transform: scale3d(1.1, 1.1, 1); }
        }
        
        @keyframes fill {
            100% { box-shadow: inset 0px 0px 0px 30px #10b981; }
        }
        
        /* Floating Elements */
        .floating-element {
            animation: float 6s ease-in-out infinite;
        }
        
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
            100% { transform: translateY(0px); }
        }
        
        /* Glass Effect */
        .glass-effect {
            background: rgba(255, 255, 255, 0.25);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(4px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        
        /* Theme Toggle Button */
        #theme_toggle {
            background: linear-gradient(135deg, #f8fafc 0%, #e1f5fe 100%) !important;
            border: 2px solid rgba(26, 188, 156, 0.3) !important;
            border-radius: 50px !important;
            padding: 0.5rem 1rem !important;
            font-size: 1.2rem !important;
            box-shadow: 0 5px 15px rgba(15, 76, 117, 0.2) !important;
            transition: all 0.3s ease !important;
            color: #0f4c75 !important;
        }
        
        #theme_toggle:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 8px 25px rgba(26, 188, 156, 0.3) !important;
        }
        
        /* Hide Streamlit Elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #0f4c75 0%, #1abc9c 100%);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #1abc9c 0%, #0f4c75 100%);
        }
        </style>
        """, unsafe_allow_html=True)
    
    
    # Enhanced Animated Header with theme-aware styling
    if st.session_state.dark_mode:
        header_class = "main-header"
        feature_icons = "⭐ Smart Analysis | 🎯 Personalized Content | ⚡ Lightning Fast | 🌙 Dark Mode"
    else:
        header_class = "main-header"
        feature_icons = "⭐ Smart Analysis | 🎯 Personalized Content | ⚡ Lightning Fast | ☀️ Light Mode"
    
    st.markdown(f"""
    <div class="{header_class}">
        <h1>AI Newsletter Generator</h1>
        <p>🚀 Enter your interests and get a personalized newsletter powered by cutting-edge AI</p>
        <div style="text-align: center; margin-top: 1.5rem;">
            <span style="display: inline-block; margin: 0 1rem; opacity: 0.9; font-size: 0.9rem;">
                {feature_icons}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'interests_analyzed' not in st.session_state:
        st.session_state.interests_analyzed = False
    if 'current_interests' not in st.session_state:
        st.session_state.current_interests = []
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = {}
    
    
    # Check for Gemini API key
    api_key = os.getenv("GEMINI_API_KEY")
    use_offline_mode = True
    
    # Enhanced API Key Status with visual indicators and theme info
    if api_key:
        theme_status = "🌙 Dark Mode" if st.session_state.dark_mode else "☀️ Light Mode"
        st.markdown(f"""
        <div class="feature-card status-success">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 20px; background: #10b981; border-radius: 50%; margin-right: 1rem;"></div>
                    <div>
                        <h3 style="margin: 0; color: white;"> Gemini AI Activated</h3>
                        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Full AI features available - Premium summaries & analysis • </p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            use_offline_mode = st.toggle("🔄 Offline Mode", value=False, 
                                       help="Generate newsletters without Gemini API calls")
    else:
        theme_status = "🌙 Dark Mode" if st.session_state.dark_mode else "☀️ Light Mode"
        st.markdown(f"""
        <div class="feature-card status-info">
            <div style="display: flex; align-items: center;">
                <div style="width: 20px; height: 20px; background: #3b82f6; border-radius: 50%; margin-right: 1rem;"></div>
                <div>
                    <h3 style="margin: 0; color: white;">🔄 Offline Mode Active</h3>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Basic summaries available - Add Gemini API for premium features • {theme_status}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🔑 Unlock Premium AI Features", expanded=True):
            st.markdown("""
            <div class="glass-effect" style="padding: 2rem; margin: 1rem 0;">
                <h3 style="color: #0f4c75; margin-top: 0;">🚀 Get Your Free Gemini API Key</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin: 1.5rem 0;">
                    <div style="text-align: center; padding: 1rem;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎯</div>
                        <strong>15 requests/min</strong>
                        <div style="color: #6b7280; font-size: 0.9rem;">Fast processing</div>
                    </div>
                    <div style="text-align: center; padding: 1rem;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🧠</div>
                        <strong>1M tokens/min</strong>
                        <div style="color: #6b7280; font-size: 0.9rem;">Advanced analysis</div>
                    </div>
                    <div style="text-align: center; padding: 1rem;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚡</div>
                        <strong>1,500 requests/day</strong>
                        <div style="color: #6b7280; font-size: 0.9rem;">Generous limits</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**Quick Setup Steps:**")
            steps_col1, steps_col2 = st.columns(2)
            
            with steps_col1:
                st.markdown("""
                1. 🌐 Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
                2. 🔐 Sign in with Google account
                3. ➕ Click "Create API key"
                """)
            
            with steps_col2:
                st.markdown("""
                4. 📋 Copy your API key
                5. 📝 Paste it below or add to `.env`
                6. 🎉 Enjoy premium features!
                """)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            gemini_key_input = st.text_input("🔑 Enter Gemini API Key", type="password", 
                                            placeholder="Paste your Gemini API key here...",
                                            help="Paste your Gemini API key to unlock AI-powered summaries")
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
            if st.button("🚀 Activate", use_container_width=True):
                if gemini_key_input:
                    os.environ["GEMINI_API_KEY"] = gemini_key_input
                    st.balloons()
                    st.success("🎉 Gemini AI activated! Refresh to enable premium features.")
                    api_key = gemini_key_input
                    use_offline_mode = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Please enter a valid API key")
    
    # Load configuration
    config = load_config()
    if not config:
        st.error("Failed to load configuration. Please check the config.yaml file.")
        return
    
    # Enhanced Main interface tabs with icons and descriptions
    tab_icons = ["🎯", "⚙️", "📰", "📁"]
    tab_names = ["Enter Interests", "Configure", "Generate", "View Results"]
    tab_descriptions = [
        "Tell us what you're passionate about",
        "Customize your newsletter settings", 
        "Create your personalized newsletter",
        "Read and download your newsletters"
    ]
    
    # Create tabs with enhanced styling
    tabs = st.tabs([f"{icon} {name}" for icon, name in zip(tab_icons, tab_names)])
    
    tab1, tab2, tab3, tab4 = tabs
    
    # Tab 1: Enhanced Interest Entry and Analysis
    with tab1:
        st.markdown("""
        <div class="feature-card">
            <h2 style="color: #0f4c75; margin-top: 0;">🎯 Tell Us What Interests You!</h2>
            <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">
                Share your passions, hobbies, and topics you'd love to stay updated on. 
                Our AI will analyze and categorize them to curate the perfect newsletter for you.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced interest input with better styling
        st.markdown("""
        <div class="interest-card">
            <h3 style="color: #0f4c75; margin-top: 0;">✨ Your Interests</h3>
            <p style="color: #6b7280; margin-bottom: 1rem;">
                You can enter topics in any format - separate with commas, use new lines, or just write naturally!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Interest input with enhanced placeholder
        interests_text = st.text_area(
            "",
            placeholder="""Examples:
• Artificial intelligence, machine learning, deep learning
• Space exploration, NASA missions, astronomy
• Climate science, renewable energy, sustainability
• Startup news, venture capital, fintech
• Python programming, web development, cloud computing
• Quantum physics, biotechnology, medical breakthroughs

Be as specific or broad as you like! 🚀""",
            height=200,
            help="💡 Pro tip: The more specific you are, the better your newsletter will be!"
        )
        
        # Enhanced action buttons with animations
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🔍 Analyze My Interests", type="primary", use_container_width=True):
                if interests_text.strip():
                    with st.spinner("🧠 AI is analyzing your interests..."):
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.01)
                            progress_bar.progress(i + 1)
                        
                        interests, analysis = analyze_interests(interests_text)
                        st.session_state.current_interests = interests
                        st.session_state.current_analysis = analysis
                        st.session_state.interests_analyzed = True
                        
                        # Success animation
                        st.balloons()
                        st.success("🎉 Analysis complete! Check out your results below.")
                else:
                    st.error("🤔 Please enter some interests first!")
        
        with col2:
            if st.button("🎲 Try Example Interests", use_container_width=True):
                example_interests = [
                    "artificial intelligence", "machine learning", "python programming", 
                    "data science", "technology trends", "space exploration", "climate science",
                    "renewable energy", "biotech innovations", "quantum computing"
                ]
                st.session_state.current_interests = example_interests
                st.session_state.current_analysis = {
                    'total_interests': len(example_interests),
                    'detected_categories': ['technology', 'science'],
                    'recommendations': ["Perfect blend of cutting-edge tech and scientific breakthroughs!"],
                    'suggested_feeds': []
                }
                st.session_state.interests_analyzed = True
                st.success("🎲 Example interests loaded! Perfect for tech enthusiasts.")
                
        with col3:
            if st.button("🔄 Clear All", use_container_width=True):
                st.session_state.interests_analyzed = False
                st.session_state.current_interests = []
                st.session_state.current_analysis = {}
                st.rerun()
        
        
        # Enhanced analysis results display
        if st.session_state.interests_analyzed and st.session_state.current_interests:
            # Success header with animation
            st.markdown("""
            <div class="feature-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; text-align: center; margin: 2rem 0;">
                <h2 style="margin: 0; color: white;">🎊 Analysis Complete!</h2>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Your interests have been intelligently processed and categorized</p>
            </div>
            """, unsafe_allow_html=True)
            
            analysis = st.session_state.current_analysis
            
            # Enhanced metrics with better visual design
            col1, col2, col3, col4 = st.columns(4)
            
            metrics_data = [
                ("🎯", "Interests Found", analysis.get('total_interests', 0), "#0f4c75"),
                ("🏷️", "Categories", len(analysis.get('detected_categories', [])), "#10b981"), 
                ("📡", "Feed Sources", len(analysis.get('suggested_feeds', [])), "#f59e0b"),
                ("⭐", "Relevance", "High", "#8b5cf6")
            ]
            
            for i, (icon, label, value, color) in enumerate(metrics_data):
                with [col1, col2, col3, col4][i]:
                    st.markdown(f"""
                    <div class="metric-container" style="border-left: 4px solid {color};">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                        <div class="metric-value" style="color: {color};">{value}</div>
                        <div class="metric-label">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Enhanced interests display with tags
            st.markdown("### ✨ Your Processed Interests")
            
            # Create interest tags with simpler HTML structure
            interests_html = '<div class="feature-card" style="display: flex; flex-wrap: wrap; gap: 0.5rem; padding: 2rem;">'
            
            for i, interest in enumerate(st.session_state.current_interests):
                color = ["#0f4c75", "#10b981", "#1abc9c", "#3282b8", "#2c3e50", "#34495e"][i % 6]
                interests_html += f'''<span style="display: inline-block; background: {color}; color: white; padding: 0.5rem 1rem; margin: 0.25rem; border-radius: 25px; font-weight: 500; box-shadow: 0 4px 15px rgba(0,0,0,0.2); animation: fadeInUp 0.5s ease {i * 0.1}s both;">{interest}</span>'''
            
            interests_html += '</div>'
            
            # Render the HTML with animation styles
            st.markdown(f"""
            {interests_html}
            <style>
            @keyframes fadeInUp {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            </style>
            """, unsafe_allow_html=True)
            
            # Enhanced categories and recommendations
            col1, col2 = st.columns(2)
            
            with col1:
                if analysis.get('detected_categories'):
                    st.markdown("### 🏷️ Detected Categories")
                    for i, category in enumerate(analysis['detected_categories']):
                        category_icons = {
                            'technology': '💻',
                            'science': '🔬', 
                            'business': '💼',
                            'sports': '⚽',
                            'entertainment': '🎬',
                            'politics': '🏛️',
                            'world': '🌍'
                        }
                        icon = category_icons.get(category, '📂')
                        
                        st.markdown(f"""
                        <div class="interest-card floating-element" style="animation-delay: {i * 0.2}s;">
                            <div style="display: flex; align-items: center;">
                                <div style="font-size: 1.5rem; margin-right: 1rem;">{icon}</div>
                                <div>
                                    <h4 style="margin: 0; color: #667eea; text-transform: capitalize;">{category}</h4>
                                    <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">News and updates</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            with col2:
                if analysis.get('recommendations'):
                    st.markdown("### 💡 Smart Recommendations")
                    for i, rec in enumerate(analysis['recommendations']):
                        st.markdown(f"""
                        <div class="feature-card" style="background: linear-gradient(135deg, #f8f9ff 0%, #e8f2ff 100%); animation: slideInRight 0.5s ease {i * 0.1}s both;">
                            <div style="display: flex; align-items: start;">
                                <div style="font-size: 1.2rem; margin-right: 1rem; margin-top: 0.2rem;">💡</div>
                                <p style="margin: 0; color: #4b5563; line-height: 1.6;">{rec}</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Enhanced feed suggestions
            if analysis.get('suggested_feeds'):
                st.markdown("### 📡 Suggested RSS Sources")
                feed_cols = st.columns(min(len(analysis['suggested_feeds']), 3))
                
                for i, feed in enumerate(analysis['suggested_feeds'][:3]):
                    with feed_cols[i % 3]:
                        st.markdown(f"""
                        <div class="glass-effect" style="padding: 1.5rem; text-align: center; height: 120px; display: flex; flex-direction: column; justify-content: center;">
                            <h4 style="margin: 0 0 0.5rem 0; color: #667eea;">{feed['name']}</h4>
                            <p style="margin: 0; color: #6b7280; font-size: 0.9rem; text-transform: capitalize;">{feed['category']} news</p>
                            <div style="margin-top: 0.5rem; color: #10b981;">✓ Active feed</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Add CSS animations
            st.markdown("""
            <style>
            @keyframes slideInRight {
                from { opacity: 0; transform: translateX(30px); }
                to { opacity: 1; transform: translateX(0); }
            }
            </style>
            """, unsafe_allow_html=True)
    
    # Tab 2: Enhanced Configuration
    with tab2:
        st.markdown("""
        <div class="feature-card">
            <h2 style="color: #0f4c75; margin-top: 0;">⚙️ Customize Your Newsletter Experience</h2>
            <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">
                Fine-tune every aspect of your newsletter to match your preferences perfectly.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced configuration with better organization
        config_col1, config_col2 = st.columns(2)
        
        with config_col1:
            st.markdown("""
            <div class="feature-card">
                <h3 style="color: #0f4c75; margin-top: 0; display: flex; align-items: center;">
                    <span style="margin-right: 0.5rem;">📰</span> Newsletter Settings
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            newsletter_title = st.text_input(
                "📝 Newsletter Title",
                value=config.get("newsletter", {}).get("title", "My AI-Powered Newsletter"),
                help="Give your newsletter a catchy title!"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                summary_length = st.selectbox(
                    "📏 Summary Length",
                    ["short", "medium", "long"],
                    index=1,
                    help="How detailed should the article summaries be?"
                )
                
                output_format = st.selectbox(
                    "📋 Output Format", 
                    ["markdown", "pdf", "both"],
                    index=2,  # Default to "both"
                    help="Choose the format for your newsletter"
                )
            
            with col2:
                include_images = st.checkbox("🖼️ Include Images", value=True, 
                                           help="Add relevant images to articles")
                include_quotes = st.checkbox("💬 Include Quotes", value=True,
                                           help="Extract key quotes from articles")
        
        with config_col2:
            st.markdown("""
            <div class="feature-card">
                <h3 style="color: #0f4c75; margin-top: 0; display: flex; align-items: center;">
                    <span style="margin-right: 0.5rem;">🎯</span> Content Settings
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            max_articles = st.slider(
                "📊 Maximum Articles per Newsletter",
                min_value=5,
                max_value=25,
                value=config.get("fetching", {}).get("max_total_articles", 15),
                help="More articles = more comprehensive newsletter"
            )
            
            min_relevance = st.slider(
                "🎯 Relevance Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                step=0.1,
                help="Higher values = more focused content"
            )
            
            age_limit = st.slider(
                "⏰ Article Age Limit (days)",
                min_value=1,
                max_value=7,
                value=2,
                help="Only include recent articles"
            )
            
            # Visual feedback for settings
            st.markdown(f"""
            <div class="interest-card">
                <h4 style="color: #0f4c75;">📊 Current Configuration</h4>
                <p><strong>Articles:</strong> Up to {max_articles} articles</p>
                <p><strong>Relevance:</strong> {min_relevance*100:.0f}% minimum match</p>
                <p><strong>Freshness:</strong> Last {age_limit} day{'s' if age_limit > 1 else ''}</p>
                <p><strong>Format:</strong> {output_format.title()} {'(Markdown + PDF)' if output_format == 'both' else ''}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Update config with user preferences
        config["newsletter"]["title"] = newsletter_title
        config["summarization"]["length"] = summary_length
        config["newsletter"]["output_format"] = output_format
        config["newsletter"]["include_images"] = include_images
        config["summarization"]["include_quotes"] = include_quotes
        config["fetching"]["max_total_articles"] = max_articles
        config["user"]["min_relevance_score"] = min_relevance
        config["fetching"]["article_age_limit_days"] = age_limit
    
    # Tab 3: Enhanced Newsletter Generation
    with tab3:
        st.markdown("""
        <div class="feature-card">
            <h2 style="color: #0f4c75; margin-top: 0;">📰 Generate Your Personalized Newsletter</h2>
            <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">
                Ready to create something amazing? Let's generate your custom newsletter!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.interests_analyzed:
            st.markdown("""
            <div class="feature-card status-warning">
                <div style="display: flex; align-items: center;">
                    <div style="font-size: 2rem; margin-right: 1rem;">⚠️</div>
                    <div>
                        <h3 style="margin: 0; color: white;">Setup Required</h3>
                        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Please analyze your interests in the first tab before generating a newsletter.</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Enhanced generation summary
        summary_col1, summary_col2 = st.columns([2, 1])
        
        with summary_col1:
            st.markdown("""
            <div class="feature-card">
                <h3 style="color: #0f4c75; margin-top: 0;">📋 Generation Summary</h3>
            </div>
            """, unsafe_allow_html=True)
            
            interests_display = ", ".join(st.session_state.current_interests[:5])
            if len(st.session_state.current_interests) > 5:
                interests_display += f" +{len(st.session_state.current_interests) - 5} more"
            
            # Enhanced summary with icons and styling
            summary_items = [
                ("🎯", "Your Interests", interests_display),
                ("📰", "Newsletter Title", newsletter_title),
                ("📊", "Max Articles", f"{max_articles} articles"),
                ("🤖", "AI Mode", "🔄 Offline (Mock Summaries)" if use_offline_mode or not api_key else "🌟 Gemini AI-Powered"),
                ("📄", "Output Format", f"{output_format.title()} {'(MD + PDF)' if output_format == 'both' else '('+output_format.upper()+')'}"),
                ("🏷️", "Categories", ", ".join([cat.title() for cat in st.session_state.current_analysis.get('detected_categories', [])]) if st.session_state.current_analysis.get('detected_categories') else "Auto-detected")
            ]
            
            for icon, label, value in summary_items:
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin: 1rem 0; padding: 0.5rem; background: rgba(15, 76, 117, 0.08); border-radius: 10px;">
                    <span style="font-size: 1.2rem; margin-right: 1rem;">{icon}</span>
                    <strong style="color: #0f4c75; margin-right: 1rem; min-width: 120px;">{label}:</strong>
                    <span style="color: #4b5563;">{value}</span>
                </div>
                """, unsafe_allow_html=True)
        
        with summary_col2:
            # Enhanced generation button with preview
            st.markdown("""
            <div class="feature-card" style="text-align: center; background: linear-gradient(135deg, #0f4c75 0%, #1abc9c 100%); color: white;">
                <h3 style="margin-top: 0; color: white;">🚀 Ready to Launch?</h3>
                <p style="margin-bottom: 2rem; opacity: 0.9;">Your personalized newsletter is just one click away!</p>
            </div>
            """, unsafe_allow_html=True)
            
            generate_button_text = "🚀 Generate My Newsletter" if st.session_state.current_interests else "🚀 Generate Newsletter"
            
            if st.button(generate_button_text, type="primary", use_container_width=True):
                if not st.session_state.current_interests:
                    st.error("❌ Please enter and analyze your interests first!")
                    return
                
                # Enhanced progress tracking with animations
                st.markdown("""
                <div class="feature-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; text-align: center;">
                    <h3 style="margin: 0; color: white;">🎯 Generating Your Newsletter</h3>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Processing {0} interests across {1} categories...</p>
                </div>
                """.format(
                    len(st.session_state.current_interests),
                    len(st.session_state.current_analysis.get('detected_categories', []))
                ), unsafe_allow_html=True)
                
                # Show what we're doing with better formatting
                st.info(f"🎯 **Target Topics:** {', '.join(st.session_state.current_interests[:3])}{'...' if len(st.session_state.current_interests) > 3 else ''}")
                
                # Generate the newsletter with enhanced progress tracking
                if use_offline_mode or not api_key:
                    output_files = run_newsletter_generation_offline(config, st.session_state.current_interests)
                else:
                    output_files = run_newsletter_generation_gemini(config, st.session_state.current_interests)
                
                if output_files:
                    st.session_state.last_generated_files = output_files
                    
                    # Success celebration
                    st.balloons()
                    st.markdown("""
                    <div class="feature-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; text-align: center;">
                        <h2 style="margin: 0; color: white;">🎉 Newsletter Generated Successfully!</h2>
                        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Your personalized newsletter is ready to read</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Enhanced file display
                    for format_type, file_path in output_files.items():
                        st.markdown(f"""
                        <div class="interest-card">
                            <div style="display: flex; align-items: center; justify-content: between;">
                                <div style="display: flex; align-items: center;">
                                    <span style="font-size: 1.2rem; margin-right: 1rem;">📄</span>
                                    <div>
                                        <strong style="color: #0f4c75;">{format_type.upper()}</strong>
                                        <div style="color: #6b7280; font-size: 0.9rem;">{file_path}</div>
                                    </div>
                                </div>
                                <span style="color: #10b981;">✓</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Enhanced generation results summary
                    st.markdown("### 📊 Generation Results")
                    
                    result_cols = st.columns(3)
                    with result_cols[0]:
                        st.markdown(f"""
                        <div class="metric-container">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎯</div>
                            <div class="metric-value">{len(st.session_state.current_interests)}</div>
                            <div class="metric-label">Interests Processed</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with result_cols[1]:
                        st.markdown(f"""
                        <div class="metric-container">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🏷️</div>
                            <div class="metric-value">{len(st.session_state.current_analysis.get('detected_categories', []))}</div>
                            <div class="metric-label">Categories Searched</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with result_cols[2]:
                        st.markdown(f"""
                        <div class="metric-container">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📰</div>
                            <div class="metric-value">{max_articles}</div>
                            <div class="metric-label">Max Articles</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Auto-switch prompt
                    st.markdown("""
                    <div class="feature-card" style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white; text-align: center;">
                        <h3 style="margin: 0; color: white;">👆 Ready to Read?</h3>
                        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Switch to the 'View Results' tab to see your personalized newsletter!</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="feature-card status-warning">
                        <div style="display: flex; align-items: center;">
                            <div style="font-size: 2rem; margin-right: 1rem;">❌</div>
                            <div>
                                <h3 style="margin: 0; color: white;">Generation Failed</h3>
                                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Please check your settings and try again</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Tab 4: Enhanced Results Viewing
    with tab4:
        st.markdown("""
        <div class="feature-card">
            <h2 style="color: #0f4c75; margin-top: 0;">📁 Your Newsletter Collection</h2>
            <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">
                Read, download, and manage all your personalized newsletters in one place.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        output_dir = project_root / config.get("newsletter", {}).get("output_dir", "data/output")
        
        # Latest generated newsletter
        if hasattr(st.session_state, 'last_generated_files') and st.session_state.last_generated_files:
            st.markdown("""
            <div class="feature-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white;">
                <h3 style="margin: 0; color: white;">🆕 Latest Generated Newsletter</h3>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Fresh from the AI kitchen, your newest personalized newsletter</p>
            </div>
            """, unsafe_allow_html=True)
            
            latest_files = st.session_state.last_generated_files
            
            # Enhanced display for latest newsletter with both formats
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Show markdown preview if available
                markdown_file = latest_files.get("markdown")
                if markdown_file and os.path.exists(markdown_file):
                    with st.expander("📄 Preview Newsletter", expanded=True):
                        display_newsletter(markdown_file)
                else:
                    st.info("📄 Markdown preview not available")
            
            with col2:
                st.markdown("""
                <div class="feature-card" style="text-align: center;">
                    <h4 style="color: #667eea; margin-top: 0;">📥 Download Options</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # Enhanced download options for all available formats
                for format_type, file_path in latest_files.items():
                    if os.path.exists(file_path):
                        if format_type == "markdown":
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    newsletter_content = f.read()
                                
                                st.download_button(
                                    label="📝 Download Markdown",
                                    data=newsletter_content,
                                    file_name=os.path.basename(file_path),
                                    mime="text/markdown",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"Error reading markdown file: {str(e)}")
                        
                        elif format_type == "pdf":
                            try:
                                with open(file_path, "rb") as f:
                                    pdf_bytes = f.read()
                                
                                # Enhanced PDF handling with preview and download
                                col_a, col_b = st.columns([1, 1])
                                
                                with col_a:
                                    st.download_button(
                                        label="📄 Download PDF",
                                        data=pdf_bytes,
                                        file_name=os.path.basename(file_path),
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                                
                                with col_b:
                                    # Create base64 encoded version for preview
                                    import base64
                                    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                                    
                                    # Styled preview button
                                    pdf_preview = f"""
                                    <a href="data:application/pdf;base64,{base64_pdf}" target="_blank">
                                        <button style="
                                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                            color: white;
                                            border: none;
                                            border-radius: 10px;
                                            padding: 0.75rem 1.5rem;
                                            font-size: 1rem;
                                            font-weight: 600;
                                            cursor: pointer;
                                            width: 100%;
                                            transition: all 0.3s ease;
                                            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                                        ">
                                            👁️ Preview PDF
                                        </button>
                                    </a>
                                    """
                                    st.markdown(pdf_preview, unsafe_allow_html=True)
                                
                                # Show PDF file info
                                file_size = len(pdf_bytes) / 1024  # KB
                                st.markdown(f"""
                                <div class="interest-card" style="text-align: center; margin-top: 0.5rem;">
                                    <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">
                                        📄 PDF • {file_size:.1f} KB • Preview opens in new tab
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"Error reading PDF file: {str(e)}")
                
                # Add sharing options
                st.markdown("""
                <div class="interest-card" style="text-align: center; margin-top: 1rem;">
                    <h5 style="color: #667eea; margin-top: 0;">📤 Share</h5>
                    <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">Files saved in your output directory</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Previous newsletters section
        if output_dir.exists():
                            # Add reading time estimate
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                word_count = len(content.split())
                                reading_time = max(1, word_count // 200)  # Assuming 200 words per minute
                                
                                st.markdown(f"""
                                <div class="interest-card">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div>
                                            <h4 style="margin: 0; color: #667eea;">📖 Reading Stats</h4>
                                            <p style="margin: 0.5rem 0 0 0; color: #6b7280;">
                                                {word_count:,} words • ~{reading_time} min read • Generated {datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%B %d, %Y at %I:%M %p")}
                                            </p>
                                        </div>
                                        <div style="font-size: 1.5rem;">📰</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                display_newsletter(file_path)
                            except Exception as e:
                                st.error(f"Error reading newsletter: {str(e)}")
        
        # Previous newsletters section
        if output_dir.exists():
            st.markdown("### 📚 Newsletter Archive")
            markdown_files = sorted(list(output_dir.glob("*.md")), key=os.path.getmtime, reverse=True)
            pdf_files = sorted(list(output_dir.glob("*.pdf")), key=os.path.getmtime, reverse=True)
            
            if markdown_files:
                # Enhanced file display with grid layout
                for i, file_path in enumerate(markdown_files[:6]):  # Show last 6
                    file_name = file_path.name
                    file_date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%B %d, %Y")
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%I:%M %p")
                    file_size = os.path.getsize(file_path)
                    
                    # Check for corresponding PDF file
                    pdf_file = output_dir / file_path.name.replace('.md', '.pdf')
                    has_pdf = pdf_file.exists()
                    
                    # Calculate reading stats
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        word_count = len(content.split())
                        reading_time = max(1, word_count // 200)
                    except:
                        word_count = 0
                        reading_time = 1
                    
                    with st.expander(f"📄 {file_name} - {file_date}", expanded=False):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"""
                            <div class="interest-card">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <h4 style="margin: 0; color: #667eea;">📊 Newsletter Stats</h4>
                                        <p style="margin: 0.5rem 0 0 0; color: #6b7280;">
                                            📅 {file_date} at {file_time}<br>
                                            📖 {word_count:,} words • ~{reading_time} min read<br>
                                            💾 {file_size / 1024:.1f} KB
                                            {' • 📄 PDF Available' if has_pdf else ''}
                                        </p>
                                    </div>
                                    <div style="font-size: 2rem;">📰</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            if st.button(f"👀 Preview", key=f"preview_{i}", use_container_width=True):
                                display_newsletter(str(file_path))
                            
                            # Download buttons for archived newsletters
                            try:
                                # Markdown download
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                st.download_button(
                                    label="� Download MD",
                                    data=content,
                                    file_name=file_name,
                                    mime="text/markdown",
                                    key=f"download_md_{i}",
                                    use_container_width=True
                                )
                                
                                # PDF download if available
                                if has_pdf:
                                    with open(pdf_file, "rb") as f:
                                        pdf_bytes = f.read()
                                    st.download_button(
                                        label="📄 Download PDF",
                                        data=pdf_bytes,
                                        file_name=pdf_file.name,
                                        mime="application/pdf",
                                        key=f"download_pdf_{i}",
                                        use_container_width=True
                                    )
                            except Exception as e:
                                st.error(f"Error reading file: {str(e)}")
                
                # Show total statistics
                st.markdown(f"""
                <div class="feature-card" style="background: linear-gradient(135deg, #0f4c75 0%, #3282b8 100%); color: white; text-align: center;">
                    <h3 style="margin: 0; color: white;">📊 Your Newsletter Journey</h3>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
                        You've generated {len(markdown_files)} newsletters • {len(pdf_files)} PDFs • Keep exploring new topics!
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                # Empty state with call-to-action
                st.markdown("""
                <div class="feature-card" style="text-align: center; padding: 3rem;">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">📰</div>
                    <h3 style="color: #667eea; margin-bottom: 1rem;">No Newsletters Yet</h3>
                    <p style="color: #6b7280; margin-bottom: 2rem;">
                        Ready to create your first personalized newsletter?<br>
                        Head back to the previous tabs to get started!
                    </p>
                    <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
                        <span style="background: rgba(15, 76, 117, 0.15); padding: 0.5rem 1rem; border-radius: 20px; color: #0f4c75;">
                            🎯 Enter interests
                        </span>
                        <span style="background: rgba(26, 188, 156, 0.15); padding: 0.5rem 1rem; border-radius: 20px; color: #1abc9c;">
                            ⚙️ Configure settings
                        </span>
                        <span style="background: rgba(50, 130, 184, 0.15); padding: 0.5rem 1rem; border-radius: 20px; color: #3282b8;">
                            📰 Generate newsletter
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # No output directory
            st.markdown("""
            <div class="feature-card" style="text-align: center; padding: 3rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🚀</div>
                                <h3 style="color: #0f4c75; margin-bottom: 1rem;">Ready to Start?</h3>
                <p style="color: #6b7280; margin-bottom: 2rem;">
                    Your newsletter collection will appear here once you generate your first one!
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Simple Professional Footer
    st.markdown("---")
    
    # Developer info section
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #1e293b 0%, #334155 100%); border-radius: 15px; margin-top: 3rem;">
        <h3 style="color: #1abc9c; margin-bottom: 1rem;"> Developed by Wajahat Hussain</h3>
        <p style="color: rgba(255,255,255,0.8); margin-bottom: 2rem;">AI Developer & Machine Learning Engineer</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Social links using columns
    st.markdown("### 🔗 Connect with me:")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**GitHub**")
        st.markdown("[wajahattt-dev](https://github.com/wajahattt-dev)")
    
    with col2:
        st.markdown("**LinkedIn**") 
        st.markdown("[wajahattthussain](https://linkedin.com/in/wajahattthussain)")
    
    with col3:
        st.markdown("**Twitter**")
        st.markdown("[WajahattHussain](https://x.com/WajahattHussain)")
    
    with col4:
        st.markdown("**Email**")
        st.markdown("[wajahattt.hussain@gmail.com](mailto:wajahattt.hussain@gmail.com)")
    
    # Project info
    st.markdown("### 🚀 About This Project")
    st.info("""
    **AI-Powered Newsletter Generator** - This project leverages advanced machine learning to create personalized content experiences. 
    Built with Python, Streamlit, and Gemini AI, it represents the future of intelligent content curation.
    
    **Features:** 🤖 AI-Powered • ⚡ Lightning Fast • 🎯 Personalized • 📄 Multi-Format Export
    """)
    
if __name__ == "__main__":
    main()