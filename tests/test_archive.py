#!/usr/bin/env python

import lcatr.archive

def test_path():
    '''
    Test forming an archive path
    '''

    assert "a/b/c/4" == lcatr.archive.path("a","b","c",4)


if __name__ == '__main__':
    test_path()
