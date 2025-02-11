import re
from urllib.parse import unquote


class SSTIDetector:
    def __init__(self):
        self.patterns = [
            r'\{\{.*?\}\}',
            r'\{\%.*?\%\}',
            r'\$\{.*?\}',
            r'\{\#.*?\#\}',
            r'<%=.*?%>',
        ]

    def decode_input(self, data: str) -> str:
        # Decode URL-encoded characters
        return unquote(data)

    def is_malicious(self, data: str) -> bool:
        decoded_data = self.decode_input(data)
        for pattern in self.patterns:
            if re.search(pattern, decoded_data, re.IGNORECASE):
                return True
        return False

    def inspect_request(self, path: str, query: str, body: str) -> bool:
        return self.is_malicious(path) or self.is_malicious(query) or self.is_malicious(body)
