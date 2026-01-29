import sys
import os

sys.path.append(os.getcwd())

try:
    from app.routers import skills
    print("Syntax verification successful!")
except Exception as e:
    print(f"Syntax error found: {e}")
    sys.exit(1)
