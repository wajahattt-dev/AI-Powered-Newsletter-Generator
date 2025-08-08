# 🌟 AI-Powered Newsletter Generator

A **luxurious**, professional-grade AI newsletter generator that creates personalized newsletters from trending news articles. Features a stunning glass morphism web interface, advanced AI summarization, and seamless PDF generation with preview capabilities.

## ✨ Key Features

### 🎨 **Luxurious Web Interface**
- **Glass Morphism Design**: Stunning translucent effects with backdrop blur
- **Dual Theme Support**: Beautiful dark and light modes with smooth transitions
- **Enhanced User Experience**: Centered, enlarged navigation tabs with premium styling
- **Professional Animations**: Smooth hover effects and gradient backgrounds
- **High Contrast Inputs**: Optimized text input fields for maximum readability

### 🤖 **AI-Powered Content Generation**
- **Intelligent Summarization**: Advanced OpenAI GPT models via LangChain
- **Personalized Content**: Smart filtering based on user interests and preferences
- **Multiple Content Sources**: Fetches from configurable RSS feeds and web articles
- **Full Content Extraction**: Complete article parsing with newspaper3k

### 📄 **Advanced PDF Features**
- **Dual PDF Functionality**: Both download and in-browser preview
- **Professional Layout**: Clean, readable PDF formatting with proper typography
- **Unicode Support**: Handles international characters and special symbols
- **Error-Free Generation**: Robust PDF creation with comprehensive error handling

### 🔧 **Professional Development**
- **Modular Architecture**: Clean, maintainable code structure
- **Configuration Management**: Easy customization through YAML settings
- **Comprehensive Logging**: Detailed application logs for debugging
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/wajahattt-dev/AI-Powered-Newsletter-Generator.git
cd AI-Powered-Newsletter-Generator
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure your OpenAI API key**
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-api-key-here"

# Linux/macOS
export OPENAI_API_KEY="your-api-key-here"
```

4. **Launch the application**
```bash
# Quick start with batch file (Windows)
start_web_ui.bat

# Or manually
streamlit run src/web_app.py --server.port 8504
```

## 🎯 Usage

### Web Interface
1. Open your browser to `http://localhost:8504`
2. Enter your interests in the intuitive input field
3. Specify your preferred newsletter title
4. Click "Generate Newsletter" and watch the AI work its magic
5. **Preview** your newsletter in the browser or **download** as PDF

### Command Line
```bash
python -m src.main
```

## 📁 Project Architecture

```
AI-Powered-Newsletter-Generator/
├── 🎨 src/
│   ├── web_app.py         # Luxurious Streamlit interface (2,254 lines)
│   ├── fetcher.py         # RSS feed and article fetching
│   ├── parser.py          # Intelligent content extraction
│   ├── summarizer.py      # AI-powered summarization engine
│   ├── generator.py       # Multi-format newsletter generation
│   ├── user_profile.py    # User preference management
│   ├── cli.py             # Command-line interface
│   └── main.py            # Core application pipeline
├── ⚙️ config/
│   └── config.yaml        # Application configuration
├── 📝 templates/
│   └── newsletter.md      # Newsletter template
├── 🧠 prompts/
│   └── summarization.txt  # AI prompt engineering
├── 📊 data/
│   ├── output/            # Generated newsletters
│   └── user_profiles/     # User preferences
├── 🔧 requirements.txt    # Python dependencies
├── 🚀 start_web_ui.bat    # Enhanced startup script
└── 📖 README.md           # This documentation
```

## ⚙️ Configuration

Customize your newsletter generator by editing `config/config.yaml`:

```yaml
# RSS Feed Sources
rss_feeds:
  - "https://feeds.bbci.co.uk/news/world/rss.xml"
  - "https://rss.cnn.com/rss/edition.rss"
  - "https://feeds.reuters.com/reuters/topNews"

# User Preferences
user_interests:
  - "artificial intelligence"
  - "technology"
  - "business"

# Generation Settings
newsletter:
  max_articles: 10
  summary_length: "medium"
  output_formats: ["markdown", "pdf"]
```

## 🎨 UI Features

### Glass Morphism Design
- **Translucent Effects**: Beautiful backdrop blur with rgba transparency
- **Gradient Backgrounds**: Stunning color transitions and hover effects
- **Responsive Layout**: Adapts seamlessly to different screen sizes
- **Professional Typography**: Enhanced fonts and spacing for premium feel

### Enhanced User Experience
- **Intuitive Navigation**: Centered, enlarged tabs with clear icons
- **High Contrast Inputs**: Optimized text fields for both light and dark modes
- **Smooth Animations**: Elegant transitions and hover effects
- **Real-time Feedback**: Progress indicators and status messages

## 🛠️ Technical Stack

### Core Dependencies
```bash
streamlit>=1.28.0          # Web interface framework
openai>=1.0.0              # GPT model integration
langchain>=0.0.350         # LLM orchestration
feedparser>=6.0.10         # RSS feed parsing
newspaper3k>=0.2.8         # Article content extraction
fpdf2>=2.7.6               # PDF generation
markdown2>=2.4.10          # Markdown processing
PyYAML>=6.0.1              # Configuration management
requests>=2.31.0           # HTTP requests
beautifulsoup4>=4.12.2     # HTML parsing
```

### Optional Enhancements
- **FAISS**: Vector similarity search for content matching
- **sentence-transformers**: Semantic content analysis
- **APScheduler**: Automated newsletter scheduling
- **Typer**: Enhanced CLI interface

## 🔍 Advanced Features

### AI Summarization Engine
- **Context-Aware**: Understands article context and user preferences
- **Customizable Prompts**: Tailor summarization style and length
- **Multi-Model Support**: Compatible with various OpenAI models
- **Error Handling**: Robust failure recovery and retry mechanisms

### PDF Generation
- **Professional Formatting**: Clean layout with proper typography
- **Unicode Support**: Handles international characters flawlessly
- **Embedded Preview**: View PDFs directly in the browser
- **Download Options**: Save locally or preview online

### Content Intelligence
- **Interest Matching**: Smart filtering based on user preferences
- **Duplicate Detection**: Avoids redundant content
- **Quality Scoring**: Prioritizes high-quality articles
- **Source Diversity**: Ensures varied content sources

## 🚀 Quick Commands

```bash
# Start web interface
streamlit run src/web_app.py --server.port 8504

# Generate newsletter via CLI
python -m src.main

# Install additional packages
pip install fpdf2 markdown2

# View logs
cat newsletter_generator_*.log
```

## 🎯 Use Cases

- **Personal Newsletter**: Stay updated with your interests
- **Business Intelligence**: Track industry trends and news
- **Research Assistant**: Automated content curation
- **Educational Tool**: Learn about AI and web development
- **Portfolio Project**: Showcase full-stack development skills

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- **OpenAI** for powerful language models
- **Streamlit** for the amazing web framework
- **LangChain** for LLM orchestration
- **Contributors** who made this project better

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/wajahattt-dev/AI-Powered-Newsletter-Generator/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/wajahattt-dev/AI-Powered-Newsletter-Generator/discussions)
- 📧 **Contact**: Open an issue for support

---

***Made by Wajahat Hussain*** | *Transform your news consumption with intelligent automation*