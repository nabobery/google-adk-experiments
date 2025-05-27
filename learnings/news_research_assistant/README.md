# News Research Assistant - Google ADK Implementation

A comprehensive news research and analysis system built with **Google Agent Development Kit (ADK)** featuring proper **FunctionTool** implementations, official Google Search integration, and advanced content analysis capabilities.

## 🚀 Key Features

### Official Google ADK Integration

- **Built-in Google Search**: Uses `google_search` tool (requires Gemini 2.0 Flash model)
- **FunctionTool Implementation**: Properly implemented custom tools following ADK best practices
- **LlmAgent Architecture**: Modern ADK agent architecture with proper tool integration
- **ToolContext Support**: Full ADK tool context for session and state management

### Advanced Analysis Capabilities

- **Enhanced Web Scraping**: Multi-fallback content extraction with metadata parsing
- **Advanced Content Analysis**: Comprehensive analysis including:
  - Sentiment analysis with confidence scoring
  - Credibility assessment with weighted indicators
  - Bias detection and linguistic pattern analysis
  - Key points extraction with intelligent scoring
  - Statistical fact extraction
- **AI-Powered Insights**: Optional LangChain Google integration for deeper analysis

### Multi-Agent Architecture

- **NewsSearchAgent**: Specialized for finding and extracting news content
- **ContentSummarizerAgent**: Advanced analysis and summarization
- **NewsResearchCoordinator**: Main orchestrating agent for comprehensive research

## 🏗️ Architecture

```bash
NewsResearchAssistant (Main Coordinator)
├── NewsSearchAgent
│   ├── google_search (Built-in ADK tool)
│   └── enhanced_web_scraping_tool (Custom FunctionTool)
├── ContentSummarizerAgent
│   └── advanced_content_analysis_tool (Custom FunctionTool)
└── NewsResearchCoordinator (LlmAgent)
```

## 📦 Installation

### Prerequisites

- Python 3.8+
- Google ADK installed
- Gemini 2.0 Flash model access (required for `google_search`)

### Required Dependencies

```bash
pip install -r requirements.txt
```

### Requirements.txt

```txt
google-adk>=0.4.0
requests>=2.28.0
beautifulsoup4>=4.11.0
newspaper3k>=0.2.8
langchain-google-genai>=2.0.0  # Optional for AI insights
langchain-core>=0.3.0          # Optional for AI insights
```

### Optional Setup

For enhanced AI analysis capabilities:

```bash
export GOOGLE_API_KEY="your-google-api-key"
```

## 🔧 Usage

### Basic Usage

```python
import asyncio
from agent import NewsResearchAssistant

async def main():
    # Initialize the assistant
    assistant = NewsResearchAssistant(api_key="optional-google-api-key")

    # Perform comprehensive research
    result = await assistant.research_topic(
        query="climate change latest developments",
        max_articles=5,
        analysis_depth="comprehensive"
    )

    if result.get("success"):
        print("Research Report:")
        print(result["research_report"])
        print(f"\nMethodology: {result['methodology']}")
    else:
        print(f"Error: {result.get('error')}")

asyncio.run(main())
```

### Quick Search

```python
# Quick search without detailed analysis
quick_result = await assistant.quick_search(
    query="AI news today",
    num_articles=3
)
print(quick_result["quick_results"])
```

### Article Analysis

```python
# Analyze specific content
analysis = await assistant.analyze_article(
    content="Article content here...",
    title="Article Title",
    analysis_type="all"  # or "sentiment", "credibility", "bias"
)
print(analysis["analysis"])
```

### Focused Insights

```python
# Generate focused insights
insights = await assistant.get_insights(
    topic="renewable energy",
    focus_area="trends"  # or "credibility", "bias", "general"
)
print(insights["insights"])
```

## 🛠️ ADK Tools Implementation

### Custom FunctionTool Creation

The implementation follows Google ADK best practices for FunctionTool creation:

```python
from google.adk.tools import FunctionTool, ToolContext

async def enhanced_scrape_article(url: str, max_length: int = 3000, tool_context: ToolContext = None) -> Dict[str, Any]:
    """Enhanced web scraping with proper ADK tool signature"""
    # Implementation with ToolContext support
    pass

# Create FunctionTool instance
enhanced_web_scraping_tool = FunctionTool(func=enhanced_scrape_article)
```

### Tool Integration

```python
from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from tools import enhanced_web_scraping_tool

agent = LlmAgent(
    name="NewsSearchAgent",
    model="gemini-2.0-flash",  # Required for google_search
    instruction="Your instructions here...",
    tools=[google_search, enhanced_web_scraping_tool]
)
```

## 📊 Response Format

### Research Report Response

```python
{
    "success": True,
    "query": "search query",
    "research_report": "Comprehensive research report...",
    "search_results": {
        "success": True,
        "articles_found": "Article content and metadata..."
    },
    "analysis_results": {
        "success": True,
        "summary": "Detailed analysis..."
    },
    "methodology": {
        "search_agent": "NewsSearchAgent with Google ADK Search",
        "analysis_agent": "ContentSummarizerAgent with Advanced Analysis",
        "coordination": "NewsResearchCoordinator",
        "articles_analyzed": 5,
        "analysis_depth": "comprehensive"
    },
    "metadata": {
        "total_agents_used": 3,
        "primary_tools": ["google_search", "enhanced_web_scraping", "advanced_content_analysis"],
        "model_used": "gemini-2.0-flash"
    }
}
```

### Article Analysis Response

```python
{
    "success": True,
    "title": "Article Title",
    "analysis": "Detailed analysis including sentiment, credibility, bias assessment...",
    "analysis_type": "all",
    "agent_used": "ContentSummarizerAgent with Advanced Analysis"
}
```

## 🔍 Advanced Features

### Enhanced Web Scraping

- **Multiple Fallback Methods**: newspaper3k → BeautifulSoup → basic requests
- **Metadata Extraction**: Authors, publish dates, keywords, images
- **Content Cleaning**: Advanced pattern-based cleaning and normalization
- **Error Handling**: Graceful degradation with informative error messages

### Comprehensive Content Analysis

- **Sentiment Analysis**: Multi-dimensional sentiment with confidence scoring
- **Credibility Assessment**:
  - Source verification indicators
  - Statistical evidence presence
  - Expert source identification
  - Citation and verification markers
- **Bias Detection**:
  - Emotional language analysis
  - Political terminology detection
  - Balance and perspective indicators
  - Objectivity scoring

### AI-Powered Insights (Optional)

- **LangChain Google Integration**: Enhanced analysis using Gemini models
- **Advanced Theme Extraction**: AI-powered topic and theme identification
- **Cross-Reference Analysis**: Intelligent fact and claim verification
- **Contextual Understanding**: Deep semantic analysis of content

## ⚙️ Configuration

### Environment Variables

```bash
# Optional for enhanced AI analysis
export GOOGLE_API_KEY="your-google-api-key"

# For debugging
export GOOGLE_ADK_DEBUG="true"
```

### Agent Configuration

```python
assistant = NewsResearchAssistant(
    api_key="optional-google-api-key"  # For enhanced AI features
)
```

## 📚 API Reference

### NewsResearchAssistant

#### Methods

- `research_topic(query, max_articles=5, analysis_depth="comprehensive")`: Comprehensive research
- `quick_search(query, num_articles=3)`: Fast search without detailed analysis
- `analyze_article(content, title="", analysis_type="all")`: Analyze specific content
- `get_insights(topic, focus_area="trends")`: Generate focused insights

### Tool Functions

- `enhanced_scrape_article(url, max_length=3000, tool_context=None)`: Advanced web scraping
- `advanced_analyze_content(content, title="", analysis_type="all", tool_context=None)`: Comprehensive analysis

## 🚨 Limitations and Considerations

### Google Search Tool Requirements

- **Gemini 2.0 Flash Model**: Required for `google_search` tool functionality
- **Tool Restrictions**: Cannot combine built-in tools with certain custom configurations
- **Rate Limiting**: Google Search may have usage limitations

### Content Analysis Limitations

- **Language Support**: Optimized for English content
- **Context Dependency**: Analysis quality depends on content length and quality
- **Bias Detection**: Pattern-based detection may not catch all subtle biases

### Performance Considerations

- **API Dependencies**: Requires stable internet connection for Google services
- **Processing Time**: Comprehensive analysis may take 30-60 seconds per request
- **Memory Usage**: Large content analysis may require significant memory

## 🔄 Migration from Custom Implementation

### Key Changes Made

1. **Tool Architecture**: Migrated from `BaseTool` inheritance to `FunctionTool` creation
2. **Agent Structure**: Updated to use `LlmAgent` instead of custom `Agent` classes
3. **Search Integration**: Replaced custom search with official `google_search` tool
4. **Model Requirements**: Updated to Gemini 2.0 Flash for tool compatibility

### Migration Example

**Before (Custom Implementation):**

```python
class CustomSearchTool(BaseTool):
    def __init__(self):
        super().__init__(name="search", description="...", parameters={})

    async def execute(self, query: str):
        # Custom implementation
        pass
```

**After (ADK FunctionTool):**

```python
async def enhanced_search(query: str, tool_context: ToolContext = None) -> Dict[str, Any]:
    """Proper ADK function tool implementation"""
    # Implementation using ToolContext
    pass

search_tool = FunctionTool(func=enhanced_search)
```

## 🚀 Future Enhancements

### Planned Features

- **Multi-language Support**: Extended analysis for non-English content
- **Visual Content Analysis**: Image and video content analysis capabilities
- **Real-time Monitoring**: Continuous topic monitoring and alerts
- **Advanced Fact-checking**: Integration with professional fact-checking APIs
- **Custom Model Support**: Support for different AI models beyond Gemini

### Integration Opportunities

- **Google Cloud Tools**: Integration with additional Google Cloud ADK tools
- **Third-party APIs**: Enhanced with specialized news and analysis APIs
- **Database Integration**: Persistent storage for research history and insights

## 📞 Support

For issues related to:

- **Google ADK**: [Google ADK Documentation](https://google.github.io/adk-docs/)
- **Tool Implementation**: Check the ADK Function Tools guide
- **Model Compatibility**: Ensure Gemini 2.0 Flash model access

## 🤝 Contributing

Contributions welcome! Please follow Google ADK best practices and ensure compatibility with the official tool implementations.

---

**Built with Google Agent Development Kit (ADK)** - Leveraging official Google tools and best practices for reliable, scalable news research and analysis.
