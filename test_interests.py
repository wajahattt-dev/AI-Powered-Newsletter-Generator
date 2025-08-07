"""
Test script to verify the enhanced interest analysis
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.web_app import analyze_interests

def test_interest_analysis():
    """Test the enhanced interest analysis function."""
    
    # Test cases
    test_inputs = [
        "AI, machine learning, space exploration, climate change",
        "artificial intelligence and blockchain technology", 
        "I'm interested in programming, especially Python and web development",
        "finance, startups, venture capital, fintech innovation",
        "space, NASA, Mars exploration, rocket technology",
        "climate science, renewable energy, environmental policy"
    ]
    
    print("🧪 Testing Enhanced Interest Analysis\n" + "="*50)
    
    for i, input_text in enumerate(test_inputs, 1):
        print(f"\nTest {i}: {input_text}")
        print("-" * 40)
        
        interests, analysis = analyze_interests(input_text)
        
        print(f"✅ Processed Interests ({len(interests)}):")
        for interest in interests:
            print(f"   • {interest}")
        
        print(f"\n🏷️ Detected Categories: {', '.join(analysis['detected_categories'])}")
        
        print(f"\n💡 Recommendations:")
        for rec in analysis['recommendations']:
            print(f"   • {rec}")
        
        if analysis['suggested_feeds']:
            print(f"\n📡 Suggested Feeds:")
            for feed in analysis['suggested_feeds'][:3]:
                print(f"   • {feed['name']} ({feed['category']})")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    test_interest_analysis()
