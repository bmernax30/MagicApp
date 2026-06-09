#!/usr/bin/env python3

import os
import runpy
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent


def main():
    os.chdir(APP_DIR)
    runpy.run_path(str(APP_DIR / "main.py"), run_name="__main__")


if __name__ == "__main__":
    main()
