from dput.util import run_command
from dput import upload
from dput.exceptions import UploadException
import dput.core
import os.path
import os

dput.core.CONFIG_LOCATIONS = {
    os.path.abspath("./tests/dputng"): 0
}  # Isolate.


def _build_fnord():
    popdir = os.path.abspath(os.getcwd())
    os.chdir("tests/fake_package/fake-package-1.0")
    stdout, stederr, ret = run_command("dpkg-buildpackage -us -uc -S")
    os.unlink("../fnord_1.0_source.test.upload")
    os.chdir(popdir)
    return os.path.abspath("tests/fake_package/fnord_1.0_source.changes")


def test_upload():
    path = _build_fnord()
    upload(path, 'test')


def test_double_upload():
    path = _build_fnord()
    upload(path, 'test')
    try:
        upload(path, 'test')
        assert True is False
    except UploadException:
        pass
