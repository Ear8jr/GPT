from flask import Flask, request, jsonify, render_template_string
import os
import requests
import sqlite3
import time
import tracemalloc  # For memory usage tracking
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Groq API Key (Hardcoded for this unified codebase)
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/v1/completions"

# Database setup for storing conversations
DATABASE = "conversations.db"

# Ensure database exists and create table for conversations
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT,
            response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Save conversation to the database
def save_conversation(prompt, response):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversations (prompt, response) VALUES (?, ?)", (prompt, response))
    conn.commit()
    conn.close()

# Fetch all conversations from the database
def get_conversations():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT prompt, response, timestamp FROM conversations ORDER BY timestamp DESC")
    conversations = cursor.fetchall()
    conn.close()
    return conversations

# Cleanup old conversations (older than 30 days)
def clean_conversations():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations WHERE timestamp < datetime('now', '-30 days')")
    conn.commit()
    conn.close()

# ANA: Enhanced Analytics Module
class ANA:
    """Analytics module for measuring performance metrics."""
    metrics = {
        "energy_usage": 0,  # Simulated value
        "memory_usage": 0,
        "code_length": 0,
        "processing_speed": 0
    }

    @staticmethod
    def measure_energy_usage():
        # Simulate calculating energy usage
        ANA.metrics["energy_usage"] += 0.01  # Increment for each call (simulated)
        return ANA.metrics["energy_usage"]

    @staticmethod
    def measure_memory_usage():
        # Track memory usage
        tracemalloc.start()
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        ANA.metrics["memory_usage"] = peak_memory / (1024 * 1024)  # Convert to MB
        return ANA.metrics["memory_usage"]

    @staticmethod
    def measure_code_length():
        # Count lines of code in this file
        with open(__file__, 'r') as f:
            ANA.metrics["code_length"] = sum(1 for _ in f)
        return ANA.metrics["code_length"]

    @staticmethod
    def measure_processing_speed(start_time, end_time):
        # Calculate time elapsed for processing
        ANA.metrics["processing_speed"] = end_time - start_time
        return ANA.metrics["processing_speed"]

    @staticmethod
    def generate_report():
        return {
            "energy_usage": ANA.metrics["energy_usage"],
            "memory_usage": ANA.metrics["memory_usage"],
            "code_length": ANA.metrics["code_length"],
            "processing_speed": ANA.metrics["processing_speed"]
        }

# Modular Components
class LML:
    """Language comprehension module."""
    @staticmethod
    def comprehend_language(prompt):
        start_time = time.time()
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": prompt,
            "max_tokens": 100,
            "temperature": 0.7
        }
        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload)
            response.raise_for_status()  # Raise an error for HTTP codes >= 400
            result = response.json()
            end_time = time.time()
            ANA.measure_processing_speed(start_time, end_time)
            ANA.measure_energy_usage()
            ANA.measure_memory_usage()
            return result.get("choices", [{}])[0].get("text", "").strip()
        except requests.exceptions.RequestException as e:
            return f"Error: Unable to process request - {str(e)}"

# EDT: Enhanced Self-Editing Module
class EDT:
    """Self-editing module using Groq API for dynamic code modifications."""
    @staticmethod
    def edit_code(command, code_snippet):
        """
        Sends a command and code snippet to the AI model for self-editing.

        Args:
            command (str): The user's edit command.
            code_snippet (str): The code snippet to modify.
        
        Returns:
            str: The modified code or an error message.
        """
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        prompt = f"Modify the following code to {command}:\n\n{code_snippet}"
        payload = {
            "prompt": prompt,
            "max_tokens": 200,
            "temperature": 0.7
        }
        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            modified_code = result.get("choices", [{}])[0].get("text", "").strip()

            # Validate the modified code (basic syntax check for Python)
            if "def " in modified_code or "function" in modified_code:
                return modified_code
            else:
                return f"Modification failed validation: {modified_code}"
        except requests.exceptions.RequestException as e:
            return f"Error: Unable to process request - {str(e)}"

# HTML Template (Synthwave-themed)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GPTEJ</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #1a1a2e;
            color: #e94560;
            margin: 0;
            padding: 0;
        }
        #container {
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        textarea, input {
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            border: none;
            border-radius: 5px;
        }
        button {
            background-color: #0f3460;
            color: white;
            padding: 10px 15px;
            border: none;
            cursor: pointer;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div id="container">
        <h1>GPTEJ</h1>
        <textarea id="prompt" placeholder="Enter your prompt here..."></textarea>
        <button onclick="submitPrompt()">Submit</button>
        <div id="response"></div>
        <h2>Past Conversations</h2>
        <ul>
            {% for convo in conversations %}
                <li><strong>{{ convo[2] }}</strong>: {{ convo[0] }} -> {{ convo[1] }}</li>
            {% endfor %}
        </ul>
    </div>
    <script>
        async function submitPrompt() {
            const prompt = document.getElementById('prompt').value;
            const responseDiv = document.getElementById('response');
            const response = await fetch('/prompt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt })
            });
            const data = await response.json();
            responseDiv.textContent = data.response || data.error;
        }
    </script>
</body>
</html>
"""

# Routes
@app.route('/')
def index():
    conversations = get_conversations()
    return render_template_string(HTML_TEMPLATE, conversations=conversations)

@app.route('/prompt', methods=['POST'])
def handle_prompt():
    data = request.json
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    # Use LML to process the prompt
    response = LML.comprehend_language(prompt)
    save_conversation(prompt, response)
    return jsonify({'response': response}), 200

@app.route('/analytics', methods=['GET'])
def analytics():
    ANA.measure_code_length()
    return jsonify(ANA.generate_report())

@app.route('/edit', methods=['POST'])
def edit_code():
    data = request.json
    command = data.get('command')
    code_snippet = data.get('code_snippet')
    if not command or not code_snippet:
        return jsonify({'error': 'Both command and code_snippet are required'}), 400

    # Use EDT to modify the code
    modified_code = EDT.edit_code(command, code_snippet)
    return jsonify({'modified_code': modified_code})

# Initialize Database
init_db()
clean_conversations()

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
