import openai
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from google.cloud import storage
from pydantic import BaseModel
import requests
import openai
import os
import random
import string

from dotenv import load_dotenv
load_dotenv()

# Get the OpenAI API key from an environment variable
api_key = os.environ.get("OPENAI_API_KEY")
bucket_name = os.environ.get('GCP_BUCKET_NAME')

def rand_str(count):
    """Generate a random 8-character string."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=count))

# Set up OpenAI API credentials
openai.api_key = api_key

# Create a storage client using the default credentials
storage_client = storage.Client()

# Set up FastAPI app
app = FastAPI()

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

def save(image_url, bucket_name, object_name):
    # Get the bucket object
    bucket = storage_client.get_bucket(bucket_name)

    # Create a blob object with the desired object name
    blob = bucket.blob(object_name)

    # Download the image data from the URL
    response = requests.get(image_url)
    image_data = response.content

    # Upload the image data to the blob
    blob.upload_from_string(image_data, content_type='image/jpeg')

    # Print the public URL of the uploaded image
    return blob.public_url

# Define a method to generate frames using OpenAI API
@app.post("/frames")
async def generate_frames(prompt: str, style: str):
    prompt = style + ", " + prompt
    try:
        # Generate image URLs using OpenAI API
        response = openai.api.Completion.create(
            engine="image-alpha-001",
            prompt=prompt,
            num_images=2,
            size='512x256'
        )

        image_urls = [d['url'] for d in response['data']]
        for url in image_urls:
            save(url, bucket_name, prompt + rand_str(8))

        # Return a success message
        return JSONResponse(content={"message": "Frames generated and saved.", "urls": image_urls})

    except Exception as e:
        # Return an error message if an exception occurs
        return JSONResponse(content={"error": str(e)}, status_code=500)