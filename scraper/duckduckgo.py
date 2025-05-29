import datetime
import os
from urllib.parse import quote_plus

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

import config

RESULTS_CSS_SELECTOR = "article, .result, [data-testid='result']"

class DuckDuckGoScraper:
    """DuckDuckGo search results scraper using Selenium."""

    def __init__(self):
        import pytz
        thailand_tz = pytz.timezone('Asia/Bangkok')
        self.scrape_time = datetime.datetime.now(thailand_tz).isoformat()

    def _setup_driver(self, headless: bool = True):
        """Setup and configure Chrome driver with performance optimizations."""
        chrome_options = Options()
        
        # Basic Chrome options
        for option in config.CHROME_OPTIONS:
            chrome_options.add_argument(option)
        
        # Force headless in cloud environments or when requested
        if headless or os.getenv('STREAMLIT_SHARING') or os.getenv('STREAMLIT_CLOUD'):
            chrome_options.add_argument('--headless=new')
        
        # Performance-focused options
        performance_options = [
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-default-apps',
            '--disable-popup-blocking',
            '--disable-translate',
            '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            '--disable-client-side-phishing-detection',
            '--disable-sync',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--memory-pressure-off',
            '--max_old_space_size=4096',
            '--aggressive-cache-discard',
            '--disable-background-networking',
            '--disable-component-update',
            '--disable-domain-reliability'
        ]
        
        for option in performance_options:
            chrome_options.add_argument(option)
        
        # Set user agent
        chrome_options.add_argument(f'--user-agent={config.USER_AGENT}')
        
        # Disable automation detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Enhanced performance preferences
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values": {
                "images": 2,  # Block images
                "plugins": 2,  # Block plugins
                "popups": 2,
                "geolocation": 2,
                "notifications": 2,
                "media_stream": 2,
            },
            "profile.managed_default_content_settings": {
                "images": 2
            }
        })
        
        driver = None
        last_error = None
        
        setup_methods = [
            ("WebDriver Manager", self._setup_with_webdriver_manager),
            ("System Chrome", self._setup_with_system_chrome),
            ("Basic Chrome", self._setup_basic_chrome)
        ]
        
        for method_name, setup_func in setup_methods:
            try:
                driver = setup_func(chrome_options)
                if driver:
                    break
            except Exception as e:
                last_error = e
                continue
        
        if not driver:
            raise RuntimeError(f"All Chrome setup methods failed. Last error: {last_error}")
        
        # Set optimized timeouts
        driver.set_page_load_timeout(20)
        driver.implicitly_wait(5)
        
        # Apply stealth settings
        try:
            self._apply_stealth_settings(driver)
        except Exception:
            pass  # Silent fail for stealth settings
        
        return driver

    def _setup_with_webdriver_manager(self, chrome_options):
        """Setup using webdriver-manager with enhanced error handling."""
        driver_path = ChromeDriverManager().install()
        service = Service(driver_path)
        service.creation_flags = 0x08000000  # CREATE_NO_WINDOW flag for Windows
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def _setup_with_system_chrome(self, chrome_options):
        """Setup using system Chrome/Chromium."""
        chrome_paths = [
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser', 
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable'
        ]
        
        chrome_binary = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_binary = path
                break
        
        if not chrome_binary:
            raise FileNotFoundError("No system Chrome/Chromium found")
        
        chrome_options.binary_location = chrome_binary
        
        driver_paths = [
            '/usr/bin/chromedriver',
            '/usr/local/bin/chromedriver',
            '/usr/bin/chromium-driver'
        ]
        
        for driver_path in driver_paths:
            if os.path.exists(driver_path):
                try:
                    service = Service(driver_path)
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    driver.set_page_load_timeout(30)
                    return driver
                except Exception:
                    continue
        
        # Fallback to webdriver-manager for system Chrome
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            raise RuntimeError(f"System Chrome setup failed: {e}")

    def _setup_basic_chrome(self, chrome_options):
        """Basic Chrome setup as last resort."""
        chrome_options.binary_location = None
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            from selenium.common.exceptions import WebDriverException
            raise WebDriverException(f"Basic Chrome setup failed: {e}")

    def _apply_stealth_settings(self, driver):
        """Apply stealth settings to avoid detection."""
        stealth_script = """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        
        window.chrome = {
            runtime: {},
        };
        
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        """
        
        try:
            driver.execute_script(stealth_script)
        except Exception:
            pass

    def _wait_for_results(self, driver) -> bool:
        """Wait for search results with enhanced selectors."""
        wait = WebDriverWait(driver, 15)
        
        for selector in config.RESULT_SELECTORS:
            try:
                if selector.startswith('#'):
                    elements = wait.until(EC.presence_of_all_elements_located((By.ID, selector[1:])))
                elif selector.startswith('.'):
                    elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, selector[1:])))
                else:
                    elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                
                if elements:
                    return True
                    
            except (TimeoutException, Exception):
                continue
        
        return False

    def _handle_page_not_loaded(self, driver):
        """Optimized page loading error handling."""
        try:
            page_url = driver.current_url
            
            page_info = driver.execute_script("""
                return {
                    title: document.title,
                    bodyText: document.body ? document.body.innerText.slice(0, 200) : '',
                    readyState: document.readyState
                };
            """)
            
            # Check for blocking patterns
            blocking_keywords = ['blocked', 'captcha', 'verify', 'protection', 'cloudflare', 'access denied']
            if any(keyword in page_info['bodyText'].lower() for keyword in blocking_keywords):
                raise RuntimeError("Page blocked or CAPTCHA detected.")
            
            # Verify we're on DuckDuckGo
            if "duckduckgo" not in page_info['title'].lower() and "duckduckgo" not in page_url.lower():
                raise RuntimeError(f"Wrong page loaded. Expected DuckDuckGo, got: {page_info['title']}")
            
            # Quick recovery attempt
            driver.execute_script("window.scrollTo(0, Math.min(500, document.body.scrollHeight));")
            
            WebDriverWait(driver, 5).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, RESULTS_CSS_SELECTOR))
            )
            
            return True
            
        except TimeoutException:
            raise RuntimeError("Could not find search results after recovery attempts")
        # Let all other exceptions propagate automatically

    def _click_more_results(self, driver, max_clicks: int) -> int:
        """Enhanced more results clicking with efficient waits and reduced complexity."""
        pages_retrieved = 1

        for _ in range(max_clicks - 1):
            try:
                initial_results = len(driver.find_elements(By.CSS_SELECTOR, RESULTS_CSS_SELECTOR))
                self._scroll_page(driver)
                self._wait_for_page_ready(driver)
                if not self._try_click_more_results(driver, initial_results):
                    break
                pages_retrieved += 1
            except Exception:
                break

        return pages_retrieved

    def _scroll_page(self, driver):
        """Scroll the page to trigger loading more results."""
        driver.execute_script("""
            const scrollHeight = document.body.scrollHeight;
            const currentScroll = window.pageYOffset;
            const targetScroll = scrollHeight - window.innerHeight;
            window.scrollTo(0, Math.min(currentScroll + 800, targetScroll));
        """)

    def _wait_for_page_ready(self, driver):
        """Wait until the page is fully loaded."""
        WebDriverWait(driver, 5).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def _try_click_more_results(self, driver, initial_results) -> bool:
        """Try to click the 'more results' button using configured selectors."""
        for selector in config.MORE_RESULTS_SELECTORS:
            try:
                element = self._find_clickable_element(driver, selector)
                if element and element.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    driver.execute_script("arguments[0].click();", element)
                    if self._wait_for_new_results(driver, initial_results):
                        return True
            except (NoSuchElementException, TimeoutException, Exception):
                continue
        return False

    def _find_clickable_element(self, driver, selector):
        """Find a clickable element by selector, supporting :contains()."""
        if ':contains(' in selector:
            text = selector.split("':contains('")[1].split("')")[0]
            tag = selector.split(':contains(')[0]
            xpath = f"//{tag}[contains(text(), '{text}')]"
            return WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
        else:
            return WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )

    def _wait_for_new_results(self, driver, initial_results) -> bool:
        """Wait for new results to appear after clicking 'more results'."""
        try:
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, RESULTS_CSS_SELECTOR)) > initial_results
            )
            return True
        except TimeoutException:
            return False

    def _parse_results(self, html: str) -> list:
        """Enhanced result parsing with better error handling and reduced complexity."""
        soup = BeautifulSoup(html, "html.parser")
        articles = self._select_articles(soup)
        if not articles:
            return self._extract_fallback_links(soup)
        return self._build_results_from_articles(articles)

    def _select_articles(self, soup):
        """Select articles using configured selectors."""
        for selector in config.RESULT_SELECTORS:
            try:
                found_articles = soup.select(selector)
                if found_articles:
                    return found_articles
            except Exception:
                continue
        return []

    def _build_results_from_articles(self, articles):
        """Build results list from article elements."""
        results = []
        for article in articles:
            try:
                link = self._find_title_link(article)
                if not link:
                    continue
                title = link.get_text(strip=True)
                href = link.get('href')
                if not (title and href and len(title) > 5):
                    continue
                href = self._normalize_href(href)
                results.append({
                    "title": title,
                    "url": href,
                    "scraped_at": self.scrape_time
                })
            except Exception:
                continue
        return results

    def _normalize_href(self, href):
        """Normalize href to absolute URL if needed."""
        if href.startswith('//'):
            return 'https:' + href
        elif href.startswith('/'):
            return 'https://duckduckgo.com' + href
        return href

    def _find_title_link(self, article):
        """Find title link with enhanced selector support."""
        for selector in config.LINK_SELECTORS:
            try:
                link = article.select_one(selector)
                if link and link.get('href'):
                    return link
            except Exception:
                continue
        return None

    def _extract_fallback_links(self, soup) -> list:
        """Enhanced fallback link extraction."""
        results = []
        
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            try:
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                if (title and len(title) > 10 and len(title) < 200 and
                    not href.startswith(('/', '#', 'javascript:', 'mailto:')) and
                    'duckduckgo.com' not in href and
                    any(protocol in href for protocol in ['http://', 'https://']) and
                    not any(skip in href.lower() for skip in ['facebook.com', 'twitter.com', 'linkedin.com'])):
                    
                    results.append({
                        "title": title,
                        "url": href,
                        "scraped_at": self.scrape_time
                    })
                    
            except Exception:
                continue
        
        return results

    def scrape(self, query: str, max_pages: int, headless: bool = True) -> tuple[pd.DataFrame, int]:
        """
        Enhanced scraping with better error handling and recovery.
        
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
        driver = None
        
        try:
            driver = self._setup_driver(headless)
            
            driver.get("https://duckduckgo.com/")
            
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.ID, "searchbox_input")))
            
            driver.get(url)
            
            if not self._wait_for_results(driver):
                self._handle_page_not_loaded(driver)
            
            pages_retrieved = self._click_more_results(driver, max_pages)
            
            html = driver.page_source
            
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
        
        results = self._parse_results(html)
        df = pd.DataFrame(results)
        
        return df, pages_retrieved