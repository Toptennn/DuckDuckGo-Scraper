import time
import streamlit as st
import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from scraper import DuckDuckGoScraper, create_download_files, display_error_suggestions, display_no_results_info

def _add_normal_query(queries, query_parts):
    if queries.get('normal_query'):
        query_parts.append(queries['normal_query'])

def _add_exact_phrase(queries, query_parts):
    if queries.get('exact_phrase'):
        query_parts.append(f'"{queries["exact_phrase"]}"')

def _add_semantic_query(queries, query_parts):
    if queries.get('semantic_query'):
        query_parts.append(f'~"{queries["semantic_query"]}"')

def _add_include_terms(queries, query_parts):
    if queries.get('include_terms'):
        terms = [term.strip() for term in queries['include_terms'].split(',') if term.strip()]
        query_parts.extend([f"+{term}" for term in terms])

def _add_exclude_terms(queries, query_parts):
    if queries.get('exclude_terms'):
        terms = [term.strip() for term in queries['exclude_terms'].split(',') if term.strip()]
        query_parts.extend([f"-{term}" for term in terms])

def _add_filetype(queries, query_parts):
    if queries.get('filetype'):
        query_parts.append(f"filetype:{queries['filetype']}")

def _add_site_include(queries, query_parts):
    if queries.get('site_include'):
        query_parts.append(f"site:{queries['site_include']}")

def _add_site_exclude(queries, query_parts):
    if queries.get('site_exclude'):
        query_parts.append(f"-site:{queries['site_exclude']}")

def _add_intitle(queries, query_parts):
    if queries.get('intitle'):
        query_parts.append(f"intitle:{queries['intitle']}")

def _add_inurl(queries, query_parts):
    if queries.get('inurl'):
        query_parts.append(f"inurl:{queries['inurl']}")

def build_advanced_query(queries):
    """Build advanced search query with multiple query types."""
    query_parts = []
    _add_normal_query(queries, query_parts)
    _add_exact_phrase(queries, query_parts)
    _add_semantic_query(queries, query_parts)
    _add_include_terms(queries, query_parts)
    _add_exclude_terms(queries, query_parts)
    _add_filetype(queries, query_parts)
    _add_site_include(queries, query_parts)
    _add_site_exclude(queries, query_parts)
    _add_intitle(queries, query_parts)
    _add_inurl(queries, query_parts)
    return " ".join(query_parts)

def display_results(df, pages_retrieved, max_pages, final_query=None):
    """Display the search results and download buttons."""
    if df.empty:
        st.warning("ไม่พบผลลัพธ์ใด ๆ")
        display_no_results_info()
    else:
        st.success(f"พบผลลัพธ์ {len(df)} รายการ จาก {pages_retrieved} หน้า")
        if final_query:
            st.info(f"**คำค้นหาที่ใช้:** `{final_query}`")
        if pages_retrieved < max_pages:
            st.info(f"หมายเหตุ: Scraping ทำได้เพียง {pages_retrieved} หน้า จากที่ตั้งค่า {max_pages} หน้า")
        
        st.dataframe(df, use_container_width=True)
        
        try:
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
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการสร้างไฟล์ดาวน์โหลด: {str(e)}")

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="🦆 DuckDuckGo Advanced Scraper", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("🦆 DuckDuckGo Advanced Scraper")
    st.markdown("กรุณากรอกคำค้นหาและตั้งค่าต่าง ๆ จากนั้นคลิก Search เพื่อดูผลลัพธ์")


    # Initialize session state
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'pages_retrieved' not in st.session_state:
        st.session_state.pages_retrieved = 0
    if 'last_query' not in st.session_state:
        st.session_state.last_query = ""
    if 'final_query_used' not in st.session_state:
        st.session_state.final_query_used = ""

    # Sidebar configuration
    st.sidebar.header("การตั้งค่า Scraper")
    max_pages = st.sidebar.number_input(
        "จำนวนหน้า", 
        min_value=1, 
        value=20, 
        step=1,
        help="หมายเหตุ: จำนวนหน้ามากอาจใช้เวลานานและอาจถูกบล็อก"
    )

    if max_pages > 100:
        st.sidebar.warning("⚠️ จำนวนหน้ามาก อาจใช้เวลานานในการดาวน์โหลด")

    # Main search inputs
    st.header("🔍 ประเภทการค้นหา")
    
    col1, col2 = st.columns(2)
    
    with col1:
        normal_query = st.text_input(
            "คำค้นหาทั่วไป:",
            placeholder="เช่น artificial intelligence",
            help="การค้นหาปกติ - ผลลัพธ์เกี่ยวกับคำใดคำหนึ่ง"
        )
        
        semantic_query = st.text_input(
            "ค้นหาแบบ Semantic (~):",
            placeholder="เช่น machine learning",
            help="ค้นหาผลลัพธ์ที่มีความหมายคล้ายกัน"
        )
    
    with col2:
        exact_phrase = st.text_input(
            "คำค้นหาแม่นยำ (\"):",
            placeholder="เช่น data science",
            help="ค้นหาวลีที่ตรงกันแน่นอน"
        )

    # Advanced search options in sidebar
    st.sidebar.header("🔧 ตัวเลือกขั้นสูง")
    
    # Include/Exclude terms
    include_terms = st.sidebar.text_input(
        "คำที่ต้องการเน้น (+):",
        placeholder="python, tutorial",
        help="คำที่คั่นด้วยคอมม่า เพื่อเน้นในผลลัพธ์"
    )
    
    exclude_terms = st.sidebar.text_input(
        "คำที่ต้องการยกเว้น (-):",
        placeholder="basic, beginner",
        help="คำที่คั่นด้วยคอมม่า เพื่อยกเว้นจากผลลัพธ์"
    )
    
    # File type filter
    filetype = st.sidebar.selectbox(
        "ชนิดไฟล์:",
        ["", "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "html"],
        help="เลือกชนิดไฟล์ที่ต้องการ"
    )
    
    # Site filters
    site_include = st.sidebar.text_input(
        "เว็บไซต์เฉพาะ (site:):",
        placeholder="arxiv.org",
        help="ค้นหาเฉพาะในเว็บไซต์นี้"
    )
    
    site_exclude = st.sidebar.text_input(
        "ยกเว้นเว็บไซต์ (-site:):",
        placeholder="wikipedia.org",
        help="ยกเว้นเว็บไซต์นี้จากผลลัพธ์"
    )
    
    # Title and URL filters
    intitle = st.sidebar.text_input(
        "ใน Title (intitle:):",
        placeholder="research",
        help="ค้นหาคำในหัวข้อหน้าเว็บ"
    )
    
    inurl = st.sidebar.text_input(
        "ใน URL (inurl:):",
        placeholder="blog",
        help="ค้นหาคำใน URL ของหน้าเว็บ"
    )

    # Build queries dict
    queries = {
        'normal_query': normal_query,
        'exact_phrase': exact_phrase,
        'semantic_query': semantic_query,
        'include_terms': include_terms,
        'exclude_terms': exclude_terms,
        'filetype': filetype,
        'site_include': site_include,
        'site_exclude': site_exclude,
        'intitle': intitle,
        'inurl': inurl
    }
    
    # Build final query
    final_query = build_advanced_query(queries)
    
    # Display the constructed query
    if final_query:
        st.info(f"**คำค้นหาที่จะใช้:** `{final_query}`")
    
    # Validation
    has_any_query = any([normal_query.strip(), exact_phrase.strip(), semantic_query.strip()])
    
    # Clear previous results if query changed
    if final_query != st.session_state.last_query and final_query.strip():
        st.session_state.search_results = None
        st.session_state.pages_retrieved = 0
    
    if st.button("Search", type="primary"):
        if not has_any_query:
            st.error("กรุณาใส่คำค้นหาอย่างน้อย 1 ประเภทก่อนคลิก Search")
            return

        scraper = DuckDuckGoScraper()
        
        with st.spinner("กำลังค้นหา... กรุณารอสักครู่"):
            try:
                df, pages_retrieved = scraper.scrape(final_query, max_pages, headless=True)
                st.session_state.search_results = df
                st.session_state.pages_retrieved = pages_retrieved
                st.session_state.last_query = final_query
                st.session_state.final_query_used = final_query
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดระหว่างการสแครป: {str(e)}")
                display_error_suggestions()
                return

    # Display results if they exist in session state
    if st.session_state.search_results is not None:
        df = st.session_state.search_results
        pages_retrieved = st.session_state.pages_retrieved
        final_query_used = st.session_state.final_query_used
        display_results(df, pages_retrieved, max_pages, final_query_used)


if __name__ == "__main__":
    main()