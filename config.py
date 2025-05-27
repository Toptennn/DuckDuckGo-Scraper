USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
BROWSER_ARGS = [
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
        "button:has-text('More results')",
        "button:has-text('ผลลัพธ์เพิ่มเติม')",
        "a:has-text('More results')",
        ".more_results"
]
