import datetime
import os
from urllib.parse import quote_plus
import time
import re

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

from backend import config

class DuckDuckGoScraper:
    """DuckDuckGo search results scraper using Selenium."""

    def __init__(self):
        # This constructor is intentionally left empty because
        # all configuration and setup are handled in other methods.
        pass

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
        
        # Rest of setup method remains the same...
        driver = None
        last_error = None
        
        setup_methods = [
            ("WebDriver Manager", self._setup_with_webdriver_manager),
            ("System Chrome", self._setup_with_system_chrome),
            ("Basic Chrome", self._setup_basic_chrome)
        ]
        
        for method_name, setup_func in setup_methods:
            try:
                print(f"Attempting {method_name} setup...")
                driver = setup_func(chrome_options)
                if driver:
                    print(f"✅ {method_name} setup successful")
                    break
            except Exception as e:
                last_error = e
                print(f"❌ {method_name} failed: {e}")
                continue
        
        if not driver:
            raise RuntimeError(f"All Chrome setup methods failed. Last error: {last_error}")
        
        # Set cloud-optimized timeouts
        if os.getenv('STREAMLIT_SHARING') or os.getenv('STREAMLIT_CLOUD'):
            driver.set_page_load_timeout(60)  # Increased for cloud
            driver.implicitly_wait(10)  # Increased for cloud
        else:
            driver.set_page_load_timeout(20)
            driver.implicitly_wait(5)
        
        # Apply stealth settings
        try:
            self._apply_stealth_settings(driver)
        except Exception as e:
            print(f"Warning: Could not apply stealth settings: {e}")
        
        return driver

    def _setup_with_webdriver_manager(self, chrome_options):
        """Setup using webdriver-manager with enhanced error handling."""
        try:
            # Download and install the correct ChromeDriver
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
            
            # Add service arguments for better stability
            service.creation_flags = 0x08000000  # CREATE_NO_WINDOW flag for Windows
            
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            return driver
            
        except Exception as e:
            print(f"WebDriver Manager failed: {e}")
            raise

    def _setup_with_system_chrome(self, chrome_options):
        """Setup using system Chrome/Chromium."""
        # Look for system Chrome/Chromium
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
                print(f"Found Chrome at: {path}")
                break
        
        if not chrome_binary:
            raise Exception("No system Chrome/Chromium found")
        
        chrome_options.binary_location = chrome_binary
        
        # Try to find system ChromeDriver
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
                except Exception as e:
                    print(f"Failed with system driver {driver_path}: {e}")
                    continue
        
        # Fallback to webdriver-manager for system Chrome
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            raise Exception(f"System Chrome setup failed: {e}")

    def _setup_basic_chrome(self, chrome_options):
        """Basic Chrome setup as last resort."""
        # Remove binary location to use default
        chrome_options.binary_location = None
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            raise Exception(f"Basic Chrome setup failed: {e}")

    def _apply_stealth_settings(self, driver):
        """Apply stealth settings to avoid detection."""
        stealth_script = """
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
        
        // Add chrome object
        window.chrome = {
            runtime: {},
        };
        
        // Mock permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        """
        
        try:
            driver.execute_script(stealth_script)
        except Exception as e:
            print(f"Could not execute stealth script: {e}")

    def _wait_for_results(self, driver) -> bool:
        """Wait for search results with enhanced selectors."""
        wait = WebDriverWait(driver, 15)  # Increased timeout
        
        # Try each selector with different strategies
        for selector in config.RESULT_SELECTORS:
            try:
                if selector.startswith('#'):
                    elements = wait.until(EC.presence_of_all_elements_located((By.ID, selector[1:])))
                elif selector.startswith('.'):
                    elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, selector[1:])))
                else:
                    elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                
                if elements:
                    print(f"✅ Found {len(elements)} results with selector: {selector}")
                    return True
                    
            except TimeoutException:
                print(f"⏰ Timeout waiting for selector: {selector}")
                continue
            except Exception as e:
                print(f"❌ Error with selector {selector}: {e}")
                continue
        
        return False

    def _handle_page_not_loaded(self, driver):
        """Optimized page loading error handling."""
        try:
            # Quick checks first
            page_url = driver.current_url
            
            # Fast content check using JavaScript
            page_info = driver.execute_script("""
                return {
                    title: document.title,
                    bodyText: document.body ? document.body.innerText.slice(0, 200) : '',
                    readyState: document.readyState
                };
            """)
            
            print(f"🔍 Debug Info:")
            print(f"   Title: {page_info['title']}")
            print(f"   URL: {page_url}")
            print(f"   Content preview: {page_info['bodyText'][:100]}...")
            
            # Check for blocking patterns
            blocking_keywords = ['blocked', 'captcha', 'verify', 'protection', 'cloudflare', 'access denied']
            if any(keyword in page_info['bodyText'].lower() for keyword in blocking_keywords):
                raise RuntimeError(f"❌ Page blocked or CAPTCHA detected.")
            
            # Verify we're on DuckDuckGo
            if "duckduckgo" not in page_info['title'].lower() and "duckduckgo" not in page_url.lower():
                raise RuntimeError(f"❌ Wrong page loaded. Expected DuckDuckGo, got: {page_info['title']}")
            
            # Quick recovery attempt
            print("🔄 Attempting page recovery...")
            
            # Single scroll to trigger any lazy loading
            driver.execute_script("window.scrollTo(0, Math.min(500, document.body.scrollHeight));")
            
            # Wait for complete state
            WebDriverWait(driver, 5).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Quick check for results
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article, .result, [data-testid='result']"))
            )
            
            print("✅ Page recovery successful")
            return True
            
        except TimeoutException:
            raise RuntimeError("❌ Could not find search results after recovery attempts")
        except Exception as e:
            print(f"❌ Page handling error: {e}")
            raise

    def _click_more_results(self, driver, max_clicks: int, progress_callback=None) -> int:
        """Enhanced more results clicking with progress tracking."""
        pages_retrieved = 1
        consecutive_failures = 0
        max_consecutive_failures = 3
        
        print(f"🔄 Attempting to load {max_clicks} pages (Cloud optimized)...")
        
        # Initial progress update
        if progress_callback:
            progress_callback(pages_retrieved, max_clicks, "Loaded initial page")
        
        for i in range(max_clicks - 1):
            try:
                # Stop if "No more results found for" appears anywhere on the page
                if driver.execute_script("return document.body.innerText.includes('No more results found for');"):
                    print("🛑 No more results found message detected.")
                    if progress_callback:
                        progress_callback(pages_retrieved, max_clicks, "🛑 No more results found, stopping pagination.")
                    break

                # Update progress at start of each page attempt
                if progress_callback:
                    progress_callback(pages_retrieved, max_clicks, f"Loading page {pages_retrieved + 1}...")
                
                # Longer wait for cloud environments
                cloud_timeout = 30 if os.getenv('STREAMLIT_SHARING') or os.getenv('STREAMLIT_CLOUD') else 20
                wait = WebDriverWait(driver, cloud_timeout)
                
                # Store initial result count
                initial_results = len(driver.find_elements(By.CSS_SELECTOR, "article, .result, [data-testid='result']"))
                
                # Update progress - scrolling
                if progress_callback:
                    progress_callback(pages_retrieved, max_clicks, f"Scrolling to find more results button...")
                
                # More conservative scrolling for cloud
                driver.execute_script("""
                    window.scrollTo({
                        top: document.body.scrollHeight - window.innerHeight,
                        behavior: 'smooth'
                    });
                """)
                
                # Wait longer for page stabilization in cloud
                time.sleep(0.5 if os.getenv('STREAMLIT_SHARING') or os.getenv('STREAMLIT_CLOUD') else 0.3)
                
                # Wait for document ready with longer timeout
                WebDriverWait(driver, cloud_timeout).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                
                button_found = False
                
                # Update progress - finding button
                if progress_callback:
                    progress_callback(pages_retrieved, max_clicks, f"Looking for 'More results' button...")
                
                for selector in config.MORE_RESULTS_SELECTORS:
                    try:
                        if ':contains(' in selector:
                            text = selector.split("':contains('")[1].split("')")[0]
                            tag = selector.split(':contains(')[0]
                            xpath = f"//{tag}[contains(text(), '{text}')]"
                            element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                        else:
                            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        
                        if element and element.is_displayed():
                            # Update progress - clicking
                            if progress_callback:
                                progress_callback(pages_retrieved, max_clicks, f"Clicking 'More results' for page {pages_retrieved + 1}...")
                            
                            # Scroll to element with animation
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                            
                            # Click using JavaScript
                            driver.execute_script("arguments[0].click();", element)
                            
                            # Update progress - waiting for content
                            if progress_callback:
                                progress_callback(pages_retrieved, max_clicks, f"Waiting for new content to load...")
                            
                            # Wait for new content with extended timeout for cloud
                            try:
                                WebDriverWait(driver, cloud_timeout * 2).until(
                                    lambda d: len(d.find_elements(By.CSS_SELECTOR, "article, .result, [data-testid='result']")) > initial_results
                                )
                                button_found = True
                                pages_retrieved += 1
                                consecutive_failures = 0  # Reset failure counter
                                print(f"✅ Loaded page {pages_retrieved}")
                                
                                # Update progress - success
                                if progress_callback:
                                    progress_callback(pages_retrieved, max_clicks, f"✅ Successfully loaded page {pages_retrieved}")
                                break
                            except TimeoutException:
                                print(f"⚠️ Timeout waiting for new content on page {i+2}")
                                consecutive_failures += 1
                                if progress_callback:
                                    progress_callback(pages_retrieved, max_clicks, f"⚠️ Timeout loading page {pages_retrieved + 1}")
                                continue
                                
                    except (NoSuchElementException, TimeoutException):
                        continue
                    except Exception as e:
                        print(f"⚠️ Error with selector {selector}: {e}")
                        continue
                
                if not button_found:
                    consecutive_failures += 1
                    print(f"🔚 No more results button found (attempt {consecutive_failures})")
                    if progress_callback:
                        progress_callback(pages_retrieved, max_clicks, f"🔚 No more results available (stopped at page {pages_retrieved})")
                    
                    # Exit early if too many consecutive failures
                    if consecutive_failures >= max_consecutive_failures:
                        print(f"❌ Stopping after {consecutive_failures} consecutive failures")
                        if progress_callback:
                            progress_callback(pages_retrieved, max_clicks, f"❌ Stopped after {consecutive_failures} consecutive failures")
                        break
                        
            except Exception as e:
                consecutive_failures += 1
                print(f"❌ Error loading page {i+2}: {e}")
                if progress_callback:
                    progress_callback(pages_retrieved, max_clicks, f"❌ Error loading page {i+2}: {str(e)[:50]}...")
                
                # Exit early if too many consecutive failures
                if consecutive_failures >= max_consecutive_failures:
                    print(f"❌ Stopping after {consecutive_failures} consecutive failures")
                    if progress_callback:
                        progress_callback(pages_retrieved, max_clicks, f"❌ Stopped after {consecutive_failures} consecutive failures")
                    break
        
        print(f"📊 Successfully loaded {pages_retrieved} pages")
        if progress_callback:
            progress_callback(pages_retrieved, max_clicks, f"🎉 Completed! Loaded {pages_retrieved} pages total")
        
        return pages_retrieved

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
        print("🔄 Using fallback link extraction...")
        
        # Find all links
        all_links = soup.find_all('a', href=True)
        print(f"🔍 Found {len(all_links)} total links")
        
        for link in all_links:
            try:
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                # Enhanced filtering
                if (title and len(title) > 10 and len(title) < 200 and
                    not href.startswith(('/', '#', 'javascript:', 'mailto:')) and
                    'duckduckgo.com' not in href and
                    any(protocol in href for protocol in ['http://', 'https://']) and
                    not any(skip in href.lower() for skip in ['facebook.com', 'twitter.com', 'linkedin.com'])):
                    
                    # Try to find date in the parent or nearby elements
                    published_date = None
                    try:
                        # Look for date in parent elements
                        parent = link.parent
                        if parent:
                            published_date = self._extract_published_date(parent)
                    except:
                        pass
                    
                    results.append({
                        "title": title,
                        "url": href,
                        "published_date": published_date
                    })
                    
            except Exception as e:
                continue
        
        print(f"📊 Fallback extraction found {len(results)} results")
        return results

    def _extract_published_date(self, article):
        """Extract published date from article with English date handling."""
        try:
            # Debug: Print the article HTML to see what we're working with
            # print(f"🔍 Article HTML snippet: {str(article)[:500]}...")
            
            date_span = None
            date_text = None
            
            # Primary selector - the exact class from your example
            date_span = article.select_one("span.MILR5XIVy9h75WrLvKiq.qsXMqKZNYEaWqGnWVdoa")
            if date_span:
                date_text = date_span.get_text(strip=True)
                print(f"✅ Found date with primary selector: '{date_text}'")
            
            if not date_span or not date_text:
                # Enhanced fallback selectors - more comprehensive search
                date_selectors = [
                    # Class-based selectors
                    "span[class*='MILR5XIVy9h75WrLvKiq']",
                    "span[class*='qsXMqKZNYEaWqGnWVdoa']",
                    "span[class*='date']",
                    "span[class*='time']",
                    "span[class*='published']",
                    "span[class*='timestamp']",
                    
                    # Generic time/date elements
                    "time",
                    "time[datetime]",
                    
                    # Common class names
                    ".date",
                    ".published",
                    ".timestamp",
                    ".publish-date",
                    ".post-date",
                    ".article-date",
                ]
                
                for selector in date_selectors:
                    try:
                        date_span = article.select_one(selector)
                        if date_span:
                            date_text = date_span.get_text(strip=True)
                            if date_text:
                                print(f"✅ Found date with fallback selector '{selector}': '{date_text}'")
                                break
                    except Exception as e:
                        # Continue to next selector if this one fails
                        continue
            
            if not date_text:
                # Last resort: search for any text that looks like an English date in the entire article
                article_text = article.get_text()
                
                # Look for English date patterns in the text
                import re
                
                # Pattern for dates like "Mar 19, 2025" or "March 19, 2025"
                english_date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
                matches = re.findall(english_date_pattern, article_text)
                if matches:
                    date_text = matches[0].strip()
                    print(f"✅ Found date with regex pattern: '{date_text}'")
                
                # Pattern for "Today"
                elif 'Today' in article_text:
                    date_text = 'Today'
                    print(f"✅ Found 'Today' in article text")
                
                # Pattern for "x days ago" or "x day ago"
                else:
                    days_ago_pattern = r'\b\d+\s+days?\s+ago\b'
                    matches = re.findall(days_ago_pattern, article_text)
                    if matches:
                        date_text = matches[0].strip()
                        print(f"✅ Found days ago pattern: '{date_text}'")
            
            if not date_text:
                print("⚠️ No date found in article")
                return None
            
            # Parse the found date text
            parsed_date = self._parse_english_date(date_text)
            if parsed_date:
                print(f"✅ Successfully parsed date: '{date_text}' -> '{parsed_date}'")
            else:
                print(f"⚠️ Failed to parse date: '{date_text}'")
            
            return parsed_date
            
        except Exception as e:
            print(f"⚠️ Error extracting date: {e}")
            return None

    def _parse_english_date(self, date_text: str):
        """Parse English date text and convert to ISO format."""
        try:
            current_date = datetime.datetime.now()
            
            # Clean up the date text
            date_text = date_text.strip()
            print(f"🔍 Parsing date text: '{date_text}'")
            
            # Handle "Today"
            if "Today" in date_text or "today" in date_text:
                result = current_date.date().isoformat()
                print(f"✅ Parsed 'Today' as: {result}")
                return result
            
            # Handle "x days ago" or "x day ago"
            days_ago_pattern = r'(\d+)\s+days?\s+ago'
            match = re.search(days_ago_pattern, date_text, re.IGNORECASE)
            if match:
                days_ago = int(match.group(1))
                target_date = current_date - datetime.timedelta(days=days_ago)
                result = target_date.date().isoformat()
                print(f"✅ Parsed '{days_ago} days ago' as: {result}")
                return result
            
            # Handle "Yesterday"
            if "Yesterday" in date_text or "yesterday" in date_text:
                target_date = current_date - datetime.timedelta(days=1)
                result = target_date.date().isoformat()
                print(f"✅ Parsed 'Yesterday' as: {result}")
                return result
            
            # Month name mapping (both abbreviated and full)
            month_mapping = {
                'jan': 1, 'january': 1,
                'feb': 2, 'february': 2,
                'mar': 3, 'march': 3,
                'apr': 4, 'april': 4,
                'may': 5,
                'jun': 6, 'june': 6,
                'jul': 7, 'july': 7,
                'aug': 8, 'august': 8,
                'sep': 9, 'september': 9,
                'oct': 10, 'october': 10,
                'nov': 11, 'november': 11,
                'dec': 12, 'december': 12
            }
            
            # Parse English date formats like "Mar 19, 2025" or "March 19, 2025"
            # Pattern with optional comma
            english_date_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})'
            match = re.search(english_date_pattern, date_text, re.IGNORECASE)
            if match:
                month_name = match.group(1).lower()
                day = int(match.group(2))
                year = int(match.group(3))
                
                print(f"🔍 Extracted: month='{month_name}', day={day}, year={year}")
                
                # Find month number
                month_num = month_mapping.get(month_name)
                
                if month_num:
                    try:
                        parsed_date = datetime.date(year, month_num, day)
                        result = parsed_date.isoformat()
                        print(f"✅ Successfully created date: {day}/{month_num}/{year} = {result}")
                        return result
                    except ValueError as e:
                        print(f"⚠️ Invalid date: {day}/{month_num}/{year} - {e}")
                        return None
                else:
                    print(f"⚠️ Could not match English month: '{month_name}'")
            
            # Try parsing other common date formats using strptime
            date_formats = [
                '%B %d, %Y',    # March 19, 2025
                '%b %d, %Y',    # Mar 19, 2025
                '%B %d %Y',     # March 19 2025
                '%b %d %Y',     # Mar 19 2025
                '%Y-%m-%d',     # 2025-03-19
                '%m/%d/%Y',     # 03/19/2025
                '%d/%m/%Y',     # 19/03/2025
                '%Y/%m/%d',     # 2025/03/19
            ]
            
            for date_format in date_formats:
                try:
                    parsed_date = datetime.datetime.strptime(date_text, date_format).date()
                    result = parsed_date.isoformat()
                    print(f"✅ Parsed with format '{date_format}': {result}")
                    return result
                except ValueError:
                    continue
            
            # If no pattern matches, return None
            print(f"⚠️ No matching pattern found for: '{date_text}'")
            return None
            
        except Exception as e:
            print(f"⚠️ Error parsing English date '{date_text}': {e}")
            return None
    
    def _parse_results(self, html: str) -> list:
        """Enhanced result parsing with date extraction."""
        soup = BeautifulSoup(html, "html.parser")
        results = []
        
        print("🔍 Parsing search results...")
        
        # Try to find articles using each selector
        articles = []
        successful_selector = None
        
        for selector in config.RESULT_SELECTORS:
            try:
                found_articles = soup.select(selector)
                if found_articles:
                    articles = found_articles
                    successful_selector = selector
                    print(f"✅ Found {len(articles)} articles using: {selector}")
                    break
            except Exception as e:
                print(f"❌ Selector failed {selector}: {e}")
                continue
        
        if not articles:
            print("⚠️ No articles found, trying fallback method...")
            return self._extract_fallback_links(soup)
        
        # Extract data from articles
        for i, article in enumerate(articles):
            try:
                link = self._find_title_link(article)
                if link:
                    title = link.get_text(strip=True)
                    href = link.get('href')
                    
                    # Validate result
                    if title and href and len(title) > 5:
                        # Clean up URL if needed
                        if href.startswith('//'):
                            href = 'https:' + href
                        elif href.startswith('/'):
                            href = 'https://duckduckgo.com' + href
                        
                        # Extract published date
                        published_date = self._extract_published_date(article)
                        
                        results.append({
                            "title": title,
                            "url": href,
                            "published_date": published_date
                        })
                        
            except Exception as e:
                print(f"⚠️ Error parsing article {i}: {e}")
                continue
        
        print(f"📊 Successfully parsed {len(results)} results")
        return results

    def scrape(self, query: str, max_pages: int, headless: bool = True, progress_callback=None, start_date=None, end_date=None) -> tuple[pd.DataFrame, int]:
        """
        Enhanced scraping with progress tracking and date range support.
        
        Args:
            query: Search query string
            max_pages: Maximum number of pages to retrieve
            headless: Whether to run browser in headless mode
            progress_callback: Function to call with progress updates
            start_date: Start date for search range (YYYY-MM-DD format)
            end_date: End date for search range (YYYY-MM-DD format)
            
        Returns:
            Tuple of (DataFrame with results, number of pages retrieved)
        """
        if not query.strip():
            raise ValueError("❌ Query cannot be empty")
        
        print(f"🔍 Starting scrape for: '{query}' (max {max_pages} pages)")
        
        if progress_callback:
            progress_callback(0, max_pages, "🚀 Starting browser...")
        
        # Build URL with optional date range
        url = f"https://duckduckgo.com/?q={quote_plus(query)}&t=h_"
        
        # Add date range if provided
        if start_date and end_date:
            # Validate date format
            try:
                datetime.datetime.strptime(start_date, '%Y-%m-%d')
                datetime.datetime.strptime(end_date, '%Y-%m-%d')
                url += f"&df={start_date}..{end_date}&ia=web"
                print(f"📅 Date range filter: {start_date} to {end_date}")
            except ValueError as e:
                print(f"⚠️ Invalid date format: {e}. Expected YYYY-MM-DD")
                raise ValueError("Date format must be YYYY-MM-DD")
        
        driver = None
        
        try:
            # Setup driver
            if progress_callback:
                progress_callback(0, max_pages, "🔧 Setting up Chrome driver...")
            
            driver = self._setup_driver(headless)
            print("✅ Driver setup complete")
            
            # Navigate to DuckDuckGo
            if progress_callback:
                progress_callback(0, max_pages, "🌐 Loading DuckDuckGo homepage...")
            
            print("🌐 Loading DuckDuckGo homepage...")
            driver.get("https://duckduckgo.com/")
            
            # Wait for search box
            if progress_callback:
                progress_callback(0, max_pages, "⏳ Waiting for homepage to load...")
            
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.ID, "searchbox_input")))
            print("✅ Homepage loaded")
            
            # Navigate to search results
            if progress_callback:
                progress_callback(0, max_pages, f"🔍 Searching for: {query[:50]}...")
            
            print(f"🔍 Searching for: {query}")
            print(f"🔗 URL: {url}")
            driver.get(url)
            
            # Wait for results with multiple fallbacks
            if progress_callback:
                progress_callback(1, max_pages, "⏳ Loading initial search results...")
            
            print("⏳ Waiting for search results...")
            if not self._wait_for_results(driver):
                if progress_callback:
                    progress_callback(1, max_pages, "🔄 Recovery mode - reloading page...")
                print("⚠️ Initial result loading failed, trying recovery...")
                self._handle_page_not_loaded(driver)
            
            print("✅ Search results loaded")
            
            # Load additional pages
            if progress_callback:
                progress_callback(1, max_pages, "✅ Initial page loaded, loading more pages...")
            
            pages_retrieved = self._click_more_results(driver, max_pages, progress_callback)
            
            # Get final HTML
            if progress_callback:
                progress_callback(pages_retrieved, max_pages, "📄 Extracting and parsing results...")
            
            print("📄 Extracting page content...")
            html = driver.page_source
            
        except Exception as e:
            print(f"❌ Scraping error: {e}")
            if progress_callback:
                progress_callback(0, max_pages, f"❌ Error: {str(e)[:50]}...")
            raise
        finally:
            if driver:
                try:
                    driver.quit()
                    print("🔄 Browser closed")
                except:
                    pass
        
        # Parse results
        print("🔄 Parsing results...")
        results = self._parse_results(html)
        
        df = pd.DataFrame(results)
        print(f"✅ Scraping complete: {len(df)} results from {pages_retrieved} pages")
        
        if progress_callback:
            progress_callback(pages_retrieved, max_pages, f"🎉 Complete! Found {len(df)} results from {pages_retrieved} pages")
        
        return df, pages_retrieved