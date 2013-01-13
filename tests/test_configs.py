from dput.util import validate_object, load_config
from dput.exceptions import InvalidConfigError
import dput.core
import os


dput.core.CONFIG_LOCATIONS = {
    os.path.abspath("./tests/dputng"): 0
}  # Isolate.


def test_config_load():
    """ Make sure we can cleanly load a config """
    obj = load_config('profiles', 'test_profile')
    comp = {
        "incoming": "/dev/null",
        "method": "local",
        "meta": "ubuntu"
    }
    for key in comp:
        assert obj[key] == comp[key]


def test_config_validate():
    """ Make sure we can validate a good config """
    obj = load_config('profiles', 'test_profile')
    validate_object('config', obj, "profiles/test_profile")


def test_config_invalidate():
    """ Make sure a bad validation breaks """
    obj = load_config('profiles', 'test_profile_bad')
    try:
        validate_object('config', obj, "profiles/test_profile_bad")
        assert True is False
    except InvalidConfigError as e:
        assert e.config_name == "profiles/test_profile_bad"
