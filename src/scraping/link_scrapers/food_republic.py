from time import sleep
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

base_page = "https://www.foodrepublic.com/category/recipes/?ajax=1&offset={offset}"
recipe_page_base = "https://www.foodrepublic.com"
max_offset = 286

# Copied headers from web browser request to mimic real user
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
}

recipe_links = set()

with tqdm(range(max_offset), desc="Scraping Recipes") as progress_bar:
    for offset in progress_bar:
        request_url = base_page.format(offset=offset + 1)
        food_republic_page = requests.get(request_url, headers=headers)

        if food_republic_page.content == b"0":
            sleep(5)
            food_republic_page = requests.get(request_url, headers=headers)

        progress_bar.set_description(
            f"Offset {offset + 1}, Status {food_republic_page.status_code}"
        )

        if food_republic_page.status_code == 200:
            food_republic_soup = BeautifulSoup(
                food_republic_page.content, "html.parser"
            )

            recipes = [
                recipe_page_base + div.find("a", href=True)["href"]
                for div in food_republic_soup.find_all(
                    "div", class_="read-more", recursive=True
                )
            ]

            recipe_links.update(recipes)
        else:
            print(food_republic_page.json())

        if offset % 100 == 0:
            sleep(5)

with open("food_republic_links.txt", "w") as f:
    f.write("\n".join(recipe_links))
