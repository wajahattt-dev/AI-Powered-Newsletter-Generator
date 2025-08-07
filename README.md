# Auto-Newsletter Generator

A professional-grade Python application that automatically generates personalized newsletters from trending news articles. This project demonstrates advanced AI integration for content summarization and personalization.

## Features

- **Automated Content Collection**: Fetches articles from multiple RSS feeds
- **Full Content Extraction**: Parses complete article content from web pages
- **AI-Powered Summarization**: Uses OpenAI GPT models via LangChain for intelligent summarization
- **Personalization**: Filters content based on user interests and preferences
- **Multi-format Output**: Generates newsletters in both Markdown and PDF formats
- **Configurable**: Easily customizable through YAML configuration

## Project Structure

```
auto_newsletter/
├── src/
│   ├── fetcher.py         # RSS feed article fetching
│   ├── parser.py          # Article content extraction
│   ├── summarizer.py      # AI-powered content summarization
│   ├── generator.py       # Newsletter generation (MD/PDF)
│   ├── user_profile.py    # User interest management
│   └── main.py            # Main application pipeline
├── config/
│   └── config.yaml        # Configuration settings
├── templates/
│   └── newsletter.md      # Newsletter template
├── prompts/
│   └── summarization.txt  # LLM prompt templates
├── data/
│   ├── output/            # Generated newsletters
│   └── user_profiles/     # User preference data
├── requirements.txt       # Project dependencies
└── README.md             # Project documentation
```

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Configuration

Edit `config/config.yaml` to customize:

- RSS feed sources
- User interests and preferences
- Output format settings
- Summarization parameters
- Newsletter generation options

## Usage

Run the main application:

```bash
python -m src.main
```

This will:
1. Fetch articles from configured RSS feeds
2. Extract full content from each article
3. Generate AI-powered summaries
4. Filter based on user interests
5. Create a personalized newsletter in Markdown and PDF formats

## Dependencies

- Python 3.11+
- feedparser: RSS feed parsing
- newspaper3k: Article extraction
- langchain: LLM integration framework
- openai: GPT model access
- fpdf2: PDF generation
- PyYAML: Configuration management
- markdown2: Markdown processing

## Optional Extensions

- FAISS/sentence-transformers: Enhanced content matching
- APScheduler: Automated scheduling
- Streamlit/Typer: Interactive interface

## License

MIT