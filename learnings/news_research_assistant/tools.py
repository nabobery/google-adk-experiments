import requests
import json
import logging
import os
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from newspaper import Article
import re

# Import Google ADK tools properly
from google.adk.tools import google_search
from google.adk.tools import FunctionTool, ToolContext
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

# Import LangChain Google tools for enhanced functionality
try:
    from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
    from langchain_core.messages import HumanMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain Google tools not available. Install with: pip install langchain-google-genai")

logger = logging.getLogger(__name__)

# Note: The Google Search functionality is now handled by the built-in google_search tool from ADK
# This provides official Google Search integration without custom API setup

async def enhanced_scrape_article(url: str, max_length: int = 3000, tool_context: ToolContext = None) -> Dict[str, Any]:
    """Extract and clean content from a web article URL using advanced parsing.
    
    This tool provides enhanced web scraping capabilities with better content extraction,
    metadata parsing, and fallback methods for reliable article content retrieval.
    
    Args:
        url: The URL of the article to scrape
        max_length: Maximum length of content to extract (default: 3000)
        tool_context: ADK tool context for session and state management
        
    Returns:
        A dictionary containing the article title, content, and metadata with better 
        accuracy than basic scraping. Includes authors, publish date, keywords, and images.
    """
    try:
        logger.info(f"Enhanced scraping article: {url}")
        
        # Use newspaper3k for article extraction - it's more robust than basic scraping
        article = Article(url)
        article.download()
        article.parse()
        
        # Extract and clean content
        content = article.text[:max_length] if article.text else ""
        
        # Clean up the content
        content = _clean_content(content)
        
        return {
            "success": True,
            "url": url,
            "title": article.title or "No title found",
            "content": content,
            "authors": article.authors,
            "publish_date": str(article.publish_date) if article.publish_date else None,
            "summary": article.summary[:300] if article.summary else "",
            "keywords": article.keywords[:15] if article.keywords else [],
            "top_image": article.top_image,
            "meta_keywords": article.meta_keywords[:10] if hasattr(article, 'meta_keywords') else []
        }
        
    except Exception as e:
        logger.error(f"Error scraping article {url}: {str(e)}")
        # Fallback to basic requests + BeautifulSoup
        return await _fallback_scrape(url, max_length)

async def _fallback_scrape(url: str, max_length: int) -> Dict[str, Any]:
    """Enhanced fallback scraping method using requests and BeautifulSoup"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            element.decompose()
        
        # Extract title with fallbacks
        title = _extract_title(soup)
        
        # Extract content from multiple selectors in priority order
        content = _extract_content(soup)
        
        # Extract metadata
        meta_data = _extract_metadata(soup)
        
        content = _clean_content(content)[:max_length]
        
        return {
            "success": True,
            "url": url,
            "title": title,
            "content": content,
            "authors": meta_data.get("authors", []),
            "publish_date": meta_data.get("publish_date"),
            "summary": content[:300] if content else "",
            "keywords": meta_data.get("keywords", []),
            "top_image": meta_data.get("image"),
            "meta_keywords": []
        }
        
    except Exception as e:
        logger.error(f"Enhanced fallback scraping failed for {url}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "url": url,
            "title": "",
            "content": "",
            "authors": [],
            "publish_date": None,
            "summary": "",
            "keywords": [],
            "top_image": None,
            "meta_keywords": []
        }

def _extract_title(soup: BeautifulSoup) -> str:
    """Extract title with multiple fallback strategies"""
    # Try various title selectors
    title_selectors = [
        'h1',
        '.entry-title',
        '.post-title', 
        '.article-title',
        '[data-testid="headline"]',
        'title'
    ]
    
    for selector in title_selectors:
        element = soup.select_one(selector)
        if element and element.get_text().strip():
            return element.get_text().strip()
    
    return "No title found"

def _extract_content(soup: BeautifulSoup) -> str:
    """Extract content with enhanced selectors"""
    content_selectors = [
        'article .entry-content',
        'article .post-content', 
        '.article-body',
        '.post-body',
        '.content-body',
        '[data-testid="article-body"]',
        '.story-body',
        'article',
        '.entry-content',
        '.post-content',
        'main',
        '.content'
    ]
    
    for selector in content_selectors:
        elements = soup.select(selector)
        if elements:
            content = ' '.join([elem.get_text().strip() for elem in elements])
            if len(content.split()) > 50:  # Ensure substantial content
                return content
    
    # Final fallback to paragraph tags
    paragraphs = soup.find_all('p')
    content = ' '.join([p.get_text().strip() for p in paragraphs])
    return content

def _extract_metadata(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract metadata from the page"""
    metadata = {}
    
    # Extract authors
    author_selectors = [
        '[rel="author"]',
        '.author',
        '.byline',
        '[data-testid="author"]',
        '.post-author'
    ]
    
    authors = []
    for selector in author_selectors:
        elements = soup.select(selector)
        for element in elements:
            author = element.get_text().strip()
            if author and author not in authors:
                authors.append(author)
    
    metadata["authors"] = authors[:3]  # Limit to 3 authors
    
    # Extract publish date
    date_selectors = [
        'time[datetime]',
        '.publish-date',
        '.post-date',
        '[data-testid="timestamp"]'
    ]
    
    for selector in date_selectors:
        element = soup.select_one(selector)
        if element:
            if element.get('datetime'):
                metadata["publish_date"] = element.get('datetime')
                break
            elif element.get_text().strip():
                metadata["publish_date"] = element.get_text().strip()
                break
    
    # Extract keywords from meta tags
    keywords = []
    meta_keywords = soup.find('meta', {'name': 'keywords'})
    if meta_keywords:
        keywords.extend([kw.strip() for kw in meta_keywords.get('content', '').split(',') if kw.strip()])
    
    meta_tags = soup.find_all('meta', {'property': 'article:tag'})
    for tag in meta_tags:
        if tag.get('content'):
            keywords.append(tag.get('content').strip())
    
    metadata["keywords"] = keywords[:10]
    
    # Extract featured image
    img_selectors = [
        'meta[property="og:image"]',
        'meta[name="twitter:image"]',
        '.featured-image img',
        '.post-thumbnail img'
    ]
    
    for selector in img_selectors:
        element = soup.select_one(selector)
        if element:
            if element.name == 'meta':
                metadata["image"] = element.get('content')
            else:
                metadata["image"] = element.get('src')
            break
    
    return metadata

def _clean_content(content: str) -> str:
    """Enhanced content cleaning"""
    if not content:
        return ""
    
    # Remove extra whitespace and newlines
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'\n+', '\n', content)
    
    # Remove common unwanted patterns (enhanced list)
    unwanted_patterns = [
        r'Subscribe to.*?newsletter',
        r'Follow us on.*?social media',
        r'Sign up.*?updates',
        r'Advertisement',
        r'ADVERTISEMENT',
        r'Related Articles',
        r'Read More:',
        r'Share this article',
        r'Tweet\s*Facebook\s*Email',
        r'Click here to.*?',
        r'Download our app',
        r'Enable notifications',
        r'Accept cookies',
        r'Privacy Policy',
        r'Terms of Service',
        r'Comments \(\d+\)',
        r'Share on Facebook',
        r'Share on Twitter',
        r'Copy link'
    ]
    
    for pattern in unwanted_patterns:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    # Remove common footer/header text
    footer_patterns = [
        r'Copyright \d{4}.*',
        r'©.*',
        r'All rights reserved.*'
    ]
    
    for pattern in footer_patterns:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    return content.strip()

async def advanced_analyze_content(content: str, title: str = "", analysis_type: str = "all", tool_context: ToolContext = None) -> Dict[str, Any]:
    """Perform comprehensive analysis of article content including sentiment, credibility, key points extraction, and bias detection.
    
    This tool uses advanced NLP techniques and optional AI-powered analysis to provide 
    comprehensive insights into news article content including credibility assessment,
    bias detection, sentiment analysis, and key information extraction.
    
    Args:
        content: The article content to analyze
        title: The article title for context (optional)
        analysis_type: Type of analysis - 'summary', 'sentiment', 'credibility', 'bias', or 'all' (default: 'all')
        tool_context: ADK tool context for session and state management
        
    Returns:
        A dictionary containing comprehensive analysis results including sentiment scores,
        credibility indicators, bias assessment, key points, and AI insights when available.
    """
    try:
        # Initialize AI analysis if available
        ai_analysis_available = False
        llm = None
        embeddings = None
        
        if LANGCHAIN_AVAILABLE and os.getenv("GOOGLE_API_KEY"):
            try:
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash-preview-05-20",
                    temperature=0.1
                )
                embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
                ai_analysis_available = True
            except Exception as e:
                logger.warning(f"Could not initialize AI analysis tools: {e}")
                ai_analysis_available = False
        
        analysis_result = {
            "success": True,
            "content_length": len(content),
            "word_count": len(content.split()) if content else 0,
            "title": title
        }
        
        if analysis_type in ["summary", "all"]:
            analysis_result["key_points"] = await _extract_key_points(content, title)
        
        if analysis_type in ["sentiment", "all"]:
            analysis_result["sentiment"] = await _analyze_sentiment(content)
        
        if analysis_type in ["credibility", "all"]:
            analysis_result["credibility_indicators"] = await _assess_credibility(content, title)
        
        if analysis_type in ["bias", "all"]:
            analysis_result["bias_analysis"] = await _analyze_bias(content, title)
        
        # Add AI-powered insights if available
        if ai_analysis_available and analysis_type in ["all", "ai_insights"] and llm:
            analysis_result["ai_insights"] = await _get_ai_insights(content, title, llm)
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error analyzing content: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "content_length": len(content) if content else 0
        }

async def _extract_key_points(content: str, title: str = "") -> List[str]:
    """Enhanced key point extraction using multiple strategies"""
    if not content:
        return []
    
    sentences = content.split('.')
    key_points = []
    
    # Enhanced key indicators
    key_indicators = [
        'according to', 'reported that', 'announced', 'revealed', 'discovered',
        'found that', 'concluded', 'stated that', 'research shows', 'study found',
        'data indicates', 'experts say', 'officials confirmed', 'breaking news',
        'investigation reveals', 'sources indicate', 'poll shows', 'survey results'
    ]
    
    # Look for sentences with statistical information
    stat_patterns = [
        r'\d+%', r'\d+\s*percent', r'\$\d+', r'\d+\s*million', r'\d+\s*billion',
        r'\d+\s*thousand', r'increased by \d+', r'decreased by \d+', r'rose \d+%'
    ]
    
    # Priority scoring for sentences
    sentence_scores = {}
    
    for i, sentence in enumerate(sentences[:30]):  # Analyze first 30 sentences
        sentence = sentence.strip()
        if len(sentence) < 20:  # Skip very short sentences
            continue
            
        score = 0
        
        # Score based on key indicators
        for indicator in key_indicators:
            if indicator.lower() in sentence.lower():
                score += 2
        
        # Score based on statistical information
        for pattern in stat_patterns:
            if re.search(pattern, sentence):
                score += 1
        
        # Score based on position (earlier sentences get higher score)
        if i < 5:
            score += 1
        elif i < 10:
            score += 0.5
        
        # Score based on length (moderate length preferred)
        if 50 < len(sentence) < 200:
            score += 0.5
        
        sentence_scores[sentence] = score
    
    # Select top scoring sentences
    sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
    key_points = [sentence for sentence, score in sorted_sentences[:8] if score > 0]
    
    return key_points

async def _analyze_sentiment(content: str) -> Dict[str, Any]:
    """Enhanced sentiment analysis with more sophisticated scoring"""
    if not content:
        return {"sentiment": "neutral", "confidence": 0.0}
    
    content_lower = content.lower()
    
    # Enhanced sentiment word lists
    positive_words = [
        'good', 'great', 'excellent', 'positive', 'success', 'achievement', 'breakthrough',
        'improvement', 'progress', 'beneficial', 'advantage', 'victory', 'triumph',
        'outstanding', 'remarkable', 'impressive', 'effective', 'efficient', 'innovative',
        'promising', 'encouraging', 'optimistic', 'thriving', 'flourishing'
    ]
    
    negative_words = [
        'bad', 'terrible', 'negative', 'failure', 'problem', 'issue', 'crisis',
        'decline', 'harmful', 'disadvantage', 'concern', 'worry', 'alarming',
        'devastating', 'tragic', 'catastrophic', 'disappointing', 'concerning',
        'troubling', 'disturbing', 'challenging', 'difficult', 'struggling'
    ]
    
    neutral_words = [
        'stated', 'reported', 'according', 'official', 'announced', 'confirmed',
        'data', 'statistics', 'research', 'study', 'analysis', 'findings'
    ]
    
    # Count weighted occurrences
    positive_count = sum(2 if word in content_lower else 0 for word in positive_words)
    negative_count = sum(2 if word in content_lower else 0 for word in negative_words)
    neutral_count = sum(1 if word in content_lower else 0 for word in neutral_words)
    
    total_sentiment_words = positive_count + negative_count + neutral_count
    total_words = len(content.split())
    
    # Calculate sentiment
    if total_sentiment_words == 0:
        sentiment = "neutral"
        confidence = 0.5
    else:
        positive_ratio = positive_count / total_sentiment_words
        negative_ratio = negative_count / total_sentiment_words
        
        if positive_ratio > negative_ratio + 0.1:
            sentiment = "positive"
            confidence = min(positive_ratio * 0.8 + 0.2, 0.9)
        elif negative_ratio > positive_ratio + 0.1:
            sentiment = "negative"
            confidence = min(negative_ratio * 0.8 + 0.2, 0.9)
        else:
            sentiment = "neutral"
            confidence = 0.6
    
    return {
        "sentiment": sentiment,
        "confidence": round(confidence, 2),
        "positive_indicators": positive_count,
        "negative_indicators": negative_count,
        "neutral_indicators": neutral_count,
        "sentiment_density": round(total_sentiment_words / total_words * 100, 2) if total_words > 0 else 0
    }

async def _assess_credibility(content: str, title: str = "") -> Dict[str, Any]:
    """Enhanced credibility assessment with more comprehensive indicators"""
    if not content:
        return {"credibility_score": 0.0, "indicators": []}
    
    content_lower = content.lower()
    title_lower = title.lower() if title else ""
    combined_text = f"{title_lower} {content_lower}"
    
    credibility_score = 0.5  # Start with neutral score
    indicators = []
    
    # Positive credibility indicators (weighted)
    positive_indicators = [
        ('direct_quotes', ['"', 'said', 'stated', 'commented', 'told reporters'], 0.15),
        ('official_sources', ['official', 'spokesperson', 'representative', 'ministry', 'department'], 0.2),
        ('expert_sources', ['expert', 'professor', 'researcher', 'analyst', 'scientist', 'doctor'], 0.2),
        ('data_evidence', ['data shows', 'statistics', 'percentage', 'survey found', 'poll indicates'], 0.15),
        ('specific_details', ['on monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'january', 'february'], 0.1),
        ('verification', ['confirmed', 'verified', 'authenticated', 'corroborated'], 0.1),
        ('citations', ['according to', 'source:', 'study by', 'research from', 'report by'], 0.1)
    ]
    
    for indicator_type, keywords, weight in positive_indicators:
        found_keywords = [kw for kw in keywords if kw in combined_text]
        if found_keywords:
            credibility_score += weight
            indicators.append(f"✓ {indicator_type.replace('_', ' ').title()}: {', '.join(found_keywords[:3])}")
    
    # Negative credibility indicators
    negative_indicators = [
        ('uncertainty', ['rumor', 'allegedly', 'unconfirmed', 'speculation', 'claims'], 0.2),
        ('anonymous_sources', ['anonymous source', 'unnamed source', 'insider claims'], 0.15),
        ('sensational_language', ['shocking', 'unbelievable', 'you wont believe'], 0.1),
        ('clickbait_titles', ['this will', 'you need to', 'doctors hate'], 0.1)
    ]
    
    for indicator_type, keywords, weight in negative_indicators:
        found_keywords = [kw for kw in keywords if kw in combined_text]
        if found_keywords:
            credibility_score -= weight
            indicators.append(f"⚠ {indicator_type.replace('_', ' ').title()}: {', '.join(found_keywords[:2])}")
    
    # Additional checks
    if len(content.split()) < 100:
        credibility_score -= 0.1
        indicators.append("⚠ Very short article content")
    
    if title and any(word in title_lower for word in ['breaking', 'urgent', 'alert']):
        credibility_score += 0.05
        indicators.append("✓ Breaking news indicators")
    
    credibility_score = max(0.0, min(1.0, credibility_score))
    
    return {
        "credibility_score": round(credibility_score, 2),
        "indicators": indicators,
        "assessment": _get_credibility_assessment(credibility_score),
        "recommendation": _get_credibility_recommendation(credibility_score)
    }

async def _analyze_bias(content: str, title: str = "") -> Dict[str, Any]:
    """Analyze potential bias in the content"""
    if not content:
        return {"bias_score": 0.5, "bias_indicators": []}
    
    content_lower = content.lower()
    title_lower = title.lower() if title else ""
    combined_text = f"{title_lower} {content_lower}"
    
    bias_indicators = []
    bias_score = 0.5  # Start neutral
    
    # Emotional language indicators (potential bias)
    emotional_words = [
        'outrageous', 'ridiculous', 'absurd', 'shocking', 'devastating',
        'brilliant', 'amazing', 'terrible', 'horrible', 'wonderful'
    ]
    
    emotional_count = sum(1 for word in emotional_words if word in combined_text)
    if emotional_count > 3:
        bias_score += 0.2
        bias_indicators.append(f"High emotional language usage ({emotional_count} instances)")
    
    # Political bias indicators
    political_terms = ['liberal', 'conservative', 'left-wing', 'right-wing', 'progressive', 'traditional']
    political_count = sum(1 for term in political_terms if term in combined_text)
    if political_count > 2:
        bias_indicators.append(f"Political terminology present ({political_count} instances)")
    
    # Check for balanced reporting
    balance_indicators = [
        'however', 'on the other hand', 'alternatively', 'critics argue',
        'supporters claim', 'both sides', 'different perspectives'
    ]
    
    balance_count = sum(1 for indicator in balance_indicators if indicator in combined_text)
    if balance_count > 0:
        bias_score -= 0.1
        bias_indicators.append(f"Balanced reporting indicators present ({balance_count})")
    else:
        bias_score += 0.1
        bias_indicators.append("Limited perspective balance")
    
    bias_score = max(0.0, min(1.0, bias_score))
    
    return {
        "bias_score": round(bias_score, 2),
        "bias_indicators": bias_indicators,
        "bias_assessment": _get_bias_assessment(bias_score)
    }

async def _get_ai_insights(content: str, title: str = "", llm = None) -> Dict[str, Any]:
    """Get AI-powered insights using LangChain Google"""
    if not llm:
        return {"available": False, "reason": "AI analysis not configured"}
    
    try:
        # Prepare analysis prompt
        analysis_prompt = f"""
        Please analyze the following news article for:
        1. Main themes and topics
        2. Factual claims that can be verified
        3. Overall tone and objectivity
        4. Potential areas of concern or interest
        
        Title: {title}
        Content: {content[:2000]}...
        
        Provide a concise analysis in JSON format with keys: themes, factual_claims, tone_analysis, concerns.
        """
        
        message = HumanMessage(content=analysis_prompt)
        response = llm.invoke([message])
        
        # Try to parse the response as JSON, fallback to text analysis
        try:
            import json
            ai_analysis = json.loads(response.content)
        except:
            ai_analysis = {
                "themes": ["Content analysis available"],
                "factual_claims": ["See full response"],
                "tone_analysis": "Professional analysis provided",
                "concerns": ["Review full AI response"],
                "full_response": response.content
            }
        
        return {
            "available": True,
            "analysis": ai_analysis,
            "model_used": "gemini-2.5-flash-preview-05-20"
        }
    
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        return {
            "available": False,
            "error": str(e)
        }

def _get_credibility_assessment(score: float) -> str:
    """Convert credibility score to assessment"""
    if score >= 0.8:
        return "Very High Credibility"
    elif score >= 0.65:
        return "High Credibility"
    elif score >= 0.5:
        return "Moderate Credibility"
    elif score >= 0.35:
        return "Low Credibility"
    else:
        return "Very Low Credibility"

def _get_credibility_recommendation(score: float) -> str:
    """Get recommendation based on credibility score"""
    if score >= 0.8:
        return "Highly reliable source with strong credibility indicators"
    elif score >= 0.65:
        return "Generally reliable with good credibility markers"
    elif score >= 0.5:
        return "Moderately reliable - verify claims with additional sources"
    elif score >= 0.35:
        return "Low reliability - cross-reference with multiple trusted sources"
    else:
        return "Very low reliability - treat with significant skepticism"

def _get_bias_assessment(score: float) -> str:
    """Convert bias score to assessment"""
    if score <= 0.3:
        return "Low bias - appears balanced and objective"
    elif score <= 0.5:
        return "Moderate bias - some subjective elements present"
    elif score <= 0.7:
        return "High bias - significant subjective language or perspective"
    else:
        return "Very high bias - heavily subjective or one-sided reporting"

# Create FunctionTool instances using the proper ADK pattern
enhanced_web_scraping_tool = FunctionTool(func=enhanced_scrape_article)
advanced_content_analysis_tool = FunctionTool(func=advanced_analyze_content)

google_search_agent = Agent(
    model="gemini-2.0-flash",
    name="google_search_agent",
    tools=[google_search],
    instruction="You are a helpful assistant that can search the web for information.",
    description="You are a helpful assistant that can search the web for information."
)

google_search_tool = AgentTool(
    agent=google_search_agent,
)

# Export the tools and the built-in google_search
__all__ = [
    'enhanced_web_scraping_tool',
    'advanced_content_analysis_tool',
    'enhanced_scrape_article',  # Function for direct use
    'advanced_analyze_content',  # Function for direct use
    'google_search_tool'
] 