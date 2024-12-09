import xml.etree.ElementTree as ET
from recipe_link_scraper import RecipeLinkScraper


class FoodDotComLinkScraper(RecipeLinkScraper):
    base_link = "https://api.food.com/services/mobile/fdc/search/sectionfront?pn={page}&recordType=Recipe&collectionId=17/"
    num_pages = 20000  # 52482
    sleep_rate = 50

    def _page_specfic_scraping(self, page_content):
        try:
            root = ET.fromstring(page_content)

            recipe_links = []
            for result in root.findall(".//results"):
                record_url = result.find("record_url")

                if record_url is not None:
                    recipe_links.append(record_url.text)

            return recipe_links
        except:
            return []


if __name__ == "__main__":
    FoodDotComLinkScraper().gather_links("food.txt")
