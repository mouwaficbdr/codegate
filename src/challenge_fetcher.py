import json
import random
import requests
import os

class ChallengeFetcher:
    def __init__(self, local_path="assets/challenges.json", remote_url=None):
        self.local_path = local_path
        self.remote_url = remote_url
        self.challenges = []
        self._load_challenges()

    def _load_challenges(self):
        # Try remote first
        if self.remote_url:
            try:
                response = requests.get(self.remote_url, timeout=5)
                response.raise_for_status()
                self.challenges = response.json()
                return
            except requests.RequestException:
                print("Failed to fetch remote challenges. Falling back to local.")

        # Fallback to local
        if os.path.exists(self.local_path):
            try:
                with open(self.local_path, 'r') as f:
                    self.challenges = json.load(f)
            except json.JSONDecodeError:
                print("Error decoding local challenges file.")
        else:
            print(f"Local challenges file not found at {self.local_path}")

    def get_random_challenge(self):
        if not self.challenges:
            return None
        return random.choice(self.challenges)

    def validate_solution(self, challenge_id, user_code):
        # In a real app, this would run the code in a sandbox or check against test cases.
        # For MVP, we'll just check if the code is non-empty.
        return len(user_code.strip()) > 10
