import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "example_project"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example_project.settings")
django.setup()
