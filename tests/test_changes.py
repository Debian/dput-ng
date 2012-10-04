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
        Changes(filename='fake/file',
                string='some string content')
        assert True is False
    except TypeError:
        pass

    try:
        Changes()
        assert True is False
    except TypeError:
        pass


def test_empty_changes():
    try:
        Changes(filename='/dev/null')
        assert True is False
    except ChangesFileException:
        pass


def test_parse_basics_string():
    ch = Changes(string=test_changes)
    assert ch.get_filename() is None
    for key in ref_obj:
        assert ch[key] == ref_obj[key]
    assert "Files" in ch
    assert not "KruftyTag" in ch
    assert "srcpkg" == ch.get("source", None)
    assert ch.get('kruftykrufty', None) is None
    assert ch.get_pool_path() == 'pool/main/s/srcpkg'


def test_parse_basics_file():
    ch = Changes(filename=chfd)
    assert ch.get_filename() == 'test.changes'
    assert ch.get_changes_file() == 'test.changes'
    assert ch.get_files() == ['fileone', 'filetwo', 'filethree', 'foo.dsc']

    assert ch.get_component() == 'main'
    assert ch.get_priority() == 'priority'
    assert ch.get_dsc() == 'foo.dsc'
    assert ch.get_diff() is None
    # XXX: test the positive condition.


def test_section_parse():
    ch = Changes(filename=chfd)
    test = {
        "non-free/python": ['non-free', 'python'],
        "contrib/foobar": ['contrib', 'foobar'],
        "python": ['main', 'python'],
    }
    for t in test:
        assert test[t] == ch._parse_section(t)


def test_directory_stuff():
    ch = Changes(filename=chfd)
    assert ch._directory == ""
    ch.set_directory('foobar')
    assert ch._directory == "foobar"
    ch.set_directory(None)
    assert ch._directory == ""
