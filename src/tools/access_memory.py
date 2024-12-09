import chromadb

# Initialize ChromaDB client for persistent storage
client = chromadb.PersistentClient(path="./chromadb")


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
    collection = client.get_or_create_collection(name="memory")

    # Query the collection and retrieve the specified number of results
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    # Return the documents from the query results
    return results["documents"]
