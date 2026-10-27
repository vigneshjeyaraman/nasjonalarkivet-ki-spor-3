import os
import re
import argparse
from pathlib import Path

def clean_filename(filename):
    # Try to find a date pattern (YYYY_MM_DD or YYYY-MM-DD)
    date_match = re.search(r"(\d{4})[-_](\d{2})[-_](\d{2})", filename)
    if date_match:
        date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
        # Remove the date part and clean up the rest
        desc = filename.replace(date_match.group(0), "").strip(" _-")
        # Remove common junk like (1)
        desc = re.sub(r"\s*\(\d+\)", "", desc).strip(" _-")
        ext = Path(filename).suffix
        return f"{date_str}_{desc}{ext}"
    
    # Fallback: just clean up spaces and underscores
    return filename.strip(" _-")

def main():
    parser = argparse.ArgumentParser(description="Standardize filenames in the inbox.")
    parser.add_argument("--apply", action="store_true", help="Actually rename the files.")
    args = parser.parse_args()

    inbox = Path("exercises/k/inbox")
    if not inbox.exists():
        print(f"Error: {inbox} not found.")
        return

    files = sorted([f for f in inbox.iterdir() if f.is_file()])
    
    print(f"Mode: {'APPLY' if args.apply else 'DRY RUN (no changes made)'}")
    print("-" * 50)

    for file_path in files:
        old_name = file_path.name
        new_name = clean_filename(old_name)
        
        if old_name == new_name:
            print(f"Skipping: {old_name} (already clean)")
            continue
            
        print(f"Rename: {old_name}  -->  {new_name}")
        
        if args.apply:
            new_path = file_path.with_name(new_name)
            if new_path.exists():
                print(f"  [ERROR] Target {new_name} already exists. Skipping.")
            else:
                file_path.rename(new_path)

if __name__ == "__main__":
    main()
