import json
from pathlib import Path

class LinkTracker:
    def __init__(self, file_path='data/banned_links.json'):
        self.file_path = Path(file_path)
        if not self.file_path.parent.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists only if it does not exist
        self.banned_links = self.load_data()

    def load_data(self):
        if self.file_path.exists():
            with open(self.file_path, 'r') as file:
                return json.load(file)
        else:
            # Create the file if it does not exist
            self.file_path.touch(exist_ok=True)
            return []

    def save_data(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.banned_links, file, indent=4)

    def add_link(self, link: str):
        if link not in self.banned_links:
            self.banned_links.append(link)
            self.save_data()

    def is_banned(self, link: str):
        return link in self.banned_links
