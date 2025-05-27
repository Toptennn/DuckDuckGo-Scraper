import asyncio
import sys
import datetime
import io
import time
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Configure Windows event loop policy for subprocess support
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


class DuckDuckGoScraper:
    """DuckDuckGo search results scraper using Playwright."""
    
    # Browser launch arguments for stealth mode
    BROWSER_ARGS = [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--disable-gpu',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
        '--disable-features=TranslateUI',
        '--disable-ipc-flooding-protection',
        '--disable-blink-features=AutomationControlled',
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-default-apps',
        '--no-default-browser-check',
        '--disable-hang-monitor',
        '--disable-prompt-on-repost',
        '--disable-sync',
        '--metrics-recording-only',
        '--no-crash-upload',
        '--disable-background-networking'
    ]
    
    # User agent for realistic browser behavior
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    # Selectors for finding search results
    RESULT_SELECTORS = [
        "article[data-testid='result']",
        ".result",
        "[data-testid='result']",
        ".web-result",
        ".result__body",
        "div[data-area='primary'] > div > div",
        "#links .result",
        ".organic-result"
    ]
    
    # Selectors for finding title links within results
    LINK_SELECTORS = [
        "a[data-testid='result-title-a']",
        "h2 a",
        "h3 a", 
        ".result__title a",
        ".result-title a",
        "a"
    ]
    
    # Selectors for "More results" button
    MORE_RESULTS_SELECTORS = [
        "button#more-results",
        "button[id='more-results']",
        ".more-results",
        "button:has-text('More results')",
        "button:has-text('ผลลัพธ์เพิ่มเติม')",
        "a:has-text('More results')",
        ".more_results"
    ]

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
            'User-Agent': self.USER_AGENT
        }

    def _setup_browser(self, playwright, headless: bool):
        """Setup and configure browser with stealth settings."""
        browser = playwright.chromium.launch(headless=headless, args=self.BROWSER_ARGS)
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=self.USER_AGENT,
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
        for selector in self.RESULT_SELECTORS:
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
            for selector in self.MORE_RESULTS_SELECTORS:
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
        for selector in self.RESULT_SELECTORS:
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
        for selector in self.LINK_SELECTORS:
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


def create_download_files(df: pd.DataFrame) -> tuple[str, bytes]:
    """Create CSV and Excel files for download."""
    # CSV
    csv_data = df.to_csv(index=False, encoding='utf-8-sig')
    
    # Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Results')
    excel_data = excel_buffer.getvalue()
    
    return csv_data, excel_data


def display_error_suggestions():
    """Display troubleshooting suggestions for users."""
    st.info("💡 แนะนำการแก้ไข:")
    suggestions = [
        "ปิด Headless Mode เพื่อดูว่าเกิดอะไรขึ้น",
        "เพิ่มหน่วงเวลาหลังคลิก",
        "ลดจำนวนการคลิก 'ผลลัพธ์เพิ่มเติม'",
        "DuckDuckGo อาจมีการป้องกัน bot - ลองใช้เว็บไซต์อื่น"
    ]
    for suggestion in suggestions:
        st.info(f"• {suggestion}")


def display_no_results_info():
    """Display information when no results are found."""
    st.info("💡 สาเหตุที่เป็นไปได้:")
    reasons = [
        "เว็บไซต์มีการป้องกัน bot",
        "โครงสร้าง HTML ของเว็บไซต์เปลี่ยนแปลง",
        "คำค้นหาไม่มีผลลัพธ์",
        "เครือข่ายอินเทอร์เน็ตช้าหรือมีปัญหา"
    ]
    for reason in reasons:
        st.info(f"• {reason}")


def main():
    """Main Streamlit application."""
    st.set_page_config(page_title="🦆 DuckDuckGo Scraper", layout="wide")
    st.title("🦆 DuckDuckGo Playwright Scraper")
    st.markdown("กรุณากรอกคำค้นหาและตั้งค่าต่าง ๆ จากนั้นคลิก Search เพื่อดูผลลัพธ์")

    # Sidebar configuration
    st.sidebar.header("การตั้งค่า Scraper")
    max_pages = st.sidebar.slider("จำนวนหน้า", 1, 50, 20)

    # Main input
    query = st.text_input(
        "🔍 คำค้นหา:", 
        value="", 
        placeholder="เช่น artificial intelligence"
    )
    
    if st.button("Search"):
        if not query.strip():
            st.error("กรุณาใส่คำค้นหาก่อนคลิก Search")
            return

        scraper = DuckDuckGoScraper()
        
        with st.spinner("กำลังค้นหา... กรุณารอสักครู่"):
            try:
                df, pages_retrieved = scraper.scrape(query, max_pages, headless=True)
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดระหว่างการสแครป: {e}")
                display_error_suggestions()
                return

        # Display results
        if df.empty:
            st.warning("ไม่พบผลลัพธ์ใด ๆ")
            display_no_results_info()
        else:
            st.success(f"พบผลลัพธ์ {len(df)} รายการ จาก {pages_retrieved} หน้า")
            
            if pages_retrieved < max_pages:
                st.info(f"หมายเหตุ: Scraping ทำได้เพียง {pages_retrieved} หน้า จากที่ตั้งค่า {max_pages} หน้า")
            
            st.dataframe(df, use_container_width=True)

            # Download buttons
            csv_data, excel_data = create_download_files(df)
            timestamp = int(time.time())
            
            st.download_button(
                "⬇️ ดาวน์โหลด CSV", 
                data=csv_data, 
                file_name=f"ddg_{timestamp}.csv"
            )
            
            st.download_button(
                "⬇️ ดาวน์โหลด Excel", 
                data=excel_data, 
                file_name=f"ddg_{timestamp}.xlsx"
            )


if __name__ == "__main__":
    main()