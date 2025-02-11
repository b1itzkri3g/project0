import re

class PathTraversalDetector:
    def __init__(self):
        self.patterns = [
            r'\.\./', 
            r'\.\.\\', 
            r'~/', 
            r'\%2e\%2e/', 
            r'\%2e\%2e\\',
        ]

    def is_malicious(self, data: str) -> bool:
        for pattern in self.patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return True
        return False

    def inspect_request(self, path: str, query: str, body: str) -> bool:
        return self.is_malicious(path) or self.is_malicious(query) or self.is_malicious(body)
