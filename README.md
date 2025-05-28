# 🗞️ Currents API MCP Server

A professional, production-ready Model Context Protocol (MCP) server for news search and retrieval using the Currents API. This server provides comprehensive news data access with multi-language support, category filtering, and intelligent caching.

## 🚀 Features

-   **🌍 Multi-language Support** - 15+ languages including English, French, German, Spanish, Chinese, Arabic, and more
-   **📊 Category Filtering** - Filter by technology, business, sports, health, politics, and 12+ other categories
-   **📅 Date Range Search** - Search news within specific time periods
-   **🗺️ Geographic Filtering** - Filter news by country/region
-   **⚡ Smart Caching** - Efficient caching for static data (languages, regions, categories)
-   **🛡️ Rate Limiting Aware** - Handles API quotas gracefully (600 requests/hour for free tier)
-   **🔄 Real-time Updates** - Get the latest news as it happens
-   **📋 Comprehensive Tools** - 6 powerful tools + 3 information resources

## 📋 Quick Start

### 1. Get Your API Key

1. Visit [Currents API](https://currentsapi.services)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Free tier includes **600 requests per hour**

### 2. Installation

```bash
# Clone or download the server files
git clone <your-repo-url>
cd currents-mcp

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API key
```

### 3. Configuration

Edit your `.env` file:

```bash
# Required
CURRENTS_API_KEY=your_actual_api_key_here

# Optional (with defaults)
DEFAULT_LANGUAGE=en
API_TIMEOUT=15
MAX_RESULTS=20
```

### 4. Run the Server

```bash
python currents_server.py
```

## 🛠️ Available Tools

### 1. **search_news**

Advanced news search with multiple filters:

```json
{
    "keywords": "artificial intelligence",
    "language": "en",
    "country": "US",
    "category": "technology",
    "start_date": "2025-05-01T00:00:00+00:00",
    "end_date": "2025-05-28T23:59:59+00:00"
}
```

### 2. **get_latest_news**

Get the most recent news by language:

```json
{
    "language": "fr"
}
```

### 3. **get_available_languages**

List all supported language codes:

```json
{}
```

### 4. **get_available_regions**

Get supported country/region codes:

```json
{}
```

### 5. **get_available_categories**

List available news categories:

```json
{}
```

### 6. **check_api_status**

Test API connectivity and configuration:

```json
{}
```

## 📚 Information Resources

### 1. **config://news-api**

Complete API configuration and setup information

### 2. **data://supported-languages**

Language reference with ISO codes

### 3. **data://news-categories**

Category descriptions and usage examples

## 🌐 Supported Languages

| Language   | Code | Language | Code  |
| ---------- | ---- | -------- | ----- |
| Arabic     | `ar` | Chinese  | `zh`  |
| Dutch      | `nl` | English  | `en`  |
| Finnish    | `fi` | French   | `fr`  |
| German     | `de` | Hindi    | `hi`  |
| Italian    | `it` | Japanese | `ja`  |
| Korean     | `ko` | Malay    | `msa` |
| Portuguese | `pt` | Russian  | `ru`  |
| Spanish    | `es` |          |       |

## 📰 Available Categories

-   **general** - General news and current events
-   **technology** - Tech innovation and digital trends
-   **business** - Business news and markets
-   **sports** - Sports news and events
-   **entertainment** - Entertainment and pop culture
-   **health** - Health and medical news
-   **science** - Scientific discoveries
-   **politics** - Political news and government
-   **world** - International news
-   **regional** - Regional and local news
-   **lifestyle** - Lifestyle and culture
-   **programming** - Software development
-   **academia** - Academic and educational
-   **opinion** - Opinion pieces and editorials
-   **food** - Food and culinary news
-   **finance** - Financial markets
-   **game** - Gaming industry news

## 💡 Usage Examples

### Search Technology News

```python
await search_news(
    keywords="machine learning",
    language="en",
    category="technology"
)
```

### Get Latest French News

```python
await get_latest_news("fr")
```

### Search by Date Range

```python
await search_news(
    keywords="climate change",
    start_date="2025-05-01T00:00:00+00:00",
    end_date="2025-05-28T23:59:59+00:00"
)
```

### Filter by Country

```python
await search_news(
    keywords="election",
    country="GB",
    language="en"
)
```

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t currents-mcp .
```

### Run Container

```bash
docker run -e CURRENTS_API_KEY=your_key_here currents-mcp
```

### Docker Compose

```yaml
version: "3.8"
services:
    currents-mcp:
        build: .
        environment:
            - CURRENTS_API_KEY=your_key_here
            - DEFAULT_LANGUAGE=en
            - MAX_RESULTS=20
```

## ☁️ Smithery Deployment

1. **Create GitHub Repository**

    - Make it **PUBLIC** for easier Smithery integration
    - Upload all server files including `smithery.yaml`

2. **Connect to Smithery**

    - Link your GitHub repository
    - Configure deployment settings
    - Set API key in Smithery environment

3. **Deploy and Test**
    - Deploy the server
    - Test with Smithery's MCP tools
    - Verify all functions work correctly

## 🔧 Configuration Options

| Variable           | Default    | Description                |
| ------------------ | ---------- | -------------------------- |
| `CURRENTS_API_KEY` | _required_ | Your Currents API key      |
| `DEFAULT_LANGUAGE` | `en`       | Default language for news  |
| `API_TIMEOUT`      | `15`       | Request timeout in seconds |
| `MAX_RESULTS`      | `20`       | Max articles per request   |
| `ENABLE_CACHING`   | `true`     | Enable static data caching |

## 📊 Response Format

All tools return structured JSON responses:

```json
{
    "status": "success",
    "total_results": 15,
    "articles": [
        {
            "id": "article-uuid",
            "title": "Article Title",
            "description": "Article description...",
            "url": "https://example.com/article",
            "author": "Author Name",
            "image": "https://example.com/image.jpg",
            "language": "en",
            "category": ["technology"],
            "published": "2025-05-28T10:30:00+00:00",
            "source": "Currents API"
        }
    ],
    "retrieved_at": "2025-05-28T12:00:00"
}
```

## ⚠️ Rate Limits

-   **Free Tier**: 600 requests per hour
-   **Paid Tiers**: Higher limits available
-   Rate limit status included in error messages
-   Use caching to optimize API usage

## 🔐 Security Best Practices

-   ✅ Never commit API keys to version control
-   ✅ Use environment variables for configuration
-   ✅ Run containers as non-root user
-   ✅ Validate all input parameters
-   ✅ Handle errors gracefully
-   ✅ Mask API keys in logs

## 🧪 Testing

### Local Testing

```bash
# Test API connectivity
python -c "
import asyncio
from currents_server import check_api_status
print(asyncio.run(check_api_status()))
"

# Test search functionality
python -c "
import asyncio
from currents_server import search_news
result = asyncio.run(search_news('technology', 'en'))
print(result)
"
```

### Test with MCP Client

```python
import asyncio
from fastmcp import Client
import currents_server

async def test():
    client = Client(currents_server.mcp)
    async with client:
        # Test latest news
        result = await client.call_tool("get_latest_news", {"language": "en"})
        print("Latest News:", result[0].text)

        # Test search
        result = await client.call_tool("search_news", {
            "keywords": "technology",
            "language": "en"
        })
        print("Search Results:", result[0].text)

asyncio.run(test())
```

## 🐛 Troubleshooting

### Common Issues

**"CURRENTS_API_KEY not set"**

```bash
# Check environment variable
echo $CURRENTS_API_KEY  # Linux/Mac
echo %CURRENTS_API_KEY%  # Windows
```

**"Invalid API key"**

-   Verify key is correct in Currents dashboard
-   Check for extra spaces or characters
-   Ensure key has proper permissions

**"Rate limit exceeded"**

-   Free tier: 600 requests/hour
-   Check usage in Currents dashboard
-   Wait for quota reset or upgrade plan

**"Module not found"**

```bash
pip install fastmcp httpx python-dateutil
```

**Network/Timeout Errors**

-   Check internet connection
-   Verify firewall settings
-   Increase timeout value if needed

### Debug Mode

Set debug environment variables:

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
python currents_server.py
```

## 📖 API Documentation

-   **Currents API Docs**: https://currentsapi.services/docs
-   **Get API Key**: https://currentsapi.services/register
-   **Dashboard**: https://currentsapi.services/dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

-   **Issues**: Open a GitHub issue
-   **API Support**: Contact Currents API support
-   **Documentation**: Check the official docs

## 🎯 Roadmap

-   [ ] Webhook support for real-time updates
-   [ ] Advanced search operators
-   [ ] Sentiment analysis integration
-   [ ] Export functionality (CSV, JSON)
-   [ ] Custom RSS feed generation
-   [ ] News trend analysis

---

**Built with ❤️ for the MCP Workshop**

_Get started with professional news integration in minutes!_ 🚀
