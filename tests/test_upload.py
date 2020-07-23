from dput.util import run_command
from dput import upload
from dput.exceptions import UploadException
import dput.core
import glob
import os.path
import os

dput.core.CONFIG_LOCATIONS = {
    os.path.abspath("./tests/dputng"): 0
}  # Isolate.


def _build_fnord(version='1.0'):
    popdir = os.path.abspath(os.getcwd())
    os.chdir("tests/fake_package/fake-package-%s" % version)
    cmd = "dpkg-buildpackage -us -uc -S"
    env = {
        "DEB_VENDOR": "Ubuntu",
        "DPKG_ORIGINS_DIR": "../../dpkg-origins",
        "PATH": os.environ["PATH"],
    }
    stdout, stderr, ret = run_command(cmd, env=env)
    upload_files = glob.glob("../fnord_%s_source.*.upload" % version)
    for fn in upload_files:
        os.unlink(fn)
    os.chdir(popdir)
    if ret != 0:
        print('Package build failed.')
        print(f'cmd: {cmd}')
        print(f'env: {env}')
        print('###### stdout:')
        print(stdout)
        print('###### stderr:')
        print(stderr)
        print('###### - end log')
        assert False
    return os.path.abspath("tests/fake_package/fnord_%s_source.changes"
                           % version)


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


def test_ppa_upload():
    """ Test the upload of a package to a PPA (no Launchpad-Bugs-Fixed) """
    path = _build_fnord(version='1.1')
    upload(path, 'ppa:foo/bar')
