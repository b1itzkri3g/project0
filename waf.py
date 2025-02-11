from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import requests
from urllib.parse import urlparse
from sql_injection_detection import SQLInjectionDetector
from xss_detection import XSSDetector
from ssrf_detection import SSRFDetector
from ssti_detection import SSTIDetector
from rate_limiting import RateLimiter
from anti_bot import AntiBot
from path_traversal_detection import PathTraversalDetector
from xxe_detection import XXEDetector
from os_command_injection_detection import OSCommandInjectionDetector
from crlf_injection_detection import CRLFInjectionDetector

BACKEND_SERVER = 'http://localhost:8080'  # The backend server to forward requests to

class WAFHTTPRequestHandler(BaseHTTPRequestHandler):
    rate_limiter = RateLimiter(max_requests=100, time_window=60)  # 100 requests per 60 seconds
    anti_bot = AntiBot(max_requests_per_minute=20)  # 20 requests per minute for anti-bot

    def __init__(self, *args, **kwargs):
        self.sql_injection_detector = SQLInjectionDetector()
        self.xss_detector = XSSDetector()
        self.ssrf_detector = SSRFDetector()
        self.ssti_detector = SSTIDetector()
        self.path_traversal_detector = PathTraversalDetector()
        self.xxe_detector = XXEDetector()
        self.os_command_injection_detector = OSCommandInjectionDetector()
        self.crlf_injection_detector = CRLFInjectionDetector()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def handle_request(self):
        # Get client IP
        client_ip = self.client_address[0]

        # Get user agent
        user_agent = self.headers.get('User-Agent', '')

        # Anti-bot detection
        if self.anti_bot.is_malicious_request(client_ip, user_agent):
            self.send_error_page(403)
            logging.warning(f"Blocked bot request from {client_ip} with user agent {user_agent}")
            return

        # Rate limiting
        if self.rate_limiter.is_rate_limited(client_ip):
            self.send_error_page(429)
            logging.warning(f"Rate limited request from {client_ip}")
            return

        # Log the incoming request
        logging.info(f"Received {self.command} request for {self.path}")

        # Read the request body if it's a POST request
        content_length = int(self.headers.get('Content-Length', 0))
        request_body = self.rfile.read(content_length).decode('utf-8') if content_length else ''

        # Parse the URL to get the path and query
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parsed_url.query
        print(request_body)
        # Check if the request is malicious
        if (self.sql_injection_detector.inspect_request(path, query, request_body) or 
            self.xss_detector.inspect_request(path, query, request_body) or
            self.ssrf_detector.inspect_request(path, query, request_body) or
            self.ssti_detector.inspect_request(path, query, request_body) or
            self.path_traversal_detector.inspect_request(path, query, request_body) or
            self.xxe_detector.inspect_request(request_body) or
            self.os_command_injection_detector.inspect_request(path, query, request_body) or
            self.crlf_injection_detector.inspect_request(path, query, request_body)):
            self.send_error_page(403)
            logging.warning(f"Blocked malicious request: {self.path} with body {request_body}")
        else:
            # Forward the request to the backend server
            self.forward_request(request_body)

    def forward_request(self, request_body):
        headers = {key: self.headers[key] for key in self.headers}
        method = self.command.lower()
        url = f"{BACKEND_SERVER}{self.path}"

        if method == 'get':
            response = requests.get(url, headers=headers)
        elif method == 'post':
            response = requests.post(url, data=request_body, headers=headers)
        else:
            self.send_error_page(501)
            return

        self.send_response(response.status_code)
        for key, value in response.headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(response.content)

    def send_error_page(self, status_code):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open('error_page.html', 'r') as file:
            self.wfile.write(file.read().encode('utf-8'))

def run(server_class=HTTPServer, handler_class=WAFHTTPRequestHandler, port=8085):
    logging.basicConfig(level=logging.DEBUG)
    
    # Create separate loggers
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create file handlers for each log level
    info_handler = logging.FileHandler('waf_info.log')
    info_handler.setLevel(logging.INFO)
    warning_handler = logging.FileHandler('waf_warning.log')
    warning_handler.setLevel(logging.WARNING)
    error_handler = logging.FileHandler('waf_error.log')
    error_handler.setLevel(logging.ERROR)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create formatters and add them to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    info_handler.setFormatter(formatter)
    warning_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(info_handler)
    logger.addHandler(warning_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info(f"Starting WAF on port {port}, proxying to {BACKEND_SERVER}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
