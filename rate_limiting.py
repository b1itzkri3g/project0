import time

class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}

    def is_rate_limited(self, client_ip: str) -> bool:
        current_time = time.time()
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip] = [timestamp for timestamp in self.requests[client_ip] if current_time - timestamp < self.time_window]
        if len(self.requests[client_ip]) >= self.max_requests:
            return True
        self.requests[client_ip].append(current_time)
        return False
