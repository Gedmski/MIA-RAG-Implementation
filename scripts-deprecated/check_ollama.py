
import requests
import sys
import subprocess
import time

def check_ollama():
    print("Checking Ollama connection...")
    try:
        response = requests.get("http://localhost:11434")
        if response.status_code == 200:
            print("SUCCESS: Ollama is running.")
            return True
        else:
            print(f"WARNING: Ollama responded with status code {response.status_code}")
            return True # It's running at least
    except requests.exceptions.ConnectionError:
        print("FAILURE: Could not connect to Ollama at http://localhost:11434")
        return False

if __name__ == "__main__":
    if not check_ollama():
        print("Attempting to start Ollama...")
        try:
            # Try to start it in a new window
            subprocess.Popen(["start", "ollama", "serve"], shell=True)
            print("Launched 'ollama serve'. Waiting for 10 seconds to initialize...")
            time.sleep(10)
            if check_ollama():
                print("SUCCESS: Ollama started successfully.")
            else:
                print("FAILURE: Ollama did not start in time. Please start it manually.")
        except Exception as e:
            print(f"Error trying to launch Ollama: {e}")
            print("Please run 'ollama serve' in a separate terminal.")
