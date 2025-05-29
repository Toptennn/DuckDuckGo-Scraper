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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

import config

class DuckDuckGoScraper:
    """DuckDuckGo search results scraper using Selenium."""

    def __init__(self):
        self.scrape_time = datetime.datetime.now().isoformat()

    def _setup_driver(self, headless: bool = True):
        """Setup and configure Chrome driver with stealth settings."""
        chrome_options = Options()
        
        # Add all Chrome options
        for option in config.CHROME_OPTIONS:
            chrome_options.add_argument(option)
        
        # Always headless in cloud environments
        if headless or os.getenv('STREAMLIT_SHARING'):
            chrome_options.add_argument('--headless')
        
        # Set user agent
        chrome_options.add_argument(f'--user-agent={config.USER_AGENT}')
        
        # Disable automation detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Performance preferences
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values": {
                "images": 2,  # Block images
                "plugins": 2,  # Block plugins
                "popups": 2,  # Block popups
                "geolocation": 2,  # Block location sharing
                "notifications": 2,  # Block notifications
                "media_stream": 2,  # Block media stream
            }
        })
        
        # Enhanced driver setup with better error handling
        driver = None
        
        # Try multiple approaches to setup the driver
        setup_attempts = [
            # Attempt 1: Use webdriver-manager (works for most cases)
            lambda: self._setup_with_webdriver_manager(chrome_options),
            # Attempt 2: Use system Chrome/Chromium in cloud
            lambda: self._setup_with_system_chrome(chrome_options),
            # Attempt 3: Fallback to basic setup
            lambda: self._setup_basic_chrome(chrome_options)
        ]
        
        for i, setup_func in enumerate(setup_attempts):
            try:
                driver = setup_func()
                if driver:
                    print(f"Driver setup successful with method {i+1}")
                    break
            except Exception as e:
                print(f"Setup method {i+1} failed: {e}")
                if i == len(setup_attempts) - 1:  # Last attempt
                    raise RuntimeError(f"Failed to setup Chrome driver after all attempts. Last error: {e}")
        
        # Execute stealth script
        driver.execute_script("""
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
        """)
        
        return driver

    def _setup_with_webdriver_manager(self, chrome_options):
        """Setup driver using webdriver-manager (auto-downloads compatible ChromeDriver)."""
        try:
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"WebDriver Manager setup failed: {e}")
            raise

    def _setup_with_system_chrome(self, chrome_options):
        """Setup driver using system Chrome/Chromium."""
        if not os.getenv('STREAMLIT_SHARING') and not os.path.exists('/usr/bin/chromium'):
            raise Exception("System Chrome not available")
        
        # For cloud environments, try to use system Chrome with compatible driver
        chrome_options.binary_location = '/usr/bin/chromium'
        
        # Try to find compatible ChromeDriver
        possible_drivers = [
            '/usr/bin/chromedriver',
            '/usr/local/bin/chromedriver',
            '/opt/chrome/chromedriver'
        ]
        
        for driver_path in possible_drivers:
            if os.path.exists(driver_path):
                try:
                    service = Service(driver_path)
                    return webdriver.Chrome(service=service, options=chrome_options)
                except Exception as e:
                    print(f"Failed with driver at {driver_path}: {e}")
                    continue
        
        raise Exception("No compatible system ChromeDriver found")

    def _setup_basic_chrome(self, chrome_options):
        """Basic Chrome setup as last resort."""
        try:
            # Remove binary location if set
            chrome_options.binary_location = None
            return webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Basic Chrome setup failed: {e}")
            raise

    def _wait_for_results(self, driver) -> bool:
        """Wait for search results to appear on the page."""
        wait = WebDriverWait(driver, 10)
        
        for selector in config.RESULT_SELECTORS:
            try:
                # Convert CSS selector to appropriate By strategy
                if selector.startswith('#'):
                    elements = wait.until(EC.presence_of_all_elements_located((By.ID, selector[1:])))
                elif selector.startswith('.'):
                    elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, selector[1:])))
                else:
                    elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                
                if elements:
                    print(f"Found {len(elements)} results using selector: {selector}")
                    return True
            except TimeoutException:
                continue
        return False

    def _handle_page_not_loaded(self, driver):
        """Handle cases where search results don't load properly."""
        page_title = driver.title
        page_url = driver.current_url
        page_content = driver.find_element(By.TAG_NAME, "body").text[:500] if driver.find_elements(By.TAG_NAME, "body") else "No body found"
        
        print(f"Debug - Title: {page_title}, URL: {page_url}")
        
        # Check for blocking patterns
        blocking_keywords = ['blocked', 'captcha', 'verify', 'protection', 'cloudflare']
        if any(keyword in page_content.lower() for keyword in blocking_keywords):
            raise RuntimeError("Page appears to be blocked or showing CAPTCHA")
        
        if "duckduckgo" not in page_title.lower():
            raise RuntimeError(f"Unexpected page loaded. Title: {page_title}")
        
        # Try scrolling and waiting
        driver.execute_script("window.scrollTo(0, 500);")
        driver.execute_script("window.scrollTo(0, 0);")
        
        # Final attempt
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-testid='result'], .result")))
            return True
        except TimeoutException:
            raise RuntimeError("Could not find search results after multiple attempts")

    def _click_more_results(self, driver, max_clicks: int) -> int:
        """Click 'More results' button multiple times and return actual clicks."""
        pages_retrieved = 1
        wait = WebDriverWait(driver, 5)
        
        for i in range(max_clicks - 1):
            # Scroll to bottom gradually
            driver.execute_script("""
                const scrollHeight = document.body.scrollHeight;
                const currentScroll = window.pageYOffset;
                const targetScroll = scrollHeight - window.innerHeight;
                window.scrollTo(0, Math.min(currentScroll + 500, targetScroll));
            """)

            # Wait for any dynamic content to load using explicit wait
            try:
                # Wait for page height to stabilize or new content to appear
                WebDriverWait(driver, 2).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            except TimeoutException:
                pass
            
            # Try to click more results button
            clicked = False
            for selector in config.MORE_RESULTS_SELECTORS:
                try:
                    # Handle different selector types
                    if ':contains(' in selector:
                        # Convert CSS :contains() to XPath
                        text = selector.split("':contains('")[1].split("')")[0]
                        tag = selector.split(':contains(')[0]
                        xpath = f"//{tag}[contains(text(), '{text}')]"
                        element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    else:
                        element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    
                    if element.is_displayed():
                        driver.execute_script("arguments[0].click();", element)

                        # Wait for new results to load
                        old_height = driver.execute_script("return document.body.scrollHeight")
                        WebDriverWait(driver, 3).until(
                            lambda d: d.execute_script("return document.body.scrollHeight") > old_height
                        )

                        clicked = True
                        print(f"Clicked more results button {i+1} times")
                        pages_retrieved += 1
                        break
                except (TimeoutException, NoSuchElementException):
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
        
        driver = self._setup_driver(headless)
        
        try:
            # Navigate to DuckDuckGo homepage first
            driver.get("https://duckduckgo.com/")
            
            # Wait for search box and navigate to search results
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.ID, "searchbox_input")))
            
            # Navigate to search results
            driver.get(url)
            
            # Wait for results to load
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-nrn='result'] a[data-testid='result-title-a']")))
            
            # Wait for results to load
            if not self._wait_for_results(driver):
                self._handle_page_not_loaded(driver)
            
            # Click more results button
            pages_retrieved = self._click_more_results(driver, max_pages)
            
            # Get final HTML
            html = driver.page_source
            
        finally:
            driver.quit()
        
        # Parse results
        results = self._parse_results(html)
        return pd.DataFrame(results), pages_retrieved