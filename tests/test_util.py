# These files aren't really copyrightable.

# A little temporary hack for those of us not using virtualenv
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import dput.core
from dput.exceptions import NoSuchConfigError
from dput.util import load_obj
from dput.conf import (load_configuration, load_conf)

import logging
import json


dput.core.logger.setLevel(logging.WARNING)
dput.core.DPUT_CONFIG_LOCATIONS = [
    "tests/resources/dputcf/global.cf",
    "tests/resources/dputcf/local.cf"
]

dput.core.CONFIG_LOCATIONS = [
    "tests/resources/config/global.d",
    "tests/resources/config/local.d"
]


def test_importer():
    """ Ensure loaded objects are sane """
    jl = load_obj("json.load")
    assert jl == json.load


def test_dput_cf_loader():
    config = load_configuration(dput.core.DPUT_CONFIG_LOCATIONS)
    assert config.sections() == ['global-one', 'global-two', 'local-one']

    assert config.items('global-one') == [
                        ('foo', 'foo'), ('bar', 'baz'), ('local', 'false')]
    assert config.items('global-two') == [
                        ('foo', 'bar'), ('bar', 'bar'), ('local', 'false')]
    assert config.items('local-one') == [
                        ('foo', 'bar'), ('bar', 'baz'), ('local', 'true')]

    assert config.get('global-one', 'local') == 'false'
    assert config.get('global-two', 'local') == 'false'
    assert config.get('local-one', 'local') == 'true'


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
