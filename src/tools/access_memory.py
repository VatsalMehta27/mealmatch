import chromadb
import os

# Get the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

# Initialize a persistent ChromaDB client to store agent memory
database = chromadb.PersistentClient(path=f"{project_root}/chromadb")


def access_memory(query: str, n_results: int = 1) -> list[dict]:
    """
    Retrieve documents from the 'memory' collection in ChromaDB based on a query.

    Args:
        query (str): The query string to search for in the collection.
        n_results (int): The maximum number of results to return. Defaults to 1.

    Returns:
        list[dict]: A list of retrieved documents matching the query.
    """
    # Get or create a 'memory' collection for storing and retrieving recipes
    collection = database.get_or_create_collection(name="memory")

    # Query the collection and retrieve the specified number of results
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    # Return the documents from the query results
    return results["documents"]
