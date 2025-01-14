import openai
import textwrap
from os import path
import json
from typing import Any
import re

class OpenAISummarizer:

    @staticmethod
    def extract_json(response_string: str) -> Any:
        """
        Extracts valid JSON from a string with extraneous text and converts it into a Python object.

        Args:
            response_string (str): The string containing the JSON content.

        Returns:
            Any: The Python object (usually a list or dict) obtained from the extracted JSON.
        """
        # Use regex to find the first valid JSON block (assuming it's wrapped in brackets [])
        match = re.search(r'\[\s*{.*?}\s*\]', response_string, re.DOTALL)
        
        if match:
            json_str = match.group(0)  # Extract the matched JSON string
            try:
                return json.loads(json_str)  # Convert JSON string to Python object
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON: {e}")
        else:
            raise ValueError("No valid JSON found in the input string.")
    
    @staticmethod
    def get_last_denser_summary(data: list[dict[str, Any]]) -> str:
        """
        Returns the Denser_Summary property of the last instance in the provided list.

        Args:
            data (List[Dict[str, Any]]): A list of dictionaries containing the data.

        Returns:
            str: The Denser_Summary of the last instance.
        """
        if not data:
            raise ValueError("The input list is empty.")
        
        if "Denser_Summary" not in data[-1]:
            raise KeyError("The last instance does not have a 'Denser_Summary' property.")
        
        return data[-1]["Denser_Summary"]


    @staticmethod
    def LoadAndSummarize(dir : str, filename:str)->str:
        full_path = path.join(dir, filename)
        text:str = ''
        with open(full_path, 'r', encoding='utf-8') as f:
            text = f.read()
        response:str = OpenAISummarizer.summarize_document(text)
        return response
    
    
        
    @staticmethod
    def summarize_document(text: str) -> str:
        """
        Summarizes a document using OpenAI's API.

        Args:
            text (str): The content of the document to be summarized.
            summarization_prompt (str): The summarization instruction to be used as the system prompt.

        Returns:
            str: The summarized text.
        """
        summarization_prompt : str = OpenAISummarizer._GetPrompt()

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": summarization_prompt},
                {"role": "user", "content": text}
            ],
            max_tokens=1500,  # Adjust based on expected summary length
            temperature=0.7
        )
        return str(response.choices[0].message.content).strip()
    
    @staticmethod   
    def _GetPrompt()->str:
        prompt : str = """
            I will provide you a story. You will generate increasingly concise, entity-dense summaries of the story. 

            Repeat the following 2 steps 5 times. 

            Step 1. Identify 1-3 informative entities (";" delimited) from the story which are missing from the previously generated summary. 
            Step 2. Write a new, denser summary of identical length which covers every entity and detail from the previous summary plus the missing entities. 

            A missing entity is:
            - relevant to the main story, 
            - specific yet concise (5 words or fewer), 
            - novel (not in the previous summary), 
            - faithful (present in the story), 
            - anywhere (can be located anywhere in the story).

            Guidelines:

            - The first summary should be long (4-5 sentences, ~80 words) yet highly non-specific, containing little information beyond the entities marked as missing. Use overly verbose language and fillers (e.g., "this story discusses") to reach ~80 words.
            - Make every word count: rewrite the previous summary to improve flow and make space for additional entities.
            - Make space with fusion, compression, and removal of uninformative phrases like "the story discusses".
            - The summaries should become highly dense and concise yet self-contained, i.e., easily understood without the story. 
            - Missing entities can appear anywhere in the new summary.
            - Never drop entities from the previous summary. If space cannot be made, add fewer new entities. 

            Remember, use the exact same number of words for each summary.
            Answer in JSON. The JSON should be a list (length 5) of dictionaries whose keys are "Missing_Entities" and "Denser_Summary".
        """
        return textwrap.dedent(prompt)[1:]

