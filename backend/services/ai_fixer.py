import os
import requests
import re

def generate_fix(code_content, error_message):
    api_key = os.getenv("GEMINI_API_KEY")

    prompt = f"""
You are an expert Python engineer.

The following file is failing tests.

TEST FAILURE OUTPUT:
{error_message}

CURRENT FILE CONTENT:
{code_content}

Fix the file so all tests pass.

Return ONLY valid Python code.
Do not explain anything.
Do not include markdown.
Do not include backticks.
Only return the full corrected file.
"""

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"

    headers = {"Content-Type": "application/json"}

    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)

        if response.status_code != 200:
            print("Gemini error:", response.text)
            return None

        result = response.json()

        text = result["candidates"][0]["content"]["parts"][0]["text"]

        # 🔥 Strip markdown if Gemini adds it
        text = re.sub(r"```python", "", text)
        text = re.sub(r"```", "", text)

        # 🔥 Basic sanity check
        if "def " not in text:
            return None

        return text.strip()

    except Exception as e:
        print("Gemini exception:", e)
        return None
