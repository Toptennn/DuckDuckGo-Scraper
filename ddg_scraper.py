import subprocess
import streamlit as st

import asyncio
import sys

# สำหรับ Windows ให้ใช้ ProactorEventLoopPolicy เพื่อรองรับ subprocess
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st
from urllib.parse import quote_plus
# ————————————————————————————————————————————————
# Ensure Playwright has downloaded its browser binaries
# ————————————————————————————————————————————————
@st.cache_resource
def _install_playwright_browsers():
    """
    On Streamlit Cloud the playwright CLI may not be on PATH,
    so we invoke it via Python: `python -m playwright install`.
    """
    cmd = [
        sys.executable, "-m", "playwright", "install", "--with-deps"
    ]
    # Let the logs show up in the Cloud logs so we can debug if it still fails
    subprocess.run(cmd, check=True)

_install_playwright_browsers()

# now it’s safe to import Playwright
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import pandas as pd
import io
import datetime

# main.py (top of file)

# --- Scraper function using Playwright ---
def scrape_duckduckgo(query: str,
                       max_clicks: int = 20,
                       delay: float = 1.0) -> pd.DataFrame:
    """
    Scrape DuckDuckGo search results dynamically via Playwright.

    Args:
        query (str): Search query string.
        max_clicks (int): Maximum times to click "ผลลัพธ์เพิ่มเติม" button.
        delay (float): Seconds to wait after each click.

    Returns:
        pd.DataFrame: DataFrame with columns [title, url, scraped_at].
    """
    url = f"https://duckduckgo.com/?q={quote_plus(query)}&t=h_"
    results = []
    scrape_time = datetime.datetime.now().isoformat()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector("article[data-testid='result']", timeout=10000)

        for _ in range(max_clicks):
            # Scroll to bottom so button is in view
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            try:
                page.wait_for_selector("button#more-results", timeout=5000)
            except:
                break

            page.click("button#more-results")
            page.wait_for_load_state("networkidle")
            time.sleep(delay)

        html = page.content()
        browser.close()

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    for article in soup.select("article[data-testid='result']"):
        a = article.select_one("a[data-testid='result-title-a']")
        if not a:
            continue
        title = a.get_text(strip=True)
        href = a.get('href')
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
    delay = st.sidebar.slider("หน่วงเวลาหลังคลิก (วินาที)", 0.5, 5.0, 1.0)

    query = st.text_input("🔍 คำค้นหา:", value="", placeholder="เช่น artificial intelligence")
    if st.button("Search"):
        if not query.strip():
            st.error("กรุณาใส่คำค้นหาก่อนคลิก Search")
            return

        with st.spinner("กำลังค้นหา... กรุณารอสักครู่"):
            try:
                df = scrape_duckduckgo(query, max_clicks=max_clicks, delay=delay)
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดระหว่างการสแครป: {e}")
                return

        if df.empty:
            st.warning("ไม่พบผลลัพธ์ใด ๆ")
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