import json

config = "configuration/configuration.json"
threads = "configuration/threads.json"

class Config:
    def __init__(self):
        pass
    
    def get(self) -> dict:
        with open(config, "r") as cf:
            data = json.load(cf)
        return data

    def save(self, conf: dict) -> None:
        with open(config, "w") as cf:
            json.dump(conf, cf, indent=4)

class Thread:
    def __init__(self):
        pass
    
    def get(self) -> dict:
        with open(threads, "r") as tf:
            data = json.load(tf)
        return data
    
    def get_thread(self, channel_id: int) -> dict | None:
        with open(threads, "r") as tf:
            data = json.load(tf)
        return data[str(channel_id)] if str(channel_id) in data else None        

    def save(self, thread: dict) -> None:
        with open(threads, "w") as tf:
            json.dump(thread, tf, indent=4)