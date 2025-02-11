import re

class XXEDetector:
    def __init__(self):
        self.patterns = [
            r'<!ENTITY\s+.*?SYSTEM\s+["\'].*?["\']>',
            r'<!DOCTYPE\s+.*?\[.*?<!ENTITY.*?\]>',
        ]

    def is_malicious(self, data: str) -> bool:
        for pattern in self.patterns:
            if re.search(pattern, data, re.IGNORECASE | re.DOTALL):
                return True
        return False

    def inspect_request(self, body: str) -> bool:
        return self.is_malicious(body)
