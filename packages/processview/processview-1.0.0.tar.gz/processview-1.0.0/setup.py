#!/usr/bin/python
# coding: utf8
# /*##########################################################################
#
# Copyright (c) 2015-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

__authors__ = ["Henri Payno", "Jérôme Kieffer", "Thomas Vincent"]
__date__ = "29/01/2021"
__license__ = "MIT"


import sys
import os
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


from setuptools import find_packages

try:
    from setuptools import Command
    from setuptools.command.build_py import build_py as _build_py
    from setuptools.command.build_ext import build_ext
    from setuptools.command.sdist import sdist

    logger.info("Use setuptools")
except ImportError:
    try:
        from numpy.distutils.core import Command
    except ImportError:
        from distutils.core import Command
    from distutils.command.build_py import build_py as _build_py
    from distutils.command.build_ext import build_ext
    from distutils.command.sdist import sdist

    logger.info("Use distutils")

try:
    import sphinx
    import sphinx.util.console

    sphinx.util.console.color_terminal = lambda: False
    from sphinx.setup_command import BuildDoc
except ImportError:
    sphinx = None
from collections import namedtuple


PROJECT = "processview"

if "LANG" not in os.environ and sys.platform == "darwin" and sys.version_info[0] > 2:
    print(
        """WARNING: the LANG environment variable is not defined,
an utf-8 LANG is mandatory to use setup.py, you may face unexpected UnicodeError.
export LANG=en_US.utf-8
export LC_ALL=en_US.utf-8
"""
    )


def get_version():
    """Returns current version number from version.py file"""
    from processview.version import strictversion

    return strictversion


def get_readme():
    """Returns content of README.md file"""
    import io

    dirname = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(dirname, "README.md")
    with io.open(filename, "r", encoding="utf-8") as fp:
        long_description = fp.read()
    return long_description


classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Environment :: X11 Applications :: Qt",
    "Intended Audience :: Education",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: POSIX",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Topic :: Scientific/Engineering :: Physics",
    "Topic :: Software Development :: Libraries :: Python Modules",
]


########
# Test #
########


class PyTest(Command):
    """Command to start tests running the script: run_tests.py -i"""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess

        errno = subprocess.call([sys.executable, "run_tests.py"])
        if errno != 0:
            raise SystemExit(errno)


# ################### #
# build_doc command   #
# ################### #

if sphinx is None:

    class SphinxExpectedCommand(Command):
        """Command to inform that sphinx is missing"""

        user_options = []

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            raise RuntimeError(
                "Sphinx is required to build or test the documentation.\n"
                "Please install Sphinx (http://www.sphinx-doc.org)."
            )


class BuildMan(Command):
    """Command to build man pages"""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def entry_points_iterator(self):
        """Iterate other entry points available on the project."""
        entry_points = self.distribution.entry_points
        console_scripts = entry_points.get("console_scripts", [])
        gui_scripts = entry_points.get("gui_scripts", [])
        scripts = []
        scripts.extend(console_scripts)
        scripts.extend(gui_scripts)
        for script in scripts:
            # Remove ending extra dependencies
            script = script.split("[")[0]
            elements = script.split("=")
            target_name = elements[0].strip()
            elements = elements[1].split(":")
            module_name = elements[0].strip()
            function_name = elements[1].strip()
            yield target_name, module_name, function_name

    def run_targeted_script(self, target_name, script_name, env, log_output=False):
        """Execute targeted script using --help and --version to help checking
        errors. help2man is not very helpful to do it for us.
        :return: True is both return code are equal to 0
        :rtype: bool
        """
        import subprocess

        if log_output:
            extra_args = {}
        else:
            try:
                # Python 3
                from subprocess import DEVNULL
            except ImportError:
                # Python 2
                import os

                DEVNULL = open(os.devnull, "wb")
            extra_args = {"stdout": DEVNULL, "stderr": DEVNULL}

        succeeded = True
        command_line = [sys.executable, script_name, "--help"]
        if log_output:
            logger.info("See the following execution of: %s", " ".join(command_line))
        p = subprocess.Popen(command_line, env=env, **extra_args)
        status = p.wait()
        if log_output:
            logger.info("Return code: %s", status)
        succeeded = succeeded and status == 0
        command_line = [sys.executable, script_name, "--version"]
        if log_output:
            logger.info("See the following execution of: %s", " ".join(command_line))
        p = subprocess.Popen(command_line, env=env, **extra_args)
        status = p.wait()
        if log_output:
            logger.info("Return code: %s", status)
        succeeded = succeeded and status == 0
        return succeeded

    def run(self):
        build = self.get_finalized_command("build")
        path = sys.path
        path.insert(0, os.path.abspath(build.build_lib))

        env = dict((str(k), str(v)) for k, v in os.environ.items())
        env["PYTHONPATH"] = os.pathsep.join(path)

        import subprocess

        status = subprocess.call(["mkdir", "-p", "build/man"])
        if status != 0:
            raise RuntimeError("Fail to create build/man directory")

        import tempfile
        import stat

        script_name = None

        entry_points = self.entry_points_iterator()
        for target_name, module_name, function_name in entry_points:
            logger.info("Build man for entry-point target '%s'" % target_name)

            # help2man expect a single executable file to extract the help
            # we create it, execute it, and delete it at the end
            py3 = sys.version_info >= (3, 0)
            try:
                # create a launcher using the right python interpreter
                script_fid, script_name = tempfile.mkstemp(
                    prefix="%s_" % target_name, text=True
                )
                script = os.fdopen(script_fid, "wt")
                script.write("#!%s\n" % sys.executable)
                script.write("import %s as app\n" % module_name)
                script.write("app.%s()\n" % function_name)
                script.close()
                # make it executable
                mode = os.stat(script_name).st_mode
                os.chmod(script_name, mode + stat.S_IEXEC)

                # execute help2man
                man_file = "build/man/%s.1" % target_name
                command_line = ["help2man", script_name, "-o", man_file]
                if not py3:
                    # Before Python 3.4, ArgParser --version was using
                    # stderr to print the version
                    command_line.append("--no-discard-stderr")
                    # Then we dont know if the documentation will contains
                    # durtty things
                    succeeded = self.run_targeted_script(
                        target_name, script_name, env, False
                    )
                    if not succeeded:
                        logger.info(
                            "Error while generating man file for target '%s'.",
                            target_name,
                        )
                        self.run_targeted_script(target_name, script_name, env, True)
                        raise RuntimeError(
                            "Fail to generate '%s' man documentation" % target_name
                        )

                p = subprocess.Popen(command_line, env=env)
                status = p.wait()
                if status != 0:
                    logger.info(
                        "Error while generating man file for target '%s'.", target_name
                    )
                    self.run_targeted_script(target_name, script_name, env, True)
                raise RuntimeError(
                    "Fail to generate '%s' man documentation" % target_name
                )
            finally:
                # clean up the script
                if script_name is not None:
                    os.remove(script_name)


if sphinx is not None:

    class BuildDocCommand(BuildDoc):
        """Command to build documentation using sphinx.

        Project should have already be built.
        """

        def run(self):
            # make sure the python path is pointing to the newly built
            # code so that the documentation is built on this and not a
            # previously installed version

            build = self.get_finalized_command("build")
            sys.path.insert(0, os.path.abspath(build.build_lib))

            # Build the Users Guide in HTML and TeX format
            for builder in ["html", "htmlhelp"]:
                self.builder = builder
                self.builder_target_dir = os.path.join(self.build_dir, builder)
                self.mkpath(self.builder_target_dir)
                BuildDoc.run(self)
            sys.path.pop(0)

    class BuildDocAndGenerateScreenshotCommand(BuildDocCommand):
        def run(self):
            old = os.environ.get("DIRECTIVE_SNAPSHOT_QT")
            os.environ["DIRECTIVE_SNAPSHOT_QT"] = "True"
            BuildDocCommand.run(self)
            if old is not None:
                os.environ["DIRECTIVE_SNAPSHOT_QT"] = old
            else:
                del os.environ["DIRECTIVE_SNAPSHOT_QT"]

else:
    BuildDocCommand = SphinxExpectedCommand
    BuildDocAndGenerateScreenshotCommand = SphinxExpectedCommand


# ################### #
# test_doc command    #
# ################### #

if sphinx is not None:

    class TestDocCommand(BuildDoc):
        """Command to test the documentation using sphynx doctest.

        http://www.sphinx-doc.org/en/1.4.8/ext/doctest.html
        """

        def run(self):
            # make sure the python path is pointing to the newly built
            # code so that the documentation is built on this and not a
            # previously installed version

            build = self.get_finalized_command("build")
            sys.path.insert(0, os.path.abspath(build.build_lib))

            # Build the Users Guide in HTML and TeX format
            for builder in ["doctest"]:
                self.builder = builder
                self.builder_target_dir = os.path.join(self.build_dir, builder)
                self.mkpath(self.builder_target_dir)
                BuildDoc.run(self)
            sys.path.pop(0)

else:
    TestDocCommand = SphinxExpectedCommand

# ############################# #
# numpy.distutils Configuration #
# ############################# #


def configuration(parent_package="", top_path=None):
    """Recursive construction of package info to be used in setup().

    See http://docs.scipy.org/doc/numpy/reference/distutils.html#numpy.distutils.misc_util.Configuration
    """
    try:
        from numpy.distutils.misc_util import Configuration
    except ImportError:
        raise ImportError(
            "To install this package, you must install numpy first\n"
            "(See https://pypi.python.org/pypi/numpy)"
        )
    config = Configuration(None, parent_package, top_path)
    config.set_options(
        ignore_setup_xxx_py=True,
        assume_default_configuration=True,
        delegate_options_to_subpackages=True,
        quiet=True,
    )
    config.add_subpackage(PROJECT)
    return config


class sdist_debian(sdist):
    """
    Tailor made sdist for debian
    * remove auto-generated doc
    * remove cython generated .c files
    * remove cython generated .c files
    * remove .bat files
    * include .l man files
    """

    @staticmethod
    def get_debian_name():
        from processview import version

        name = "%s_%s" % (PROJECT, version.debianversion)
        return name

    def prune_file_list(self):
        sdist.prune_file_list(self)
        to_remove = [
            "doc/build",
            "doc/pdf",
            "doc/html",
            "pylint",
            "epydoc",
            "doc/htmlhelp",
        ]
        print("Removing files for debian")
        for rm in to_remove:
            self.filelist.exclude_pattern(pattern="*", anchor=False, prefix=rm)

    def make_distribution(self):
        self.prune_file_list()
        sdist.make_distribution(self)
        dest = self.archive_files[0]
        dirname, basename = os.path.split(dest)
        base, ext = os.path.splitext(basename)
        while ext in [".zip", ".tar", ".bz2", ".gz", ".Z", ".lz", ".orig"]:
            base, ext = os.path.splitext(base)
        if ext:
            dest = "".join((base, ext))
        else:
            dest = base
        # sp = dest.split("-")
        # base = sp[:-1]
        # nr = sp[-1]
        debian_arch = os.path.join(dirname, self.get_debian_name() + ".orig.tar.gz")
        os.rename(self.archive_files[0], debian_arch)
        self.archive_files = [debian_arch]
        print("Building debian .orig.tar.gz in %s" % self.archive_files[0])


# ##### #
# setup #
# ##### #

PACKAGES = find_packages()


def get_project_configuration(dry_run):
    """Returns project arguments for setup"""
    install_requires = [
        # for most of the computation
        "silx>=0.14b",
    ]

    full_requires = [
        "PyQt5",
    ]

    extras_require = {"full": full_requires}

    setup_requires = ["setuptools", "numpy"]

    package_data = {
        # Resources files for processview library
        "processview.resources": [
            "gui/icons/*.png",
            "gui/icons/*.svg",
            "gui/icons/*.npy",
        ],
    }
    entry_points = {}

    cmdclass = dict(
        test=PyTest,
        build_doc=BuildDocCommand,
        build_screenshots=BuildDocAndGenerateScreenshotCommand,
        test_doc=TestDocCommand,
        build_man=BuildMan,
        debian_src=sdist_debian,
    )

    if dry_run:
        # DRY_RUN implies actions which do not require NumPy
        #
        # And they are required to succeed without Numpy for example when
        # pip is used to install processview when Numpy is not yet present in
        # the system.
        setup_kwargs = {}
    else:
        config = configuration()
        setup_kwargs = config.todict()
    setup_kwargs.update(
        name=PROJECT,
        version=get_version(),
        url="https://gitlab.esrf.fr/workflow/processview",
        author="data analysis unit",
        author_email="henri.payno@esrf.fr",
        classifiers=classifiers,
        description="Library workflow process supervision",
        long_description=get_readme(),
        packages=PACKAGES,
        install_requires=install_requires,
        setup_requires=setup_requires,
        cmdclass=cmdclass,
        package_data=package_data,
        zip_safe=False,
        entry_points=entry_points,
        extras_require=extras_require,
    )
    return setup_kwargs


def setup_package():
    """Run setup(**kwargs)

    Depending on the command, it either runs the complete setup which depends on numpy,
    or a *dry run* setup with no dependency on numpy.
    """

    # Check if action requires build/install
    dry_run = len(sys.argv) == 1 or (
        len(sys.argv) >= 2
        and (
            "--help" in sys.argv[1:]
            or sys.argv[1]
            in ("--help-commands", "egg_info", "--version", "clean", "--name")
        )
    )

    if dry_run:
        # DRY_RUN implies actions which do not require dependancies, like NumPy
        try:
            from setuptools import setup

            logger.info("Use setuptools.setup")
        except ImportError:
            from distutils.core import setup

            logger.info("Use distutils.core.setup")
    else:
        try:
            from setuptools import setup
        except ImportError:
            from numpy.distutils.core import setup

            logger.info("Use numpydistutils.setup")

    setup_kwargs = get_project_configuration(dry_run)
    setup(**setup_kwargs)


DATA_FILES = [
    # Data files that will be installed outside site-packages folder
]


def include_documentation(local_dir, install_dir):
    global DATA_FILES
    if "bdist_wheel" in sys.argv and not os.path.exists(local_dir):
        print(
            "Directory '{}' does not exist. "
            "Please build documentation before running bdist_wheel.".format(
                os.path.abspath(local_dir)
            )
        )
        sys.exit(0)

    doc_files = []
    for dirpath, dirs, files in os.walk(local_dir):
        doc_files.append(
            (
                dirpath.replace(local_dir, install_dir),
                [os.path.join(dirpath, f) for f in files],
            )
        )
    DATA_FILES.extend(doc_files)


if __name__ == "__main__":
    include_documentation("build/sphinx/html", "help/processview")
    setup_package()
