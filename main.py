import time
from selenium.webdriver.common.by import By
import mlx_functions as mlx
from proxies_and_extensions import proxies, extension_paths

def automation(driver, profile_id, token) -> None:

    try:
        driver.get("https://www.scrapethissite.com/pages/")
        print(f'The title of the webpage is: "{driver.title}"\n')
        articles = driver.find_elements(By.CLASS_NAME, "page")
        print(f'There are {len(articles)} different articles on this page:\n')
        for i, article in enumerate(articles):
             article_text = article.find_element(By.TAG_NAME, "a").text
             print(f"{i+1}. {article_text}")
        time.sleep(60)
        print("\nBasic automation finished.\n")
            
    except Exception as e:
            print(f"Something happened: {e}")
            driver.quit()
    finally:
        driver.quit()
        mlx.stop_profile(profile_id, token)

def main(proxy, index, extension_paths) -> None:
    token = mlx.signin()
    profile_started = False
    while profile_started != True:
        profile_id, profile_started, message = mlx.create_profile(token, proxy, index, extension_paths)
        if profile_started == True:
                break
        print(f"Profile couldn't be started. Probably downloading core. Will wait for 60 seconds and try again. Here is the message: {message}")
        time.sleep(60)

    profile_port = mlx.start_profile(token, profile_id)
    driver = mlx.instantiate_driver(profile_port)
    automation(driver, profile_id, token)

if __name__ == "__main__":
    for i, proxy in enumerate(proxies):
        index = i + 1
        print("\n#------------------------\n")
        print(f"Starting profile number {index}\n")
        main(proxy, index, extension_paths)