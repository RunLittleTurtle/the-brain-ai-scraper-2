# Web Scraping & Automation Tools

## this is a giant list of python scraping tools

https://github.com/lorien/awesome-web-scraping/blob/master/python.md

## Other

Another way of scraping for the pipeline builder is to find a tool that can use the backend api of the ecommecre site per exemple : https://www.youtube.com/watch?v=ji8F8ppY8bs

## Browser Automation

### 1. Playwright (Python)  
**Overview:** Automates Chromium, Firefox and WebKit through a unified API  
**Paid/Free:** Free  
**Popularity:** ~13 000 GitHub stars  
**Open Source:** Yes  
**Mode:** Async / Sync  
**FastAPI Integration:** Supported  
**Notes:** Native async and sync calls; very smooth.

### 2. Selenium  
**Overview:** Implements the W3C WebDriver interface for all major browsers  
**Paid/Free:** Free  
**Popularity:** ~32 200 GitHub stars  
**Open Source:** Yes  
**Mode:** Sync  
**FastAPI Integration:** Via `run_in_threadpool(...)`  
**Notes:** Blocking by default.

### 3. Puppeteer  
**Overview:** Unofficial Python port of Puppeteer for headless Chromium  
**Paid/Free:** Free  
**Popularity:** ~3 837 GitHub stars  
**Open Source:** Yes  
**Mode:** Async  
**FastAPI Integration:** Can be used in `async def` endpoints  
**Notes:** Native async support.

### 4. Helium  
**Overview:** High-level API that simplifies Selenium usage  
**Paid/Free:** Free  
**Popularity:** ~7 700 GitHub stars  
**Open Source:** Yes  
**Mode:** Sync  
**FastAPI Integration:** Via threadpool  
**Notes:** Wrapper around Selenium.

## Crawling Frameworks

### 5. Scrapy  
**Overview:** High-performance asynchronous framework built on Twisted  
**Paid/Free:** Free  
**Popularity:** ~55 000 GitHub stars  
**Open Source:** Yes  
**Mode:** Async  
**FastAPI Integration:** Via subprocess or Scrapyd  
**Notes:** Best run as a separate service.

### 6. Crawlee  
**Overview:** Unified crawling/scraping toolkit from Apify with sessions, retries and proxy rotation  
**Paid/Free:** Free  
**Popularity:** ~5 600 GitHub stars  
**Open Source:** Yes  
**Mode:** Async  
**FastAPI Integration:** Via Apify REST API  
**Notes:** Integrates through service calls.

### 7. Pyspider  
**Overview:** Distributed spider with built-in UI, scheduling and monitoring (Tornado)  
**Paid/Free:** Free  
**Popularity:** ~16 600 GitHub stars  
**Open Source:** Yes  
**Mode:** Async  
**FastAPI Integration:** Embed Tornado or run as subprocess  
**Notes:** Includes its own UI and scheduler.

## Anti-blocking & Anti-bot

### 8. cloudscraper  
**Overview:** Bypasses Cloudflare, Distil, DataDome, etc.  
**Paid/Free:** Free  
**Popularity:** ~4 800 GitHub stars  
**Open Source:** Yes  
**Mode:** Sync  
**FastAPI Integration:** Via threadpool  
**Notes:** Wrapper around Requests.

### 9. cfscrape  
**Overview:** Cloudflare bypass tool for Node.js and Python  
**Paid/Free:** Free  
**Popularity:** ~3 500 GitHub stars  
**Open Source:** Yes  
**Mode:** Sync  
**FastAPI Integration:** Via threadpool  
**Notes:** API similar to cloudscraper.

## Proxy & Anti-bot Services

### 10. ScraperAPI  
**Overview:** Rotating proxy API with anti-bot and JS rendering  
**Paid/Free:** Paid (free trial available)  
**Popularity:** Used by 10 000+ companies  
**Open Source:** No  
**Mode:** REST  
**FastAPI Integration:** Python SDK or httpx/requests  
**Notes:** Turn-key service.

### 11. ZenRows  
**Overview:** Anti-bot bypass API with proxy rotation and headless rendering  
**Paid/Free:** Paid  
**Popularity:** ~12 GitHub stars  
**Open Source:** Yes  
**Mode:** REST  
**FastAPI Integration:** Via requests or httpx  
**Notes:** Lightweight Python SDK.

### 12. ProxyCrawl  
**Overview:** Python wrapper for the ProxyCrawl API (anonymization, bypass)  
**Paid/Free:** Paid  
**Popularity:** Popular community wrapper  
**Open Source:** Yes  
**Mode:** Sync / Async  
**FastAPI Integration:** Supports requests, aiohttp, Scrapy  
**Notes:** Multi-client support.

## CAPTCHA Solving

### 13. python-anticaptcha  
**Overview:** Python client for the AntiCaptcha.com API  
**Paid/Free:** Free (API key paid)  
**Popularity:** ~224 GitHub stars  
**Open Source:** Yes  
**Mode:** Sync  
**FastAPI Integration:** Via threadpool  
**Notes:** Community-maintained client.

### 14. anticaptchaofficial  
**Overview:** Official library for anti-captcha.com  
**Paid/Free:** Free (API key paid)  
**Popularity:** ~30 GitHub stars  
**Open Source:** Yes  
**Mode:** Sync  
**FastAPI Integration:** Via threadpool  
**Notes:** Official SDK.

## Stealth & Human Behavior

### 15. undetected-chromedriver  
**Overview:** Patched Chromedriver to evade anti-bot protections  
**Paid/Free:** Free  
**Popularity:** ~11 000 GitHub stars  
**Open Source:** Yes  
**Mode:** Sync  
**FastAPI Integration:** Via threadpool  
**Notes:** Bypasses most WAFs.

### 16. selenium-stealth  
**Overview:** Plugin for Selenium to simulate more human-like browsing  
**Paid/Free:** Free  
**Popularity:** ~696 GitHub stars  
**Open Source:** Yes  
**Mode:** Sync  
**FastAPI Integration:** Via threadpool  
**Notes:** Complementary to Selenium.

## Connection & Session Management

### 17. MechanicalSoup  
**Overview:** Automates form submissions and cookie handling without JS  
**Paid/Free:** Free  
**Popularity:** ~4 700 GitHub stars  
**Open Source:** Yes  
**Mode:** Sync  
**FastAPI Integration:** Direct calls  
**Notes:** Ideal for simple, non-JS forms.

### 18. RoboBrowser  
**Overview:** Lightweight headless browser using Requests + BeautifulSoup  
**Paid/Free:** Free  
**Popularity:** ~3 700 GitHub stars  
**Open Source:** Yes  
**Mode:** Sync  
**FastAPI Integration:** Direct calls  
**Notes:** Simple and minimal dependencies.

## HTTP Clients

### 19. Requests  
**Overview:** Elegant and powerful HTTP client for Python  
**Paid/Free:** Free  
**Popularity:** ~52 800 GitHub stars  
**Open Source:** Yes  
**Mode:** Sync  
**FastAPI Integration:** Via threadpool  
**Notes:** Industry standard.

### 20. HTTPX  
**Overview:** HTTP/1.1 & HTTP/2 client with sync & async support, Requests-compatible API  
**Paid/Free:** Free  
**Popularity:** ~14 000 GitHub stars  
**Open Source:** Yes  
**Mode:** Sync / Async  
**FastAPI Integration:** Native async support  
**Notes:** Recommended for FastAPI.

## Parsing Libraries

### 21. BeautifulSoup4  
**Overview:** Parses HTML/XML with various parsers (lxml, html.parser, etc.)  
**Paid/Free:** Free  
**Popularity:** N/A  
**Open Source:** Yes  
**Mode:** Sync  
**FastAPI Integration:** Direct calls  
**Notes:** Essential for DOM parsing.

### 22. Parsel  
**Overview:** Unified CSS, XPath and JSON selectors (used by Scrapy)  
**Paid/Free:** Free  
**Popularity:** ~1 200 GitHub stars  
**Open Source:** Yes  
**Mode:** Sync  
**FastAPI Integration:** Direct calls  
**Notes:** Provides unified selector syntax.

## Scraping APIs

### 23. ScrapingBee  
**Overview:** Headless browser API with proxy rotation and anti-bot  
**Paid/Free:** Paid  
**Popularity:** ~27 GitHub stars  
**Open Source:** Yes  
**Mode:** REST  
**FastAPI Integration:** Python SDK or httpx async  
**Notes:** Built-in JS & proxy management.

### 24. Zyte API  
**Overview:** Python client (sync/async) for Zyte Cloud services (Scrapy Cloud, Smart Proxy)  
**Paid/Free:** Paid  
**Popularity:** ~24 GitHub stars  
**Open Source:** Yes  
**Mode:** Sync / Async  
**FastAPI Integration:** AsyncZyteAPI or sync ZyteAPI  
**Notes:** CLI tools and Scrapy integration.