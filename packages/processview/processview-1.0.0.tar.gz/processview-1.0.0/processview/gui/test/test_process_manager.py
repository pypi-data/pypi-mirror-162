# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
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

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "02/11/2020"


import unittest
from processview.core.superviseprocess import SuperviseProcess
from processview.core.dataset import Dataset
from processview.core.dataset import DatasetIdentifier
from processview.gui.processmanager import ProcessManager
from processview.core.manager import DatasetState
from silx.gui.utils.testutils import SignalListener
from silx.gui.utils.testutils import TestCaseQt
import gc


class TestProcessManager(TestCaseQt):
    """
    test ProcessManager
    """

    def setUp(self):
        TestCaseQt.setUp(self)
        self.signalListener = SignalListener()
        self.manager = ProcessManager()
        self.manager.sigUpdated.connect(self.signalListener)

    def tearDown(self):
        self.signalListener = None
        self.processManager = None
        gc.collect()
        TestCaseQt.tearDown(self)

    def testProcessStatesUpdate(self):
        """insure providing states works well"""
        p1 = SuperviseProcess()
        p2 = SuperviseProcess()
        scan_1 = _DummyScan("scan1")
        scan_2 = _DummyScan("scan2")
        self.manager.notify_dataset_state(
            dataset=scan_1, state=DatasetState.PENDING, process=p1
        )
        self.manager.notify_dataset_state(
            dataset=scan_2, state=DatasetState.SUCCEED, process=p1
        )
        self.manager.notify_dataset_state(
            dataset=scan_2, state=DatasetState.FAILED, process=p2
        )
        self.assertEqual(self.signalListener.callCount(), 3)


class _DummyScan(Dataset):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __str__(self) -> str:
        return self.name

    def get_identifier(self) -> DatasetIdentifier:
        return _DummyIdentifier(self)


class _DummyIdentifier(DatasetIdentifier):
    def __init__(self, dataset):
        super().__init__(dataset)
        self.name = dataset.name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


def suite():
    test_suite = unittest.TestSuite()
    for ui in (TestProcessManager,):
        test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ui))
    return test_suite
