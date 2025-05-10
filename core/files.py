import json, os
from datetime import datetime


class Files:
    def create(name, folder=None):
        if not folder:
            folder = "cards"
        filename = f"{name}.json"
        cards_dir = os.path.join(os.getcwd(), folder)
        os.makedirs(cards_dir, exist_ok=True)
        filepath = os.path.join(cards_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)

    @staticmethod
    def last_modified(name: str, folder: str = 'cards') -> float:
        filename = name if name.lower().endswith('.json') else f"{name}.json"
        filepath = os.path.join(os.getcwd(), folder, filename)
        return os.path.getmtime(filepath)
    
    @staticmethod
    def last_modified_dt(name: str, folder: str = 'cards') -> datetime:
        ts = Files.last_modified(name, folder)
        return datetime.fromtimestamp(ts)

    @staticmethod
    def delete(name, folder="cards"):
        filename = f"{name}.json"
        cards_dir = os.path.join(os.getcwd(), folder)
        filepath = os.path.join(cards_dir, filename)

        if os.path.exists(filepath):
            os.remove(filepath)
        else:
            print(f"Could not delete {filepath!r}: file isn't found.")

    def exists(name: str, folder: str = "cards"):
        filename = name if name.lower().endswith(".json") else f"{name}.json"
        cards_dir = os.path.join(os.getcwd(), folder)
        filepath = os.path.join(cards_dir, filename)
        return os.path.isfile(filepath)


    def read(name: str, folder: str = "cards") -> dict:
        
        filename = name if name.lower().endswith(".json") else f"{name}.json"
        cards_dir = os.path.join(os.getcwd(), folder)
        filepath = os.path.join(cards_dir, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Could not find file: {filepath!r}")

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
        

    def record(name, data, folder="cards"):
        filename = f"{name}.json"
        cards_dir = os.path.join(os.getcwd(), folder)
        filepath = os.path.join(cards_dir, filename)

        if os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)


    def get_all_ids(file):
        try:
            with open(file, 'r', encoding='utf-8') as file:
                words = json.load(file)

            ids = [word.get('id') for word in words if "id" in word]
            return ids
        
        except FileNotFoundError: 
            print("Could not get all ID's: file not found.")
            return []
        
        except json.JSONDecodeError:
            print("Could not get all ID's: file corrupted or empty.")
            return []
        
    
    def delete_id(file_p, id):
        try:
            with open(file_p, "r", encoding="utf-8") as file:
                words = json.load(file)

            words = [word for word in words if word.get('id') != id]

            for new_id, word in enumerate(words, start=1):
                word['id'] = new_id

            with open(file_p, "w", encoding="utf-8") as file:
                json.dump(words, file, ensure_ascii=False, indent=2)

        except FileNotFoundError: 
            print("Could not get all ID's: file not found.")
        
        except json.JSONDecodeError:
            print("Could not get all ID's: file corrupted or empty.")

    def get_all_titles():
        titles = []
        folder = "cards"
        if not os.path.exists(folder):
            return titles
        for file in os.listdir(folder):
            if file.endswith(".json"):
                title = os.path.splitext(file)[0]
                titles.append(title)
        return titles
