# from bs4 import BeautifulSoup
# import requests



# # Standard headers to fetch a website
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
# }


# def fetch_website_contents(url):
#     """
#     Return the title and contents of the website at the given url;
#     truncate to 2,000 characters as a sensible limit
#     """
#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.content, "html.parser")
#     title = soup.title.string if soup.title else "No title found"
#     if soup.body:
#         for irrelevant in soup.body(["script", "style", "img", "input"]):
#             irrelevant.decompose()
#         text = soup.body.get_text(separator="\n", strip=True)
#     else:
#         text = ""
#     return (title + "\n\n" + text)[:2_000]


# def fetch_website_links(url):
#     """
#     Return the links on the webiste at the given url
#     I realize this is inefficient as we're parsing twice! This is to keep the code in the lab simple.
#     Feel free to use a class and optimize it!
#     """
#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.content, "html.parser")
#     links = [link.get("href") for link in soup.find_all("a")]
#     return [link for link in links if link]

from contextlib import contextmanager
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@contextmanager
def make_browser(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1366,768")
    opts.add_argument("--disable-dev-shm-usage")
    # Helpful to look less “botty”
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/117.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=opts)
    try:
        yield driver
    finally:
        driver.quit()

def _render(url, wait_css="body", timeout=15):
    with make_browser(headless=True) as d:
        d.get(url)
        WebDriverWait(d, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_css)))
        # If the page lazy-loads, scroll to the bottom once or twice:
        d.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        WebDriverWait(d, 3).until(lambda drv: True)  # tiny pause
        return d.page_source

        
def fetch_website_contents(url, limit=2000, wait_css="main, article, #app, body"):
    html = _render(url, wait_css=wait_css)
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string if soup.title else "No title found"
    if soup.body:
        for t in soup.body(["script", "style", "img", "input", "noscript"]):
            t.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""
    return (title + "\n\n" + text)[:limit]

def fetch_website_links(url, wait_css="a"):
    html = _render(url, wait_css=wait_css)
    soup = BeautifulSoup(html, "html.parser")
    links = []
    seen = set()
    for a in soup.find_all("a", href=True):
        abs_link = urljoin(url, a["href"].strip())
        if abs_link.startswith(("http://", "https://")) and abs_link not in seen:
            seen.add(abs_link)
            links.append(abs_link)
    return links
