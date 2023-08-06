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


from typing import Union
from silx.gui import qt
from collections import OrderedDict
from processview.core.manager import DatasetState
from processview.core.manager import ProcessManager as _ProcessManager
from processview.core.superviseprocess import SuperviseProcess
from processview.core.dataset import DatasetIdentifier
from processview.gui import icons as icons
from processview.gui.messagebox import MessageBox
from processview.utils import docstring
import fnmatch


_DATASET_STATE_BACKGROUND = {
    DatasetState.ON_GOING: qt.QColor("#839684"),  # light blue
    DatasetState.SUCCEED: qt.QColor("#068c0c"),  # green
    DatasetState.FAILED: qt.QColor("#f52718"),  # red
    DatasetState.PENDING: qt.QColor("#609ab3"),  # blue gray
    DatasetState.SKIPPED: qt.QColor("#f08e0e"),  # light orange
    DatasetState.WAIT_USER_VALIDATION: qt.QColor("#cb34c1"),  # pink
}


class ProcessManagerWindow(qt.QMainWindow):
    """
    Main window of the process manager
    """

    def __init__(self, parent):
        qt.QMainWindow.__init__(self, parent)
        self.setWindowFlags(qt.Qt.Widget)

        self._centralWidget = ProcessManagerWidget(parent=self)
        self.setCentralWidget(self._centralWidget)


class ObservationTable(qt.QTableView):
    def __init__(self, parent):
        qt.QTableView.__init__(self, parent)
        self.verticalHeader().setSectionsClickable(True)

        # QMenu for cell from on dataset and one process
        self.menu_dataset_vs_process = qt.QMenu()
        self._reprocessAction = qt.QAction("reprocess")
        self.menu_dataset_vs_process.addAction(self._reprocessAction)
        self._infoAction = qt.QAction("info")
        self.menu_dataset_vs_process.addAction(self._infoAction)

        self._target = (None, None)
        # register target of the last menu (process, DatasetIdentifier)

        self.copy_menu = qt.QMenu()
        self._copyAction = qt.QAction("copy")
        self.copy_menu.addAction(self._copyAction)

        # connect signal / slot
        self._copyAction.triggered.connect(self._requestDatasetIdCopy)
        self._reprocessAction.triggered.connect(self._requestReprocessing)
        self._infoAction.triggered.connect(self._requestInfo)

        self.verticalHeader().setContextMenuPolicy(qt.Qt.CustomContextMenu)
        self.verticalHeader().customContextMenuRequested.connect(
            self._activeVerticalHeaderMenu
        )

    def _processAt(self, x_pos):
        column = self.columnAt(x_pos)
        if column >= 0:
            processes = self.model()._processes
            if column < len(processes):
                return processes[list(processes.keys())[column]]

    def _datasetAt(self, y_pos):
        row = self.rowAt(y_pos)
        if row >= 0:
            datasets = self.model()._datasets
            if row < len(datasets):
                return datasets[list(datasets.keys())[row]]

    def _activeVerticalHeaderMenu(self, pos):
        process = self._processAt(pos.x())
        dataset = self._datasetAt(pos.y())
        if dataset is not None:
            self._target = (None, dataset)
            self.copy_menu.exec_(self.mapToGlobal(pos))

    def contextMenuEvent(self, event):
        process = self._processAt(event.pos().x())
        dataset = self._datasetAt(event.pos().y())
        if (
            process is not None
            and dataset is not None
            and _ProcessManager().met(process=process, dataset=dataset)
        ):
            self._target = (process, dataset)
            self.menu_dataset_vs_process.exec_(event.globalPos())
        else:
            self._target = (None, None)
        super().contextMenuEvent(event)

    def _requestReprocessing(self, *args, **kwargs):
        process, dataset = self._target
        if process is not None and dataset is not None:
            assert isinstance(process, SuperviseProcess)
            assert isinstance(dataset, DatasetIdentifier)
            process.reprocess(dataset.recreate_dataset())

    def _requestDatasetIdCopy(self, *args, **kwargs):
        _, dataset = self._target
        if dataset is not None:
            clipboard = qt.QGuiApplication.clipboard()
            clipboard.setText(dataset.to_str())

    def _requestInfo(self, *args, **kwargs):
        process, dataset = self._target
        if process is not None and dataset is not None:
            infos = ProcessManager().get_dataset_details(
                dataset=dataset, process=process
            )
            if infos in (None, ""):
                infos = "No extra information provided"

            msg = MessageBox(self)
            msg.setInfos(infos=infos)
            extra_info = "{} processing {}".format(process.name, dataset)
            msg.setWindowTitle(extra_info)
            msg.setWindowModality(qt.Qt.NonModal)
            msg.show()


class ProcessManagerWidget(qt.QWidget):
    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())

        self._manager = ProcessManager()

        self.filterWidget = _ToggleableFilterWidget(parent=self)
        self.layout().setContentsMargins(4, 4, 4, 4)
        self.layout().setSpacing(4)
        self.filterWidget.layout().setSpacing(4)
        self.layout().addWidget(self.filterWidget)

        self.observationTable = ObservationTable(self)
        self.layout().addWidget(self.observationTable)
        self.observationTable.setModel(
            _DatasetProcessModel(parent=self.observationTable, header=tuple())
        )
        self.observationTable.resizeColumnsToContents()
        self.observationTable.setSortingEnabled(True)
        self.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)

        # connect signal / slot
        self._manager.sigUpdated.connect(self._updateDatasetStates)
        self._manager.sigNewProcessRegistered.connect(self._updateProcesses)
        self.filterWidget.filterWidget.sigDatasetPatternEditingFinished.connect(
            self._filterUpdated
        )
        self.filterWidget.filterWidget.sigProcessPatternEditingFinished.connect(
            self._filterUpdated
        )
        self._manager.sigProcessUnregistered.connect(self._updateProcesses)
        # update to fit existing processes / datasets
        self._updateProcesses()
        self._updateDatasetStates()

    def _updateDatasetStates(self):
        self.observationTable.model().setDatasets(self._manager.get_datasets())

    def _updateProcesses(self):
        self.observationTable.model().setProcesses(self._manager.get_processes())

    def _filterUpdated(self):
        self.observationTable.model().process_patterns = (
            self.filterWidget.getProcessPatterns()
        )
        self._updateProcesses()
        self.observationTable.model().dataset_patterns = (
            self.filterWidget.getDatasetPatterns()
        )
        self._updateDatasetStates()


class _DatasetProcessModel(qt.QAbstractTableModel):
    def __init__(self, parent, header, *args):
        qt.QAbstractTableModel.__init__(self, parent, *args)
        self.header = header
        self._processes = OrderedDict()
        self._datasets = OrderedDict()
        self._processPatterns = tuple()
        # is there some process name pattern to follow ?
        self._datasetPatterns = tuple()
        # is there some dataset id pattern to follow ?

    def _match_dataset_patterns(self, dataset):
        if len(self._datasetPatterns) == 0:
            return True
        for pattern in self._datasetPatterns:
            if fnmatch.fnmatch(str(dataset), pattern):
                return True
        return False

    def _match_process_patterns(self, process):
        if len(self.process_patterns) == 0:
            return True
        for pattern in self._processPatterns:
            if fnmatch.fnmatch(process.name, pattern):
                return True
        return False

    @property
    def process_patterns(self):
        return self._processPatterns

    @process_patterns.setter
    def process_patterns(self, patterns):
        self._processPatterns = patterns

    @property
    def dataset_patterns(self):
        return self._datasetPatterns

    @dataset_patterns.setter
    def dataset_patterns(self, patterns):
        self._datasetPatterns = patterns

    def add(self, dataset, status):
        self._processes[dataset] = status
        self.endResetModel()

    def remove(self, dataset):
        if dataset in self._processes:
            del self._processes[dataset]
        self.endResetModel()

    def update_dataset(self, dataset, status):
        self._processes[dataset] = status
        self.endResetModel()

    def clear(self):
        self._processes = OrderedDict()
        self.endResetModel()

    def rowCount(self, parent=None):
        return len(self._datasets)

    def columnCount(self, parent=None):
        return len(self._processes)

    def setProcesses(self, processes):
        assert isinstance(processes, (tuple, list))
        self._processes = {}
        processes = list(filter(self._match_process_patterns, processes))
        for i_process, process in enumerate(processes):
            self._processes[i_process] = process
        self.endResetModel()

    def setDatasets(self, datasets):
        assert isinstance(datasets, (tuple, list))
        self._datasets = {}
        datasets = list(filter(self._match_dataset_patterns, datasets))
        for i_dataset, dataset in enumerate(datasets):
            self._datasets[i_dataset] = dataset
        self.endResetModel()

    def headerData(self, col, orientation, role):
        if orientation == qt.Qt.Horizontal and role == qt.Qt.DisplayRole:
            if col < len(self._processes):
                return self._processes[col].name
        elif orientation == qt.Qt.Vertical:
            if col < len(self._datasets):
                if role == qt.Qt.DisplayRole:
                    return self._datasets[col].short_description() or str(
                        self._datasets[col]
                    )
                elif role == qt.Qt.ToolTipRole:
                    return self._datasets[col].long_description()
        return None

    def data(self, index, role):
        if index.isValid() is False:
            return None

        if role not in (qt.Qt.DisplayRole, qt.Qt.ToolTipRole, qt.Qt.BackgroundRole):
            return None

        dataset_short_name = self._datasets[index.row()]
        process_name = self._processes[index.column()]
        dataset_process_state = ProcessManager().get_dataset_state(
            dataset=dataset_short_name, process=process_name
        )
        dataset_process_details = ProcessManager().get_dataset_details(
            dataset=dataset_short_name, process=process_name
        )
        if role == qt.Qt.BackgroundRole:
            if dataset_process_state is None:
                # if "unmet"
                return qt.QColor("#ffffff")
            else:
                return _DATASET_STATE_BACKGROUND[dataset_process_state]
        elif role == qt.Qt.DisplayRole:
            if dataset_process_state is None:
                return ""
            else:
                return dataset_process_state.value
        if role == qt.Qt.ToolTipRole:
            if dataset_process_details is None:
                return ""
            else:
                return dataset_process_details


class _ToggleableFilterWidget(qt.QWidget):

    _BUTTON_ICON = qt.QStyle.SP_ToolBarVerticalExtensionButton  # noqa

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QGridLayout())
        self._toggleButton = qt.QPushButton("", self)
        self.layout().addWidget(self._toggleButton, 0, 0, 1, 1)
        self._filterWidget = _FilterWidget(parent=self)
        self.layout().addWidget(self._filterWidget, 0, 1, 4, 4)

        self._toggleButton.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        self._setButtonIcon(show=True)

        # connect signal / slot
        self._toggleButton.clicked.connect(self._toggleFilterWidget)

        # expose API
        self.getProcessPatterns = self._filterWidget.getProcessPatterns
        self.getDatasetPatterns = self._filterWidget.getDatasetPatterns

    @property
    def filterWidget(self):
        return self._filterWidget

    def _setButtonIcon(self, show):
        style = qt.QApplication.instance().style()
        # return a QIcon
        icon = style.standardIcon(self._BUTTON_ICON)
        if show is True:
            pixmap = icon.pixmap(32, 32).transformed(qt.QTransform().scale(1, -1))
            icon = qt.QIcon(pixmap)
        self._toggleButton.setIcon(icon)

    def _toggleFilterWidget(self):
        visible = not self._filterWidget.isVisible()
        self._setButtonIcon(show=visible)
        self._filterWidget.setVisible(visible)


class _FilterWidget(qt.QWidget):
    """
    Widget to define some filtering pattern on dataset and / or processes
    """

    sigProcessPatternEditingFinished = qt.Signal()
    """signal emit when the process pattern editing finished"""

    sigDatasetPatternEditingFinished = qt.Signal()
    """signal emit when the dataset pattern editing finished"""

    def __init__(self, parent=None, name="filter", font_size=12, icon_size=20):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QGridLayout())

        font = self.font()
        font.setPixelSize(font_size)
        self.setFont(font)

        icon = icons.getQIcon("magnifying_glass")
        self._researchLabelIcon = qt.QLabel("", parent=self)
        self._researchLabelIcon.setPixmap(icon.pixmap(icon_size, state=qt.QIcon.On))
        self.layout().addWidget(qt.QLabel(name, self), 0, 1, 1, 1)
        self.layout().addWidget(self._researchLabelIcon, 0, 2, 1, 1)

        # filter by dataset id / name
        self._datasetLabel = qt.QLabel("dataset", self)
        self.layout().addWidget(self._datasetLabel, 1, 2, 1, 2)
        self._datasetPatternLE = qt.QLineEdit("", self)
        self.layout().addWidget(self._datasetPatternLE, 1, 4, 1, 1)
        tooltip = (
            "Provide one or several dataset name or pattern to only "
            " display those datasets. Pattern should be separated by a "
            "semi colon. Handle linux wild card. Example: "
            "`pattern1; *suffix; prefix*`"
        )
        for widget in self._datasetLabel, self._datasetPatternLE:
            widget.setToolTip(tooltip)
        self._clearDatasetPatternPB = qt.QPushButton("clear", self)
        self._clearDatasetPatternPB.setAutoDefault(True)
        self.layout().addWidget(self._clearDatasetPatternPB, 1, 5, 1, 1)

        # filter by process name
        self._processLabel = qt.QLabel("process", self)
        self.layout().addWidget(self._processLabel, 2, 2, 1, 2)
        self._processPatternLE = qt.QLineEdit("", self)
        self.layout().addWidget(self._processPatternLE, 2, 4, 1, 1)
        tooltip = (
            "Provide one or several process name or pattern to only "
            " display those datasets. Pattern should be separated by a "
            "semi colon. Handle linux wild card. Example: "
            "`pattern1; *suffix; prefix*`"
        )
        for widget in self._processLabel, self._processPatternLE:
            widget.setToolTip(tooltip)
        self._clearProcessPatternPB = qt.QPushButton("clear", self)
        self._clearProcessPatternPB.setAutoDefault(True)
        self.layout().addWidget(self._clearProcessPatternPB, 2, 5, 1, 1)

        # connect signal / slot
        self._clearProcessPatternPB.released.connect(self._processPatternLE.clear)
        self._clearProcessPatternPB.released.connect(
            self._processPatternEditingFinished
        )
        self._clearDatasetPatternPB.released.connect(self._datasetPatternLE.clear)
        self._clearDatasetPatternPB.released.connect(
            self._datasetPatternEditingFinished
        )
        self._datasetPatternLE.editingFinished.connect(
            self._datasetPatternEditingFinished
        )
        self._processPatternLE.editingFinished.connect(
            self._processPatternEditingFinished
        )

    def getProcessPatterns(self) -> tuple:
        if self._processPatternLE.text() == "":
            return ("*",)
        res = self._processPatternLE.text().replace(" ", "")
        return tuple(res.split(";"))

    def getDatasetPatterns(self) -> tuple:
        if self._datasetPatternLE.text() == "":
            return ("*",)
        res = self._datasetPatternLE.text().replace(" ", "")
        return tuple(res.split(";"))

    def _datasetPatternEditingFinished(self, *args, **kwargs):
        self.sigDatasetPatternEditingFinished.emit()

    def _processPatternEditingFinished(self, *args, **kwargs):
        self.sigProcessPatternEditingFinished.emit()


class ProcessManager(qt.QObject):
    sigUpdated = qt.Signal()
    """Signal emitted when the state of some process / dataset is updated
    """

    sigNewProcessRegistered = qt.Signal()
    """Signal emitted when a new process is registered"""

    sigProcessUnregistered = qt.Signal()
    """Signal emitted when a process is unregistered"""

    def __init__(self):
        qt.QObject.__init__(self)
        self.manager = _ProcessManager()

        # monkey patch manager updated function
        # TODO: add / remove callback would be simpler
        self.manager.add_update_callback(self.updated)
        self.manager.add_new_process_callback(self.processAdded)
        self.manager.add_process_removed_callback(self.processRemoved)

    def updated(self):
        self.sigUpdated.emit()

    def processAdded(self):
        self.sigNewProcessRegistered.emit()

    def processRemoved(self):
        self.sigProcessUnregistered.emit()

    def processNameChanged(self, process):
        self.sigProcessNameChanged.emit(process)

    def destroyed(self, object_):
        self.manager.remove_update_callback(self.updated)
        qt.QObject.destroyed(object_)

    # expose some of the original ProcessManager API
    @docstring(_ProcessManager)
    def notify_dataset_state(self, dataset, process, state, details=None) -> None:
        self.manager.notify_dataset_state(
            dataset=dataset, process=process, state=state, details=details
        )

    @docstring(_ProcessManager)
    def get_dataset_state(self, dataset, process) -> Union[None, DatasetState]:
        return self.manager.get_dataset_state(dataset_id=dataset, process=process)

    @docstring(_ProcessManager)
    def get_dataset_details(self, dataset, process) -> Union[None, DatasetState]:
        return self.manager.get_dataset_details(dataset_id=dataset, process=process)

    @docstring(_ProcessManager)
    def get_dataset_stream(self, dataset, time_stamp=False) -> tuple:
        return self.manager.get_dataset_stream(dataset=dataset, time_stamp=time_stamp)

    @docstring(_ProcessManager)
    def get_process_history(self, process, time_stamp=False) -> tuple:
        return self.manager.get_process_history(process=process, time_stamp=time_stamp)

    @docstring(_ProcessManager)
    def get_processes(self):
        return self.manager.get_processes()

    @docstring(_ProcessManager)
    def get_datasets(self):
        return self.manager.get_datasets()
