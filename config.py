import os
from pathlib import Path
from dotenv import load_dotenv

# Path Discovery
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_PATH = SCRIPT_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)

# Environment Variables
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

# Added Linux trash folders to ignore list
IGNORE_LIST = [
    "lost+found", ".trash", ".warden-manifest.md", 
    ".env", ".git", ".DS_Store", ".Trash-1000", ".Trash-100"
]
