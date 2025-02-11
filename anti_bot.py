import time
from collections import defaultdict

class AntiBot:
    def __init__(self, max_requests_per_minute=20):
        self.max_requests_per_minute = max_requests_per_minute
        self.request_times = defaultdict(list)
        self.blocked_ips = set()
        self.suspicious_user_agents = [
            'bot', 'crawl', 'spider', 'curl', 'wget', 'scrapy'
        ]

    def is_malicious_request(self, client_ip, user_agent):
        current_time = time.time()
        request_times = self.request_times[client_ip]
        
        # Filter out old request times beyond one minute
        request_times = [t for t in request_times if current_time - t < 60]
        self.request_times[client_ip] = request_times

        # Add the current request time
        request_times.append(current_time)

        # Check for suspicious user agents
        if any(sus_agent in user_agent.lower() for sus_agent in self.suspicious_user_agents):
            self.blocked_ips.add(client_ip)
            return True

        # Check if the IP is already blocked
        if client_ip in self.blocked_ips:
            return True

        return False

    def unblock_ip(self, client_ip):
        """Unblock an IP address if it was blocked erroneously."""
        if client_ip in self.blocked_ips:
            self.blocked_ips.remove(client_ip)
            del self.request_times[client_ip]
