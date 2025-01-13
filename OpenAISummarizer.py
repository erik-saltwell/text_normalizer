import openai

class OpenAISummarizer:

    @staticmethod
    def summarize_document(text: str, summarization_prompt: str) -> str:
        """
        Summarizes a document using OpenAI's API.

        Args:
            text (str): The content of the document to be summarized.
            summarization_prompt (str): The summarization instruction to be used as the system prompt.

        Returns:
            str: The summarized text.
        """
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": summarization_prompt},
                {"role": "user", "content": text}
            ],
            max_tokens=500,  # Adjust based on expected summary length
            temperature=0.7
        )
        return str(response.choices[0].message.content).strip()
