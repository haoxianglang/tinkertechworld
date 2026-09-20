"""Regression: deploying a hand-edited page must not restore template text."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class DeploymentPreservationTest(unittest.TestCase):
    def test_both_current_and_legacy_build_commands_preserve_reviewed_pages(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ['scripts', 'knowledge', 'content']:
                shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns('__pycache__'))
            for name in ['server', 'functions/api', 'cloudflare-worker', 'assets', 'zh/programs']:
                (root / name).mkdir(parents=True, exist_ok=True)
            # Deliberately differs from the template, like the reported WRO edit.
            reviewed = '<!doctype html><html lang="zh"><body>已审核的新文案，保留原文件。\n</body></html>'.encode()
            (root / 'index.html').write_bytes(b'<!doctype html><title>Reviewed home</title>')
            page = root / 'zh/programs/wro.html'
            page.write_bytes(reviewed)
            (root / 'assets/example.css').write_bytes(b'body { color: #17333f; }\n')
            (root / '.dev.vars').write_text('GEMINI_API_KEY=test-only-not-a-secret')
            for script in ['scripts/prepare_deploy.py', 'scripts/build_site.py']:
                with self.subTest(command=script):
                    subprocess.run([sys.executable, script], cwd=root, check=True, capture_output=True)
                    self.assertEqual(page.read_bytes(), reviewed)
                    self.assertEqual((root / 'dist/zh/programs/wro.html').read_bytes(), reviewed)
                    self.assertEqual((root / 'dist/assets/example.css').read_bytes(), (root / 'assets/example.css').read_bytes())
                    self.assertTrue((root / 'server/knowledge.mjs').is_file())
                    self.assertFalse((root / 'dist/.dev.vars').exists())
                    self.assertFalse((root / 'dist/server').exists())


if __name__ == '__main__':
    unittest.main()
