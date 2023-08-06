import time

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def playListTitle(link):
    '''
    find the title of play-list
    :param str link
    :return: the title of play-list
    :rtype: str
    '''

    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options, service=Service(
        ChromeDriverManager().install()))
    driver.get(link)
    time.sleep(20)
    soup = bs(driver.page_source, 'html.parser')
    return soup.find_all('div', attrs={'class': 'single-playlist__head'})[0].find_all('span')[0].text


def videoTitle(link):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options, service=Service(
        ChromeDriverManager().install()))
    driver.get(link)
    time.sleep(20)
    return driver.title


def resolutionFinder(link):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options, service=Service(
        ChromeDriverManager().install()))
    driver.get(link)
    time.sleep(20)
    driver.find_element(
        By.CSS_SELECTOR,
        "#primary > div.single-details > div.single-details__info > div.single-details__utils > div > div > div.download-button > div > div > button").click()
    resolutions = ['1080p', '720p', '480p', '360p', '240p', '144p']
    existLinks = []
    for i in resolutions:
        try:
            if driver.find_element(By.XPATH, f"//*[@id='{i}']").is_displayed():
                existLinks.append(i)
        except Exception as e:

            pass

    return existLinks


def directLink(link, res='720p'):
    '''
    find the best quality that available and return it
    :param str link
    :reutrn: the best quality
    :rtype: str
    '''

    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options, service=Service(
        ChromeDriverManager().install()))
    driver.get(link)
    time.sleep(20)
    driver.find_element(
        By.CSS_SELECTOR,
        "#primary > div.single-details > div.single-details__info > div.single-details__utils > div > div > div.download-button > div > div > button").click()

    driver.find_element(By.XPATH, f"//*[@id='{res}']").click()
    time.sleep(3)
    driver.switch_to.window(driver.window_handles[-1])
    return driver.current_url


# by pass loading using selenium
def playListVideos(link):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options, service=Service(
        ChromeDriverManager().install()))
    driver.get(link)
    time.sleep(20)
    videoLinks = []
    links = driver.find_elements(By.CSS_SELECTOR,
                                 "a.titled-link.title[data-refer=playlists]")
    for link in links:
        videoLinks.append(link.get_attribute("href"))

    res_dct = {i: videoLinks[i] for i in range(0, len(videoLinks))}
    return res_dct
