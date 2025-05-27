import datetime
from urllib.parse import quote_plus

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

import config

class DuckDuckGoScraper:
    """DuckDuckGo search results scraper using Playwright."""

    def __init__(self):
        self.scrape_time = datetime.datetime.now().isoformat()

    def _get_stealth_script(self) -> str:
        """Return JavaScript code to make browser appear more human-like."""
        return """
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Hide automation
            window.chrome = {
                runtime: {},
            };
        """

    def _get_http_headers(self) -> dict:
        """Return realistic HTTP headers."""
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,th;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': config.USER_AGENT
        }

    def _setup_browser(self, playwright, headless: bool):
        """Setup and configure browser with stealth settings."""
        browser = playwright.chromium.launch(headless=headless, args=config.BROWSER_ARGS)
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=config.USER_AGENT,
            locale='en-US',
            timezone_id='America/New_York',
            java_script_enabled=True,
            accept_downloads=False,
            ignore_https_errors=True
        )
        
        page = context.new_page()
        page.add_init_script(self._get_stealth_script())
        page.set_extra_http_headers(self._get_http_headers())
        
        return browser, context, page

    def _wait_for_results(self, page) -> bool:
        """Wait for search results to appear on the page."""
        for selector in config.RESULT_SELECTORS:
            try:
                page.wait_for_selector(selector, timeout=5000)
                elements = page.query_selector_all(selector)
                if elements:
                    print(f"Found {len(elements)} results using selector: {selector}")
                    return True
            except:
                continue
        return False

    def _handle_page_not_loaded(self, page):
        """Handle cases where search results don't load properly."""
        page_title = page.title()
        page_url = page.url
        page_content = page.inner_text("body")[:500] if page.query_selector("body") else "No body found"
        
        print(f"Debug - Title: {page_title}, URL: {page_url}")
        
        # Check for blocking patterns
        blocking_keywords = ['blocked', 'captcha', 'verify', 'protection', 'cloudflare']
        if any(keyword in page_content.lower() for keyword in blocking_keywords):
            raise Exception("Page appears to be blocked or showing CAPTCHA")
        
        if "duckduckgo" not in page_title.lower():
            raise Exception(f"Unexpected page loaded. Title: {page_title}")
        
        # Try scrolling and waiting
        page.evaluate("window.scrollTo(0, 500)")
        page.wait_for_load_state("networkidle")
        page.evaluate("window.scrollTo(0, 0)")
        
        # Final attempt
        try:
            page.wait_for_selector("article[data-testid='result'], .result", timeout=10000)
            return True
        except:
            raise Exception("Could not find search results after multiple attempts")

    def _click_more_results(self, page, max_clicks: int) -> int:
        """Click 'More results' button multiple times and return actual clicks."""
        pages_retrieved = 1
        
        for i in range(max_clicks - 1):
            # Scroll to bottom gradually
            page.evaluate("""
                const scrollHeight = document.body.scrollHeight;
                const currentScroll = window.pageYOffset;
                const targetScroll = scrollHeight - window.innerHeight;
                window.scrollTo(0, Math.min(currentScroll + 500, targetScroll));
            """)
            page.wait_for_load_state("networkidle")
            
            # Try to click more results button
            clicked = False
            for selector in config.MORE_RESULTS_SELECTORS:
                try:
                    if page.locator(selector).is_visible():
                        page.click(selector)
                        page.wait_for_load_state("networkidle", timeout=10000)
                        clicked = True
                        print(f"Clicked more results button {i+1} times")
                        pages_retrieved += 1
                        break
                except:
                    continue
            
            if not clicked:
                print(f"No more results button found after {i} clicks")
                break
                
        return pages_retrieved

    def _parse_results(self, html: str) -> list:
        """Parse HTML content and extract search results."""
        soup = BeautifulSoup(html, "html.parser")
        results = []
        
        # Find articles using selectors
        articles = []
        for selector in config.RESULT_SELECTORS:
            articles = soup.select(selector)
            if articles:
                print(f"Found {len(articles)} articles using selector: {selector}")
                break
        
        if not articles:
            # Fallback: find any relevant links
            return self._extract_fallback_links(soup)
        
        # Extract data from articles
        for article in articles:
            link = self._find_title_link(article)
            if link:
                title = link.get_text(strip=True)
                href = link.get('href')
                
                if title and href and len(title) > 5:
                    results.append({
                        "title": title,
                        "url": href,
                        "scraped_at": self.scrape_time
                    })
        
        return results

    def _find_title_link(self, article):
        """Find the main title link within an article."""
        for selector in config.LINK_SELECTORS:
            link = article.select_one(selector)
            if link:
                return link
        return None

    def _extract_fallback_links(self, soup) -> list:
        """Extract links as fallback when no articles are found."""
        results = []
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            # Filter out internal and irrelevant links
            if (title and len(title) > 10 and 
                not href.startswith(('/', '#', 'javascript:')) and
                'duckduckgo.com' not in href and
                'http' in href):
                results.append({
                    "title": title,
                    "url": href,
                    "scraped_at": self.scrape_time
                })
        
        return results

    def scrape(self, query: str, max_pages: int, headless: bool = True) -> tuple[pd.DataFrame, int]:
        """
        Scrape DuckDuckGo search results.
        
        Args:
            query: Search query string
            max_pages: Maximum number of pages to retrieve
            headless: Whether to run browser in headless mode
            
        Returns:
            Tuple of (DataFrame with results, number of pages retrieved)
        """
        if not query.strip():
            raise ValueError("Query cannot be empty")
            
        url = f"https://duckduckgo.com/?q={quote_plus(query)}&t=h_"
        
        with sync_playwright() as p:
            browser, context, page = self._setup_browser(p, headless)
            
            try:
                # Navigate to DuckDuckGo homepage first
                page.goto("https://duckduckgo.com/", wait_until='domcontentloaded', timeout=30000)
                page.wait_for_selector("input#searchbox_input", timeout=10000)
                
                # Navigate to search results
                page.goto(url, wait_until='domcontentloaded', timeout=30000)
                page.wait_for_selector("article[data-nrn='result'] a[data-testid='result-title-a']", timeout=10000)
                
                # Wait for results to load
                if not self._wait_for_results(page):
                    self._handle_page_not_loaded(page)
                
                # Click more results button
                pages_retrieved = self._click_more_results(page, max_pages)
                
                # Get final HTML
                html = page.content()
                
            finally:
                context.close()
                browser.close()
        
        # Parse results
        results = self._parse_results(html)
        return pd.DataFrame(results), pages_retrieved
