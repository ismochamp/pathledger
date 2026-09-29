# Synthetic archive fixture

`archive_manifest.json` preserves the contents and relative names of the verification archive. All data is fictional. Run `python3 generate_fixture.py` from the project root on macOS/POSIX to materialize it under ignored `runtime/operations-archive/`.

Keeping filenames in a manifest makes the repository checkout portable: the deliberately Windows-invalid names and long fixture paths are created only when requested on a filesystem that supports them. The screenshot fixture produces three blocking findings, one projected path-length warning and one Unicode review item.
