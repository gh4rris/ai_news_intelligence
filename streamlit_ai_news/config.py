import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

# paths
ROOT_PATH = Path(__file__).parent
PAGES_PATH = ROOT_PATH / "pages"

# pages
MAIN_PAGE = PAGES_PATH / "main_page.py"

# databricks
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")
DATABRICKS_ACCESS_TOKEN = os.getenv("DATABRICKS_ACCESS_TOKEN")
DATABRICKS_CATALOG = os.getenv("DATABRICKS_CATALOG")
print(DATABRICKS_HOST)