from source.utils import ConfigLogging, get_selenium_driver, login_to_zoon

logger = ConfigLogging().setup_logger()



def main():
    try:
        email = input("Enter your email: ")
        password = input("Enter your password: ")
        logger.info("Загрузка драйвера Chrome...")

        driver = get_selenium_driver()
        login_to_zoon(driver, email, password)
    except KeyboardInterrupt as e:
        logger.info("Вы вышли из приложения")


if __name__ == '__main__':
    main()
