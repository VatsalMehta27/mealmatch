from bs4 import BeautifulSoup
from recipe_link_scraper import RecipeLinkScraper


class BeyondFrostingLinkScraper(RecipeLinkScraper):
    base_link = "https://beyondfrosting.com/finder/?_paged={page}/"
    num_pages = 41

    def _page_specfic_scraping(self, page_content):
        page_soup = BeautifulSoup(page_content, "html.parser")
        links = [
            div.find("a")["href"]
            for div in page_soup.find_all(
                "div", class_="post-thumb-img-content post-thumb", recursive=True
            )
        ]

        return links


if __name__ == "__main__":
    BeyondFrostingLinkScraper().gather_links("beyond_frosting.txt")
