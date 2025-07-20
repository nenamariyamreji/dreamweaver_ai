from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from dream_journal import DreamJournalAI
import os
import google.generativeai as genai

# Load .env
load_dotenv()

# API Key for Gemini
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY not found! Please set it in your .env file.")

genai.configure(api_key=API_KEY)

# Gemini Model
model = genai.GenerativeModel("gemini-2.5-flash")

# Flask App
app = Flask(__name__)
CORS(app)

# Dream Journal instance
journal = DreamJournalAI()

# ---------- ROUTES ----------

# Landing page
@app.route("/")
def landing():
    return render_template("landing.html")

# Dream Generator page
@app.route("/app")
def index():
    return render_template("index.html")

# Dream Journal page (loads saved entries)
@app.route("/journal")
def journal_page():
    entries = journal.load_entries()
    return render_template("journal.html", entries=entries)

# Comic Generator page
@app.route("/comic")
def comic_page():
    return render_template("comic_generator.html")

# Dream Visualizer page
@app.route("/visualizer")
def visualizer_page():
    return render_template("dream_visualizer.html")

# ---------- API ENDPOINTS ----------

# Generate dream story
@app.route("/generate_dream", methods=["POST"])
def generate_dream():
    try:
        data = request.json
        user_prompt = data.get("prompt", "")
        if not user_prompt:
            return jsonify({"error": "No dream idea provided"}), 400

        prompt_text = f"""
You are DreamWeaver AI — an imaginative dream story generator.
Create a vivid, immersive dream story based on this idea: "{user_prompt}".

Requirements:
- Make it detailed, descriptive, and poetic.
- Minimum 300 words unless the user explicitly says they want it shorter.
- Include surreal elements, unexpected scenes, and sensory details.
- Write it as a single flowing narrative, not bullet points.
- Return only the story, no extra explanation.

The user’s idea: "{user_prompt}"

Start the dream now:
"""

        response = model.generate_content(prompt_text)
        print("DEBUG: Gemini dream:", response)

        if not hasattr(response, "text") or not response.text:
            return jsonify({"error": "No response from Gemini API"}), 500

        return jsonify({"dream": response.text})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Generate comic script
@app.route("/generate_comic", methods=["POST"])
def generate_comic():
    try:
        data = request.json
        user_prompt = data.get("prompt", "")
        if not user_prompt:
            return jsonify({"error": "No comic idea provided"}), 400

        prompt_text = f"""
You are DreamWeaver AI — an imaginative comic script writer.
Create a short, creative comic strip script based on this dream idea: "{user_prompt}".

Requirements:
- Write it like comic panels.
- Include short dialogues and scene directions.
- Make it whimsical, dreamlike, or surreal.
- Return only the comic script, no extra explanation.

The idea: "{user_prompt}"
"""

        response = model.generate_content(prompt_text)
        print("DEBUG: Gemini comic:", response)

        if not hasattr(response, "text") or not response.text:
            return jsonify({"error": "No response from Gemini API"}), 500

        return jsonify({"comic": response.text})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Generate dream visualizer image URL (mock)
@app.route("/generate_visual", methods=["POST"])
def generate_visual():
    try:
        data = request.json
        user_prompt = data.get("prompt", "")
        if not user_prompt:
            return jsonify({"error": "No visual idea provided"}), 400

        # For now, return a dummy placeholder image.
        # Replace with DALL·E or Gemini Vision later.
        fake_image_url = f"https://dummyimage.com/800x400/000/fff&text={user_prompt.replace(' ', '+')}"
        return jsonify({"image_url": fake_image_url})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Save journal entry
@app.route("/save_journal", methods=["POST"])
def save_journal():
    try:
        data = request.json
        dream_text = data.get("dream", "").strip()
        mood = data.get("mood", "").strip()

        if not dream_text:
            return jsonify({"error": "No dream text provided."}), 400
        if not mood:
            return jsonify({"error": "No mood provided."}), 400

        journal.save_entry(dream_text, mood)
        return jsonify({"success": True})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# API to list entries
@app.route("/journal_entries", methods=["GET"])
def journal_entries():
    entries = journal.load_entries()
    return jsonify(entries)

if __name__ == "__main__":
    app.run(debug=True)
