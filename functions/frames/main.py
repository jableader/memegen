import openai
import os
import random
import string
import asyncio
import aiohttp
import functions_framework

from google.cloud import storage
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

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

async def load_images(urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(asyncio.ensure_future(load_image(session, url)))
        return await asyncio.gather(*tasks)

async def load_image(session, url):
    async with session.get(url) as response:
        image_data = await response.read()
        return Image.open(BytesIO(image_data))

def stitch_frames(frames, captions):
    # Assume all frames are the same size
    width, height = frames[0].size
    
    # Create a new image to hold the stitched frames
    new_image = Image.new('RGB', (2 * width, 2 * height))
    
    # Iterate through the frames and captions and paste them into the new image
    for i in range(len(frames)):
        # Resize the caption to fit within the width of the frame
        font = ImageFont.truetype('FreeMono.ttf', size=20)
        text = captions[i]
        text_width, text_height = font.getsize(text)
        
        # Line-wrap the text
        words = text.split()
        lines = []
        line = ''
        for word in words:
            if font.getsize(line + ' ' + word)[0] <= width:
                line += ' ' + word
            else:
                lines.append(line.lstrip())
                line = word
        if line:
            lines.append(line.lstrip())
        
        # Create a new image for the caption and draw the text
        text_image = Image.new('RGB', (width, len(lines) * text_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(text_image)
        for j, line in enumerate(lines):
            text_width, text_height = font.getsize(line)
            x = (width - text_width) / 2
            y = j * text_height
            # Draw white text with black stroke
            draw.text((x, y), line, font=font, fill=(255, 255, 255), stroke_width=1, stroke_fill=(0, 0, 0))
        
        # Calculate the coordinates to paste the frame and caption into the new image
        row = i // 2
        col = i % 2
        x = col * width
        y = row * height
        
        # Paste the frame and caption into the new image
        new_image.paste(frames[i], (x, y))
        new_image.paste(text_image, (x, y + (2 * height // 3) - (len(lines) * text_height // 2)))
        
    return new_image

def save(image: Image, bucket_name: str, object_name: str):
    """
    Saves an Image to a Google Cloud Storage bucket.
    """
    # Convert image to bytes
    with BytesIO() as output:
        image.save(output, format='JPEG')
        image_bytes = output.getvalue()

    # Create a client object to interact with the Google Cloud Storage API
    storage_client = storage.Client()

    # Get the bucket to save the image in
    bucket = storage_client.bucket(bucket_name)

    # Create a blob object to represent the image file and upload the image
    blob = bucket.blob(object_name)
    blob.upload_from_string(image_bytes, content_type='image/jpeg')

    return blob.public_url

class ImageCreationRefused(Exception):
	def __init__(self, err, prompt):
		self.prompt = prompt
		super().__init__(str(err))

def create_image(prompt):
    try:
        # Generate image URLs using OpenAI API
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )

        return response['data'][0]['url']
    except Exception as err:
        raise ImageCreationRefused(err, prompt)

@functions_framework.errorhandler(ImageCreationRefused)
def handle_naughty_image(er):
	return { 'message': 'Refused to render', 'prompt': er.prompt, 'error': str(er) }, 400

@functions_framework.http
def frames(request):
  r = request.get_json()

  style = r['setting']
  frame_prompts = r['frames']
  captions = [ p['caption'] for p in frame_prompts ]
  image_prompts = [ f"{style}, {p['frameDescription']}" for p in frame_prompts ]

  image_urls = [ create_image(p) for p in image_prompts ]
  images = asyncio.run(load_images(image_urls))
  img = stitch_frames(images, captions)
  url = save(img, bucket_name, rand_str(8))

  return { "message": "Frames generated and saved.", "source_images": image_urls, "meme": url }