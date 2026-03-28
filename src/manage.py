#!/usr/bin/env python
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def main() -> None:
    src_dir = Path(__file__).resolve().parent
    project_root = src_dir.parent

    load_dotenv(project_root / ".env")

    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
