from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup as bs


def do_request(url):
    headers = {"User-Agents" :"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.text
    else:
        raise ConnectionError


def retry_connection(url):
    for i in range(1, 11):
        try:
            return do_request(url)
        except ConnectionError:
            print(f"{i}. Connection Error... Retrying...")
            continue
    raise ConnectionError


def replace_whitespaces(string: str):
    return string.replace(" ", "-")


class Scraper(ABC):
    def __init__(self, media_title: str = ""):
        self.media_title = media_title.strip()
        self.title = None
        self.source = None
        self.thumbnail = None
        self.description = None
        self.image = None
        self.main_page_data = None

    @abstractmethod
    def scrape_main(self):
        ...

    @abstractmethod
    def scrape_media(self):
        ...

    def get_results(self):
        return {
            "title": self.title,
            "source": self.source,
            "thumbnail": self.thumbnail,
            "description": self.description,
            "image": self.image
        }

    def get_main_page_data(self):
        return self.main_page_data


class ScraperPutLockers(Scraper):

    def __init__(self, media_title: str):
        super().__init__(media_title)
        self.soup = None
        self.url = "https://putlockers.llc"

    def deconstruct_page_item(self, item):
        image = item.find("img", {"class": "film-poster-img"})
        image_src = image.get("data-src")
        image_alt = image.get("alt")
        title = item.find("h3", {"class": "film-name"}).text.strip()
        source = self.url + item.find("a", {"class": "film-poster-ahref"}).get("href")
        return {
            "image": {
                "src": image_src,
                "alt": image_alt
            },
            "title": title,
            "source": source
        }

    def scrape_main(self):
        html = do_request(self.url)
        self.soup = bs(html, "html.parser")
        if not self.soup:
            self.soup = retry_connection(self.url)

        def get_main_page_section_titles() -> list:
            """Scrapes the main page to get the titles of the sections. Such as Trending and Latest"""

            sections = self.soup.find_all("section", {"class": ["block_area", "block_area_home"]})
            section_titles = map(lambda x: x.find("h2", {"class", "cat-heading"}).text.strip(), sections)
            return list(section_titles)

        def get_main_page_single_section_data(section_number: int):
            outer_movies_container = self.soup.find_all("section",
                                                   {"class": ["block_area", "block_area_home"]})[section_number]
            movies_data_container = outer_movies_container.find_all("div", {"class": "flw-item"})
            movies_data = list(map(self.deconstruct_page_item, movies_data_container))
            return movies_data

        main_data = {}
        for i, section_title in enumerate(get_main_page_section_titles()):
            main_data[section_title] = get_main_page_single_section_data(section_number=i)

        return main_data

    def scrape_media(self):
        html = do_request(self.url + f"/search/{replace_whitespaces(self.media_title)}")
        self.soup = bs(html, "html.parser")
        if not self.soup:
            self.soup = retry_connection(self.url)

        results_container = self.soup.find("div", {"class": "film_list-wrap"})
        movies = results_container.find_all("div", {"class": "flw-item"})
        results = list(map(self.deconstruct_page_item, movies))
        return results
