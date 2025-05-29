import os

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Enhanced Chrome options for maximum stability in cloud environments
CHROME_OPTIONS = [
    '--no-sandbox',
    '--disable-setuid-sandbox', 
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-software-rasterizer',
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-renderer-backgrounding',
    '--disable-features=TranslateUI,VizDisplayCompositor,AudioServiceOutOfProcess',
    '--disable-ipc-flooding-protection',
    '--disable-blink-features=AutomationControlled',
    '--disable-web-security',
    '--disable-extensions',
    '--disable-plugins',
    '--disable-default-apps',
    '--no-default-browser-check',
    '--disable-hang-monitor',
    '--disable-prompt-on-repost',
    '--disable-sync',
    '--disable-background-networking',
    '--disable-infobars',
    '--disable-notifications',
    '--disable-logging',
    '--disable-gpu-logging',
    '--silent',
    '--log-level=3',
    '--window-size=1280,720',
    '--remote-debugging-port=0',
    '--disable-client-side-phishing-detection',
    '--disable-crash-reporter',
    '--disable-oopr-debug-crash-dump',
    '--no-crash-upload',
    '--disable-low-res-tiling',
    '--memory-pressure-off',
    '--disable-permissions-api',
    '--disable-component-update',
    '--disable-domain-reliability',
    '--aggressive-cache-discard',
    '--disable-file-system',
    '--disable-databases',
    '--disable-local-storage'
]

# Add cloud-specific options
if os.getenv('STREAMLIT_SHARING') or os.getenv('STREAMLIT_CLOUD'):
    CHROME_OPTIONS.extend([
        '--single-process',
        '--no-zygote',
        '--disable-gpu-sandbox',
        '--disable-software-rasterizer',
        '--disable-dev-shm-usage'
    ])

# Enhanced result selectors for better compatibility
RESULT_SELECTORS = [
    "article[data-testid='result']",
    "article[data-nrn='result']", 
    ".result",
    "[data-testid='result']",
    ".web-result",
    ".result__body",
    "div[data-area='primary'] > div > div",
    "#links .result",
    ".organic-result",
    ".results_links",
    ".result--default"
]

# Enhanced link selectors
LINK_SELECTORS = [
    "a[data-testid='result-title-a']",
    "h2 a",
    "h3 a", 
    ".result__title a",
    ".result-title a",
    ".result__url",
    "a[href*='http']"
]

# Enhanced more results selectors
MORE_RESULTS_SELECTORS = [
    "button#more-results",
    "button[id='more-results']",
    ".more-results",
    "button:contains('More results')",
    "a:contains('More results')",
    ".more_results",
    "[data-testid='more-results']"
]