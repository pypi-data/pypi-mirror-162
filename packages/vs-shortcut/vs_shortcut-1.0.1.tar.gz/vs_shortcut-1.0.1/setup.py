"""
    Setup file for vs_shortcut.

"""

import os
from shutil import rmtree
from os.path import join as pjoin
from multiprocessing import freeze_support

from setuptools import setup, Command


class CleanCommand(Command):
    """Custom command to clean the build files.
    
    """

    user_options = [("all", "a", "")]

    def initialize_options(self):
        self.all = True
        self._clean_me = []
        self._clean_trees = []

        for root, dirs, files in os.walk("./src/vs_shortcut"):
            for f in files:
                filepath = pjoin(root, f)
                if filepath in self._clean_exclude:
                    continue

                if os.path.splitext(f)[-1] in (
                    ".pyc",
                    ".so",
                    ".o",
                    ".pyo",
                    ".pyd",
                    ".c",
                    ".cpp",
                    ".orig",
                ):
                    self._clean_me.append(filepath)
            for d in dirs:
                if d == "__pycache__":
                    self._clean_trees.append(pjoin(root, d))

        for d in ("build", "dist"):
            if os.path.exists(d):
                self._clean_trees.append(d)

    def finalize_options(self):
        pass

    def run(self):
        for clean_me in self._clean_me:
            try:
                os.unlink(clean_me)
            except OSError:
                pass
        for clean_tree in self._clean_trees:
            try:
                rmtree(clean_tree)
            except OSError:
                pass


# we need to inherit from the versioneer
# class as it encodes the version info
#cmdclass = versioneer.get_cmdclass()
#cmdclass["clean"] = CleanCommand


if __name__ == "__main__":
    try:
        freeze_support()
        setup(
            version="1.0.1",
        )
    except:  # noqa
        print(
            "\n\nAn error occurred while building the project, "
            "please ensure you have the most updated version of setuptools, "
            "setuptools_scm and wheel with:\n"
            "   pip install -U setuptools setuptools_scm wheel\n\n"
        )
        raise
