"""Helper functions to work with temporary storage"""

import contextlib
import os
import shutil
import tempfile

@contextlib.contextmanager
def cd(newdir, cleanup=lambda: True):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)
        cleanup()

@contextlib.contextmanager
def tempdir(remove_upon_completion=True):
    dirpath = tempfile.mkdtemp()

    def cleanup():
        shutil.rmtree(dirpath)

    if remove_upon_completion:
        with cd(dirpath, cleanup):
            yield dirpath
    else:
        with cd(dirpath):
            yield dirpath
