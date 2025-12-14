import json
import os
import requests
import base64

class Generator:
    def __init__(self, session_dir="session_data", ollama_url="http://localhost:11434"):
        self.session_dir = session_dir
        self.log_file = os.path.join(session_dir, "log.json")
        self.output_file = "documentation.md"
        self.ollama_url = ollama_url
        self.model = "llava" # Default vision model, fallbacks to others if needed

    def _encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _query_ollama(self, prompt, image_path=None):
        url = f"{self.ollama_url}/api/generate"
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        if image_path:
            # Check availability of llava or similar vision model
            # For this simple mock/implementation we assume user has it or we instruct them.
            # If image is provided, we try to use vision capabilities.
            try:
                data["images"] = [self._encode_image(image_path)]
            except Exception as e:
                print(f"Failed to encode image: {e}")
                return "Image processing failed."

        try:
            response = requests.post(url, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                return f"LLM Error: {response.status_code}"
        except requests.exceptions.ConnectionError:
            return "Ollama not reachable. Ensure 'ollama serve' is running."
        except Exception as e:
            return f"Error: {e}"

    def generate_report(self):
        if not os.path.exists(self.log_file):
            print("No session log found.")
            return

        with open(self.log_file, "r") as f:
            events = json.load(f)

        markdown_content = "# Auto-Generated Documentation\n\n"
        markdown_content += f"**Date:** {events[0]['timestamp'] if events else 'Unknown'}\n\n"

        step_count = 1
        for event in events:
            if event["type"] in ["click", "press_special"]:
                timestamp = event["timestamp"]
                details = event["details"]
                screenshot = event.get("screenshot")
                
                print(f"Processing step {step_count}...")
                
                # Construct description
                action_desc = f"User action: {event['type']} {details}"
                llm_desc = ""

                if screenshot and os.path.exists(screenshot):
                     prompt = f"Describe the GUI element being interacted with in this image. The user performed: {event['type']}. Keep it brief, one sentence."
                     llm_desc = self._query_ollama(prompt, screenshot)
                else:
                    llm_desc = "No screenshot available."

                # Append to markdown
                markdown_content += f"## Step {step_count}\n"
                markdown_content += f"**Action:** {action_desc}\n\n"
                markdown_content += f"**Context:** {llm_desc}\n\n"
                
                if screenshot:
                    # Make path relative for the markdown
                    rel_path = os.path.relpath(screenshot, start=os.getcwd())
                    markdown_content += f"![Screenshot]({rel_path})\n\n"
                
                step_count += 1

        with open(self.output_file, "w") as f:
            f.write(markdown_content)
        
        print(f"Documentation generated: {self.output_file}")

if __name__ == "__main__":
    gen = Generator()
    gen.generate_report()
