"""
This file contains some general tools/examples to use in other test scenarios.
@author: Nathanael Jöhrmann
"""


def test_pythonconfig(pytestconfig):
    print('\n')
    print('args             :', pytestconfig.args)
    print('inifile          :', pytestconfig.inifile)
    print('invocation_dir   :', pytestconfig.invocation_dir)
    print('rootdir          :', pytestconfig.rootdir)
    print('-k EXPRESSION    :', pytestconfig.getoption('keyword'))
    print('-v, --verbose    :', pytestconfig.getoption('verbose'))
    # print('-q, -quiet       :', pytestconfig.getoption('quiet'))
    print('-l, --showlocals :', pytestconfig.getoption('showlocals'))
    print('--tb==style      :', pytestconfig.getoption('tbstyle'))
