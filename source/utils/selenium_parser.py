import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as exp_cond
from webdriver_manager.chrome import ChromeDriverManager

from logging import getLogger

logger = getLogger('parser')


def get_selenium_driver() -> webdriver.Chrome | None:
    """
    Function to create and configure a Chrome WebDriver instance.

    :return: A `webdriver.Chrome` instance if successful, otherwise `None`.
    """
    try:
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-extensions')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f'Error creating Chrome driver: {str(e)}')
        return None


def get_auto_services_link(auto_services: list[WebElement]) -> list[str] | None:
    try:
        links = []
        for auto_service in auto_services:
            link = auto_service.get_attribute('href')
            links.append(link)
            logger.info("Ссылка на автосервис добавлена в список:\n" + link)
        return links
    except Exception as e:
        logger.error(f"Ошибка формирования списка ссылок на автосервисы: {e}", exc_info=True)
        return []



def extract_last_review_and_copy(driver: webdriver.Chrome, service_link: str):
    try:
        driver.get(service_link)
        element = WebDriverWait(driver, 10).until(
            exp_cond.element_to_be_clickable((By.XPATH, f"//*[contains(text(), 'Отзывы')]"))
        )

        # Прокручиваем к элементу, если он не виден
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(3)  # Небольшая пауза, чтобы элемент полностью прогрузился

        # Кликаем по элементу
        element.click()
        print(f"Успешно кликнули на элемент с текстом: Отзывы")
        time.sleep(3)

    except Exception as e:
        logger.error(f"Ошибка копирования отзыва: {e}", exc_info=True)
        return None


def get_auto_services_with_reviews(driver: webdriver.Chrome) -> list:
    services = []
    search_url = "https://zoon.ru/search/?query%5B%5D=%D0%B0%D0%B2%D1%82%D0%BE%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B&city=msk&boost_category=autoservice"

    driver.get(search_url)

    WebDriverWait(driver, 10).until(
        exp_cond.presence_of_element_located((By.XPATH, "//*[@id='catalogContainer']/div[1]/div[2]/div/div/div[1]/div/ul/li"))
    )

    last_height = driver.execute_script("return document.body.scrollHeight")


    while True:

        # При написании заметил что, все объявления с отзывами в отличие от других имеют кликабельную ссылку на список
        # отзывов, ниже выполняется получение всех объявлений с отзывами через скролл страницы и тег 'a'
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
            exp_cond.element_to_be_clickable((By.XPATH, '//*[@id="header"]/div[1]/div[4]/ul/li/span'))
        )
        login_button.click()  # Клик по кнопке "Войти"

        email_input = WebDriverWait(driver, 15).until(
            exp_cond.presence_of_element_located((By.XPATH, '//*[@id="zhtml"]/body/div[5]/div/div/div[2]/div[2]/div[2]/form/label[1]/input'))
        )
        email_input.send_keys(username)  # Заполнение поля email


        password_input = WebDriverWait(driver, 15).until(
            exp_cond.presence_of_element_located((By.XPATH, '//*[@id="zhtml"]/body/div[5]/div/div/div[2]/div[2]/div[2]/form/label[2]/input'))
        )
        password_input.send_keys(password)  # Заполнение поля пароля

        login_button_two = WebDriverWait(driver, 15).until(
            exp_cond.element_to_be_clickable((By.XPATH, '//*[@id="zhtml"]/body/div[5]/div/div/div[2]/div[2]/div[2]/form/button'))
        )
        login_button_two.click()  # Клик по кнопке "Войти"
        time.sleep(2)

        serves_list = get_auto_services_link(get_auto_services_with_reviews(driver))
        for service in serves_list:
            extract_last_review_and_copy(driver, service)

    except TimeoutError as e:
        logger.error(f'Превышено время ожидания при входе в систему: {e}')
    except Exception as e:
        logger.error(f'Ошибка при входе в систему: {e}', exc_info=True)

