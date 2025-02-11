import re

class SQLInjectionDetector:
    def __init__(self):
        self.patterns = [
            r'\' OR 1=1', 
            r'--', 
            r';--', 
            r';', 
            r'\' OR \'a\'=\'a',
            r'\' OR \'a\'=\'a\'',
            r'\' OR \'1\'=\'1',
            r'" OR 1=1',
            r'" OR "a"="a"',
            r'" OR "1"="1"',
            r'OR 1=1',
            r'OR "a"="a"',
            r'OR "1"="1"',
            r'union',
        ]

    def is_malicious(self, data: str) -> bool:
        for pattern in self.patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return True
        return False

    def inspect_request(self, path: str, query: str, body: str) -> bool:
        return self.is_malicious(path) or self.is_malicious(query) or self.is_malicious(body)
