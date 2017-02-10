#! /usr/bin/env python

import tempfile
import unittest
import shutil
import subprocess
import logging
import sys
import os
import textwrap

logging.basicConfig(format="[%(levelname)s] %(asctime)s %(message)s")

PREREQUISITES = [subprocess.call("virtualenv --help > /dev/null", shell=True) == 0,
                 os.path.isdir("one"),
                 os.path.isdir("two"),
                 os.path.exists(os.path.join("one", "setup.py")),
                 os.path.exists(os.path.join("two", "setup.py"))]


@unittest.skipUnless(all(PREREQUISITES), "Test PREREQUISITES not satisfied: {0}".format(__file__))
class TestNamespacePackaging(unittest.TestCase):

    def test_install_one_then_two(self):
        self._install_one()
        self._install_two()
        stdout = TestNamespacePackaging._shell(self._test_command)
        self.assertTrue(stdout.startswith("bar from two"))

    def test_install_two_then_one(self):
        self._install_two()
        self._install_one()
        stdout = TestNamespacePackaging._shell(self._test_command)
        self.assertTrue(stdout.startswith("bar from one"))

    def setUp(self):
        self._test_dir = tempfile.mkdtemp()
        self._test_file_path = os.path.join(self._test_dir, "test.py")
        self._venv = os.path.join(self._test_dir, "venv")
        self._pip = os.path.join(self._venv, "bin", "pip")
        self._python = os.path.join(self._venv, "bin", "python")
        self._test_command = "{0} {1}".format(self._python, self._test_file_path)
        TestNamespacePackaging._shell("virtualenv {0}".format(self._venv))
        TestNamespacePackaging._shell("{0} install --upgrade pip".format(self._pip))
        with open(self._test_file_path, 'wb') as test_file:
            test_file.write(textwrap.dedent("""\
                              from com.foo import bar
                              bar.who_am_i()
                              """))

    def tearDown(self):
        shutil.rmtree(self._test_dir)

    def _install_one(self):
        TestNamespacePackaging._shell("{0} install one/".format(self._pip))

    def _install_two(self):
        TestNamespacePackaging._shell("{0} install two/".format(self._pip))

    @staticmethod
    def _shell(cmd):
        logging.info("Calling: " + cmd)
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        p.wait()
        stdout, stderr = p.stdout.read(), p.stderr.read()
        err = [l for l in stderr.split("\n") if l.strip()]
        for a in err:
            logging.error(a)
        if p.returncode:
            sys.exit(p.returncode)
        return stdout

if __name__ == '__main__':
    unittest.main()
