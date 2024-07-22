import json
import os
from pathlib import Path
from .utils import copy_to_dir
import hou

from omoospace import (
    Omoospace,
    create_omoospace as _create_omoospace,
    format_name
)

from hutil.Qt.QtWidgets import (
    QDialog,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
)

import hutil.Qt.QtCore as QtCore


class CreateOmoospace(QDialog):
    # self.ui only Main Window
    def __init__(self):
        super(CreateOmoospace, self).__init__()

        self.omoospace_home_input = hou.qt.InputField(
            data_type=hou.qt.InputField.StringType,
            num_components=1,
            label="Home Directory"
        )
        default_directory = Path.home().as_posix()
        self.omoospace_home_input.setValue(default_directory)
        self.omoospace_home_input.valueChanged.connect(self.on_path_changed)

        omoospace_home_btn = hou.qt.FileChooserButton()
        omoospace_home_btn.setFileChooserTitle("Where to store new omoospace?")
        omoospace_home_btn.setFileChooserFilter(hou.fileType.Directory)
        omoospace_home_btn.setFileChooserDefaultValue(default_directory)
        omoospace_home_btn.setFileChooserMode(hou.fileChooserMode.Read)
        omoospace_home_btn.fileSelected.connect(self.on_file_selected)

        omoospace_home_layout = QHBoxLayout()
        omoospace_home_layout.setContentsMargins(0, 0, 0, 0)
        omoospace_home_layout.addWidget(self.omoospace_home_input)
        omoospace_home_layout.addWidget(omoospace_home_btn)
        omoospace_home = QWidget()
        omoospace_home.setLayout(omoospace_home_layout)

        self.omoospace_name_input = hou.qt.InputField(
            data_type=hou.qt.InputField.StringType,
            num_components=1,
            label="Omoospace Name"
        )
        self.omoospace_name_input.valueChanged.connect(self.on_path_changed)

        self.subspace_name_input = hou.qt.InputField(
            data_type=hou.qt.InputField.StringType,
            num_components=1,
            label="Subspace Name"
        )
        self.subspace_name_input.valueChanged.connect(self.on_path_changed)

        self.hip_path_input = QLineEdit()
        self.hip_path_input.setEnabled(False)

        hip_path_layout = QHBoxLayout()
        hip_path_layout.setContentsMargins(0, 0, 0, 0)
        hip_path_layout.addWidget(hou.qt.FieldLabel("File Path"))
        hip_path_layout.addWidget(self.hip_path_input)
        hip_path = QWidget()
        hip_path.setLayout(hip_path_layout)

        self.save_to_btn = QPushButton('Save To')
        self.save_to_btn.clicked.connect(self.on_save_to)

        # Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(omoospace_home)
        main_layout.addWidget(self.omoospace_name_input)
        main_layout.addWidget(self.subspace_name_input)
        main_layout.addWidget(hip_path)
        main_layout.addWidget(self.save_to_btn)
        self.setLayout(main_layout)

        self.setWindowTitle("Save to New Omoospace")
        self.setMinimumWidth(600)

    @property
    def omoospace_home(self) -> str:
        return self.omoospace_home_input.value()

    @property
    def omoospace_name(self) -> str:
        return self.omoospace_name_input.value()

    @property
    def subspace_name(self) -> str:
        return self.subspace_name_input.value() or self.omoospace_name_input.value()

    @property
    def hip_path(self) -> str:
        if self.omoospace_name == "" or self.omoospace_home == "":
            return ""

        path = Path(
            self.omoospace_home,
            format_name(self.omoospace_name), 'SourceFiles',
            f'{format_name(self.subspace_name)}.hip'
        )
        return path.as_posix()

    def on_file_selected(self, file_path):
        self.omoospace_home_input.setValue(file_path)

    def on_path_changed(self):
        self.hip_path_input.setText(self.hip_path)

    def on_save_to(self):
        if self.omoospace_home == "":
            hou.ui.displayMessage(
                "Home Directory is required.",
                severity=hou.severityType.Warning
            )
            return

        if self.omoospace_name == "":
            hou.ui.displayMessage(
                "Omoospace Name is required.",
                severity=hou.severityType.Warning
            )
            return

        omoospace = _create_omoospace(
            name=self.omoospace_name,
            root_dir=self.omoospace_home,
            reveal_in_explorer=False
        )
        hou.hipFile.save(self.hip_path)
        os.startfile(omoospace.sourcefiles_path)
        self.close()


def create_omoospace():
    dialog = CreateOmoospace()
    dialog.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
    dialog.show()
