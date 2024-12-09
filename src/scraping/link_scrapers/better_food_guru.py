from bs4 import BeautifulSoup
from recipe_link_scraper import RecipeLinkScraper


class BetterFoodGuruLinkScraper(RecipeLinkScraper):
    base_link = "https://betterfoodguru.com/category/recipes/page/{page}/"
    num_pages = 5

    def _page_specfic_scraping(self, page_content):
        page_soup = BeautifulSoup(page_content, "html.parser")

        links = [
            li.find("a", class_="")["href"]
            for li in page_soup.find_all("li", class_="listing-item", recursive=True)
        ]

        return links


if __name__ == "__main__":
    BetterFoodGuruLinkScraper().gather_links("better_food_guru.txt")
