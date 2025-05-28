#!/usr/bin/env python3
"""
Currents API MCP Server
A production-ready Model Context Protocol server for news data retrieval using Currents API.
"""

from fastmcp import FastMCP, Context
import httpx
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
import asyncio
import json
import time
from dateutil import parser as date_parser
from dotenv import load_dotenv

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("CurrentsAPI")

# Configuration
API_BASE_URL = "https://api.currentsapi.services/v1"
DEFAULT_TIMEOUT = int(os.getenv("API_TIMEOUT", "15"))
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
MAX_RESULTS = int(os.getenv("MAX_RESULTS", "20"))

# Cache for static data (5 minutes TTL)
_cache = {}
CACHE_TTL = 300  # 5 minutes

# HTTP client
http_client = None


def get_api_key() -> Optional[str]:
    """Get API key from environment variables."""
    return os.getenv("CURRENTS_API_KEY")


async def get_http_client() -> httpx.AsyncClient:
    """Get or create HTTP client with proper configuration."""
    global http_client
    if http_client is None:
        http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(DEFAULT_TIMEOUT),
            headers={"User-Agent": "CurrentsMCP/1.0"},
        )
    return http_client


def is_cache_valid(cache_key: str) -> bool:
    """Check if cached data is still valid."""
    if cache_key not in _cache:
        return False
    return time.time() - _cache[cache_key]["timestamp"] < CACHE_TTL


def get_cached_data(cache_key: str) -> Optional[Any]:
    """Get data from cache if valid."""
    if is_cache_valid(cache_key):
        return _cache[cache_key]["data"]
    return None


def set_cached_data(cache_key: str, data: Any) -> None:
    """Store data in cache with timestamp."""
    _cache[cache_key] = {"data": data, "timestamp": time.time()}


def validate_date_format(date_str: str) -> bool:
    """Validate ISO 8601 date format."""
    try:
        date_parser.parse(date_str)
        return True
    except (ValueError, TypeError):
        return False


def format_news_article(article: Dict) -> Dict:
    """Format a news article for consistent output."""
    return {
        "id": article.get("id", ""),
        "title": article.get("title", "").strip(),
        "description": article.get("description", "").strip(),
        "url": article.get("url", ""),
        "author": article.get("author", "Unknown"),
        "image": article.get("image") if article.get("image") != "None" else None,
        "language": article.get("language", ""),
        "category": article.get("category", []),
        "published": article.get("published", ""),
        "source": "Currents API",
    }


async def make_api_request(endpoint: str, params: Dict = None) -> Dict:
    """Make authenticated request to Currents API."""
    api_key = get_api_key()
    if not api_key:
        raise ValueError("CURRENTS_API_KEY environment variable is required")

    client = await get_http_client()
    url = f"{API_BASE_URL}/{endpoint}"

    # Add API key to headers
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = await client.get(url, params=params or {}, headers=headers)

        if response.status_code == 401:
            raise ValueError("Invalid API key. Please check your CURRENTS_API_KEY.")
        elif response.status_code == 429:
            raise ValueError(
                "Rate limit exceeded. Free tier allows 600 requests per hour."
            )
        elif response.status_code == 400:
            raise ValueError("Bad request. Please check your parameters.")
        elif response.status_code >= 500:
            raise ValueError("API server error. Please try again later.")

        response.raise_for_status()
        return response.json()

    except httpx.TimeoutException:
        raise ValueError(f"Request timeout after {DEFAULT_TIMEOUT} seconds")
    except httpx.RequestError as e:
        raise ValueError(f"Network error: {str(e)}")


@mcp.tool()
async def search_news(
    keywords: Optional[str] = None,
    language: Optional[str] = None,
    country: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> str:
    """
    Search for news articles with various filters.

    Args:
        keywords: Search keywords to filter articles
        language: Language code (e.g., 'en', 'fr', 'de')
        country: Country code (e.g., 'US', 'GB', 'FR')
        category: News category (e.g., 'technology', 'business', 'sports')
        start_date: Start date in ISO 8601 format (YYYY-MM-DDTHH:MM:SS+00:00)
        end_date: End date in ISO 8601 format (YYYY-MM-DDTHH:MM:SS+00:00)

    Returns:
        JSON string with search results
    """
    try:
        # Validate date formats if provided
        if start_date and not validate_date_format(start_date):
            return json.dumps(
                {
                    "status": "error",
                    "message": "Invalid start_date format. Use ISO 8601: YYYY-MM-DDTHH:MM:SS+00:00",
                }
            )

        if end_date and not validate_date_format(end_date):
            return json.dumps(
                {
                    "status": "error",
                    "message": "Invalid end_date format. Use ISO 8601: YYYY-MM-DDTHH:MM:SS+00:00",
                }
            )

        # Build parameters
        params = {}
        if keywords:
            params["keywords"] = keywords
        if language:
            params["language"] = language
        if country:
            params["country"] = country
        if category:
            params["category"] = category
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        # Make API request
        response = await make_api_request("search", params)

        if response.get("status") == "ok":
            articles = response.get("news", [])
            formatted_articles = [
                format_news_article(article) for article in articles[:MAX_RESULTS]
            ]

            return json.dumps(
                {
                    "status": "success",
                    "total_results": len(formatted_articles),
                    "articles": formatted_articles,
                    "search_params": {
                        "keywords": keywords,
                        "language": language,
                        "country": country,
                        "category": category,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                },
                indent=2,
            )
        else:
            return json.dumps(
                {"status": "error", "message": "No results found or API error occurred"}
            )

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
async def get_latest_news(language: Optional[str] = None) -> str:
    """
    Get the latest news articles in a specific language.

    Args:
        language: Language code (default: 'en')

    Returns:
        JSON string with latest news articles
    """
    try:
        lang = language or DEFAULT_LANGUAGE
        params = {"language": lang}

        response = await make_api_request("latest-news", params)

        if response.get("status") == "ok":
            articles = response.get("news", [])
            formatted_articles = [
                format_news_article(article) for article in articles[:MAX_RESULTS]
            ]

            return json.dumps(
                {
                    "status": "success",
                    "language": lang,
                    "total_results": len(formatted_articles),
                    "articles": formatted_articles,
                    "retrieved_at": datetime.now().isoformat(),
                },
                indent=2,
            )
        else:
            return json.dumps(
                {"status": "error", "message": "Failed to retrieve latest news"}
            )

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
async def get_available_languages() -> str:
    """
    Get list of supported language codes and names.

    Returns:
        JSON string with supported languages
    """
    try:
        # Check cache first
        cached_data = get_cached_data("languages")
        if cached_data:
            return json.dumps(
                {"status": "success", "source": "cache", "languages": cached_data},
                indent=2,
            )

        response = await make_api_request("available/languages")

        if response.get("status") == "ok":
            languages = response.get("languages", {})
            set_cached_data("languages", languages)

            return json.dumps(
                {
                    "status": "success",
                    "source": "api",
                    "languages": languages,
                    "total_languages": len(languages),
                },
                indent=2,
            )
        else:
            return json.dumps(
                {"status": "error", "message": "Failed to retrieve supported languages"}
            )

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
async def get_available_regions() -> str:
    """
    Get list of supported country/region codes and names.

    Returns:
        JSON string with supported regions
    """
    try:
        # Check cache first
        cached_data = get_cached_data("regions")
        if cached_data:
            return json.dumps(
                {"status": "success", "source": "cache", "regions": cached_data},
                indent=2,
            )

        response = await make_api_request("available/regions")

        if response.get("status") == "ok":
            regions = response.get("regions", {})
            set_cached_data("regions", regions)

            return json.dumps(
                {
                    "status": "success",
                    "source": "api",
                    "regions": regions,
                    "total_regions": len(regions),
                },
                indent=2,
            )
        else:
            return json.dumps(
                {"status": "error", "message": "Failed to retrieve supported regions"}
            )

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
async def get_available_categories() -> str:
    """
    Get list of supported news categories.

    Returns:
        JSON string with supported categories
    """
    try:
        # Check cache first
        cached_data = get_cached_data("categories")
        if cached_data:
            return json.dumps(
                {"status": "success", "source": "cache", "categories": cached_data},
                indent=2,
            )

        response = await make_api_request("available/category")

        if response.get("status") == "ok":
            categories = response.get("categories", [])
            set_cached_data("categories", categories)

            return json.dumps(
                {
                    "status": "success",
                    "source": "api",
                    "categories": categories,
                    "total_categories": len(categories),
                },
                indent=2,
            )
        else:
            return json.dumps(
                {
                    "status": "error",
                    "message": "Failed to retrieve supported categories",
                }
            )

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
async def check_api_status() -> str:
    """
    Check Currents API connectivity and configuration status.

    Returns:
        JSON string with API status information
    """
    try:
        api_key = get_api_key()
        if not api_key:
            return json.dumps(
                {
                    "status": "error",
                    "message": "CURRENTS_API_KEY environment variable not set",
                    "configuration": {
                        "api_key_set": False,
                        "base_url": API_BASE_URL,
                        "timeout": DEFAULT_TIMEOUT,
                        "default_language": DEFAULT_LANGUAGE,
                        "max_results": MAX_RESULTS,
                    },
                    "troubleshooting": [
                        "Set CURRENTS_API_KEY environment variable",
                        "Get free API key from https://currentsapi.services",
                        "Ensure API key has proper permissions",
                    ],
                },
                indent=2,
            )

        # Test API with a simple request
        test_response = await make_api_request("latest-news", {"language": "en"})

        if test_response.get("status") == "ok":
            return json.dumps(
                {
                    "status": "success",
                    "message": "API connection successful",
                    "configuration": {
                        "api_key_set": True,
                        "api_key_masked": (
                            f"{api_key[:8]}..." if len(api_key) > 8 else "***"
                        ),
                        "base_url": API_BASE_URL,
                        "timeout": DEFAULT_TIMEOUT,
                        "default_language": DEFAULT_LANGUAGE,
                        "max_results": MAX_RESULTS,
                    },
                    "test_result": {
                        "endpoint_tested": "latest-news",
                        "response_received": True,
                        "articles_count": len(test_response.get("news", [])),
                    },
                    "cache_status": {
                        "languages_cached": is_cache_valid("languages"),
                        "regions_cached": is_cache_valid("regions"),
                        "categories_cached": is_cache_valid("categories"),
                    },
                },
                indent=2,
            )
        else:
            return json.dumps(
                {
                    "status": "error",
                    "message": "API test failed",
                    "configuration": {
                        "api_key_set": True,
                        "api_key_masked": (
                            f"{api_key[:8]}..." if len(api_key) > 8 else "***"
                        ),
                        "base_url": API_BASE_URL,
                    },
                }
            )

    except Exception as e:
        return json.dumps(
            {
                "status": "error",
                "message": f"API status check failed: {str(e)}",
                "troubleshooting": [
                    "Check internet connection",
                    "Verify API key is correct",
                    "Check if API service is operational",
                    "Ensure no firewall blocking the connection",
                ],
            }
        )


@mcp.resource("config://news-api")
async def get_api_config() -> str:
    """
    Get Currents API configuration and setup information.

    Returns:
        Configuration details and setup instructions
    """
    return json.dumps(
        {
            "api_info": {
                "name": "Currents API",
                "version": "v1",
                "provider": "https://currentsapi.services",
                "documentation": "https://currentsapi.services/docs",
            },
            "endpoints": {
                "search": f"{API_BASE_URL}/search",
                "latest_news": f"{API_BASE_URL}/latest-news",
                "languages": f"{API_BASE_URL}/available/languages",
                "regions": f"{API_BASE_URL}/available/regions",
                "categories": f"{API_BASE_URL}/available/category",
            },
            "authentication": {
                "type": "Bearer Token",
                "header": "Authorization: Bearer {API_KEY}",
                "environment_variable": "CURRENTS_API_KEY",
            },
            "rate_limits": {
                "free_tier": "600 requests per hour",
                "paid_tiers": "Higher limits available",
            },
            "setup_instructions": [
                "1. Sign up at https://currentsapi.services",
                "2. Get your API key from the dashboard",
                "3. Set CURRENTS_API_KEY environment variable",
                "4. Test connection with check_api_status tool",
            ],
            "configuration": {
                "timeout": DEFAULT_TIMEOUT,
                "default_language": DEFAULT_LANGUAGE,
                "max_results": MAX_RESULTS,
                "cache_ttl": CACHE_TTL,
            },
        },
        indent=2,
    )


@mcp.resource("data://supported-languages")
async def get_supported_languages() -> str:
    """
    Get complete list of supported languages with ISO codes.

    Returns:
        Language reference data
    """
    return json.dumps(
        {
            "languages": {
                "Arabic": "ar",
                "Chinese": "zh",
                "Dutch": "nl",
                "English": "en",
                "Finnish": "fi",
                "French": "fr",
                "German": "de",
                "Hindi": "hi",
                "Italian": "it",
                "Japanese": "ja",
                "Korean": "ko",
                "Malay": "msa",
                "Portuguese": "pt",
                "Russian": "ru",
                "Spanish": "es",
            },
            "usage_examples": [
                "language=en for English news",
                "language=fr for French news",
                "language=zh for Chinese news",
            ],
            "notes": [
                "Language codes are ISO 639-1 standard",
                "Some languages may have limited news sources",
                "Use get_available_languages() tool for real-time data",
            ],
        },
        indent=2,
    )


@mcp.resource("data://news-categories")
async def get_news_categories() -> str:
    """
    Get available news categories with descriptions and usage examples.

    Returns:
        Category reference data
    """
    return json.dumps(
        {
            "categories": [
                {"name": "general", "description": "General news and current events"},
                {
                    "name": "technology",
                    "description": "Technology, innovation, and digital trends",
                },
                {
                    "name": "business",
                    "description": "Business news, markets, and economy",
                },
                {"name": "sports", "description": "Sports news and events"},
                {
                    "name": "entertainment",
                    "description": "Entertainment, celebrity news, and pop culture",
                },
                {"name": "health", "description": "Health, medical news, and wellness"},
                {
                    "name": "science",
                    "description": "Scientific discoveries and research",
                },
                {"name": "politics", "description": "Political news and government"},
                {
                    "name": "world",
                    "description": "International news and global events",
                },
                {"name": "regional", "description": "Regional and local news"},
                {"name": "lifestyle", "description": "Lifestyle, culture, and society"},
                {
                    "name": "programming",
                    "description": "Programming, software development",
                },
                {"name": "academia", "description": "Academic and educational news"},
                {"name": "opinion", "description": "Opinion pieces and editorials"},
                {"name": "food", "description": "Food, cooking, and culinary news"},
                {
                    "name": "finance",
                    "description": "Financial markets and investment news",
                },
                {"name": "game", "description": "Gaming news and industry updates"},
            ],
            "usage_examples": [
                "category=technology for tech news",
                "category=sports for sports updates",
                "category=business for market news",
            ],
            "filtering_tips": [
                "Combine with keywords for specific results",
                "Use with language parameter for localized content",
                "Categories are ordered by source count",
            ],
        },
        indent=2,
    )


async def cleanup():
    """Cleanup resources on shutdown."""
    global http_client
    if http_client:
        await http_client.aclose()


def main():
    """Main entry point for the server."""
    import signal
    import sys

    def signal_handler(sig, frame):
        print("\nShutting down Currents MCP server...")
        try:
            asyncio.create_task(cleanup())
        except:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Check for API key on startup
    if not get_api_key():
        print("Warning: CURRENTS_API_KEY environment variable not set")
        print("Get your free API key from https://currentsapi.services")

    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()
