import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from repository.database import init_db
from repository.crud import save_listing
import time

from repository.models import Listing


def init_driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    return driver

def scrape_listing_page(driver, url):
    try:
        driver.get(url)

        wait = WebDriverWait(driver, 10)

        result = {}

        try:
            agency_map = wait.until(EC.presence_of_element_located((By.ID, "item_map")))
            latitude = float(agency_map.get_attribute("data-lat"))
            longitude = float(agency_map.get_attribute("data-lng"))

        except Exception:
            latitude = None
            longitude = None

        result["longitude"] = longitude
        result["latitude"] = latitude


        try:
            og_title = driver.find_element(By.XPATH, '//meta[@property="og:title"]').get_attribute('content')
            og_description = driver.find_element(By.XPATH, '//meta[@property="og:description"]').get_attribute(
                'content')
        except Exception as e:
            logging.error(f"Error extracting meta tags: {e}")
            og_title = "N/A"
            og_description = "N/A"

        result["og_title"] = og_title
        result["og_description"] = og_description


        try:
            owner_name = driver.find_element(By.CLASS_NAME, "product-owner__info-name").text
            owner_type = driver.find_element(By.CLASS_NAME, "product-owner__info-region").text
        except Exception:
            owner_name = driver.find_element(By.CLASS_NAME, "product-owner__residence-info-name").text
            owner_type = driver.find_element(By.CLASS_NAME, "product-owner__residence-info-region").text

        result["owner_name"] = owner_name
        result["owner_type"] = owner_type

        category_label = "Kateqoriya"
        try:
            category = driver.find_element(By.XPATH, f'//label[contains(text(), "{category_label}")]/following-sibling::span').text
        except Exception:
            category = "N/A"

        result["category"] = category

        area_label = "Sahə"
        try:
            area = driver.find_element(By.XPATH, f'//label[contains(text(), "{area_label}")]/following-sibling::span').text
        except Exception:
            area = 0.0
        result["area"] = float(area.split()[0])

        land_area_label = "Torpaq sahəsi"
        try:
            land_area = driver.find_element(By.XPATH, f'//label[contains(text(), "{land_area_label}")]/following-sibling::span').text
        except Exception:
            land_area = None

        result["land_area"] = land_area

        room_count_label = "Otaq sayı"
        try:
            room_count = driver.find_element(By.XPATH, f'//label[contains(text(), "{room_count_label}")]/following-sibling::span').text
        except Exception:
            logging.error(f"Error extracting room counts")
            room_count = 0

        result["room_count"] = int(room_count)

        deed_label = "Çıxarış"
        try:
            deed_status = driver.find_element(By.XPATH, f'//label[contains(text(), "{deed_label}")]/following-sibling::span').text
            if deed_status == "var":
                deed_status = True
            elif deed_status == "yoxdur":
                deed_status = False
        except Exception:
            logging.error(f"Error extracting deed status")
            deed_status = False

        result["deed_status"] = deed_status

        renovation_label = "Təmir"
        try:
            renovation_status = driver.find_element(By.XPATH, f'//label[contains(text(), "{renovation_label}")]/following-sibling::span').text
            if renovation_status == "var":
                renovation_status = True
            elif renovation_status == "yoxdur":
                renovation_status = False
        except Exception:
            logging.error(f"Error extracting renovation status")
            renovation_status = False

        result["renovation_status"] = renovation_status

        image_urls = []
        try:
            span_elements = driver.find_elements(By.CLASS_NAME, 'product-photos__slider-top-i_background')
            for span in span_elements:
                try:
                    style_attr = span.get_attribute('style')
                    image_url = style_attr.split("url('")[1].split("')")[0]
                    image_urls.append(image_url)
                except Exception:
                    pass

            if not image_urls:
                img_elements = driver.find_elements(By.TAG_NAME, 'img')
                for img in img_elements:
                    try:
                        image_url = img.get_attribute('src')
                        image_urls.append(image_url)
                    except Exception:
                        pass
        except Exception as e:
            pass

        result["image_urls"] = image_urls
        return result

    except Exception as e:
        logging.error(f"Error scraping listing page {url}: {e}")



def scrape_bina_az():
    driver = init_driver()

    try:
        driver.get('https://bina.az/alqi-satqi')
        wait = WebDriverWait(driver, 10)
        init_db()

        start_time = time.time()

        while True:

            elapsed_time = time.time() - start_time

            if elapsed_time >= 10 * 60:
                logging.info("10 minutes of scraping completed. Taking a break.")
                time.sleep(10 * 60)
                start_time = time.time()

            search_container = wait.until(EC.presence_of_element_located((By.ID, "js-items-search")))
            listings = search_container.find_elements(By.XPATH, './/div[contains(@class, "items-i")]')

            for listing_index in range(len(listings)):
                try:
                    listings = search_container.find_elements(By.XPATH, './/div[contains(@class, "items-i")]')
                    listing = listings[listing_index]

                    entity_to_save = Listing()

                    url = listing.find_element(By.XPATH, './/a').get_attribute('href')
                    entity_to_save.url = url

                    data_item_id = url.split("/")[-1]
                    entity_to_save.data_item_id = int(data_item_id)

                    try:
                        price = listing.find_element(By.XPATH, './/span[@class="price-val"]').text
                    except Exception:
                        logging.error(f"Error extracting price")
                        price = 0
                    entity_to_save.price = int("".join(price.split()))

                    location = listing.find_element(By.XPATH, './/div[contains(@class, "location")]').text
                    entity_to_save.location = location

                    field_dict = scrape_listing_page(driver, url)

                    entity_to_save.longitude = field_dict["longitude"]
                    entity_to_save.latitude = field_dict["latitude"]
                    entity_to_save.area = field_dict["area"]
                    entity_to_save.land_area = field_dict["land_area"]
                    entity_to_save.room_count = field_dict["room_count"]
                    entity_to_save.deed_status = field_dict["deed_status"]
                    entity_to_save.renovation_status = field_dict["renovation_status"]
                    entity_to_save.og_title = field_dict["og_title"]
                    entity_to_save.og_description = field_dict["og_description"]
                    entity_to_save.owner_name = field_dict["owner_name"]
                    entity_to_save.owner_type = field_dict["owner_type"]
                    entity_to_save.category = field_dict["category"]
                    entity_to_save.image_urls = field_dict["image_urls"]

                    print(f"Title: {entity_to_save.og_title}")
                    print(f"Url: {entity_to_save.url}")
                    print(f"Data item id: {entity_to_save.data_item_id}")
                    print(f"Description: {entity_to_save.og_description}")
                    print(f"Price: {entity_to_save.price}")
                    print(f"Location: {entity_to_save.location}")
                    print(f"Room Count: {entity_to_save.room_count}")
                    print(f"Deed Status: {entity_to_save.deed_status}")
                    print(f"Renovation Status: {entity_to_save.renovation_status}")
                    print(f"Owner Name: {entity_to_save.owner_name}")
                    print(f"Owner Type: {entity_to_save.owner_type}")
                    print(f"Category: {entity_to_save.category}")
                    print(f"Image URLs: {entity_to_save.image_urls}")
                    print(f"Longitude: {entity_to_save.longitude}")
                    print(f"Latitude: {entity_to_save.latitude}")
                    print(f"Area: {entity_to_save.area}")
                    print(f"Land Area: {entity_to_save.land_area}")
                    print("="*50)

                    save_listing(entity_to_save)


                    driver.back()
                    wait.until(EC.presence_of_element_located((By.ID, "js-items-search")))

                except Exception:
                    pass

            try:
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@rel="next"]')))
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                next_button.click()

                wait.until(EC.presence_of_element_located((By.ID, "js-items-search")))
                print("Moving to the next page...")
                time.sleep(2)

            except Exception as e:
                logging.error(f"No more pages or error with pagination: {e}")
                break

    finally:
        driver.quit()



if __name__ == "__main__":
    scrape_bina_az()
