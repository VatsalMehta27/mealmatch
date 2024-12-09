import hashlib
import json
import re
from typing import Literal
from src.datatypes import AgentResponse, TextResponse, ToolDescription, ToolResponse
from openai import OpenAI
import chromadb
import os

# Get the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

# Initialize a persistent ChromaDB client to store agent memory
database = chromadb.PersistentClient(path=f"{project_root}/chromadb")


class RecipeAgent:
    """
    A recipe-writing agent designed to create recipes tailored to user queries,
    including dietary restrictions and ingredient substitutions.
    """

    # Class attributes
    conversation: list[dict]
    client: OpenAI
    tools: list[ToolDescription]
    max_internal_iteration: int
    temperature: float

    BASE_SYSTEM_PROMPT = (
        "You are a highly accurate recipe-writing agent that assists users in creating recipes tailored to their dietary restrictions. "
        "If no dietary restrictions are specified, proceed to create a recipe without requesting clarification, assuming a standard diet. "
        "To respond to a user query, you must:\n"
        "1. Make tool calls to retrieve additional information or substitutions, formatting arguments as well-structured JSON as specified in the tool description.\n"
        "2. Wait for and use the tool responses explicitly from the user before proceeding. Do NOT assume or hallucinate tool responses.\n\n"
        "Guidelines:\n"
        "- Only search substitutions for ingredients explicitly requested by the user.\n"
        "- After retrieving complete context from tool responses, create a recipe tailored to the user’s needs.\n"
        "- If no dietary restrictions are provided, generate a recipe assuming no restrictions.\n"
        "- You can only call each tool available once.\n"
        "- Include any URLs retrieved as a '## References' section in your recipe response.\n\n"
        "When making a tool call:\n"
        "- Start with 'Call function_name:' on a new line, where function_name is replaced.\n"
        "- Follow with a properly formatted JSON object as described in the tool's specifications.\n\n"
        "Give your response in Markdown format."
    )

    def __init__(
        self,
        client: OpenAI,
        tools: list[ToolDescription] = [],
        max_internal_iteration: int = 5,
        temperature: float = 0.1,
    ):
        """
        Initialize the RecipeAgent.

        Args:
            client (OpenAI): The OpenAI client for generating completions.
            tools (list[ToolDescription]): List of tools the agent can use.
            max_internal_iteration (int): Max internal tool iterations per query.
            temperature (float): Sampling temperature for completions.
        """
        self.client = client
        self.tools = tools
        self.temperature = temperature
        self.max_internal_iteration = max_internal_iteration

        # Initialize conversation with the system prompt
        self.conversation = [
            {
                "role": "system",
                "content": (
                    self.BASE_SYSTEM_PROMPT
                    + f"You have access to {len(self.tools)} tools:\n\n{self._format_tool_description()}"
                ),
            },
        ]

        # Track tool usage results
        self.conversation_tool_results = {tool.name: None for tool in self.tools}

        # Reset or initialize the memory collection
        if "memory" in database.list_collections():
            database.delete_collection("memory")
        self.memory = database.get_or_create_collection(name="memory")

    def _format_tool_description(self) -> str:
        """
        Format the tool descriptions for the system prompt.

        Returns:
            str: A formatted string of all tool descriptions.
        """
        return "\n-".join([tool.get_prompt() for tool in self.tools])

    def _chat_completion(self, conversation: list[dict]) -> str:
        """
        Generate a chat completion based on the conversation history.

        Args:
            conversation (list[dict]): The current conversation context.

        Returns:
            str: The assistant's response.
        """
        completion = self.client.chat.completions.create(
            messages=conversation,
            model="meta-llama/Meta-Llama-3.1-8B-Instruct",
            temperature=self.temperature,
        )
        return completion.choices[0].message.content

    def _extract_json(
        self, text: str, name: str, match_num: int = 0
    ) -> dict | Literal["failed"]:
        """
        Extract a JSON object for a tool call from the assistant's response.

        Args:
            text (str): The assistant's response containing the tool call.
            name (str): The name of the tool.
            match_num (int): The match index to extract (default is 0).

        Returns:
            dict | Literal["failed"]: The extracted JSON object or "failed" if parsing fails.
        """
        pattern = rf"Call {name}:\s*```json\n\{{[\s\S]*?\n\}}\n```"
        matches = list(re.finditer(pattern, text))
        if match_num < len(matches):
            match = matches[match_num]
            json_object = match.group(0).strip(f"Call {name}:\n```json").strip("```")
            return json.loads(json_object)
        return "failed"

    def _summarization(self, text: str) -> str:
        """
        Summarize user input into a concise query.

        Args:
            text (str): The user input text.

        Returns:
            str: The summarized query.
        """
        summary_prompt = (
            "You are an expert at distilling user queries into precise, concise strings for multi-turn agent interaction. "
            "Using only the information explicitly provided in the user's query, summarize:\n"
            "1. The core intent of the query.\n"
            "2. Any key details or parameters required to fulfill the request.\n\n"
            "Do not infer or assume additional context."
        )
        summary_convo = [
            {"role": "system", "content": summary_prompt},
            {"role": "user", "content": f"Text to summarize:\n{text}"},
        ]
        return self._chat_completion(summary_convo)

    def say(
        self, user_message: str, add_to_memory: bool = True
    ) -> tuple[TextResponse, list[AgentResponse]]:
        """
        Process a user query and return the agent's response.

        Args:
            user_message (str): The user's query.
            add_to_memory (bool): Whether to store the response in memory.

        Returns:
            tuple: The final agent response and steps taken during processing.
        """
        steps_taken = []
        self.conversation_tool_results = {tool.name: None for tool in self.tools}

        # Keep only the system prompt and last response in conversation
        if len(self.conversation) > 1:
            self.conversation = [self.conversation[0], self.conversation[-1]]

        # Add user query to conversation
        self.conversation.append({"role": "user", "content": user_message})
        completion = self._chat_completion(self.conversation)
        self.conversation.append({"role": "assistant", "content": completion})

        # Process tool calls iteratively
        completion_tool_calls = [
            tool for tool in self.tools if f"Call {tool.name}" in completion
        ]
        internal_iterations = 0
        while (
            completion_tool_calls and internal_iterations < self.max_internal_iteration
        ):
            self.conversation = [
                msg for msg in self.conversation if msg["role"] != "assistant"
            ]
            for tool in completion_tool_calls:
                if self.conversation_tool_results[tool.name] is not None:
                    self.conversation.append(
                        {
                            "role": "user",
                            "content": f"Already executed {tool.name}. Do not use again.",
                        }
                    )
                    continue

                arguments = self._extract_json(completion, name=tool.name)
                if arguments == "failed":
                    continue

                result = tool.function(**arguments)
                self.conversation_tool_results[tool.name] = result
                self.conversation.append(
                    {
                        "role": "user",
                        "content": f"Assistant Call {tool.name}:\n{arguments}\nreturned:\n{result}",
                    }
                )
                steps_taken.append(
                    ToolResponse(
                        tool_name=tool.name, text=str(arguments), tool_result=result
                    )
                )

            completion = self._chat_completion(self.conversation)
            self.conversation.append({"role": "assistant", "content": completion})
            completion_tool_calls = [
                tool for tool in self.tools if f"Call {tool.name}" in completion
            ]
            internal_iterations += 1

        response = TextResponse(text=completion)
        steps_taken.append(response)

        # Add response to memory if enabled
        if add_to_memory:
            self.memory.add(
                documents=[response.text],
                ids=[hashlib.sha256(response.text.encode("utf-8")).hexdigest()],
            )

        return response, steps_taken
