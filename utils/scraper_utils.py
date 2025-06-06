import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def get_driver(headless: bool = True) -> webdriver.Chrome:
    """
    Ініціалізує і повертає Selenium WebDriver для Chrome.
    Якщо headless=True – запускає в безголовому режимі.
    """
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def extract_channel_id(url: str) -> str:
    """
    Витягає останню частину шляху (channel ID або @ім’я).
    """
    parts = url.rstrip("/").split("/")
    last = parts[-1]
    prev = parts[-2] if len(parts) > 1 else ""
    return prev.lstrip("@") if prev.startswith("@") else last

def scrape_titles(
    driver: webdriver.Chrome,
    url: str,
    max_scrolls: int = 2,
    pause: float = 2.0
) -> tuple[str, list[str]]:
    """
    Завантажує сторінку, автоматично скролить до max_scrolls разів
    і збирає всі video-title атрибути.
    Повертає (channelid, список заголовків).
    """
    driver.get(url)
    time.sleep(5)  # даємо час на завантаження

    channelid = extract_channel_id(url)
    titles = []
    last_h = driver.execute_script("return document.documentElement.scrollHeight")
    scrolls = 0

    while scrolls < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(pause)
        new_h = driver.execute_script("return document.documentElement.scrollHeight")
        if new_h == last_h:
            break
        last_h = new_h
        scrolls += 1

    elems = driver.find_elements(By.ID, "video-title")
    for a in elems:
        text = a.get_attribute("title") or a.text
        if text:
            titles.append(text.strip())

    return channelid, titles

def save_to_csv(channelid: str, titles: list[str], out_dir: str = "data/raw/") -> str:
    """
    Зберігає список заголовків у CSV-файл <out_dir>/<channelid>.csv.
    Повертає шлях до збереженого файлу.
    """
    os.makedirs(out_dir, exist_ok=True)
    filename = os.path.join(out_dir, f"{channelid}.csv")
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["title"])
        for t in titles:
            writer.writerow([t])
    return filename
