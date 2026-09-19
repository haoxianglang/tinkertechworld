#!/usr/bin/env python3
"""Compatibility launcher; local site and API now share one Node process/port."""
import os
from pathlib import Path
if __name__ == '__main__':
    os.execvp('node', ['node', str(Path(__file__).with_suffix('.mjs'))])
