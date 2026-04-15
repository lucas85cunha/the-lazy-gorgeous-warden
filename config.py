import os
from pathlib import Path
from dotenv import load_dotenv

# Path Discovery
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_PATH = SCRIPT_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)

# Environment Variables
# Now it strictly pulls from .env. If not found, it defaults to None or a generic string.
TARGET_DIR = os.getenv("TARGET_DIRECTORY")
DRY_RUN = os.getenv("DRY_RUN", "True").lower() == "true"
API_KEY = os.getenv("GOOGLE_API_KEY")

# Official Hierarchy
REQUIRED_FOLDERS = [
    "01_Personal_Documents", 
    "02_Digital_Gallery", 
    "03_Studies_and_Career", 
    "04_Entertainment", 
    "05_Device_Backups"
]

IGNORE_LIST = ["lost+found", ".trash", ".warden-manifest.md", ".env", ".git", ".DS_Store"]

# Simple validation to ensure the path was loaded
if not TARGET_DIR:
    print("⚠️  Warning: TARGET_DIRECTORY not set in .env file.")
