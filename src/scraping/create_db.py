import hashlib
import json
import os
import re
import string
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModel
import torch
import chromadb
import os

# Get the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

# Initialize a persistent ChromaDB client to store agent memory
database = chromadb.PersistentClient(path=f"{project_root}/chromadb")

collection = database.get_or_create_collection(name="recipes")

# Load the model and tokenizer from Hugging Face
model_name = "sentence-transformers/all-MiniLM-L6-v2"  # Model selection for generating sentence embeddings
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Define batch size for processing
BATCH_SIZE = 32


def preprocess_text(text):
    """
    Preprocesses the input text by converting it to lowercase, removing special characters and punctuation,
    and removing extra whitespace.

    Parameters:
    text (str): The input text to be cleaned.

    Returns:
    str: The preprocessed text.
    """
    # Convert text to lowercase
    text = text.lower()
    # Remove special characters and punctuation
    text = re.sub(f"[{string.punctuation}]", "", text)
    # Remove extra whitespace
    text = " ".join(text.split())
    return text


def generate_embeddings(batch_texts):
    """
    Generates embeddings for a batch of input texts using a pre-trained Hugging Face model.

    Parameters:
    batch_texts (list of str): The list of text inputs for which embeddings need to be generated.

    Returns:
    numpy.ndarray: The generated embeddings for the batch of texts.
    """
    inputs = tokenizer(
        batch_texts, return_tensors="pt", truncation=True, max_length=512, padding=True
    )
    with torch.no_grad():
        outputs = model(**inputs)
    # Perform mean pooling to get a single vector per text
    return outputs.last_hidden_state.mean(dim=1).numpy()


def batched_json_loader(file_path, batch_size):
    """
    Reads a JSON file and yields its content in batches.

    Parameters:
    file_path (str): The path to the JSON file to be read.
    batch_size (int): The size of each batch.

    Yields:
    list of dict: A batch of recipes from the JSON file.
    """
    with open(file_path, "r") as f:
        recipes = json.load(f)

    # Filter out recipes that have an "error" key
    recipes = [r for r in recipes if "error" not in r]

    for i in range(0, len(recipes), batch_size):
        yield recipes[i : i + batch_size]


def load_file(filename):
    """
    Processes and loads data from a JSON file into the ChromaDB collection, generating embeddings and
    adding the text, metadata, and embeddings to the collection.

    Parameters:
    filename (str): The path to the JSON file to be processed.
    """
    for batch in tqdm(
        batched_json_loader(filename, BATCH_SIZE),
        desc=f"Processing {filename} batches",
    ):
        batch_texts = []
        batch_metadata = []
        batch_ids = []

        for recipe in batch:
            # Concatenate recipe fields to form the full text input
            text = " ".join(
                [
                    str(recipe.get("title", "")),
                    str(recipe.get("description", "")),
                    " ".join(recipe.get("ingredients", [])),
                    " ".join(recipe.get("instructions", [])),
                    str(recipe.get("cuisine", "")),
                    " ".join(recipe.get("category", [])),
                ]
            )
            batch_texts.append(preprocess_text(text))

            # Create metadata dictionary for each recipe
            metadata = {
                "prep_time": str(recipe.get("prep_time")),
                "cook_time": str(recipe.get("cook_time")),
                "total_time": str(recipe.get("total_time")),
                "title": str(recipe.get("title", "")),
                "category": ", ".join(recipe.get("category", [])),
                "cuisine": str(recipe.get("cuisine", "")),
                "description": str(recipe.get("description", "")),
                "ingredients": ", ".join(recipe.get("ingredients", [])),
                "instructions": ", ".join(recipe.get("instructions", [])),
                "nutrients": json.dumps(recipe.get("nutrients", "")),
                "yields": str(recipe.get("yields", "")),
                "url": recipe.get("url", ""),
            }
            batch_metadata.append(metadata)

            # Generate a unique ID based on the recipe URL
            batch_ids.append(
                hashlib.sha256(recipe.get("url", "").encode("utf-8")).hexdigest()
            )

        # Generate embeddings for the current batch of recipes
        batch_embeddings = generate_embeddings(batch_texts)

        # Insert batch data into the ChromaDB collection
        collection.add(
            embeddings=batch_embeddings.tolist(),
            documents=batch_texts,  # Store full text of each recipe
            metadatas=batch_metadata,  # Store detailed metadata of each recipe
            ids=batch_ids,  # Unique IDs for each recipe
        )

    print(f"All recipes from {filename} inserted into the vector database.")


# Main block for loading all JSON files in the specified directory
if __name__ == "__main__":
    files = os.listdir("./data/scraped_json/")

    for file in files:
        load_file("./data/scraped_json/" + file)
