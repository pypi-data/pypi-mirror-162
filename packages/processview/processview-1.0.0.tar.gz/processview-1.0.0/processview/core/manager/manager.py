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
__date__ = "03/11/2020"


from processview.utils.singleton import singleton
from processview.core.dataset import Dataset
from processview.core.dataset import DatasetIdentifier
from collections import OrderedDict
from silx.utils.enum import Enum as _Enum
import threading
from typing import Optional, Type, Union
from datetime import datetime
import weakref
import logging

_logger = logging.getLogger(__name__)


class DatasetState(_Enum):
    """possible dataset status relatif to a Process"""

    ON_GOING = "on going"
    SUCCEED = "succeed"
    FAILED = "failed"
    PENDING = "pending"
    SKIPPED = "skipped"
    WAIT_USER_VALIDATION = "waiting user validation"


@singleton
class ProcessManager:
    """
    Manager to register and observe `SuperviseProcess`.
    """

    def __init__(self):
        self._processes = {}
        self._dataset_process_states = {}
        """key is processID, Value is a tuple of
        (dataset state, details)"""
        self._processID = 0
        self._updateCallback = set()
        """list of callback to trigger when an update is generated"""
        self._newProcessCallback = set()
        """list of callback to trigger when a process is added"""
        self._processRemovedCallback = set()
        """list of callback to trigger when a process is removed"""
        self.lock = threading.Lock()

    def met(self, process, dataset) -> bool:
        """check if a dataset has already met a dataset"""
        if isinstance(dataset, DatasetIdentifier):
            dataset_id = dataset
        elif dataset is None:
            return False
        else:
            dataset_id = dataset.get_identifier()
        if process.process_id in self._dataset_process_states:
            return dataset_id in self._dataset_process_states[process.process_id]

    def register(self, process) -> int:
        """
        Register a process to the manager

        :param SuperviseProcess process:
        """
        from processview.core.superviseprocess import (
            SuperviseProcess,
        )  # avoid cyclic import

        if not isinstance(process, SuperviseProcess):
            raise TypeError(
                f"{process} is expected to be an isntance of {SuperviseProcess}"
            )
        process_id = self._processID
        self._processID += 1
        self._processes[process_id] = weakref.ref(process)
        process._set_process_id(process_id)

        with self.lock:
            for callback in self._newProcessCallback:
                callback()
        return process_id

    def _find_dataset_id(self, data) -> Dataset:
        if isinstance(data, Dataset):
            return data.get_identifier()
        elif isinstance(data, DatasetIdentifier):
            return data
        else:
            raise TypeError(
                "dataset should be an instance of Dataset or "
                "DatasetIdentifier. Get {} instead".format(type(data))
            )

    def _find_process(self, process):
        from processview.core.superviseprocess import (
            SuperviseProcess,
        )  # avoid cyclic import

        if isinstance(process, SuperviseProcess):
            return process
        elif isinstance(process, str):
            for p in self.get_processes():
                if p.name == process:
                    return p
        else:
            raise TypeError(
                "process should be an instance of SuperviseProcess or"
                " str. Get {} instead".format(type(process))
            )

    def unregister(self, process):
        """
        Unregister a process to the manager

        :param BaseProcess process:
        """
        with self.lock:
            if process.process_id in self._processes and process.is_master_process:
                del self._processes[process.process_id]

            for callback in self._processRemovedCallback:
                callback()

    def get_processes(self) -> tuple:
        """

        :return: tuple of processes currently registered
        :rtype: tuple
        """
        processes = []
        for _, p in self._processes.items():
            if p() is not None:
                processes.append(p())
        return tuple(processes)

    def get_process(self, process_id: int):
        if process_id in self._processes:
            return self._processes[process_id]()

    def get_datasets(self) -> tuple:
        """

        :return: tuple of datasets
        """
        res = set()
        for _, dataset_states in self._dataset_process_states.items():
            [res.add(dataset) for dataset in dataset_states]
        return tuple(res)

    def notify_dataset_state(self, dataset, process, state, details=None) -> None:
        """
        Update dataset state

        :param Dataset dataset: dataset which state is updated
        :param BaseProcess process: Process concern by the new state
        :param DatasetState state: current State
        :param str info: details about the error or success
        :return:
        """
        from processview.core.superviseprocess import (
            SuperviseProcess,
        )  # avoid cyclic import

        if not isinstance(process, SuperviseProcess):
            _logger.warning(
                f"Unable to update dataset {dataset} state. Process does not inherit from SuperviseProcess"
            )
        if process.process_id not in self._processes:
            self.register(process)
        if process.process_id not in self._dataset_process_states:
            self._dataset_process_states[process.process_id] = OrderedDict()
        if details is None:
            details = ""
        dataset_id = dataset.get_identifier()
        # as we store the identifier and not a string anymore we might need to remove another instanciation
        process_states = self._dataset_process_states[process.process_id]
        to_remove = set()
        for id in process_states:
            if id == dataset_id:
                to_remove.add(id)
        for id in to_remove:
            del process_states[id]
        self._dataset_process_states[process.process_id] = process_states
        self._dataset_process_states[process.process_id][dataset_id] = (
            state,
            datetime.now(),
            details,
        )
        self.updated()

    def get_dataset_state(self, dataset_id, process) -> Union[None, DatasetState]:
        """

        :param Dataset dataset_id:
        :param BaseProcess process:
        :return: DatasetState relative to provided process if know
        :rtype: Union[None, DatasetState]
        """
        dataset_id = self._find_dataset_id(dataset_id)
        assert isinstance(dataset_id, DatasetIdentifier)
        process = self._find_process(process)
        if process is None:
            _logger.warning("process {} is no more supervised".format(process))
            return
        if dataset_id is None:
            _logger.warning("dataset {} is no more supervised".format(dataset_id))
        elif process.process_id in self._dataset_process_states:
            if dataset_id in self._dataset_process_states[process.process_id]:
                return self._dataset_process_states[process.process_id][dataset_id][0]
        return None

    def get_dataset_details(self, dataset_id, process) -> Union[None, str]:
        """

        :param Dataset dataset_id:
        :param BaseProcess process:
        :return: DatasetState relative to provided process if know
        :rtype: Union[None, DatasetState]
        """
        dataset_id = self._find_dataset_id(dataset_id)
        process = self._find_process(process)
        if process is None:
            _logger.warning("process {} is no more supervised".format(process))
            return
        if dataset_id is None:
            _logger.warning("dataset {} is no more supervised".format(dataset_id))
        if process.process_id in self._dataset_process_states:
            if dataset_id in self._dataset_process_states[process.process_id]:
                return self._dataset_process_states[process.process_id][dataset_id][2]
        return None

    def get_dataset_time_stamp(self, dataset_id, process) -> Union[None, str]:
        """

        :param Dataset dataset_id:
        :param BaseProcess process:
        :return: DatasetState relative to provided process if know
        :rtype: Union[None, DatasetState]
        """
        dataset_id = self._find_dataset_id(dataset_id)
        process = self._find_process(process)
        if process is None:
            _logger.warning("process {} is no more supervised".format(process))
            return
        if dataset_id is None:
            _logger.warning("dataset {} is no more supervised".format(dataset_id))
        if process.process_id in self._dataset_process_states:
            if dataset_id in self._dataset_process_states[process.process_id]:
                return self._dataset_process_states[process.process_id][dataset_id][1]
        return None

    def get_dataset_stream(self, dataset, time_stamp=False) -> tuple:
        """

        :param Dataset dataset: dataset the stream is focus on
        :param bool time_stamp: if True then return timestamp in the list of
                                elements
        :return: stream of (process ID, DatasetState) for a given dataset
        :rtype: tuple of (process ID, DatasetState, [timestamp])
        """
        stream = []
        for process_id, dataset_states in self._dataset_process_states.items():
            dst_id = dataset.get_identifier()
            if dst_id in dataset_states:
                state, _timestamp, _ = dataset_states[dst_id]
                stream.append((process_id, state, _timestamp))
        # order the stream
        stream = sorted(stream, key=lambda elmt: elmt[2])
        if not time_stamp:
            stream = [s[:-1] for s in stream]
        return tuple(stream)

    def get_process_history(self, process, time_stamp=False) -> tuple:
        """
        Return the know history of the process.

        :param BaseProcess process:
        :param bool time_stamp: if True then return timestamp in the list of
                                elements
        :return: tuple of (DatasetIdentifier, state, [timestamp])
        :rtype: tuple
        """
        history = []
        if process.process_id in self._dataset_process_states:
            dataset_states = self._dataset_process_states[process.process_id]
            for dataset_id, info in dataset_states.items():
                state, _timestamp, details = info
                history.append((dataset_id, state, _timestamp))

        history = sorted(history, key=lambda elmt: elmt[2])
        if not time_stamp:
            history = [s[:-1] for s in history]
        return tuple(history)

    def updated(self):
        """Function 'open' for monckey patch"""
        with self.lock:
            for callback in self._updateCallback:
                callback()

    def add_update_callback(self, callback) -> None:
        """

        :param callback: add a callback to be trigger when dataset state change
        """
        with self.lock:
            self._updateCallback.add(callback)

    def remove_update_callback(self, callback) -> None:
        """

        :param callback: remove a callback from the stack of callback to be
                         call when dataset state change
        """
        with self.lock:
            if callback in self._updateCallback:
                self._updateCallback.remove(callback)

    def add_new_process_callback(self, callback):
        self._newProcessCallback.add(callback)

    def remove_new_process_callback(self, callback):
        with self.lock:
            if callback in self._newProcessCallback:
                self._newProcessCallback.remove(callback)

    def add_process_removed_callback(self, callback):
        self._processRemovedCallback.add(callback)

    def remove_process_removed_callback(self, callback):
        with self.lock:
            if callback in self._processRemovedCallback:
                self._processRemovedCallback.remove(callback)

    def clear(self):
        """
        clear registered processes and dataset states

        :return:
        """
        self._processes = {}
        self._dataset_process_states = {}
