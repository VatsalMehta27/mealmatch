from bs4 import BeautifulSoup
from recipe_link_scraper import RecipeLinkScraper


class CelebratingSweetsLinkScraper(RecipeLinkScraper):
    base_link = "https://celebratingsweets.com/category/all-recipes/page/{page}/"
    num_pages = 12

    def _page_specfic_scraping(self, page_content):
        page_soup = BeautifulSoup(page_content, "html.parser")
        links = [
            a["href"]
            for a in page_soup.find_all(
                "a",
                class_="entry-title-link",
                recursive=True,
            )
        ]

        return links


if __name__ == "__main__":
    CelebratingSweetsLinkScraper().gather_links("celebrating_sweets.txt")
