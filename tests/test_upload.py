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
    stdout, stederr, ret = run_command("dpkg-buildpackage -us -uc -S",
                                       env={"DEB_VENDOR": "Ubuntu",
                                            "DPKG_ORIGINS_DIR": "../../dpkg-origins"})
    if os.path.exists("../fnord_1.0_source.test.upload"):
        os.unlink("../fnord_1.0_source.test.upload")
    os.chdir(popdir)
    return os.path.abspath("tests/fake_package/fnord_1.0_source.changes")


def test_upload():
    """ Test the upload of a package """
    path = _build_fnord()
    upload(path, 'test')


def test_double_upload():
    """ Test a double-upload (and force block) """
    path = _build_fnord()
    upload(path, 'test')
    try:
        upload(path, 'test')
        assert True is False
    except UploadException:
        pass
