# memegen

Just some trash I got ChatGPT to write for me.

Example command to create a story about "A cat chases a mouse" in a "Hanna-Barbera Cartoon" style, saving the story to sample.json:
```
curl -X POST -H "Content-Type: application/json" -d '{"story": "A cat chases a mouse", "style": "Hanna-Barbera Cartoon"}' http://localhost:8000/prompt -o sample.json
```

Example command posting that story back for comic generation:
```
curl -X POST -H "Content-Type: application/json" -d @sample.json http://localhost:8000/frames
```
