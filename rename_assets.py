import os
import shutil
from generative_agents.path_mapping import PERSONA_PATH_MAP

DIRECTORIES_TO_UPDATE = [
    "generative_agents/frontend/static/assets/village/agents",
    "api/static/assets/village/agents",
    "public/static/assets/village/agents"
]

def rename_directories():
    base_dir = os.getcwd()
    
    for dir_rel_path in DIRECTORIES_TO_UPDATE:
        full_path = os.path.join(base_dir, dir_rel_path)
        if not os.path.exists(full_path):
            print(f"Skipping {full_path} (not found)")
            continue
            
        print(f"Processing {dir_rel_path}...")
        
        for ch_name, en_name in PERSONA_PATH_MAP.items():
            old_path = os.path.join(full_path, ch_name)
            new_path = os.path.join(full_path, en_name)
            
            if os.path.exists(old_path):
                # Check if target already exists to avoid conflict
                if os.path.exists(new_path):
                    print(f"  Target {en_name} already exists. Merging/Skipping...")
                    # In a real scenario we might merge, but here distinct names are expected.
                    # We'll just assume it's done or partial run.
                else:
                    try:
                        os.rename(old_path, new_path)
                        print(f"  Renamed {ch_name} -> {en_name}")
                    except Exception as e:
                        print(f"  Error renaming {ch_name}: {e}")
            else:
                 # It might have been renamed already
                 if os.path.exists(new_path):
                     print(f"  {ch_name} already renamed to {en_name}")
                 else:
                     print(f"  Warning: Source {ch_name} not found in {dir_rel_path}")

if __name__ == "__main__":
    rename_directories()
