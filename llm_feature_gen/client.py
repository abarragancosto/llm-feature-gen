import requests, base64, pathlib


class OllamaClient:

    def __init__(self, host: str = "localhost", port: int = 11434, timeout: int = 600):
        self.url = f"http://{host}:{port}/api/generate"
        self.timeout = timeout

    def generate(self, model: str, prompt: str, images=None) -> str:
        payload = {"model": model, "prompt": prompt, "stream": False}
        if images:
            payload["images"] = images
        r = requests.post(self.url, json=payload, timeout=self.timeout)
        r.raise_for_status()
        return r.json()["response"].strip()

    @staticmethod
    def encode_image(path: str) -> str:
        return base64.b64encode(pathlib.Path(path).read_bytes()).decode()
