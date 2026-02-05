import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PRIMARY_STATIC_ROOT = os.path.join(REPO_ROOT, "public", "static")
FALLBACK_STATIC_ROOT = os.path.join(REPO_ROOT, "generative_agents", "frontend", "static")
STATIC_ROOT = PRIMARY_STATIC_ROOT if os.path.isdir(PRIMARY_STATIC_ROOT) else FALLBACK_STATIC_ROOT
os.environ.setdefault("STATIC_ROOT", STATIC_ROOT)

ROOT = os.path.join(REPO_ROOT, "generative_agents")
os.chdir(ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from replay import app as flask_app

app = flask_app
