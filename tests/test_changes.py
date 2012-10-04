# These files aren't really copyrightable.

from dput.changes import Changes
from dput.exceptions import ChangesFileException

chfd = 'tests/resources/changes/test.changes'
test_changes = open(chfd, 'r').read()

ref_obj = {
    "Format": "1.8",
    "Date": "Wed, 30 May 2012 22:17:42 -0400",
    "Source": "srcpkg",
    "Binary": "binpkg",
    "Architecture": "source",
    "Version": "1.3.2-1",
    "Distribution": "unstable",
    "Urgency": "low",
    "Maintainer": "Paul Tagliamonte <paultag@debian.org>",
    "Changed-By": "Paul Tagliamonte <paultag@ubuntu.com>"
}

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
    assert ch.get_filename() == None
    for key in ref_obj:
        assert ch[key] == ref_obj[key]


def test_parse_basics_file():
    ch = Changes(filename=chfd)
    assert ch.get_filename() == 'test.changes'
    for key in ref_obj:
        assert ch[key] == ref_obj[key]
    assert ch.get_changes_file() == 'test.changes'
    assert ch.get_files() == ['fileone', 'filetwo', 'filethree']
