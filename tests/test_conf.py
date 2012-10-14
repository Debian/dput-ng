# These files aren't really copyrightable.

import dput.core
import dput.profile

import logging
import json

dput.core._enable_debugging(2)

dput.core.DPUT_CONFIG_LOCATIONS = [
    "tests/resources/defklob/cf1/dput.cf",
    "tests/resources/defklob/cf2/dput.cf"
]

dput.core.CONFIG_LOCATIONS = [
    "tests/resources/defklob/js1",
    "tests/resources/defklob/js2"
]

def test_default_klob():
    profile = dput.profile.load_profile("test")
    assert profile['name'] == 'test'
    assert profile['key1'] == 'bar'
