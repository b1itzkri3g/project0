import re

class SSRFDetector:
    def __init__(self):
        self.patterns = [
            r'localhost',
            r'127\.0\.0\.1',
            r'::1',
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
            r'169\.254\.\d{1,3}\.\d{1,3}',
            r'0\.0\.0\.0',
        ]

    def is_malicious(self, data: str) -> bool:
        for pattern in self.patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return True
        return False

    def inspect_request(self, path: str, query: str, body: str) -> bool:
        return self.is_malicious(path) or self.is_malicious(query) or self.is_malicious(body)
