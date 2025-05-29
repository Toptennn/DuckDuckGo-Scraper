import os

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Chrome options for Selenium - optimized for cloud deployment
CHROME_OPTIONS = [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
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
    '--disable-background-networking',
    '--window-size=1920,1080',
    '--disable-infobars',
    '--disable-notifications',
    '--disable-logging',
    '--disable-gpu-logging',
    '--silent',
    '--log-level=3',
    '--disable-software-rasterizer'
]

# Add environment-specific options
if os.getenv('STREAMLIT_SHARING'):  # Streamlit Cloud environment
    CHROME_OPTIONS.extend([
        '--single-process',
        '--disable-dev-shm-usage',
        '--no-zygote'
    ])

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
    "button:contains('More results')",
    "button:contains('ผลลัพธ์เพิ่มเติม')",
    "a:contains('More results')",
    ".more_results"
]