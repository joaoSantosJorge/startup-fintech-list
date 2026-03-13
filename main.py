"""Serve the generated dashboard on Railway."""

import os
import subprocess
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

DASHBOARD_DIR = os.path.join(os.path.dirname(__file__), "dashboard")
PORT = int(os.environ.get("PORT", 8000))


def generate_dashboard():
    """Run 05_dashboard.py if DB exists and dashboard is missing."""
    if os.path.exists(os.path.join(DASHBOARD_DIR, "index.html")):
        print("Dashboard already generated.")
        return
    db_path = os.path.join(os.path.dirname(__file__), "fintech.db")
    if os.path.exists(db_path):
        print("Generating dashboard from database...")
        subprocess.run([sys.executable, "05_dashboard.py"], check=True)
    else:
        print("Warning: No fintech.db found. Using pre-built dashboard files.")


def serve():
    os.chdir(DASHBOARD_DIR)
    server = HTTPServer(("0.0.0.0", PORT), SimpleHTTPRequestHandler)
    print(f"Serving dashboard on port {PORT}")
    server.serve_forever()


if __name__ == "__main__":
    generate_dashboard()
    serve()
