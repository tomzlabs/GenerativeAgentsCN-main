
import os
import sys
from generative_agents.path_mapping import PERSONA_PATH_MAP

print("Verifying PERSONA_PATH_MAP...")
expected_count = 25
if len(PERSONA_PATH_MAP) != expected_count:
    print(f"Error: Expected {expected_count} personas, found {len(PERSONA_PATH_MAP)}")
    sys.exit(1)

print("Verifying directory existence...")
base_dirs = [
    "generative_agents/frontend/static/assets/village/agents",
    "api/static/assets/village/agents",
    "public/static/assets/village/agents"
]

all_good = True
for base in base_dirs:
    if not os.path.exists(base):
        print(f"Warning: Base directory {base} does not exist.")
        continue
    
    for zh, en in PERSONA_PATH_MAP.items():
        path = os.path.join(base, en)
        if not os.path.exists(path):
            print(f"Error: Directory not found: {path} (Expected for {zh})")
            all_good = False
        # Ensure Chinese dir is gone or we at least verify English exists
        old_path = os.path.join(base, zh)
        if os.path.exists(old_path) and os.path.isdir(old_path):
             print(f"Warning: Old Chinese directory still exists: {old_path}")

if all_good:
    print("Verification passed: All directories exist with English names.")
else:
    print("Verification failed.")
    sys.exit(1)

print("Verifying template changes...")
template_path = "generative_agents/frontend/templates/main_script.html"
if os.path.exists(template_path):
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
        if "persona_path_map" in content:
             print("Template check passed: persona_path_map found in main_script.html")
        else:
             print("Template check failed: persona_path_map NOT found in main_script.html")
             sys.exit(1)
else:
    print(f"Warning: {template_path} not found.")
