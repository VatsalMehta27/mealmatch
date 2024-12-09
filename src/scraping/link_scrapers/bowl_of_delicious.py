from bs4 import BeautifulSoup
from recipe_link_scraper import RecipeLinkScraper


class BowlOfDeliciousLinkScraper(RecipeLinkScraper):
    base_link = "https://www.bowlofdelicious.com/category/recipes/page/{page}/"
    num_pages = 26

    def _page_specfic_scraping(self, page_content):
        page_soup = BeautifulSoup(page_content, "html.parser")
        links = [
            a["href"]
            for a in page_soup.find_all("a", class_="entry-image-link", recursive=True)
        ]

        return links


if __name__ == "__main__":
    BowlOfDeliciousLinkScraper().gather_links("bowl_of_delicious.txt")
