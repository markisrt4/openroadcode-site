"""Regression tests for the source-owned documentation import."""

import tempfile
import unittest
from pathlib import Path

from import_readmes import import_documents, site_location


class ImportReadmesTests(unittest.TestCase):
    def test_existing_routes_are_preserved(self):
        cases = {
            "README.md": "/docs/project/",
            "docs/README.md": "/docs/",
            "controllers/radio/README.md": "/docs/controllers/radio/",
            "docs/navigation_runtime.md": "/docs/navigation-runtime/",
            "apps/orcUi/ARCHITECTURE.md": "/docs/apps/orcui/architecture/",
            "CONTRIBUTING.md": "/docs/contributing/",
        }
        for path, expected in cases.items():
            kind = "readme" if path.endswith("README.md") else "guide"
            if path == "CONTRIBUTING.md":
                kind = "contributing"
            if path.endswith("ARCHITECTURE.md"):
                kind = "curated"
            self.assertEqual(site_location({"path": path, "kind": kind})[2], expected)

    def test_import_uses_manifest_and_rewrites_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            for name, content in {
                "docs/README.md": "# Documentation\n\n[Radio](../controllers/radio/README.md)\n",
                "controllers/radio/README.md": "# Radio\n\n[Home](../../docs/README.md)\n",
            }.items():
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            records = [
                {"path": "docs/README.md", "kind": "readme", "title": "Documentation"},
                {"path": "controllers/radio/README.md", "kind": "readme", "title": "Radio"},
            ]
            output = root / "output"
            tree = root / "tree.json"
            import_documents(source, output, tree, records)
            self.assertIn("/docs/controllers/radio/", (output / "docs/index.md").read_text())
            self.assertIn("/docs/", (output / "controllers/radio/index.md").read_text())
            self.assertTrue(tree.is_file())
            with self.assertRaises(RuntimeError):
                import_documents(source, output, tree, records + [records[0]])
            with self.assertRaises(FileNotFoundError):
                import_documents(source, output, tree, records + [{"path": "missing/README.md", "kind": "readme", "title": "Missing"}])


if __name__ == "__main__":
    unittest.main()
