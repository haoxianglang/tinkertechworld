"""Create a clean Cloudflare Pages asset directory; never upload source/secrets."""
from pathlib import Path
import json
import shutil
import tempfile
ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIRS = ['assets', 'image', 'products', 'programs', 'age-groups', 'zh']
EXTENSIONS = {'.html', '.css', '.js', '.json', '.webp', '.png', '.jpg', '.jpeg', '.svg', '.gif', '.ico', '.woff', '.woff2'}

def main():
    staging = Path(tempfile.mkdtemp(prefix='.public-stage-', dir=ROOT))
    try:
        for folder in PUBLIC_DIRS:
            for source in (ROOT / folder).rglob('*'):
                if not source.is_file() or source.is_symlink() or source.suffix.lower() not in EXTENSIONS:
                    continue
                if any(part.startswith('.') for part in source.relative_to(ROOT).parts):
                    continue
                dest = staging / source.relative_to(ROOT)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, dest)
        for source in [*ROOT.glob('*.html'), *(ROOT / f for f in ['robots.txt', 'sitemap.xml', '.nojekyll', 'CNAME'])]:
            if source.is_file() and not source.is_symlink():
                shutil.copyfile(source, staging / source.name)
        (staging / '_routes.json').write_text(json.dumps({'version': 1, 'include': ['/api/chat'], 'exclude': []}))
        output = ROOT / 'dist'
        if output.is_symlink():
            raise RuntimeError('Refusing to overwrite a symlink at dist/')
        if output.exists():
            shutil.rmtree(output)
        staging.rename(output)
        print('Prepared dist/: public assets only; Pages compiles functions/ separately.')
    finally:
        if staging.exists():
            shutil.rmtree(staging)
if __name__ == '__main__':
    main()
