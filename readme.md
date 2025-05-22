HTTP Server from Scratch (Python)

This is a basic HTTP server I built completely from scratch using Python's socket module. The goal was to understand how HTTP works under the hood—no frameworks, no magic.
What the Server Can Do

    Accepts raw TCP connections and reads HTTP requests

    Parses the HTTP request method, path, headers, and body

    Supports GET and POST requests

    Serves static files from a static/ or public/ folder

    Detects and sets the correct Content-Type using file extension

    Parses JSON and form data in POST requests

    Returns proper HTTP status codes (200, 404, 405, etc.)

    Modular routing logic using a central handle_routes() function

    Optionally supports running WSGI-compatible apps

**Example Usage**

Start the server:
```
python server.py
```
Then:

    Visit http://localhost:8080/index.html to load a static HTML file


Use curl to test API routes:
```
curl -X POST http://localhost:8080/ -H "Content-Type: application/json" -d '{"name": "test"}'
```
Why I Built This

I wanted to learn how HTTP really works—how a server accepts a connection, reads headers, figures out what the client wants, and returns a valid response. Instead of using Flask or Django, I built everything from the ground up to break the black box.
