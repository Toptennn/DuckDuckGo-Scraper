import time

import streamlit as st
import asyncio
import sys
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


from scraper import DuckDuckGoScraper,create_download_files, display_error_suggestions, display_no_results_info

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
