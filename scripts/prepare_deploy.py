#!/usr/bin/env python3
"""Package the reviewed HTML and assets without rendering templates over them."""
from pathlib import Path
from generate_pages_function import main as build_chat
from generate_worker import main as build_worker
from stage_public import main as stage_public

ROOT = Path(__file__).resolve().parent.parent


def main():
    if not (ROOT / 'index.html').is_file():
        raise RuntimeError('Missing index.html. Generate pages explicitly with build_site.py --regenerate first.')
    build_chat()
    build_worker()
    stage_public()
    print('Prepared deployment from existing HTML and assets; public source files were not regenerated.')


if __name__ == '__main__':
    main()
