import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "generative_agents")
ROOT = os.path.abspath(ROOT)
os.chdir(ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from replay import app as flask_app

app = flask_app
