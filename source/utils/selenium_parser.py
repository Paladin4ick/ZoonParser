import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as exp_cond
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup

from logging import getLogger

logger = getLogger('parser')


def get_selenium_driver() -> webdriver.Chrome | None:
    """
    Function to create and configure a Chrome WebDriver instance.

    :return: A **webdriver.Chrome** instance if successful, otherwise **None**.
    """
    try:
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-extensions')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f'Ошибка создания драйвера: {str(e)}')
        return None


def get_auto_services_link(auto_services: list[WebElement]) -> list[str] | None:
    """
    Extracts links to auto services from a list of WebElements.

    :argument auto_services: A list of WebElements, each containing a link to an auto service.

    :returns: A list of strings, each representing a link to an auto service.
                Returns an empty list if an error occurs.
    """
    try:
        links = []
        for auto_service in auto_services:
            link = auto_service.get_attribute('href')
            if link:
                links.append(link)
                logger.info(f"Ссылка добавлена в список: {link}")
            else:
                logger.warning(f"Элемент не имеет атрибута **href**: {auto_service}")
        return links
    except Exception as e:
        logger.error(f"Ошибка генерации списка авто сервисов: {e}", exc_info=True)
        return []


def add_review(
        driver: webdriver.Chrome,
        service_link: str,
        comment: str | None,
        advantages: str | None,
        disadvantages: str | None,
        stars: str | None):
    """
    Automates the process of adding a review to a service on the specified website.


    :argument driver: The Selenium WebDriver instance controlling the browser.
    :argument service_link: The URL link to the service where the review will be added.
    :argument comment: The main comment or review text.
                There Can be None if not provided.
    :argument advantages: The advantages or pros of the service.
                There Can be None if not provided.
    :argument disadvantages: The disadvantages or cons of the service.
                There Can be None if not provided.
    :argument stars: The star rating for the service, represented as a string (e.g., '4.5').
                            If None, defaults to three stars.


    :raise TimeoutError: Raised if the operation exceeds the specified waiting time.
    :raise Exception: Catches all other exceptions and logs them for debugging.
    """
    try:
        driver.get(service_link)
        print(service_link)
        print(comment)
        print(advantages)
        print(disadvantages)

        star = stars.split(',')[0] if stars else 3

        star_element = WebDriverWait(driver, 10).until(
            exp_cond.element_to_be_clickable(
                (By.XPATH, f'//*[@id="reviewpage"]/form[1]/div[1]/div/div[1]/div/div/span/div/label[{star}]'))
        )

        driver.execute_script("arguments[0].scrollIntoView(true);", star_element)

        star_element.click()

        continue_button = WebDriverWait(driver, 10).until(
            exp_cond.element_to_be_clickable(
                (By.XPATH, '//*[@id="reviewpage"]/form[1]/div[1]/div/div[2]/div/button')
            )
        )

        driver.execute_script("arguments[0].scrollIntoView(true);", continue_button)

        continue_button.click()

        time.sleep(2)

        if comment:
            set_comment = WebDriverWait(driver, 10).until(
                exp_cond.presence_of_element_located(
                    (By.XPATH, '//*[@id="reviewpage"]/form[2]/div/div[1]/div[4]/div/div[1]/div/textarea')
                )
            )
            set_comment.send_keys(comment)

            logger.info('Добавлен комментарий')

        if advantages:
            set_advantages = WebDriverWait(driver, 10).until(
                exp_cond.presence_of_element_located(
                    (By.XPATH, '//*[@id="reviewpage"]/form[2]/div/div[1]/div[2]/div/div/div/textarea')
                )
            )

            set_advantages.send_keys(advantages)

            logger.info('Добавлены достоинства')

        if disadvantages:
            set_disadvantages = WebDriverWait(driver, 10).until(
                exp_cond.presence_of_element_located(
                    (By.XPATH, '//*[@id="reviewpage"]/form[2]/div/div[1]/div[3]/div/div/div/textarea')
                )
            )

            set_disadvantages.send_keys(advantages)

            logger.info('Добавлены недостатки')

        time.sleep(5)

        send_view = WebDriverWait(driver, 10).until(
            exp_cond.element_to_be_clickable(
                (By.XPATH, '//*[@id="reviewpage"]/form[2]/div/div[1]/div[5]/div/button'))
        )

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        send_view.click()

        logger.info('Отзыв добавлен успешно')

        time.sleep(5)

    except TimeoutError as e:
        logger.error(f'Превышено время ожидания: {e}')

    except Exception as e:
        logger.error(f"Ошибка добавления отзыва: {e}")



def extract_last_review_and_copy(driver: webdriver.Chrome, service_link: str):
    try:
        review_data = {}  # Словарь для хранения **Недостатков**, **Достоинства**, **Комментарий** из отзыва
        stars_count = ""
        advantages = ""
        disadvantages = ""
        comment = ""

        driver.get(f"{service_link}/reviews")

        page = driver.page_source

        bsoup = BeautifulSoup(page, 'html.parser')

        review_block = bsoup.find('li', class_='comment-item js-comment')

        if review_block:
            stars = review_block.find('div', class_='z-text--16 z-text--bold')
            stars_count = stars.get_text() if stars else None

        review_text_block = review_block.find('div', class_='js-comment-short-text comment-text z-text--16')
        review_text = review_text_block.find('div', class_='z-flex z-flex--column z-gap--12')

        if review_text:
            for block in review_text.find_all('div', class_='z-flex z-flex--column z-gap--4 js-comment-part'):
                title = block.find('div', class_='comment-text-subtitle').get_text(strip=True)
                content = block.find('span', class_='js-comment-content').get_text(strip=True)
                review_data[title] = content
                advantages = review_data.get('Достоинства')
                disadvantages = review_data.get('Недостатки')
                comment = review_data.get('Комментарий')
        else:
            comment += review_text_block.find('span', class_='js-comment-content').get_text()
            comment_hidden = review_text_block.find('span', class_='js-comment-additional-text hidden').get_text()
            comment += comment_hidden if comment_hidden else ""

        curl = driver.current_url
        if "/reviews/" in curl:
            link = curl.replace('/reviews/', '/addreview/')
        else:
            link = curl + "addreview/"

        add_review(driver, link, comment, advantages, disadvantages, stars_count)

    except Exception as e:
        logger.error(f"Ошибка копирования отзыва: {e}", exc_info=True)
    except TimeoutError as e:
        logger.error(f'Превышено время ожидания: {e}')


def get_auto_services_with_reviews(driver: webdriver.Chrome) -> list:
    services = []
    search_url = "https://zoon.ru/search/?query%5B%5D=%D0%B0%D0%B2%D1%82%D0%BE%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B&city=msk&boost_category=autoservice"

    driver.get(search_url)

    WebDriverWait(driver, 10).until(
        exp_cond.presence_of_element_located((By.XPATH, "//*[@id='catalogContainer']/div[1]/div[2]/div/div/div[1]/div/ul/li"))
    )

    last_height = driver.execute_script("return document.body.scrollHeight")


    while True:  # Прокрутка до конца страницы и получение ссылок на автосервисы с отзывами
        service_elements_with_reviews = driver.find_elements(
            By.XPATH, '//*[@id="catalogContainer"]/div[1]/div[2]/div/div/div[1]/div/ul/li/div/div[1]/div[1]/a'
        )

        services.extend(service_elements_with_reviews)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    return list(set(services))


def login_to_zoon(driver: webdriver.Chrome, username: str, password: str):
    """
    Function to log in to zoon.ru using Selenium WebDriver.

    :param driver: Instance of `webdriver.Chrome` used to navigate the site.
    :param username: User's email or username for login.
    :param password: User's password for login.
    """
    try:
        driver.get("https://zoon.ru/")

        login_button = WebDriverWait(driver, 15).until(
            exp_cond.element_to_be_clickable(
                (By.XPATH, '//*[@id="header"]/div[1]/div[4]/ul/li/span')
            )
        )
        login_button.click()  # Клик по кнопке **Войти**

        email_input = WebDriverWait(driver, 15).until(
            exp_cond.presence_of_element_located(
                (By.XPATH, '//*[@id="zhtml"]/body/div[5]/div/div/div[2]/div[2]/div[2]/form/label[1]/input')
            )
        )
        email_input.send_keys(username)  # Заполнение поля **email**


        password_input = WebDriverWait(driver, 15).until(
            exp_cond.presence_of_element_located(
                (By.XPATH, '//*[@id="zhtml"]/body/div[5]/div/div/div[2]/div[2]/div[2]/form/label[2]/input')
            )
        )
        password_input.send_keys(password)  # Заполнение поля **пароля**

        login_button_two = WebDriverWait(driver, 15).until(
            exp_cond.element_to_be_clickable(
                (By.XPATH, '//*[@id="zhtml"]/body/div[5]/div/div/div[2]/div[2]/div[2]/form/button')
            )
        )
        login_button_two.click()  # Клик по кнопке **Войти** в окне авторизации
        time.sleep(2)  # Пауза для загрузки страницы. Можно увеличить при плохом интернет-соединении

        serves_list = get_auto_services_link(get_auto_services_with_reviews(driver))
        for service in serves_list:  # Обработка списка ссылок на автосервисы с отзывами и копирование последнего отзыва
            extract_last_review_and_copy(driver, service)

    except TimeoutError as e:
        logger.error(f'Превышено время ожидания при входе в систему: {e}')
    except Exception as e:
        logger.error(f'Ошибка при входе в систему: {e}', exc_info=True)

