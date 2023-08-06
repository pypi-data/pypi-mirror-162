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
from processview.core.manager import ProcessManager
from processview.core.manager import DatasetState
from processview.core.dataset import Dataset
from processview.core.dataset import DatasetIdentifier
import gc


class TestProcessManager(unittest.TestCase):
    """
    test ProcessManager
    """

    def testRegisterProcess(self):
        """insure registration and unregistration are working"""
        manager = ProcessManager()
        manager.clear()
        self.assertEqual(len(manager.get_processes()), 0)
        p1 = SuperviseProcess()
        self.assertEqual(len(manager.get_processes()), 1)
        p1 = None
        gc.collect()
        self.assertEqual(len(manager.get_processes()), 0)
        p1 = SuperviseProcess()
        p2 = SuperviseProcess()
        self.assertEqual(len(manager.get_processes()), 2)
        self.assertEqual(len(ProcessManager().get_processes()), 2)
        self.assertTrue(p1 in manager.get_processes())
        self.assertTrue(p2 in manager.get_processes())
        p1 = None
        p2 = None
        gc.collect()
        self.assertEqual(len(manager.get_processes()), 0)

    def testProcessStatesUpdate(self):
        """insure providing states works well"""
        p1 = SuperviseProcess(name="sp1")
        p2 = SuperviseProcess(name="sp1")
        manager = ProcessManager()
        manager.clear()
        scan_1 = _DummyScan("scan1")
        scan_2 = _DummyScan("scan2")
        manager.notify_dataset_state(
            dataset=scan_1, state=DatasetState.PENDING, process=p1
        )
        manager.notify_dataset_state(
            dataset=scan_2, state=DatasetState.SUCCEED, process=p1
        )
        manager.notify_dataset_state(
            dataset=scan_2, state=DatasetState.FAILED, process=p2
        )
        # test 'getScanState'
        self.assertEqual(
            manager.get_dataset_state(dataset_id=scan_2, process=p2),
            DatasetState.FAILED,
        )

        self.assertEqual(manager.get_dataset_state(dataset_id=scan_1, process=p2), None)

        # test 'getScanStream'
        self.assertEqual(
            manager.get_dataset_stream(dataset=scan_2, time_stamp=False),
            (
                (p1.process_id, DatasetState.SUCCEED),
                (p2.process_id, DatasetState.FAILED),
            ),
        )

        # test 'getProcessHistory'
        self.assertEqual(
            manager.get_process_history(process=p1),
            (
                (scan_1.get_identifier(), DatasetState.PENDING),
                (scan_2.get_identifier(), DatasetState.SUCCEED),
            ),
        )


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
