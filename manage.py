#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import multiprocessing
import os
import sys


def main():
    # Allow to activate parallelization with python 3.8 and Django 3.1.X
    multiprocessing.set_start_method("fork")
    """Run administrative tasks."""
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE', 'huestion_project.settings'
    )
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
