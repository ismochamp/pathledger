import json
import pathlib
import sys
import tempfile
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from generate_fixture import generate_fixture


class FixtureTests(unittest.TestCase):
    def test_manifest_roundtrip_and_idempotence(self):
        with tempfile.TemporaryDirectory() as d:
            target = pathlib.Path(d).resolve() / "archive"
            generate_fixture(target)
            manifest = json.loads((pathlib.Path(__file__).resolve().parents[1] / "fixtures/archive_manifest.json").read_text())
            before = {f.relative_to(target).as_posix(): f.read_text() for f in target.rglob("*") if f.is_file()}
            self.assertEqual(before, manifest)
            self.assertEqual(generate_fixture(target), target)
            self.assertEqual(before, {f.relative_to(target).as_posix(): f.read_text() for f in target.rglob("*") if f.is_file()})

    def test_differing_existing_file_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            target = pathlib.Path(d).resolve() / "archive"
            generate_fixture(target)
            existing = target / "README.txt"
            existing.write_text("preserve this data")
            with self.assertRaises(ValueError):
                generate_fixture(target)
            self.assertEqual(existing.read_text(), "preserve this data")

    def test_symlink_destination_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            outside = pathlib.Path(d).resolve() / "outside"
            outside.mkdir()
            link = pathlib.Path(d).resolve() / "linked"
            link.symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                generate_fixture(link / "archive")
            self.assertEqual(list(outside.iterdir()), [])
