"""
Newsletter Generator Module

This module handles generating newsletters in Markdown and PDF formats.
It uses templates to format the content and supports various output options.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsletterGenerator:
    """Class for generating newsletters from processed articles."""

    def __init__(self, config: Dict):
        """Initialize the newsletter generator with configuration.

        Args:
            config: Dictionary containing newsletter configuration
        """
        self.config = config
        self.newsletter_config = config['newsletter']
        self.user_config = config['user']
        
        # Load the template
        self.template = self._load_template()
        
        # Initialize template engine
        try:
            from jinja2 import Template
            self.template_engine = Template(self.template)
        except ImportError:
            logger.warning("Jinja2 not available, using simple string replacement")
            self.template_engine = None

    def _load_template(self) -> str:
        """Load the newsletter template from file.

        Returns:
            Template string
        """
        # Get the project root directory
        project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        template_path = project_root / "templates" / "newsletter.md"
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading template: {str(e)}")
            # Return a simple fallback template
            return """# {{newsletter_title}}

*Generated on: {{generation_date}}*

{% for article in articles %}
## {{article.title}}

{{article.summary}}

{% endfor %}
"""

    def generate_newsletter(self, articles: List[Dict], introduction: str = "") -> Dict[str, str]:
        """Generate a newsletter from the processed articles.

        Args:
            articles: List of processed article dictionaries
            introduction: Optional introduction text

        Returns:
            Dictionary with paths to generated files
        """
        if not articles:
            logger.warning("No articles provided for newsletter generation")
            return {}
        
        # Group articles by category if configured
        if self.newsletter_config.get('group_by_category', True):
            articles_by_category = self._group_by_category(articles)
        else:
            articles_by_category = {"Articles": articles}
        
        # Generate the newsletter content
        markdown_content = self._render_template(articles, articles_by_category, introduction)
        
        # Save the newsletter files
        output_files = self._save_newsletter(markdown_content)
        
        return output_files

    def _group_by_category(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Group articles by their category.

        Args:
            articles: List of article dictionaries

        Returns:
            Dictionary mapping categories to lists of articles
        """
        grouped = {}
        
        for article in articles:
            category = article.get('category', 'general').title()
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(article)
        
        return grouped

    def _render_template(self, articles: List[Dict], articles_by_category: Dict[str, List[Dict]], introduction: str) -> str:
        """Render the newsletter template with the article data.

        Args:
            articles: List of all articles
            articles_by_category: Dictionary of articles grouped by category
            introduction: Introduction text

        Returns:
            Rendered markdown content
        """
        # Prepare template variables
        template_vars = {
            "newsletter_title": self.newsletter_config['title'],
            "newsletter_subtitle": self.newsletter_config['subtitle'],
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "articles": articles,
            "articles_by_category": articles_by_category,
            "introduction": introduction,
            "user_interests": self.user_config['interests'],
            "include_images": self.newsletter_config.get('include_images', True),
            "include_quotes": self.newsletter_config.get('include_quotes', True),
            "include_links": self.newsletter_config.get('include_links', True)
        }
        
        # Render the template
        if self.template_engine:
            try:
                return self.template_engine.render(**template_vars)
            except Exception as e:
                logger.error(f"Error rendering template with Jinja2: {str(e)}")
                return self._simple_render(template_vars)
        else:
            return self._simple_render(template_vars)

    def _simple_render(self, template_vars: Dict) -> str:
        """Simple template rendering fallback using string replacement.

        Args:
            template_vars: Dictionary of template variables

        Returns:
            Rendered content
        """
        content = self.template
        
        # Simple replacements
        content = content.replace("{{newsletter_title}}", template_vars["newsletter_title"])
        content = content.replace("{{newsletter_subtitle}}", template_vars["newsletter_subtitle"])
        content = content.replace("{{generation_date}}", template_vars["generation_date"])
        
        # Generate articles section
        articles_content = ""
        for article in template_vars["articles"]:
            articles_content += f"## {article['title']}\n\n"
            if article.get('image_url') and template_vars["include_images"]:
                articles_content += f"![{article['title']}]({article['image_url']})\n\n"
            articles_content += f"{article.get('summary', '')}\n\n"
            if article.get('key_points'):
                articles_content += "**Key Points:**\n"
                for point in article['key_points']:
                    articles_content += f"- {point}\n"
                articles_content += "\n"
            if template_vars["include_links"]:
                articles_content += f"[Read full article]({article.get('url', '')})\n\n"
            articles_content += "---\n\n"
        
        # Replace articles placeholder
        content = content.replace("{% for article in articles %}\n## {{article.title}}\n\n{{article.summary}}\n\n{% endfor %}", articles_content)
        
        return content

    def _save_newsletter(self, markdown_content: str) -> Dict[str, str]:
        """Save the newsletter to files in the configured formats.

        Args:
            markdown_content: Rendered markdown content

        Returns:
            Dictionary with paths to generated files
        """
        output_files = {}
        
        # Get the output directory
        project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dir = project_root / self.newsletter_config['output_dir']
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with date
        date_str = datetime.now().strftime(self.newsletter_config['date_format'])
        base_filename = f"newsletter_{date_str}"
        
        # Save markdown file
        if self.newsletter_config['output_format'] in ['markdown', 'both']:
            markdown_path = output_dir / f"{base_filename}.md"
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            output_files['markdown'] = str(markdown_path)
            logger.info(f"Saved markdown newsletter to {markdown_path}")
        
        # Generate and save PDF file
        if self.newsletter_config['output_format'] in ['pdf', 'both']:
            pdf_path = output_dir / f"{base_filename}.pdf"
            try:
                self._generate_pdf(markdown_content, pdf_path)
                output_files['pdf'] = str(pdf_path)
                logger.info(f"Saved PDF newsletter to {pdf_path}")
            except Exception as e:
                logger.error(f"Error generating PDF: {str(e)}")
        
        return output_files

    def _generate_pdf(self, markdown_content: str, output_path: Path):
        """Generate a PDF file from markdown content.

        Args:
            markdown_content: Markdown content to convert
            output_path: Path to save the PDF file
        """
        try:
            # Try using fpdf2 first
            self._generate_pdf_with_fpdf(markdown_content, output_path)
        except ImportError:
            logger.warning("fpdf2 not available, trying alternative PDF generation")
            try:
                # Try using markdown2pdf if available
                self._generate_pdf_with_markdown2pdf(markdown_content, output_path)
            except ImportError:
                logger.error("No PDF generation library available. Install fpdf2 or markdown2pdf.")
                raise

    def _generate_pdf_with_fpdf(self, markdown_content: str, output_path: Path):
        """Generate PDF using fpdf2 library.

        Args:
            markdown_content: Markdown content to convert
            output_path: Path to save the PDF file
        """
        try:
            from fpdf import FPDF, HTMLMixin
            import markdown2
            
            # Convert markdown to HTML
            html_content = markdown2.markdown(
                markdown_content,
                extras=["tables", "code-friendly", "cuddled-lists", "fenced-code-blocks"]
            )
            
            # Create PDF with HTML support
            class PDF(FPDF, HTMLMixin):
                def __init__(self):
                    super().__init__()
                    self.title = ""
                    
                def header(self):
                    if hasattr(self, 'title') and self.title:
                        self.set_font('Arial', 'B', 12)
                        title_safe = str(self.title)[:50]  # Limit title length
                        self.cell(0, 10, title_safe, 0, 1, 'C')
                        self.ln(10)
                    
                def footer(self):
                    self.set_y(-15)
                    self.set_font('Arial', 'I', 8)
                    self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
            
            pdf = PDF()
            pdf.add_page()
            
            # Set title safely
            newsletter_title = self.newsletter_config.get('title', 'Newsletter')
            if newsletter_title:
                pdf.title = str(newsletter_title)
                
            pdf.set_font("Arial", size=12)
            
            # Clean HTML content for PDF
            if html_content:
                # Simple cleaning to handle encoding issues
                html_content = html_content.replace('\u2019', "'").replace('\u2018', "'")
                html_content = html_content.replace('\u201c', '"').replace('\u201d', '"')
                html_content = html_content.replace('\u2013', '-').replace('\u2014', '-')
                pdf.write_html(html_content)
            
            pdf.output(str(output_path))
            
        except Exception as e:
            logger.error(f"Error generating PDF with fpdf2: {str(e)}")
            raise

    def _generate_pdf_with_markdown2pdf(self, markdown_content: str, output_path: Path):
        """Generate PDF using markdown2pdf library.

        Args:
            markdown_content: Markdown content to convert
            output_path: Path to save the PDF file
        """
        try:
            import markdown2pdf
            
            markdown2pdf.convert(markdown_content, str(output_path))
            
        except Exception as e:
            logger.error(f"Error generating PDF with markdown2pdf: {str(e)}")
            raise