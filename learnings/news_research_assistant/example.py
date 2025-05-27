#!/usr/bin/env python3
"""
Example usage of News Research Assistant with Google ADK
Demonstrates proper FunctionTool implementation and usage
"""

import asyncio
import logging
import os
from agent import NewsResearchAssistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def demo_comprehensive_research():
    """Demonstrate comprehensive research capabilities"""
    print("🔍 Demo: Comprehensive Research")
    print("=" * 50)
    
    # Initialize assistant with optional API key for enhanced features
    api_key = os.getenv("GOOGLE_API_KEY")
    assistant = NewsResearchAssistant(api_key=api_key)
    
    query = "renewable energy breakthroughs 2024"
    print(f"Research Query: {query}")
    
    try:
        result = await assistant.research_topic(
            query=query,
            max_articles=3,
            analysis_depth="comprehensive"
        )
        
        if result.get("success"):
            print("\n✅ Research completed successfully!")
            print("\n📊 RESEARCH REPORT:")
            print("-" * 30)
            print(result.get("research_report", "No report generated"))
            
            print("\n🔧 METHODOLOGY:")
            methodology = result.get("methodology", {})
            for key, value in methodology.items():
                print(f"  {key}: {value}")
            
            print("\n📈 METADATA:")
            metadata = result.get("metadata", {})
            for key, value in metadata.items():
                print(f"  {key}: {value}")
        else:
            print(f"❌ Research failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during research: {str(e)}")

async def demo_quick_search():
    """Demonstrate quick search functionality"""
    print("\n🚀 Demo: Quick Search")
    print("=" * 50)
    
    assistant = NewsResearchAssistant()
    query = "AI technology news today"
    print(f"Quick Search Query: {query}")
    
    try:
        result = await assistant.quick_search(query, num_articles=2)
        
        if result.get("success"):
            print("\n✅ Quick search completed!")
            print("\n📰 RESULTS:")
            print("-" * 20)
            print(result.get("quick_results", "No results"))
        else:
            print(f"❌ Search failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during search: {str(e)}")

async def demo_article_analysis():
    """Demonstrate article analysis capabilities"""
    print("\n🔬 Demo: Article Analysis")
    print("=" * 50)
    
    assistant = NewsResearchAssistant()
    
    # Sample article content for analysis
    sample_content = """
    A new breakthrough in renewable energy technology has been announced by researchers at Stanford University. 
    The innovative solar panel design achieves 35% efficiency, significantly higher than traditional panels at 20%.
    According to lead researcher Dr. Jane Smith, this technology could revolutionize clean energy adoption.
    The research, published in Nature Energy, shows promising results for commercial applications.
    Industry experts believe this could reduce solar energy costs by 40% within five years.
    However, some critics argue that manufacturing costs remain prohibitively high.
    """
    
    sample_title = "Stanford Researchers Develop 35% Efficient Solar Panels"
    
    print(f"Analyzing article: {sample_title}")
    
    try:
        result = await assistant.analyze_article(
            content=sample_content,
            title=sample_title,
            analysis_type="all"
        )
        
        if result.get("success"):
            print("\n✅ Analysis completed!")
            print("\n📋 ANALYSIS RESULTS:")
            print("-" * 25)
            print(result.get("analysis", "No analysis available"))
        else:
            print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")

async def demo_focused_insights():
    """Demonstrate focused insights generation"""
    print("\n💡 Demo: Focused Insights")
    print("=" * 50)
    
    assistant = NewsResearchAssistant()
    topic = "electric vehicle adoption"
    focus_area = "trends"
    
    print(f"Topic: {topic}")
    print(f"Focus Area: {focus_area}")
    
    try:
        result = await assistant.get_insights(topic, focus_area)
        
        if result.get("success"):
            print("\n✅ Insights generated!")
            print("\n🎯 INSIGHTS:")
            print("-" * 15)
            print(result.get("insights", "No insights available"))
        else:
            print(f"❌ Insights generation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error generating insights: {str(e)}")

async def demo_tool_functionality():
    """Demonstrate individual tool functionality"""
    print("\n🛠️ Demo: Individual Tool Usage")
    print("=" * 50)
    
    # Import the FunctionTool instances
    from tools import enhanced_web_scraping_tool, advanced_content_analysis_tool, enhanced_scrape_article, advanced_analyze_content
    
    print("Available Tools:")
    print(f"  - enhanced_web_scraping_tool: {type(enhanced_web_scraping_tool).__name__}")
    print(f"  - advanced_content_analysis_tool: {type(advanced_content_analysis_tool).__name__}")
    
    # Demonstrate direct function usage
    sample_url = "https://example.com"  # This will fail gracefully for demo
    print(f"\nTesting enhanced_scrape_article with URL: {sample_url}")
    
    try:
        scrape_result = await enhanced_scrape_article(sample_url, max_length=1000)
        print(f"Scraping result success: {scrape_result.get('success', False)}")
        if not scrape_result.get('success'):
            print(f"Expected error (demo URL): {scrape_result.get('error', 'Unknown')}")
    except Exception as e:
        print(f"Expected error for demo URL: {str(e)}")
    
    # Test analysis function
    test_content = "This is a test article about climate change and renewable energy development."
    print(f"\nTesting advanced_analyze_content with sample content...")
    
    try:
        analysis_result = await advanced_analyze_content(
            content=test_content,
            title="Test Article",
            analysis_type="sentiment"
        )
        print(f"Analysis result success: {analysis_result.get('success', False)}")
        if analysis_result.get('success'):
            print("Analysis completed successfully!")
    except Exception as e:
        print(f"Analysis error: {str(e)}")

async def main():
    """Main demo function"""
    print("🎉 News Research Assistant - Google ADK Demo")
    print("=" * 60)
    print("This demo showcases the proper Google ADK FunctionTool implementation")
    print("with built-in google_search integration and advanced analysis tools.")
    print()
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print("✅ Google API key found - Enhanced AI features available")
    else:
        print("ℹ️ No Google API key - Using basic functionality")
    print()
    
    # Run all demos
    demos = [
        demo_tool_functionality,
        demo_quick_search,
        demo_article_analysis,
        demo_focused_insights,
        demo_comprehensive_research,
    ]
    
    for i, demo in enumerate(demos, 1):
        try:
            await demo()
            if i < len(demos):
                print("\n" + "="*60)
                await asyncio.sleep(1)  # Brief pause between demos
        except Exception as e:
            print(f"❌ Demo {i} failed: {str(e)}")
            continue
    
    print("\n" + "="*60)
    print("🎯 Demo completed! The News Research Assistant is ready for use.")
    print("\n📖 Key Features Demonstrated:")
    print("  ✓ Google ADK FunctionTool implementation")
    print("  ✓ Built-in google_search integration")
    print("  ✓ Enhanced web scraping with fallbacks")
    print("  ✓ Advanced content analysis")
    print("  ✓ Multi-agent coordination")
    print("  ✓ Proper error handling")

if __name__ == "__main__":
    # Set up environment
    print("Setting up Google ADK News Research Assistant...")
    
    # Run the demo
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("  1. Ensure Google ADK is properly installed")
        print("  2. Check internet connection for Google Search")
        print("  3. Verify Gemini 2.0 Flash model access")
        print("  4. Set GOOGLE_API_KEY for enhanced features") 