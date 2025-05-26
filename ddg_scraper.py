import asyncio
import sys

# สำหรับ Windows ให้ใช้ ProactorEventLoopPolicy เพื่อรองรับ subprocess
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import pandas as pd
import io
import datetime
import random

# --- Scraper function using Playwright ---
def scrape_duckduckgo(query: str,
                       max_clicks: int = 20,
                       delay: float = 1.0,
                       headless: bool = True) -> pd.DataFrame:
    """
    Scrape DuckDuckGo search results dynamically via Playwright.

    Args:
        query (str): Search query string.
        max_clicks (int): Maximum times to click "ผลลัพธ์เพิ่มเติม" button.
        delay (float): Seconds to wait after each click.
        headless (bool): Whether to run browser in headless mode.

    Returns:
        pd.DataFrame: DataFrame with columns [title, url, scraped_at].
    """
    url = f"https://duckduckgo.com/?q={quote_plus(query)}&t=h_"
    results = []
    scrape_time = datetime.datetime.now().isoformat()

    with sync_playwright() as p:
        # Launch browser with stealth settings
        browser = p.chromium.launch(
            headless=headless,
            args=[
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
        )
        
        # Create context with realistic settings
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            java_script_enabled=True,
            accept_downloads=False,
            ignore_https_errors=True
        )
        
        page = context.new_page()
        
        # Stealth mode - remove webdriver traces
        page.add_init_script("""
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
        """)
        
        # Set realistic headers
        page.set_extra_http_headers({
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        try:
            # First, visit DuckDuckGo homepage to set cookies
            page.goto("https://duckduckgo.com/", wait_until='domcontentloaded', timeout=30000)
            time.sleep(random.uniform(2, 4))
            
            # Then navigate to search results
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Add human-like delay
            time.sleep(random.uniform(3, 5))
            
            # Debug: Take screenshot and save HTML for debugging
            if not headless:
                try:
                    page.screenshot(path="debug_screenshot.png")
                except:
                    pass
            
            # Try to find results with multiple strategies
            found_results = False
            selectors_to_try = [
                "article[data-testid='result']",
                ".result",
                "[data-testid='result']",
                ".web-result",
                ".result__body",
                "div[data-area='primary'] > div > div",
                "#links .result",
                ".organic-result"
            ]
            
            for selector in selectors_to_try:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    elements = page.query_selector_all(selector)
                    if elements and len(elements) > 0:
                        print(f"Found {len(elements)} results using selector: {selector}")
                        found_results = True
                        break
                except:
                    continue
            
            if not found_results:
                # Check if page loaded correctly
                page_title = page.title()
                page_url = page.url
                page_content_snippet = page.inner_text("body")[:500] if page.query_selector("body") else "No body found"
                
                print(f"Debug info:")
                print(f"Page title: {page_title}")
                print(f"Page URL: {page_url}")
                print(f"Page content snippet: {page_content_snippet}")
                
                # Check for common blocking patterns
                if any(keyword in page_content_snippet.lower() for keyword in ['blocked', 'captcha', 'verify', 'protection', 'cloudflare']):
                    raise Exception("Page appears to be blocked, showing CAPTCHA, or under protection")
                elif "duckduckgo" not in page_title.lower():
                    raise Exception(f"Unexpected page loaded. Title: {page_title}")
                else:
                    # Try alternative approach - wait longer and scroll
                    page.evaluate("window.scrollTo(0, 500)")
                    time.sleep(3)
                    page.evaluate("window.scrollTo(0, 0)")
                    time.sleep(2)
                    
                    # Try one more time with longer timeout
                    try:
                        page.wait_for_selector("article[data-testid='result'], .result, [data-testid='result']", timeout=10000)
                        found_results = True
                    except:
                        raise Exception("Could not find search results after multiple attempts")

            # Click "More results" button multiple times
            for i in range(max_clicks):
                # Scroll to bottom gradually
                page.evaluate("""
                    const scrollHeight = document.body.scrollHeight;
                    const currentScroll = window.pageYOffset;
                    const targetScroll = scrollHeight - window.innerHeight;
                    window.scrollTo(0, Math.min(currentScroll + 500, targetScroll));
                """)
                time.sleep(random.uniform(1, 2))
                
                try:
                    # Look for "More results" button
                    more_selectors = [
                        "button#more-results",
                        "button[id='more-results']",
                        ".more-results",
                        "button:has-text('More results')",
                        "button:has-text('ผลลัพธ์เพิ่มเติม')",
                        "a:has-text('More results')",
                        ".more_results"
                    ]
                    
                    clicked = False
                    for selector in more_selectors:
                        try:
                            if page.locator(selector).is_visible():
                                page.click(selector)
                                page.wait_for_load_state("networkidle", timeout=10000)
                                time.sleep(random.uniform(delay, delay + 2))
                                clicked = True
                                print(f"Clicked more results button {i+1} times")
                                break
                        except:
                            continue
                    
                    if not clicked:
                        print(f"No more results button found after {i} clicks")
                        break
                        
                except Exception as e:
                    print(f"Could not click more results button: {e}")
                    break

            html = page.content()
            
        except Exception as e:
            context.close()
            browser.close()
            raise e
        finally:
            context.close()
            browser.close()

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    
    # Try multiple selectors for results
    articles = []
    selectors_to_parse = [
        "article[data-testid='result']",
        ".result",
        "[data-testid='result']",
        ".web-result",
        ".result__body"
    ]
    
    for selector in selectors_to_parse:
        articles = soup.select(selector)
        if articles:
            print(f"Found {len(articles)} articles using selector: {selector}")
            break
    
    if not articles:
        # Last resort - try to find any links that look like search results
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '')
            title = link.get_text(strip=True)
            # Skip internal DuckDuckGo links and empty titles
            if (title and len(title) > 10 and 
                not href.startswith('/') and 
                'duckduckgo.com' not in href and
                not href.startswith('#') and
                not href.startswith('javascript:') and
                'http' in href):
                results.append({
                    "title": title,
                    "url": href,
                    "scraped_at": scrape_time
                })
    else:
        for article in articles:
            # Try multiple selectors for title links
            a = None
            link_selectors = [
                "a[data-testid='result-title-a']",
                "h2 a",
                "h3 a", 
                ".result__title a",
                ".result-title a",
                "a"
            ]
            
            for link_selector in link_selectors:
                a = article.select_one(link_selector)
                if a:
                    break
            
            if not a:
                continue
                
            title = a.get_text(strip=True)
            href = a.get('href')
            
            if title and href and len(title) > 5:
                results.append({
                    "title": title,
                    "url": href,
                    "scraped_at": scrape_time
                })

    return pd.DataFrame(results)

# --- Streamlit App ---
def main():
    st.set_page_config(page_title="🦆 DuckDuckGo Scraper", layout="wide")
    st.title("🦆 DuckDuckGo Playwright Scraper")
    st.markdown("กรุณากรอกคำค้นหาและตั้งค่าต่าง ๆ จากนั้นคลิก Search เพื่อดูผลลัพธ์")

    st.sidebar.header("การตั้งค่า Scraper")
    max_clicks = st.sidebar.slider("จำนวนคลิก 'ผลลัพธ์เพิ่มเติม' สูงสุด", 1, 50, 20)
    delay = st.sidebar.slider("หน่วงเวลาหลังคลิก (วินาที)", 0.5, 5.0, 2.0)
    headless = st.sidebar.checkbox("Headless Mode (ซ่อนหน้าต่าง Browser)", value=False)

    # Add debug option
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Debug Options**")
    show_debug = st.sidebar.checkbox("แสดงข้อมูล Debug", value=True)

    query = st.text_input("🔍 คำค้นหา:", value="", placeholder="เช่น artificial intelligence")
    
    if st.button("Search"):
        if not query.strip():
            st.error("กรุณาใส่คำค้นหาก่อนคลิก Search")
            return

        with st.spinner("กำลังค้นหา... กรุณารอสักครู่"):
            try:
                df = scrape_duckduckgo(query, max_clicks=max_clicks, delay=delay, headless=headless)
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดระหว่างการสแครป: {e}")
                st.info("💡 แนะนำการแก้ไข:")
                st.info("• ปิด Headless Mode เพื่อดูว่าเกิดอะไรขึ้น")
                st.info("• เพิ่มหน่วงเวลาหลังคลิก")
                st.info("• ลดจำนวนการคลิก 'ผลลัพธ์เพิ่มเติม'")
                st.info("• DuckDuckGo อาจมีการป้องกัน bot - ลองใช้เว็บไซต์อื่น")
                return

        if df.empty:
            st.warning("ไม่พบผลลัพธ์ใด ๆ")
            st.info("💡 สาเหตุที่เป็นไปได้:")
            st.info("• เว็บไซต์มีการป้องกัน bot")
            st.info("• โครงสร้าง HTML ของเว็บไซต์เปลี่ยนแปลง")
            st.info("• คำค้นหาไม่มีผลลัพธ์")
            st.info("• เครือข่ายอินเทอร์เน็ตช้าหรือมีปัญหา")
        else:
            st.success(f"พบผลลัพธ์ {len(df)} รายการ")
            st.dataframe(df, use_container_width=True)

            # Download buttons
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("⬇️ ดาวน์โหลด CSV", data=csv, file_name=f"ddg_{int(time.time())}.csv")

            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Results')
            st.download_button("⬇️ ดาวน์โหลด Excel", data=excel_buffer.getvalue(), file_name=f"ddg_{int(time.time())}.xlsx")

if __name__ == "__main__":
    main()