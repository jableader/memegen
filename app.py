from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import openai
import os

app = FastAPI()

# Get the OpenAI API key from an environment variable
api_key = os.environ.get("OPENAI_API_KEY")

# Set up OpenAI API credentials
openai.api_key = api_key

class PromptRequest(BaseModel):
    prompt: str

@app.post("/prompt")
async def generate_prompt(request: PromptRequest):
    # Use the OpenAI API to generate the prompt
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt="Show funny three sentance story titled: " + request.prompt,
        max_tokens=300
    )

    # Get the generated text from the API response
    generated_text = response.choices[0].text

    # Return the generated text as a JSON response
    return JSONResponse(content={"prompt": generated_text})
