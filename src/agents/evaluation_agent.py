from openai import OpenAI


class EvaluationAgent:
    BASE_SYSTEM_PROMPT = (
        "You are an evaluating agent tasked with determining whether a provided "
        "recipe meets the user’s specified dietary needs. This could either be restrictions or requests. Carefully review the recipe, "
        "including its ingredients and preparation methods, and compare it against the stated dietary needs. "
        "Respond exclusively with 'Yes' if the recipe fully complies with the needs or 'No' if it does not. "
        "Provide no further explanations or commentary. Make sure the recipe includess all requested ingredients. "
        "Common dietary restrictions include: vegetarian (no meat, but may include dairy and eggs), "
        "vegan (no animal products at all), gluten-free (no wheat, barley, rye, or cross-contaminated products), dairy-free (no milk or milk-based products), "
        "nut-free (no tree nuts or peanuts), and kosher (must adhere to Jewish dietary laws, such as avoiding pork and shellfish, and separating meat and dairy)."
    )

    def __init__(self, client: OpenAI, temperature: float = 0.0):
        self.client = client
        self.temperature = temperature

    def _chat_completion(self, conversation: list[dict]) -> str:
        completion = self.client.chat.completions.create(
            messages=conversation,
            model="meta-llama/Meta-Llama-3.1-8B-Instruct",
            temperature=self.temperature,
        )

        return completion.choices[0].message.content

    def say(self, recipe: str, criteria: str) -> str:
        conversation = [
            {"role": "system", "content": self.BASE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"The recipe to evaluate is:\n\n{recipe}\nThe criteria to meet is {criteria}",
            },
        ]

        completion = self._chat_completion(conversation)

        return completion
