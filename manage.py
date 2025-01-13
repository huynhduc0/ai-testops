#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from unittest.mock import patch

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'canvas.settings')
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

def test_main():
    with patch('os.environ.setdefault') as mock_setdefault, \
         patch('django.core.management.execute_from_command_line') as mock_execute:
        main()
        mock_setdefault.assert_called_once_with('DJANGO_SETTINGS_MODULE', 'canvas.settings')
        mock_execute.assert_called_once_with(sys.argv)
