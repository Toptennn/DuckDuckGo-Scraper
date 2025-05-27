# scraper/utils.py

import io
import pandas as pd
import streamlit as st

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
