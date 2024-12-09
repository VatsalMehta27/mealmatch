from bs4 import BeautifulSoup
from recipe_link_scraper import RecipeLinkScraper


class EatLiveRunLinkScraper(RecipeLinkScraper):
    base_link = "https://www.eatliverun.com/recipes/{page}"
    num_pages = 1

    def _page_specfic_scraping(self, page_content):
        page_soup = BeautifulSoup(page_content, "html.parser")
        links = [
            li.find("a")["href"] for li in page_soup.find_all("li", recursive=True)
        ]

        return links


if __name__ == "__main__":
    EatLiveRunLinkScraper().gather_links("eat_live_run.txt")
