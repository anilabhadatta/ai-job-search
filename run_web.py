"""
AI Job Search - Web Application Launcher
Runs the Flask web interface for CV ingestion, job matching, and application tracking.

Usage:
    python run_web.py                                   # Runs on port 5000 at /ai-job-search
    python run_web.py --port 8080                       # Runs on custom port 8080
    python run_web.py --url-context /my-custom-prefix   # Custom URL context path
    python run_web.py --prod                            # Runs with production Waitress WSGI server
"""

import sys
import os
import argparse

# Parse CLI arguments early to set environment variables before importing app
parser = argparse.ArgumentParser(description="Launch AI Job Search Web Application")
parser.add_argument("--host", default="0.0.0.0", help="Host interface (default: 0.0.0.0)")
parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 5000)), help="Port to listen on (default: 5000)")
parser.add_argument("--url-context", "--url-prefix", dest="url_prefix", default=os.environ.get("URL_PREFIX", "/ai-job-search"), help="URL context / base prefix (default: /ai-job-search)")
parser.add_argument("--prod", action="store_true", help="Run with production Waitress WSGI server")
args = parser.parse_args()

# Set URL prefix in environment
os.environ["URL_PREFIX"] = args.url_prefix

# Ensure current directory is on python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from web_app.app import app

def main():
    prefix = app.config.get("URL_PREFIX", "")
    local_url = f"http://localhost:{args.port}{prefix}"
    print("=" * 65)
    print("  🚀 AI Job Search Web Application")
    print("  Targeting: Indian Software Companies & Global Remote")
    print(f"  URL Context: {prefix or '/'}")
    print(f"  Access local app at: {local_url}")
    print("=" * 65)

    if args.prod:
        try:
            from waitress import serve
            print(f"[*] Starting production Waitress server on {args.host}:{args.port}...")
            serve(app, host=args.host, port=args.port)
        except ImportError:
            print("[!] Waitress not found, falling back to Flask development server...")
            app.run(host=args.host, port=args.port, debug=False)
    else:
        print(f"[*] Starting Flask development server on {args.host}:{args.port}...")
        app.run(host=args.host, port=args.port, debug=True)

if __name__ == "__main__":
    main()
