from selenium.webdriver.common.by import By

def get_opinion_articles(driver, count=5):
    driver.get("https://elpais.com/opinion/")
    articles = driver.find_elements(By.CSS_SELECTOR, 'article')[:count]
    results = []
    for article in articles:
        title = article.find_element(By.CSS_SELECTOR, 'h2, h1').text
        content = article.text
        try:
            image_url = article.find_element(By.TAG_NAME, 'img').get_attribute('src')
        except:
            image_url = None
        results.append({'title': title, 'content': content, 'image_url': image_url})
    return results
