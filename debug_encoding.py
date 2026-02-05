import os
import unicodedata

def check_normalization(path):
    if not os.path.exists(path):
        print(f"Path not found: {path}")
        return

    for filename in os.listdir(path):
        if "伊莎贝拉" in filename: # Check if we can match it loosely or just list all
            print(f"Found: {filename}")
            print(f"Bytes: {filename.encode('utf-8')}")
            is_nfc = unicodedata.is_normalized('NFC', filename)
            is_nfd = unicodedata.is_normalized('NFD', filename)
            print(f"Is NFC: {is_nfc}")
            print(f"Is NFD: {is_nfd}")

# Check both locations
print("Checking api/static/assets/village/agents")
check_normalization("api/static/assets/village/agents")

print("\nChecking public/static/assets/village/agents")
check_normalization("public/static/assets/village/agents")

print("\nChecking generative_agents/frontend/static/assets/village/agents")
check_normalization("generative_agents/frontend/static/assets/village/agents")
