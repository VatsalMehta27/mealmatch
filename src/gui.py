import os
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr
from src.agents import RecipeAgent
from src.datatypes import ToolDescription, TextResponse
from src.tools import (
    query_vectordb,
    substitution_filter,
    scrape_web_recipe,
    access_memory,
)

# Load environment variables from a .env file
load_dotenv()

# Initialize the OpenAI client with the base URL and API key from environment variables
client = OpenAI(base_url=os.getenv("URL"), api_key=os.getenv("KEY"))

# Define the tools available for the RecipeAgent
tools = [
    ToolDescription(
        name="query_vectordb",
        signature="query_vectordb(query: str, n_results=1)",
        description="This function searches a vector database for recipes similar to the query argument.",
        example_json='Call query_vectordb:\n```json\n{\n"query": "banana bread recipe"\n}\n```',
        function=query_vectordb,
    ),
    ToolDescription(
        name="substitution_filter",
        signature="substitution_filter(to_replace: list[str])",
        description=(
            "This function searches for ingredient alternatives based on a list of ingredients to be substituted."
            " Only the ingredients to substitute should be provided as arguments."
        ),
        example_json='Call substitution_filter:\n```json\n{\n"to_replace": ["eggs", "flour"]\n}\n```',
        function=substitution_filter,
    ),
    ToolDescription(
        name="scrape_web_recipe",
        signature="scrape_web_recipe(link: str)",
        description="This function scrapes the recipe at the provided link. Use when a user provides a recipe link.",
        example_json='Call scrape_web_recipe:\n```json\n{\n"link": "https://www.allrecipes.com/lemon-garlic-butter"\n}\n```',
        function=scrape_web_recipe,
    ),
    ToolDescription(
        name="access_memory",
        signature="access_memory(query: str, n_results=1)",
        description="This function retrieves the most similar previous agent-user conversation for context.",
        example_json='Call access_memory:\n```json\n{\n"query": "eggless banana bread recipe"\n}\n```',
        function=access_memory,
    ),
]

# Create the RecipeAgent instance with the initialized client and tools
recipe_agent = RecipeAgent(client, tools)


def chat(user_input: str, history):
    """
    Handles the chat interaction, using the RecipeAgent to generate a response based on user input.
    Appends the user input and agent response to the conversation history.

    Parameters:
    - user_input (str): The input message from the user.
    - history (list): The chat history to be updated.

    Returns:
    - Tuple of an empty string (for clearing input) and the updated history.
    """
    # Generate a response from the agent and get the steps taken (if needed)
    agent_response, _ = recipe_agent.say(user_input)
    message = ""

    # Check if the response is a text response and extract the text
    if isinstance(agent_response, TextResponse):
        message = agent_response.text

    # Append the user input and response to the conversation history
    history.append((user_input, message))
    return "", history


# Define the style for the chatbot interface
chatbot_style = """
<style>
  #chatbot {
    min-height: 500px; /* Adjust the minimum height as needed */
  }
</style>
"""

# Create the Gradio interface for the chatbot
with gr.Blocks() as demo:
    gr.Markdown(
        "<h1 style='text-align: center; font-size: 3em;'>MealMatch</h1>" + chatbot_style
    )

    # Set up the chat interface components
    chatbot = gr.Chatbot(elem_id="chatbot")
    user_input_box = gr.Textbox(
        show_label=False, placeholder="Type your question here..."
    )
    clear_button = gr.ClearButton([chatbot, user_input_box])

    # Bind the chat function to the user input
    user_input_box.submit(
        chat, inputs=[user_input_box, chatbot], outputs=[user_input_box, chatbot]
    )

# Launch the Gradio interface
demo.launch()
