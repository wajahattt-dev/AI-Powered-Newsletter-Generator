"""
Article Summarizer Module

This module handles summarizing article content using LangChain and OpenAI.
It processes full article text and generates concise summaries, key points, and extracts quotes.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ArticleSummarizer:
    """Class for summarizing articles using LLMs."""

    def __init__(self, config: Dict):
        """Initialize the article summarizer with configuration.

        Args:
            config: Dictionary containing summarization and API configuration
        """
        self.config = config
        self.summarization_config = config['summarization']
        self.api_config = config['api']
        
        # Load the summarization prompt template
        self.prompt_template = self._load_prompt_template()
        
        # Initialize the language model
        self.llm = ChatOpenAI(
            model=self.api_config['model'],
            temperature=self.api_config['temperature'],
            max_tokens=self.api_config['max_tokens']
        )
        
        # Create the summarization chain
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def _load_prompt_template(self) -> PromptTemplate:
        """Load the summarization prompt template from file.

        Returns:
            PromptTemplate object with the loaded template
        """
        # Get the project root directory
        project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        prompt_path = project_root / "prompts" / "summarization.txt"
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Define the input variables from the template
            input_variables = [
                "title", "source", "category", "published_date", 
                "content", "length", "num_key_points", "extract_quotes_instruction"
            ]
            
            return PromptTemplate(template=template, input_variables=input_variables)
        except Exception as e:
            logger.error(f"Error loading prompt template: {str(e)}")
            # Fallback to a basic template
            basic_template = (
                "Summarize the following article:\n\n"
                "Title: {title}\n"
                "Content: {content}\n\n"
                "Provide a {length} summary."
            )
            return PromptTemplate(template=basic_template, input_variables=["title", "content", "length"])

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
        summary_length = self.summarization_config['length']
        num_key_points = self.summarization_config['num_key_points']
        include_quotes = self.summarization_config['include_quotes']
        
        extract_quotes_instruction = (
            "Extract 2-3 notable quotes from the article."
            if include_quotes else 
            "Skip quote extraction for this article."
        )
        
        # Truncate content if it's too long to avoid token limits
        content = article['content']
        if len(content) > 12000:  # Approximate token limit
            content = content[:12000] + "..."
            logger.warning(f"Content truncated for article: {article['title']}")
        
        # Prepare the input for the LLM chain
        chain_input = {
            "title": article.get('title', 'Untitled'),
            "source": article.get('source', 'Unknown'),
            "category": article.get('category', 'general'),
            "published_date": str(article.get('published_date', '')),
            "content": content,
            "length": summary_length,
            "num_key_points": num_key_points,
            "extract_quotes_instruction": extract_quotes_instruction
        }
        
        # Run the chain to get the summary
        result = self.chain.invoke(chain_input)
        
        # Parse the JSON response
        summary_data = self._parse_summary_response(result['text'], article)
        
        # Update the article with summary data
        article.update(summary_data)
        
        return article

    def _parse_summary_response(self, response: str, article: Dict) -> Dict:
        """Parse the LLM response to extract summary, key points, and quotes.

        Args:
            response: Raw response from the LLM
            article: Original article dictionary (for fallback)

        Returns:
            Dictionary with parsed summary data
        """
        # Default values
        summary_data = {
            "summary": "",
            "key_points": [],
            "quotes": []
        }
        
        try:
            # Extract JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}')
            
            if json_start >= 0 and json_end >= 0:
                json_str = response[json_start:json_end+1]
                parsed_data = json.loads(json_str)
                
                # Update summary data with parsed values
                if "summary" in parsed_data and parsed_data["summary"]:
                    summary_data["summary"] = parsed_data["summary"]
                
                if "key_points" in parsed_data and parsed_data["key_points"]:
                    summary_data["key_points"] = parsed_data["key_points"]
                
                if "quotes" in parsed_data and parsed_data["quotes"]:
                    summary_data["quotes"] = parsed_data["quotes"]
            else:
                # If JSON parsing fails, use the whole response as summary
                logger.warning(f"Failed to parse JSON from response for article: {article.get('title', 'Unknown')}")
                summary_data["summary"] = response.strip()
        except json.JSONDecodeError:
            logger.warning(f"JSON decode error for article: {article.get('title', 'Unknown')}")
            summary_data["summary"] = response.strip()
        except Exception as e:
            logger.error(f"Error parsing summary response: {str(e)}")
            summary_data["summary"] = response.strip()
        
        # If no summary was generated, use the extracted summary or original summary
        if not summary_data["summary"]:
            summary_data["summary"] = article.get('extracted_summary', article.get('summary', ''))
        
        # If no quotes were extracted, try to use the parser's extracted quotes
        if not summary_data["quotes"] and article.get('content'):
            from .parser import ArticleParser
            parser = ArticleParser({})
            summary_data["quotes"] = parser.extract_quotes(article['content'])
        
        return summary_data

    def generate_introduction(self, articles: List[Dict]) -> str:
        """Generate an introduction for the newsletter based on the articles.

        Args:
            articles: List of summarized article dictionaries

        Returns:
            Introduction text for the newsletter
        """
        if not articles:
            return ""
        
        # Create a prompt for the introduction
        categories = set(article.get('category', 'general') for article in articles)
        titles = [article.get('title', 'Untitled') for article in articles[:5]]
        
        prompt = f"""
        Generate a brief introduction for a personalized newsletter that covers the following categories: {', '.join(categories)}.
        The newsletter includes articles with these titles: {', '.join(titles[:5])}.
        
        The introduction should be 2-3 sentences that highlight the main themes or important news of the day.
        Keep it concise, engaging, and neutral in tone.
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            logger.error(f"Error generating introduction: {str(e)}")
            return ""