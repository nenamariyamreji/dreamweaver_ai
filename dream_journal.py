import json
import os
from datetime import datetime

class DreamJournalAI:
    def __init__(self):
        self.filepath = "dream_journal.json"
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                json.dump([], f)

    def analyze_dream(self, text):
        # Very basic placeholder analysis
        return "This dream shows your inner thoughts and emotions."

    def extract_tags(self, text):
        words = text.split()
        tags = [w.strip('.,!?').lower() for w in words if len(w) > 4]
        return list(set(tags))[:5]

    def save_entry(self, text, mood):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "analysis": self.analyze_dream(text),
            "tags": self.extract_tags(text),
            "mood": mood
        }
        entries = self.load_entries()
        entries.append(entry)
        with open(self.filepath, "w") as f:
            json.dump(entries, f, indent=2)

    def load_entries(self):
        try:
            with open(self.filepath) as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
