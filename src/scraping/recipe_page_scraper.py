import json
import asyncio
import os
from aiohttp import ClientSession
from recipe_scrapers import scrape_html
from tqdm.asyncio import tqdm


async def fetch_and_scrape(link, session):
    """
    Fetches the HTML content from a given link and scrapes recipe information.

    Parameters:
    link (str): The URL of the recipe to be scraped.
    session (ClientSession): The aiohttp session used for making the HTTP request.

    Returns:
    dict: A dictionary containing the scraped recipe data or an error message.
    """
    try:
        async with session.get(link, timeout=10) as response:
            if response.status == 200:
                content = await response.read()
                recipe = scrape_html(content, org_url=link)
                recipe_dict = recipe.to_json()

                return {
                    "prep_time": recipe_dict.get("prep_time"),
                    "cook_time": recipe_dict.get("cook_time"),
                    "total_time": recipe_dict.get("total_time"),
                    "title": recipe_dict.get("title", ""),
                    "category": str(recipe_dict.get("category")).split(","),
                    "cuisine": recipe_dict.get("cuisine", ""),
                    "description": recipe_dict.get("description", ""),
                    "ingredients": recipe_dict.get("ingredients", []),
                    "instructions": recipe_dict.get("instructions_list", []),
                    "nutrients": recipe_dict.get("nutrients", ""),
                    "yields": recipe_dict.get("yields", ""),
                    "url": link,
                }
            else:
                print(response)
                return {"error": f"HTTP {response.status}", "attempted_url": link}
    except Exception as e:
        return {"error": str(e), "attempted_url": link}


async def scrape_all_links(links, batch_size=10):
    """
    Scrapes recipe data from a list of links in batches.

    Parameters:
    links (list of str): A list of URLs to be scraped.
    batch_size (int): The number of links to process in each batch.

    Returns:
    list of dict: A list of dictionaries containing the scraped recipe data or error messages.
    """
    results = []

    async with ClientSession() as session:
        for i in tqdm(
            range(0, len(links), batch_size),
            desc="Scraping recipes",
            total=(len(links) + batch_size - 1) // batch_size,
        ):
            batch_links = links[i : i + batch_size]
            tasks = [fetch_and_scrape(link, session) for link in batch_links]
            results.extend(await asyncio.gather(*tasks))

    return results


async def main(link_file, output_file):
    """
    Main function to load links from a file, scrape data from them, and save the results to an output file.

    Parameters:
    link_file (str): Path to the file containing the list of URLs to be scraped.
    output_file (str): The name of the output JSON file where the results will be stored.
    """
    # Load links
    with open(link_file, "r") as f:
        links = [link.strip() for link in f if link.strip()]  # Remove empty lines

    # Scrape recipes with full progress display
    batch_size = 10  # Adjustable batch size
    recipe_infos = await scrape_all_links(links, batch_size=batch_size)

    # Save results
    with open("./data/scraped_json/" + output_file, "w") as f:
        json.dump(recipe_infos, f, indent=4)


if __name__ == "__main__":
    # Loop through all link files in the directory and run the scraping process for each
    link_files = os.listdir("./data/scraped_links/")

    for link_file in link_files:
        output_file = f"{link_file.split('.')[0]}.json"

        asyncio.run(main("./data/scraped_links/" + link_file, output_file))
