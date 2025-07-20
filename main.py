from groq import Groq
import datetime
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class DreamJournalAI:
    def _init_(self, api_key: str = None):
        """
        Initialize the Dream Journal AI with Groq API key.
        
        Args:
            api_key: Groq API key (optional, will use .env if not provided)
        """
        api_key = api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("No API key provided. Set GROQ_API_KEY in .env file or pass directly.")
        
        self.client = Groq(api_key=api_key)
        self.available_models = {
            "1": {"name": "Llama 3 70B", "id": "llama3-70b-8192"},
            "2": {"name": "Llama 3 8B", "id": "llama3-8b-8192"}
        }
        self.model = self.select_model()
        self.journal_entries = []
        self.load_journal()
        
    def select_model(self) -> str:
        """Let user select from available models"""
        print("\nAvailable Models:")
        for key, model in self.available_models.items():
            print(f"{key}. {model['name']}")
        
        while True:
            choice = input("Select model (1-2): ")
            if choice in self.available_models:
                return self.available_models[choice]["id"]
            print("Invalid choice. Please try again.")
            
    def save_journal(self) -> None:
        """Save journal entries to a JSON file."""
        with open('dream_journal.json', 'w') as f:
            json.dump(self.journal_entries, f, indent=2)
            
    def load_journal(self) -> None:
        """Load journal entries from a JSON file if it exists."""
        try:
            with open('dream_journal.json', 'r') as f:
                self.journal_entries = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.journal_entries = []
    
    def record_dream(self, dream_description: str) -> Dict:
        """
        Record a new dream entry with timestamp and basic analysis.
        
        Args:
            dream_description: User's description of their dream
            
        Returns:
            Dictionary containing the journal entry
        """
        timestamp = datetime.datetime.now().isoformat()
        
        try:
            analysis = self.analyze_dream(dream_description)
            tags = self.extract_tags(dream_description)
            mood = self.detect_mood(dream_description)
        except Exception as e:
            print(f"Analysis error: {str(e)}")
            analysis = "Could not analyze - try again later"
            tags = ["unprocessed"]
            mood = "unknown"

        entry = {
            'timestamp': timestamp,
            'dream': dream_description,
            'analysis': analysis,
            'tags': tags,
            'mood': mood,
            'model_used': self.model
        }
        
        self.journal_entries.append(entry)
        self.save_journal()
        return entry
    
    def safe_api_call(self, prompt: str, system_msg: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Handle API calls with error recovery"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if "model_decommissioned" in str(e):
                print("Model unavailable. Falling back to Llama 3 70B")
                self.model = "llama3-70b-8192"
                return self.safe_api_call(prompt, system_msg, max_tokens, temperature)
            raise RuntimeError(f"API Error: {str(e)}")
    
    def analyze_dream(self, dream_text: str) -> str:
        """
        Analyze a dream description for common themes and meanings.
        
        Args:
            dream_text: Description of the dream
            
        Returns:
            Analysis text
        """
        prompt = f"""Analyze this dream and provide psychological insights (3-5 sentences).
Focus on recurring symbols, emotions, and potential real-life connections.

Dream: {dream_text}

Analysis:"""
        
        return self.safe_api_call(
            prompt=prompt,
            system_msg="You are a professional dream analyst.",
            max_tokens=500
        )
    
    def extract_tags(self, dream_text: str) -> List[str]:
        """
        Extract relevant tags from a dream description.
        
        Args:
            dream_text: Description of the dream
            
        Returns:
            List of tags
        """
        prompt = f"""Extract 3-5 most relevant tags from this dream description. 
Return only a comma-separated list of lowercase tags.

Dream: {dream_text}

Tags:"""
        
        response = self.safe_api_call(
            prompt=prompt,
            system_msg="You extract tags from dream descriptions.",
            max_tokens=50,
            temperature=0.3
        )
        
        tags = response.strip().split(',')
        return [tag.strip().lower() for tag in tags if tag.strip()]
    
    def detect_mood(self, dream_text: str) -> str:
        """
        Detect the predominant mood of a dream.
        
        Args:
            dream_text: Description of the dream
            
        Returns:
            Detected mood (e.g., "happy", "anxious", "neutral")
        """
        prompt = f"""Classify the mood of this dream using one word from:
happy, anxious, fearful, exciting, sad, confusing, neutral, or other.

Dream: {dream_text}

Mood:"""
        
        return self.safe_api_call(
            prompt=prompt,
            system_msg="You classify dream moods using single words.",
            max_tokens=10,
            temperature=0.2
        ).lower()
    
    def search_journal(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search through past journal entries for relevant dreams.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of matching journal entries
        """
        if not self.journal_entries:
            return []
            
        try:
            prompt = f"""Find {num_results} journal entries most relevant to: "{query}".
Consider dream content, analysis, tags, and mood.

Entries: {json.dumps(self.journal_entries[-50:])}  # Search most recent 50

Return JSON with keys: timestamp, dream_preview, analysis_preview, mood, tags"""
            
            response = self.safe_api_call(
                prompt=prompt,
                system_msg="You search dream journals and return JSON results.",
                max_tokens=1000,
                temperature=0.4
            )
            
            return json.loads(response)
        except:
            # Fallback to simple search
            query_lower = query.lower()
            return [
                entry for entry in self.journal_entries[-50:] 
                if query_lower in entry['dream'].lower() or 
                   query_lower in entry['analysis'].lower() or
                   any(query_lower in tag for tag in entry['tags'])
            ][:num_results]
    
    def identify_patterns(self) -> str:
        """
        Analyze all journal entries to identify recurring patterns.
        
        Returns:
            Analysis text
        """
        if not self.journal_entries:
            return "No journal entries available for analysis."
            
        prompt = f"""Analyze these dream journal entries for recurring patterns.
Identify 3-5 key insights about themes, symbols, or emotional trends.

Journal Entries: {json.dumps(self.journal_entries)}

Key Insights:"""
        
        return self.safe_api_call(
            prompt=prompt,
            system_msg="You identify patterns in dream journals.",
            max_tokens=1000
        )

    def get_statistics(self) -> Dict:
        """
        Generate statistics about the dream journal.
        
        Returns:
            Dictionary containing statistics
        """
        stats = {
            "total_dreams": len(self.journal_entries),
            "most_common_tags": {},
            "mood_distribution": {},
            "dream_frequency": {},
            "models_used": {}
        }
        
        if not self.journal_entries:
            return stats
        
        # Tag statistics
        tag_counts = {}
        for entry in self.journal_entries:
            for tag in entry.get('tags', []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        stats["most_common_tags"] = dict(sorted(tag_counts.items(), 
                                             key=lambda x: x[1], 
                                             reverse=True)[:5])
        
        # Mood statistics
        for entry in self.journal_entries:
            mood = entry.get('mood', 'unknown')
            stats["mood_distribution"][mood] = stats["mood_distribution"].get(mood, 0) + 1
        
        # Model usage
        for entry in self.journal_entries:
            model = entry.get('model_used', 'unknown')
            stats["models_used"][model] = stats["models_used"].get(model, 0) + 1
        
        # Date frequency
        for entry in self.journal_entries:
            date = entry['timestamp'][:10]  # YYYY-MM-DD
            stats["dream_frequency"][date] = stats["dream_frequency"].get(date, 0) + 1
        
        return stats


def main():
    try:
        print("\n🌙 Dream Journal AI 🌙")
        print("Type 'quit' anytime to exit\n")
        
        journal = DreamJournalAI()
        
        while True:
            action = input(
                "Choose an option:\n"
                "1. Record new dream\n"
                "2. Search journal\n"
                "3. View statistics\n"
                "4. Identify patterns\n"
                "> "
            ).lower()
            
            if action in ['quit', 'exit', 'q']:
                break
                
            if action == '1':
                while True:
                    dream = input("\nDescribe your dream (or 'back'): ")
                    if dream.lower() in ['back', 'quit']:
                        break
                    if dream.strip():
                        entry = journal.record_dream(dream)
                        print("\n✨ Dream recorded! ✨")
                        print(f"\nAnalysis: {entry['analysis']}")
                        print(f"Mood: {entry['mood'].capitalize()}")
                        print(f"Tags: {', '.join(entry['tags'])}")
                    else:
                        print("Please enter a dream description.")
                
            elif action == '2':
                query = input("\nSearch for: ")
                if not query.strip():
                    print("Please enter a search term.")
                    continue
                    
                results = journal.search_journal(query)
                print(f"\nFound {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result.get('timestamp', 'No date')[:10]}")
                    print(f"Preview: {result.get('dream_preview', result.get('dream', 'No content'))[:150]}...")
                    print(f"Mood: {result.get('mood', 'unknown').capitalize()}")
                    print(f"Tags: {', '.join(result.get('tags', []))}")
                
            elif action == '3':
                stats = journal.get_statistics()
                print("\n📊 Journal Statistics 📊")
                print(f"\nTotal dreams: {stats['total_dreams']}")
                
                print("\nTop Tags:")
                for tag, count in stats['most_common_tags'].items():
                    print(f"- {tag}: {count}")
                
                print("\nMood Distribution:")
                for mood, count in stats['mood_distribution'].items():
                    print(f"- {mood.capitalize()}: {count}")
                
                print("\nModels Used:")
                for model, count in stats['models_used'].items():
                    print(f"- {model}: {count}")
                
            elif action == '4':
                print("\n🔍 Analyzing patterns...")
                patterns = journal.identify_patterns()
                print("\nPatterns Found:")
                print(patterns)
                
            else:
                print("Invalid option. Please choose 1-4.")
            
            print("\n" + "="*50 + "\n")
            
    except Exception as e:
        print(f"\n⚠ Error: {str(e)}")
    finally:
        print("\nJournal saved. Sweet dreams! 🌙")


if _name_ == "_main_":
    main()