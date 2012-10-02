# These files aren't really copyrightable.

import dput.core
from dput.exceptions import NoSuchConfigError
from dput.util import (load_obj, load_dput_configs, load_config)

import logging
import json


dput.core.logger.setLevel(logging.WARNING)
dput.core.DPUT_CONFIG_LOCATIONS = [
    "tests/resources/dputcf/global.cf",
    "tests/resources/dputcf/local.cf"
]

dput.core.CONFIG_LOCATIONS = [
    "tests/resources/config/local.d",
    "tests/resources/config/global.d"
]


def test_importer():
    """ Ensure loaded objects are sane """
    jl = load_obj("json.load")
    assert jl == json.load


def test_dput_cf_loader():
    config = load_dput_configs()
    assert config['global-one'] == {
        "foo": "foo",
        "bar": "baz",
        "local": "false"
    }
    assert config['global-two'] == {
        "foo": "bar",
        "bar": "bar",
        "local": "false"
    }
    assert config['local-one'] == {
        "foo": "bar",
        "bar": "baz",
        "local": "true"
    }


def test_config_loader():
    """ Ensure loaded configs are sane """
    test = "test"
    obj1 = load_config('class-g', test)
    assert obj1 == {
        "foo": "bar",
        "bar": "baz"
    }
    obj2 = load_config('class-l', test)
    assert obj2 == {
        "foo": "foo",
        "bar": "bar"
    }


def test_throw_exception():
    try:
        load_config("foobar", "foobar")
    except NoSuchConfigError:
        pass
