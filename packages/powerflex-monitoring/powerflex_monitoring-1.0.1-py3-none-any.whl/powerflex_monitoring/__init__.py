import os.path

with open(
    os.path.normpath(os.path.join(__file__, "../", "VERSION")), encoding="utf-8"
) as versionfile:
    __version__ = versionfile.read().strip()
