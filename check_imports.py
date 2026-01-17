
import langchain
import langchain_community
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    print("Import from langchain.text_splitter: SUCCESS")
except ImportError:
    print("Import from langchain.text_splitter: FAILED")

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    print("Import from langchain_text_splitters: SUCCESS")
except ImportError:
    print("Import from langchain_text_splitters: FAILED")

print(f"LangChain Version: {langchain.__version__}")
