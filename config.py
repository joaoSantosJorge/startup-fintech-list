import os
from dotenv import load_dotenv

load_dotenv()

# Database
DB_PATH = os.path.join(os.path.dirname(__file__), "fintech.db")

# YC API
API_URL = "https://yc-oss.github.io/api/industries/fintech.json"

# Claude model config
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 1024

# Niche categories for classification
NICHE_CATEGORIES = [
    "Payments",
    "Banking",
    "Lending",
    "Insurance",
    "Wealth Management",
    "Crypto/Blockchain",
    "Infrastructure/API",
    "Accounting/Tax",
    "Consumer Finance",
    "Embedded Finance",
    "Regulatory/Compliance",
    "Other",
]
