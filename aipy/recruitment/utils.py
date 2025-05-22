from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

DRIVER_PTH = "/Users/liguang/WrokSpace/8889_crpto_analysis/crpto_analysis/aipy/recruitment/chromedriver"

def init_driver():
    """初始化Selenium WebDriver"""
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    
    try:
        # driver = webdriver.Chrome(options=options)
        # driver.set_page_load_timeout(CONFIG["timeout"])

        service = Service(executable_path=DRIVER_PTH)
        driver = webdriver.Chrome(service=service, options=options)

        return driver
    except Exception as e:
        print(f"Error initializing WebDriver: {str(e)}", file=sys.stderr)
        return None