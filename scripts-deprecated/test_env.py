
import sys
import torch
print(f"Python: {sys.version}")
print(f"Torch: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Device: {torch.cuda.get_device_name(0)}")

try:
    import langchain
    import faiss
    import transformers
    import sklearn
    print("All imports successful.")
except ImportError as e:
    print(f"Import Error: {e}")
