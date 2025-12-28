import os
import sys
import subprocess

def main():
    try:
        subprocess.call(
            [sys.executable, "-m", "streamlit", "run", "src/app.py"],
            shell=True
        )
    except Exception as e:
        print("Error:", e)
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
