import functions_framework
import openai
import json
import os

from dotenv import load_dotenv
load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")

with open('prompt.txt', 'r') as prompt_file:
    PROMPT_BASE=prompt_file.read()

@functions_framework.http
def prompt(request):
    r = request.get_json()
    story = r["story"]
    style = r["style"]

    # Use the OpenAI API to generate the prompt
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=PROMPT_BASE + f"\nStyle: {style}\nStory: {story}.\nYou:\n",
        max_tokens=1024
    )

    # Get the generated text from the API response
    generated_text = response.choices[0].text

    # Return the generated text as a JSON response
    return json.loads(generated_text)
