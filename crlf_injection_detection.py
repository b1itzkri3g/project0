import re

class CRLFInjectionDetector:
    def __init__(self):
        self.patterns = [
            r'%0d%0a', 
            r'%0d', 
            r'%0a', 
            r'\r\n', 
            r'\r', 
            r'\n',
        ]

    def is_malicious(self, data: str) -> bool:
        for pattern in self.patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return True
        return False

    def inspect_request(self, path: str, query: str, body: str) -> bool:
        return self.is_malicious(path) or self.is_malicious(query) or self.is_malicious(body)
