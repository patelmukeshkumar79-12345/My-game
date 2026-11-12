
import os
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

API_KEY = API_KEY = os.environ.get("GROQ_API_KEY", "")

class SameerAI(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_json({})

    def do_POST(self):
        if self.path != "/ask":
            self.send_json({"error": "Not found"}, 404)
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            messages = data.get("messages", [])

            if not messages:
                self.send_json({"error": "Question khali hai"}, 400)
                return

            payload = {
                "model": "openai/gpt-oss-120b",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are Sameer AI. Answer helpfully in the user's language."
                    }
                ] + messages[-20:],
                "max_completion_tokens": 2048
            }

            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + API_KEY,
                    "User-Agent": "SameerAI/1.0"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=90) as response:
                result = json.loads(response.read())

            answer = result["choices"][0]["message"]["content"]
            self.send_json({"answer": answer})

        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def log_message(self, *args):
        pass


print("Sameer AI Backend Starting...")
HTTPServer(("0.0.0.0", 8000), SameerAI).serve_forever()

