import os
import subprocess

# Set your folder paths
scrape_folder = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/Scrape'
extract_folder = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/extract'

def run_python_scripts(folder):
    py_files = [f for f in os.listdir(folder) if f.endswith('.py')]
    for script in py_files:
        script_path = os.path.join(folder, script)
        print(f"[RUNNING] {script_path}")
        
        # Add UTF-8 environment override
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            env=env  # ✅ Pass updated environment
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"[ERROR] In {script}:")
            print(result.stderr)

# Run in order
print("[INFO] Running Scrape scripts...")
run_python_scripts(scrape_folder)

print("\n[INFO] Running Extract scripts...")
run_python_scripts(extract_folder)

print("\n[DONE] All scripts executed.")
