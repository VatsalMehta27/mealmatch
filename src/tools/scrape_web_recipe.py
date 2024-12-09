from recipe_scrapers import scrape_html
import requests


def scrape_web_recipe(link: str) -> dict:
    """
    Scrape recipe information from a given web page.

    Args:
        link (str): The URL of the recipe page to scrape.

    Returns:
        dict: A dictionary containing recipe details or an error message.
    """
    try:
        # Send a GET request to the recipe page
        response = requests.get(link)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page and extract the recipe details
            recipe = scrape_html(response.content, org_url=link)
            recipe_dict = recipe.to_json()

            # Extract relevant information from the parsed recipe data
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
            # Return an error if the request was unsuccessful
            return {"error": f"HTTP {response.status_code}", "attempted_url": link}
    except requests.exceptions.RequestException as req_err:
        # Handle network-related exceptions (e.g., connection errors)
        return {"error": f"Request error: {str(req_err)}", "attempted_url": link}
    except Exception as e:
        # Handle other general exceptions
        return {
            "error": str(e),
            "attempted_url": link,
        }
