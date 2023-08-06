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
"""helper functions to notify state change for example"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "13/04/2021"


from processview.core.manager import ProcessManager
from processview.core.manager import DatasetState
from processview.core.superviseprocess import SuperviseProcess


def notify_skip(process, dataset, details=None):
    ProcessManager().notify_dataset_state(
        dataset=dataset, process=process, state=DatasetState.SKIPPED, details=details
    )


def notify_pending(process, dataset, details=None):
    ProcessManager().notify_dataset_state(
        dataset=dataset, process=process, state=DatasetState.PENDING, details=details
    )


def notify_succeed(process, dataset, details=None):
    ProcessManager().notify_dataset_state(
        dataset=dataset, process=process, state=DatasetState.SUCCEED, details=details
    )


def notify_failed(process, dataset, details=None):
    ProcessManager().notify_dataset_state(
        dataset=dataset, process=process, state=DatasetState.FAILED, details=details
    )
