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
__date__ = "29/01/2021"


from .manager import ProcessManager
from .manager import DatasetState
from .dataset import Dataset


class SuperviseProcess:
    """
    Supervise process are processes with a state.
    They are decoupled of BaseProcess because a SuperviseProcess can be
    a group of BaseProcess. This is more dedicated to users.
    For example Axis is a Base process that could only 'Suceed' or 'Failed'
    But the SuperviseProcess Axis contained a stack. So it can also be
    skipped, Pending or on going for example.
    Still for Axis we will have in fact three actors:
        - AxisProcess (tomwer.core.process.reconstruction.axis):
            core source code for doing the center of rotation calculation
        - AxisProcessStack (tomwer.synctools.stacks.reconstruction.axis):
            stack to handle several call to axis
        - _ProcessingThread (tomwer.synctools.stacks.reconstruction.axis):
            set up and call AxisProcess from a thread
        All those process will be grouped under the same SuperviseProcess
        (sharing the same id) and all will be able to notify advancement
        regarding this process.

    :param Union[str,None] name: Supervise process name
    :param int or None process_id: several Process can be 'group together'
                                   If this is the case then the "master"
                                   process should provide other the
                                   process_id
                                   if value is -1 then no supervision
                                   should be provided.
    """

    def __init__(self, name=None, process_id=None):
        self._name = name
        self._is_master_process = process_id is None
        """is this process the master process of the SuperviseProcess. Or is
        it just one of the underlying process of a master SuperviseProcess"""
        if process_id is None:
            ProcessManager().register(self)
        else:
            self._set_process_id(process_id)

    def __del__(self):
        ProcessManager().unregister(self)

    @property
    def is_master_process(self):
        return self._is_master_process

    @property
    def process_id(self):
        return self.__process_id

    def _set_process_id(self, process_id: int):
        self.__process_id = process_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if name != self._name:
            old_name = self._name
            self._name = name

    def set_dataset_state(
        self, dataset: Dataset, state: DatasetState, details=None
    ) -> None:
        """
        Notify the supervisor that the state of this dataset has changed.

        :param Dataset dataset: dataset with new state
        :param DatasetState state:
        :param Union[str,None] details: details regarding this process / dataset
        """
        ProcessManager().notify_dataset_state(
            dataset=dataset, process=self, state=state, details=details
        )

    def notify_to_state_to_managed(self, dataset, state, details) -> None:
        """
        Notify the ProcessManager that a state of a specific dataset has changed.

        :param dataset: dataset modified
        :param state: new state of the dataset regarding this SuperviseProcess
        :param details: details regarding the state (reasons, extra
                        informations...)
        """
        ProcessManager().notify_dataset_state(
            dataset=dataset, state=state, process=self, details=details
        )

    def reprocess(self, dataset):
        """
        Reprocess a dataset.

        :param Dataset: dataset to reprocess
        """
        raise NotImplementedError("Base class")
