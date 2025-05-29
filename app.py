import time
import streamlit as st
import asyncio
import sys
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from scraper import DuckDuckGoScraper,create_download_files, display_error_suggestions, display_no_results_info

def display_results(df, pages_retrieved, max_pages):
    """Display the search results and download buttons."""
    if df.empty:
        st.warning("ไม่พบผลลัพธ์ใด ๆ")
        display_no_results_info()
    else:
        st.success(f"พบผลลัพธ์ {len(df)} รายการ จาก {pages_retrieved} หน้า")
        if pages_retrieved < max_pages:
            st.info(f"หมายเหตุ: Scraping ทำได้เพียง {pages_retrieved} หน้า จากที่ตั้งค่า {max_pages} หน้า")
        st.dataframe(df, use_container_width=True)
        csv_data, excel_data = create_download_files(df)
        timestamp = int(time.time())
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "⬇️ ดาวน์โหลด CSV", 
                data=csv_data, 
                file_name=f"ddg_{timestamp}.csv",
                mime="text/csv"
            )
        with col2:
            st.download_button(
                "⬇️ ดาวน์โหลด Excel", 
                data=excel_data, 
                file_name=f"ddg_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

def main():
    """Main Streamlit application."""
    st.set_page_config(page_title="🦆 DuckDuckGo Scraper", layout="wide")
    st.title("🦆 DuckDuckGo Playwright Scraper")
    st.markdown("กรุณากรอกคำค้นหาและตั้งค่าต่าง ๆ จากนั้นคลิก Search เพื่อดูผลลัพธ์")

    # Initialize session state
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'pages_retrieved' not in st.session_state:
        st.session_state.pages_retrieved = 0
    if 'last_query' not in st.session_state:
        st.session_state.last_query = ""

    # Sidebar configuration
    st.sidebar.header("การตั้งค่า Scraper")
    max_pages = st.sidebar.slider("จำนวนหน้า", 1, 100, 20)

    # Main input
    query = st.text_input(
        "🔍 คำค้นหา:", 
        value="", 
        placeholder="เช่น artificial intelligence"
    )
    
    # Clear previous results if query changed
    if query != st.session_state.last_query and query.strip():
        st.session_state.search_results = None
        st.session_state.pages_retrieved = 0
    
    if st.button("Search"):
        if not query.strip():
            st.error("กรุณาใส่คำค้นหาก่อนคลิก Search")
            return

        scraper = DuckDuckGoScraper()
        
        with st.spinner("กำลังค้นหา... กรุณารอสักครู่"):
            try:
                df, pages_retrieved = scraper.scrape(query, max_pages, headless=True)
                # Store results in session state
                st.session_state.search_results = df
                st.session_state.pages_retrieved = pages_retrieved
                st.session_state.last_query = query
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดระหว่างการสแครป: {e}")
                display_error_suggestions()
                return

    # Display results if they exist in session state
    if st.session_state.search_results is not None:
        df = st.session_state.search_results
        pages_retrieved = st.session_state.pages_retrieved
        display_results(df, pages_retrieved, max_pages)


if __name__ == "__main__":
    main()