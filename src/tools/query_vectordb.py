import chromadb
import os

# Get the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

# Initialize a persistent ChromaDB client to store agent memory
database = chromadb.PersistentClient(path=f"{project_root}/chromadb")


def query_vectordb(query: str, n_results: int = 1) -> list[dict]:
    """
    Query the 'recipes' collection in the vector database for relevant entries.

    Args:
        query (str): The query string to search for in the collection.
        n_results (int): The number of results to retrieve. Defaults to 1.

    Returns:
        list[dict]: A list of metadata dictionaries for the matching entries.
    """
    # Get or create a 'recipes' collection in the vector database
    collection = database.get_or_create_collection(name="recipes")

    # Query the collection for the top `n_results` matching the query
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    # Return the metadata of the matched entries
    return results["metadatas"]
