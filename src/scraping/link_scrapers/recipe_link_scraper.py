from abc import ABC, abstractmethod
from time import sleep

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm


class RecipeLinkScraper(ABC):
    base_link: str
    num_pages: int
    sleep_rate: int = 10
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    }

    def gather_links(self, filename):
        all_links = set()

        with tqdm(range(self.num_pages), desc="Scraping Recipes") as progress_bar:
            for page in progress_bar:
                request_url = self.base_link.format(page=page + 1)
                page_request = requests.get(request_url, headers=self.headers)

                progress_bar.set_description(
                    f"Page {page + 1}, Status {page_request.status_code}"
                )

                if page_request.status_code == 200:
                    links = self._page_specfic_scraping(page_request.content)

                    all_links.update(links)
                else:
                    print(page_request.json())

                if page % self.sleep_rate == 0:
                    sleep(3)

                if page % 100 == 0:
                    with open(filename, "w") as file:
                        file.write("\n".join(all_links))

        with open(filename, "w") as file:
            file.write("\n".join(all_links))

    @abstractmethod
    def _page_specfic_scraping(self, page_soup: BeautifulSoup) -> list:
        pass
