import json
from datetime import datetime

class Storage:
    DATA_FILE = "data.json"

    def __init__(self):
        self._initialize_data_file()

    def _initialize_data_file(self):
        try:
            with open(self.DATA_FILE, "r") as file:
                json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.DATA_FILE, "w", encoding="utf-8") as file:
                json.dump({"presences": []}, file)
            
    def _save_to_file(self, data):
        with open(self.DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file,ensure_ascii=False, indent=4)

    def _load_from_file(self):
        with open(self.DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
        
    def save_presence(self, participants):
        data = self._load_from_file()
        presence_record = {
            "id": len(data["presences"]) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "participants": participants
        }
        data["presences"].append(presence_record)
        self._save_to_file(data)

    def get_presences_last_week(self):
        data = self._load_from_file()
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        recent_presences = [
            presence for presence in data["presences"]
            if datetime.strptime(presence["timestamp"], "%Y-%m-%d %H:%M:%S") >= one_week_ago
        ]
        
        return recent_presences