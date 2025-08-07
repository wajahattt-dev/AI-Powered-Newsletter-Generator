"""
Gemini AI Article Summarizer Module

This module provides AI-powered article summarization using Google's Gemini API
instead of OpenAI. It generates intelligent summaries, key points, and quotes.
"""

import logging
import os
import json
from typing import Dict, List, Optional
from pathlib import Path

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
    logging.warning("Google Generative AI not available. Install with: pip install google-generativeai")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeminiArticleSummarizer:
    """Class for summarizing articles using Google's Gemini AI."""

    def __init__(self, config: Dict):
        """Initialize the Gemini summarizer with configuration.

        Args:
            config: Dictionary containing API and summarization configuration settings
        """
        if not HAS_GEMINI:
            raise ImportError("Google Generative AI library not installed")
        
        self.config = config
        self.api_config = config.get('gemini', {
            'model': 'gemini-1.5-flash',  # Free tier model
            'temperature': 0.3,
            'max_output_tokens': 1000
        })
        self.summarization_config = config.get('summarization', {})
        
        # Initialize Gemini
        self._initialize_gemini()
        
        # Load prompt template
        self.prompt_template = self._load_prompt_template()

    def _initialize_gemini(self):
        """Initialize the Gemini AI client."""
        # Get API key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Initialize the model
        generation_config = {
            "temperature": self.api_config.get('temperature', 0.3),
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": self.api_config.get('max_output_tokens', 1000),
        }
        
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        self.model = genai.GenerativeModel(
            model_name=self.api_config.get('model', 'gemini-1.5-flash'),
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        logger.info(f"Initialized Gemini model: {self.api_config.get('model', 'gemini-1.5-flash')}")

    def _load_prompt_template(self) -> str:
        """Load the summarization prompt template from file.

        Returns:
            String template for prompts
        """
        # Get the project root directory
        project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        prompt_path = project_root / "prompts" / "gemini_summarization.txt"
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                template = f.read()
            logger.info(f"Loaded prompt template from {prompt_path}")
            return template
        except FileNotFoundError:
            logger.warning(f"Prompt template not found at {prompt_path}, using default")
            return self._default_prompt_template()
        except Exception as e:
            logger.error(f"Error loading prompt template: {str(e)}")
            return self._default_prompt_template()

    def _default_prompt_template(self) -> str:
        """Create a default prompt template if the file is not available.

        Returns:
            Default prompt template string
        """
        return """You are an expert news editor. Summarize the following article and provide key insights.

Article Information:
Title: {title}
Source: {source}
Category: {category}
Published: {published_date}

Article Content:
{content}

Instructions:
1. Create a {length} summary that captures the main points and key details
2. Extract {num_key_points} key points as bullet points
3. {extract_quotes_instruction}
4. Maintain a neutral, journalistic tone
5. Focus on the most newsworthy and relevant aspects

Please provide your response in this exact JSON format:
{{
  "summary": "Your concise summary here...",
  "key_points": [
    "First key point",
    "Second key point", 
    "Third key point"
  ],
  "quotes": [
    "First notable quote from the article",
    "Second notable quote from the article"
  ]
}}

Note: If there are no notable quotes, return an empty array for quotes."""

    def summarize_articles(self, articles: List[Dict]) -> List[Dict]:
        """Summarize a list of articles.

        Args:
            articles: List of article dictionaries with full content

        Returns:
            List of article dictionaries with added summaries
        """
        summarized_articles = []
        
        for article in articles:
            try:
                if not article.get('content'):
                    logger.warning(f"No content to summarize for article: {article.get('title', 'Unknown')}")
                    continue
                    
                logger.info(f"Summarizing article: {article['title']}")
                summarized_article = self._summarize_article(article)
                summarized_articles.append(summarized_article)
            except Exception as e:
                logger.error(f"Error summarizing article {article.get('title', 'Unknown')}: {str(e)}")
                # Add the original article without summary
                summarized_articles.append(article)
        
        logger.info(f"Successfully summarized {len(summarized_articles)} articles")
        return summarized_articles

    def _summarize_article(self, article: Dict) -> Dict:
        """Summarize a single article.

        Args:
            article: Dictionary containing article data with full content

        Returns:
            Updated article dictionary with summary, key points, and quotes
        """
        # Prepare the input for the prompt template
        summary_length = self.summarization_config.get('length', 'medium')
        num_key_points = self.summarization_config.get('num_key_points', 3)
        include_quotes = self.summarization_config.get('include_quotes', True)
        
        extract_quotes_instruction = (
            "Extract 2-3 notable quotes from the article."
            if include_quotes else 
            "Skip quote extraction for this article."
        )
        
        # Truncate content if it's too long to avoid token limits
        content = article['content']
        if len(content) > 15000:  # Gemini can handle more than GPT
            content = content[:15000] + "..."
            logger.warning(f"Content truncated for article: {article['title']}")
        
        # Format the prompt
        prompt = self.prompt_template.format(
            title=article.get('title', 'Untitled'),
            source=article.get('source', 'Unknown'),
            category=article.get('category', 'general'),
            published_date=str(article.get('published_date', '')),
            content=content,
            length=summary_length,
            num_key_points=num_key_points,
            extract_quotes_instruction=extract_quotes_instruction
        )
        
        # Generate response using Gemini
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            return self._create_fallback_summary(article)
        
        # Parse the JSON response
        summary_data = self._parse_summary_response(result_text, article)
        
        # Update the article with summary data
        article.update(summary_data)
        
        return article

    def _parse_summary_response(self, response_text: str, article: Dict) -> Dict:
        """Parse the JSON response from Gemini.

        Args:
            response_text: Raw response text from Gemini
            article: Original article dictionary

        Returns:
            Dictionary with summary, key_points, and quotes
        """
        try:
            # Try to extract JSON from the response
            # Sometimes the model includes extra text before/after JSON
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_text = response_text[start_idx:end_idx]
                summary_data = json.loads(json_text)
                
                # Validate the structure
                if all(key in summary_data for key in ['summary', 'key_points', 'quotes']):
                    return summary_data
                else:
                    logger.warning("Invalid JSON structure in Gemini response")
                    return self._create_fallback_summary(article)
            else:
                logger.warning("No valid JSON found in Gemini response")
                return self._create_fallback_summary(article)
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.debug(f"Response text: {response_text[:500]}...")
            return self._create_fallback_summary(article)
        except Exception as e:
            logger.error(f"Unexpected error parsing response: {str(e)}")
            return self._create_fallback_summary(article)

    def _create_fallback_summary(self, article: Dict) -> Dict:
        """Create a fallback summary when AI processing fails.

        Args:
            article: Article dictionary

        Returns:
            Dictionary with basic summary data
        """
        content = article.get('content', article.get('summary', ''))
        title = article.get('title', 'Untitled')
        
        # Create a simple summary from the first part of the content
        if content:
            sentences = content.split('. ')
            summary = '. '.join(sentences[:3]) + '.'
            if len(summary) > 300:
                summary = summary[:300] + '...'
        else:
            summary = f"Article about {title.lower()}. Full content not available for summarization."
        
        return {
            'summary': summary,
            'key_points': [
                "Key information from the article",
                "Important details discussed",
                "Relevant context and implications"
            ],
            'quotes': []
        }

    def generate_introduction(self, articles: List[Dict]) -> str:
        """Generate an introduction for the newsletter.

        Args:
            articles: List of summarized articles

        Returns:
            Introduction text for the newsletter
        """
        if not articles:
            return "Welcome to your personalized newsletter! No articles were found matching your interests today."
        
        # Prepare data about the articles
        categories = set()
        sources = set()
        for article in articles:
            if article.get('category'):
                categories.add(article['category'].title())
            if article.get('source'):
                sources.add(article['source'])
        
        categories_text = ", ".join(sorted(categories)) if categories else "various topics"
        article_count = len(articles)
        
        # Create a prompt for the introduction
        intro_prompt = f"""Write a brief, engaging introduction for a newsletter containing {article_count} articles covering {categories_text}. 

The newsletter sources include: {', '.join(sorted(sources)[:5])}

Write a 2-3 sentence introduction that:
1. Welcomes the reader
2. Mentions the key topics covered
3. Sets an engaging tone for the newsletter

Keep it professional but friendly. Do not use JSON format, just return the introduction text."""
        
        try:
            response = self.model.generate_content(intro_prompt)
            introduction = response.text.strip()
            
            # Clean up any unwanted formatting
            introduction = introduction.replace('"', '').replace('\n\n', '\n')
            
            return introduction
        except Exception as e:
            logger.error(f"Error generating introduction: {str(e)}")
            return f"Welcome to your personalized newsletter! Today we've curated {article_count} articles covering {categories_text} to keep you informed on the topics that matter most to you."
