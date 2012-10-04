# These files aren't really copyrightable.

from dput.changes import Changes
from dput.exceptions import ChangesFileException

chfd = 'tests/resources/changes/test.changes'
test_changes = open(chfd, 'r').read()


def test_nonsense_fails():
    try:
        ch = Changes(filename='fake/file',
                     string='some string content')
        assert True == False
    except TypeError:
        pass

    try:
        ch = Changes()
        assert True == False
    except TypeError:
        pass


def test_empty_changes():
    try:
        ch = Changes(filename='/dev/null')
        assert True == False
    except ChangesFileException:
        pass


def test_parse_basics_string():
    ch = Changes(string=test_changes)


def test_parse_basics_file():
    ch = Changes(filename=chfd)
