from time import sleep
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

base_page = "https://allthehealthythings.com/recipe-index/?fwp_paged={page}"
max_page = 59

# Copied headers from web browser request to mimic real user
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

recipe_links = set()

with tqdm(range(max_page), desc="Scraping Recipes") as progress_bar:
    for page in progress_bar:
        request_url = base_page.format(page=page + 1)
        page_request = requests.get(request_url, headers=headers)

        progress_bar.set_description(
            f"Page {page + 1}, Status {page_request.status_code}"
        )

        if page_request.status_code == 200:
            soup = BeautifulSoup(page_request.content, "html.parser")

            recipes = [
                a["href"]
                for a in soup.find_all("a", class_="entry-title", recursive=True)
            ]

            recipe_links.update(recipes)
        else:
            print(page_request.json())

        if page % 10 == 0:
            sleep(3)

with open("all_the_healthy_things.txt", "w") as f:
    f.write("\n".join(recipe_links))
