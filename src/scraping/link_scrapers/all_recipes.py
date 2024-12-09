from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

topic_page = "https://www.allrecipes.com/recipes-a-z-6735880"
all_recipes_page = requests.get(topic_page)
all_recipes_soup = BeautifulSoup(all_recipes_page.content, "html.parser")

topic_links = set(
    [
        i["href"]
        for i in all_recipes_soup.find("div", id="mntl-alphabetical-list_1-0").find_all(
            "a", href=True
        )
    ]
)

recipe_links = set()

for link in tqdm(topic_links, total=len(topic_links)):
    recipe_page = requests.get(link)
    recipe_soup = BeautifulSoup(recipe_page.content, "html.parser")

    recipe_links.update(
        [
            i["href"]
            for i in recipe_soup.find(
                "div", id="mntl-taxonomysc-article-list-group_1-0"
            ).find_all("a", href=True)
        ]
    )

with open("allrecipes_links.txt", "w") as f:
    f.write("\n".join(recipe_links))
