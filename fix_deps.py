
import sys
import subprocess
import importlib

def install(package):
    print(f"Installing {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

packages = ["langchain-community", "langchain-huggingface", "langchain"]

for package in packages:
    try:
        importlib.import_module(package.replace("-", "_"))
        print(f"{package} is already installed.")
    except ImportError:
        print(f"{package} not found. Attempting install...")
        try:
            install(package)
            print(f"{package} installed successfully.")
        except Exception as e:
            print(f"Failed to install {package}: {e}")

try:
    from langchain_community.llms import Ollama
    print("SUCCESS: langchain_community.llms.Ollama imported.")
except ImportError as e:
    print(f"FAILURE: Could not import Ollama: {e}")
