import os
import requests
from io import BytesIO
from PIL import Image
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from dotenv import load_dotenv

from utils.scraper import get_opinion_articles
from utils.translator import translate_titles
from utils.analyzer import analyze_words

load_dotenv()

USERNAME = os.getenv("BROWSERSTACK_USERNAME")
ACCESS_KEY = os.getenv("BROWSERSTACK_ACCESS_KEY")

BROWSERSTACK_URL = f"https://{USERNAME}:{ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub"

print("Username:", USERNAME)
print("Access Key:", ACCESS_KEY)

capabilities_list = [
    {"os": "Windows", "os_version": "11", "browserName": "Chrome"},
    {"os": "Windows", "os_version": "11", "browserName": "Firefox"},
    {"os": "OS X", "os_version": "Monterey", "browserName": "Safari"},
    {"deviceName": "iPhone 13", "realMobile": "true", "os_version": "15"},
    {"deviceName": "Samsung Galaxy S21", "realMobile": "true", "os_version": "11.0"}
]


def download_image(url, filename):
    if not url:
        return
    response = requests.get(url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        if not os.path.exists("images"):
            os.makedirs("images")
        img.save(f'images/{filename}')


def run_test(cap):
    browser = cap.get("browserName", "").lower()

    if browser == "chrome":
        options = ChromeOptions()
        for key, value in cap.items():
            options.set_capability(key, value)
    elif browser == "firefox":
        options = FirefoxOptions()
        for key, value in cap.items():
            options.set_capability(key, value)
    else:
        # For Safari and mobile devices, use a generic options object (ChromeOptions used here for example)
        options = ChromeOptions()
        for key, value in cap.items():
            options.set_capability(key, value)

    driver = webdriver.Remote(
        command_executor=BROWSERSTACK_URL,
        options=options
    )
    try:
        articles = get_opinion_articles(driver)
        assert articles, "No articles found!"

        titles = [a.get('title') for a in articles]
        print("All titles fetched:", titles)  # Debug output to check titles

        # Filter out invalid or empty titles
        valid_titles = [t for t in titles if isinstance(t, str) and t.strip()]
        print("Valid titles after filtering:", valid_titles)  # Debug output after filtering

        assert valid_titles, "No valid titles found after filtering empty or invalid titles"

        # Filter articles with non-empty content
        valid_articles = [a for a in articles if a.get('content', '').strip()]
        assert valid_articles, "No articles with valid content found"

        for i, article in enumerate(valid_articles):
            # Check if image_url is valid and download image if present
            if article.get('image_url'):
                assert article['image_url'].startswith('http'), f"Article {i} has invalid image URL"
                download_image(article['image_url'], f"cover_{i}.jpg")

        translated = translate_titles(valid_titles)
        assert translated, "Translation failed or returned empty list"

        print("\nTranslated Titles:")
        for t in translated:
            print(t)

        analysis = analyze_words(translated)
        assert all(count > 2 for count in analysis.values()), "Analysis contains words with count <= 2"

        print("\nRepeated Words (Count > 2):")
        for word, count in analysis.items():
            print(f"{word}: {count}")

    finally:
        driver.quit()


@pytest.mark.parametrize("cap", capabilities_list)
def test_cross_browser(cap):
    run_test(cap)
