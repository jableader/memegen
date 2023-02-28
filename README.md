# memegen

Just some trash I got ChatGPT to write for me. There are two endpoints, `/prompt` which uses GPT-3 to generate a four-part story with accompanying scene descriptions, and `/frames` which turns those frame descriptions into a real comic using DALL-E.

Example command to create a story about "A cat chases a mouse" in a "Hanna-Barbera Cartoon" style, saving the story to sample.json:
```
curl -X POST -H "Content-Type: application/json" -d '{"story": "A cat chases a mouse", "style": "Hanna-Barbera Cartoon"}' http://localhost:8000/prompt -o sample.json
```

Example command posting that story back for comic generation:
```
curl -X POST -H "Content-Type: application/json" -d @sample.json http://localhost:8000/frames
```
