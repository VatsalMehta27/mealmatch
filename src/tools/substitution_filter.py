import json
from rapidfuzz import fuzz
import os

# Get the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

# Build the path to the substitutions JSON file
substitutions_path = os.path.join(project_root, "data", "substitutions.json")

# Load substitution data with error handling
try:
    with open(substitutions_path) as file:
        ALL_SUBSTITUTIONS = json.load(file)
except (FileNotFoundError, json.JSONDecodeError) as e:
    raise ValueError(f"Error loading substitutions data: {e}")


def fuzzy_string_match(str1, str2) -> bool:
    """
    Compares two strings and returns True if their similarity is at least 80%.
    """
    return fuzz.ratio(str1.lower(), str2.lower()) >= 80.0


def substitution_filter(to_replace: list[str]) -> list[dict]:
    """
    Filters substitutions based on fuzzy matching with the ingredients to replace.

    Args:
        to_replace (list): A list of ingredient names to find substitutes for.

    Returns:
        list: A list of unique substitutions or a default response.
    """
    relevant_substitutions = []

    # Iterate over each ingredient to find relevant substitutions
    for ing in to_replace:
        filtered_substitutions = filter(
            lambda sub: fuzzy_string_match(ing, sub.get("Ingredient", "")),
            ALL_SUBSTITUTIONS,
        )
        relevant_substitutions.extend(filtered_substitutions)

    # Remove duplicates by converting to a set of frozensets and back to list
    unique_substitutions = [
        dict(d) for d in {frozenset(d.items()) for d in relevant_substitutions}
    ]

    if unique_substitutions:
        return unique_substitutions

    # Default response if no relevant substitutions are found
    return [{"substitute": "remove ingredient"}]
