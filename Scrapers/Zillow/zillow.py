import os
import json

# Date & Time
import time
import datetime as dt

import numpy as np
import pandas as pd

# Periphery
from Scrapers.Zillow.Periphery.mappings import urls

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (iPhone14,3; U; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/19A346 Safari/602.1",
    # Add more User-Agent strings as needed
]


my_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument(f"--user-agent={user_agents[0]}")
# chrome_options.add_argument("--headless") NOTE: Running in headless will result in empty dataframes.
chrome_options.add_argument("--disable-gpu")


class Zillow:
    def __init__(self, city: str, state: str) -> None:
        self.city = city
        self.state = state
        self.label = f"{city.lower()}-{state.lower()}"

        # Urls
        self.url = (
            "https://www.zillow.com/{}/sold/?searchQueryState=%7B%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-122.4534480199699%2C%22east%22%3A-120.7066218480949%2C%22south%22%3A37.18351884593523%2C%22north%22%3A38.37418115473503%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A12592%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%2C%22rs%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22apco%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22usersSearchTerm%22%3A%22{}%20{}%22%7D",
        )

        self.alt_url = (
            "https://www.zillow.com/{}/sold/{}_p/?searchQueryState=%7B%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-122.4534480199699%2C%22east%22%3A-120.7066218480949%2C%22south%22%3A37.18351884593523%2C%22north%22%3A38.37418115473503%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A12592%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%2C%22rs%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22apco%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22usersSearchTerm%22%3A%22{}%20{}%22%2C%22pagination%22%3A%7B%22currentPage%22%3A2%7D%7D",
        )

        self.chrome_driver_path = self._get_chrome_driver_path()
        self.data_export_path = self._get_data_export_path()

        self.data_export_path = f"{self.data_export_path}\\Zillow"
        os.makedirs(self.data_export_path, exist_ok=True)

    """
    ====================================
    Local Paths
    ====================================
    """

    def _get_data_export_path(self):
        project = "HomePrices"
        try:
            internal_path = f"{os.getcwd()}\\config.json"
            with open(internal_path, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            external_path = f"{os.getcwd()}\\{project}\\config.json"
            with open(external_path, "r") as file:
                data = json.load(file)
        return data["data_export_path"]

    def _get_chrome_driver_path(self):
        project = "HomePrices"
        try:
            internal_path = f"{os.getcwd()}\\config.json"
            with open(internal_path, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            external_path = f"{os.getcwd()}\\{project}\\config.json"
            with open(external_path, "r") as file:
                data = json.load(file)
        return data["chrome_driver_path"]

    """-----------------------------------"""
    """
    ====================================
    Browser Operations
    ====================================
    """

    def _create_browser(self, url=None):
        """
        :param url: The website to visit.
        :return: None
        """
        service = Service(executable_path=self.chrome_driver_path)
        self.browser = webdriver.Chrome(service=service, options=chrome_options)
        # Default browser route
        if url == None:
            self.browser.get(url=self.sec_annual_url)
        # External browser route
        else:
            self.browser.get(url=url)

    def _clean_close(self) -> None:
        self.browser.close()
        self.browser.quit()

    def _read_data(
        self, xpath: str, wait: bool = False, _wait_time: int = 5, tag: str = ""
    ) -> str:
        """
        :param xpath: Path to the web element.
        :param wait: Boolean to determine if selenium should wait until the element is located.
        :param wait_time: Integer that represents how many seconds selenium should wait, if wait is True.
        :return: (str) Text of the element.
        """

        if wait:
            try:
                data = (
                    WebDriverWait(self.browser, _wait_time)
                    .until(EC.presence_of_element_located((By.XPATH, xpath)))
                    .text
                )
            except TimeoutException:
                print(f"[Failed Xpath] {xpath}")
                if tag != "":
                    print(f"[Tag]: {tag}")
                raise NoSuchElementException("Element not found")
            except NoSuchElementException:
                print(f"[Failed Xpath] {xpath}")
                return "N\A"
        else:
            try:
                data = self.browser.find_element("xpath", xpath).text
            except NoSuchElementException:
                data = "N\A"
        # Return the text of the element found.
        return data

    def _click_button(
        self,
        xpath: str,
        wait: bool = False,
        _wait_time: int = 5,
        scroll: bool = False,
        tag: str = "",
    ) -> None:
        """
        :param xpath: Path to the web element.
        :param wait: Boolean to determine if selenium should wait until the element is located.
        :param wait_time: Integer that represents how many seconds selenium should wait, if wait is True.
        :return: None. Because this function clicks the button but does not return any information about the button or any related web elements.
        """

        if wait:
            try:
                element = WebDriverWait(self.browser, _wait_time).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                # If the webdriver needs to scroll before clicking the element.
                if scroll:
                    self.browser.execute_script("arguments[0].click();", element)
                element.click()
            except TimeoutException:
                print(f"[Failed Xpath] {xpath}")
                if tag != "":
                    print(f"[Tag]: {tag}")
                raise NoSuchElementException("Element not found")
        else:
            element = self.browser.find_element("xpath", xpath)
            if scroll:
                self.browser.execute_script("arguments[0].click();", element)
            element.click()

    def scroll_page(
        self,
        pixel_to_scroll: int = 500,
        element_to_scroll="",
        by_pixel: bool = True,
        by_element: bool = False,
    ) -> None:
        """
        :param element_to_scroll: Scroll to the specified element on the webpage.
        :returns: There is no data to return.
        """
        if by_pixel:
            self.browser.execute_script(f"window.scrollBy(0, {pixel_to_scroll})", "")

        if by_element:
            self.browser.execute_script(
                "arguments[0].scrollIntoView(true);", element_to_scroll
            )

    """
    ====================================
    Browser Operations
    ====================================
    """

    def scrape_page(self, page: int, export: bool = False, overwrite: bool = False):
        # if page == 1:
        #     if type(self.url) == tuple:
        #         self.url = self.url[0]

        #     self._create_browser(self.url.format(self.label, self.city, self.state))

        # else:
        #     if type(self.alt_url) == tuple:
        #         self.alt_url = self.alt_url[0]
        #     self._create_browser(
        #         self.alt_url.format(self.label, page, self.city, self.state)
        #     )
        url = urls[page].format(self.label, self.city, self.state)
        print(f"Url: {url}")
        self._create_browser(url)
        start_card_index = 1
        card_xpath = "/html/body/div[1]/div/div[2]/div/div/div[1]/div[1]/ul/li[{}]"
        card_data = []
        fail_count = 0
        scraping = True
        while scraping:
            try:
                current_card = card_xpath.format(start_card_index)
                c = self._scrape_card2(current_card)
                if c != {}:
                    card_data.append(c)
                    print(f"--------------------------[Card]: {card_data}")
                start_card_index += 1
            except NoSuchElementException:
                fail_count += 1
                start_card_index += 1
                self.scroll_page(pixel_to_scroll=1500, by_pixel=True)
                if fail_count >= 10:
                    # self._click_button(next_page, wait=True)
                    scraping = False

            # if start_card_index == 15:
            #     self.scroll_page(pixel_to_scroll=500, by_pixel=True)
        self._clean_close()
        df = pd.DataFrame(card_data)

        if export:

            self._export_page(df, page_number=page, overwrite=overwrite)

    def _export_page(self, df: pd.DataFrame, page_number: int, overwrite: bool):
        path = f"Pages\\page_{page_number}.csv"

        if overwrite:
            df.to_csv(path)
        else:
            try:
                local = pd.read_csv(path)
            except FileNotFoundError:
                df.to_csv(path)

    def _scrape_card(self, xpath: str):
        ad_xpath = f"{xpath}/html/body/div[2]/div[1]/div/a/div[1]/div[1]"
        sponsor_xpath = f"{xpath}/html/body/div[2]/div[1]/div/a/div[1]/div[1]"
        date_xpath = f"{xpath}/div/div/article/div/div[2]/div[1]/div[1]/span"
        price_xpath = f"{xpath}/div/div/article/div/div[1]/div[2]/div/span"
        bed_xpath = f"{xpath}/div/div/article/div/div[1]/div[3]/ul/li[1]/b"
        bed_xpath = f"{xpath}/div/div/article/div/div[1]/div[3]/ul/li[1]/b"
        bath_xpath = f"{xpath}/div/div/article/div/div[1]/div[3]/ul/li[2]/b"
        sqft_xpath = f"{xpath}/div/div/article/div/div[1]/div[3]/ul/li[3]/b"
        location_xpath = f"{xpath}/div/div/article/div/div[1]/a/address"

        is_ad = self.is_advertisement(ad_xpath, sponsor_xpath)

        if not is_ad:
            # Get date & clean
            date = self._read_data(date_xpath, wait=True)
            date = date.split(" ")[1]

            # Get price & clean data
            try:
                price = self._read_data(price_xpath, wait=True)
                price = price.replace("$", "").replace(",", "")
                if "M" in price:
                    price = price.replace("M", "")
                    price = float(price) * 1_000_000

                price = int(price)
            except ValueError:
                price = np.nan
            # Get number of bedrooms and clean
            try:
                bedrooms = self._read_data(bed_xpath, wait=True)
                bedrooms = int(bedrooms)
            except ValueError:
                bedrooms = np.nan
            # Get number of bathrooms and clean
            try:
                bathrooms = self._read_data(bath_xpath, wait=True)
                bathrooms = int(bathrooms)
            except ValueError:
                bathrooms = np.nan
            # Get sqft and clean
            try:
                sqft = self._read_data(sqft_xpath, wait=True)
                sqft = sqft.replace(",", "")
                sqft = int(sqft)
            except ValueError:
                sqft = np.nan
            # Get Location and clean
            location = self._read_data(location_xpath, wait=True)
            address, city, state = location.split(",")
            city = city.strip(" ")
            state = state.split(" ")[1]
            state = state.strip(" ")

            # Calculate price/sqft
            try:
                price_sqft = price / sqft
                price_sqft = "{:,.2f}".format(price_sqft)
            except ValueError:
                price_sqft = np.nan

            data = {
                "date": date,
                "price": price,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "sqft": sqft,
                "$/sqft": price_sqft,
                "address": address,
                "city": city,
                "state": state,
            }
            return data
        else:
            return {}

    def _scrape_card2(self, xpath: str):
        ad_xpath = f"{xpath}/html/body/div[2]/div[1]/div/a/div[1]/div[1]"
        sponsor_xpath = f"{xpath}/html/body/div[2]/div[1]/div/a/div[1]/div[1]"
        date_xpath = f"{xpath}/div/div/article/div/div[2]/div[1]/div[1]/span"
        price_xpath = f"{xpath}/div/div/article/div/div[1]/div[2]/div/span"
        bed_xpath = f"{xpath}/div/div/article/div/div[1]/div[3]/ul/li[1]/b"
        bed_xpath = f"{xpath}/div/div/article/div/div[1]/div[3]/ul/li[1]/b"
        bath_xpath = f"{xpath}/div/div/article/div/div[1]/div[3]/ul/li[2]/b"
        sqft_xpath = f"{xpath}/div/div/article/div/div[1]/div[3]/ul/li[3]/b"
        location_xpath = f"{xpath}/div/div/article/div/div[1]/a/address"
        # Get date & clean
        date = self._read_data(date_xpath, wait=True)
        date = date.split(" ")

        if len(date) == 2:
            date = date[1]
            # Get price & clean data
            try:
                price = self._read_data(price_xpath, wait=True)
                price = price.replace("$", "").replace(",", "")
                if "M" in price:
                    price = price.replace("M", "")
                    price = float(price) * 1_000_000

                price = int(price)
            except ValueError:
                price = np.nan
            # Get number of bedrooms and clean
            try:
                bedrooms = self._read_data(bed_xpath, wait=True)
                bedrooms = int(bedrooms)
            except ValueError:
                bedrooms = np.nan
            # Get number of bathrooms and clean
            try:
                bathrooms = self._read_data(bath_xpath, wait=True)
                bathrooms = int(bathrooms)
            except ValueError:
                bathrooms = np.nan
            # Get sqft and clean
            try:
                sqft = self._read_data(sqft_xpath, wait=True)
                sqft = sqft.replace(",", "")
                sqft = int(sqft)
            except ValueError:
                sqft = np.nan
            # Get Location and clean
            location = self._read_data(location_xpath, wait=True)
            address, city, state = location.split(",")
            city = city.strip(" ")
            state = state.split(" ")[1]
            state = state.strip(" ")

            # Calculate price/sqft
            try:
                price_sqft = price / sqft
                price_sqft = "{:,.2f}".format(price_sqft)
            except ValueError:
                price_sqft = np.nan

            data = {
                "date": date,
                "price": price,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "sqft": sqft,
                "$/sqft": price_sqft,
                "address": address,
                "city": city,
                "state": state,
            }
            return data
        else:
            return {}

    def is_advertisement(self, ad_xpath, sponsor_xpath):
        is_ad = False
        is_sponsor = False

        try:
            ad = self._read_data(ad_xpath, wait=True)
            is_ad = True
        except NoSuchElementException:
            pass
        try:
            sponsor = self._read_data(sponsor_xpath, wait=True)
            is_sponsor = True
        except NoSuchElementException:
            pass

        if is_ad or is_sponsor:
            return True
        else:
            return False

    def test(self):

        data = None
        df = pd.DataFrame(data)
        df = df.drop_duplicates("address", keep="first")
        # df.reset_index(drop=True, inplace=True)
        # print(f"DF: {df}")
        # df.to_csv(f"{self.data_export_path}\\martinez_ca.csv")

    def compile_pages(self, export: bool = False):
        dirs = os.listdir("Pages")
        all_df = pd.DataFrame()
        index = 0
        for d in dirs:
            path = f"Pages\\{d}"
            df = pd.read_csv(path)
            df.rename(columns={"Unnamed: 0": "index"}, inplace=True)
            df.set_index("index", inplace=True)

            if index == 0:
                all_df = df
            else:

                all_df = pd.concat([all_df, df], ignore_index=True)

            index += 1

        all_df = all_df.drop_duplicates("address", keep="first")
        all_df.reset_index(drop=True, inplace=True)
        print(f"All: {all_df}")
        if export:
            all_df.to_csv(f"Data\\Zillow\\{self.label}.csv")
