import json
import os
from pathlib import Path
from .utils import copy_to_dir
import hou

from omoospace import Omoospace

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

NODE_CONFIG_PATH = Path(__file__).parent.parent.parent / "nodes.json"

with NODE_CONFIG_PATH.open('r') as f:
    data = json.load(f)
    EXPORT_PARMS = data['output_parms']
    IMPORT_PARMS = data['input_parms']
    copy_dir_MARKERS = data['copy_dir_markers']


def collect_nodes(nodes):
    collection = []
    for node in nodes:
        collection.append(node)
        children = node.allSubChildren(
            top_down=True,
            recurse_in_locked_nodes=False
        )
        collection.extend(children)
    collection = [node for node in collection if node.parent().isEditable()]
    return collection


def is_in_omoospace(self, node_parm):
    input_path_eval: str = self.input_path_dict[node_parm]['input_path_eval']
    return self.omoospace.root_path in Path(input_path_eval).resolve().parents


def correct_input_path(root, path: Path, category="Misc", copy_dir: bool = False):
    main_path = self.omoospace.root_path / "Contents" \
        if self.is_in_contents(path) else self.omoospace.root_path / "ExternalData"

    if copy_dir:
        corrected_path = main_path / category / path.parent.name / path.name
    else:
        corrected_path = main_path / category / path.name

    return corrected_path


class ManageInputPaths(QDialog):
    # self.ui only Main Window
    def __init__(self, input_paths, omoospace):
        super(ManageInputPaths, self).__init__()

        self.omoospace = omoospace
        self.input_paths = input_paths

        # Create a QListWidget
        list_widget = QListWidget()

        # init input_path_dict copy_dir switch
        for node_parm in self.input_path_dict.keys():
            input_path_raw: str = self.input_path_dict[node_parm]['input_path_raw']

            copy_dir = False
            for mark in copy_dir_MARKERS:
                if mark in input_path_raw:
                    copy_dir = True
                    break

            self.input_path_dict[node_parm]['copy_dir'] = copy_dir
            changed_path_raw = self.get_changed_path_raw(
                node_parm, copy_dir)

            item = QListWidgetItem(
                f"{node_parm}: {input_path_raw} => {changed_path_raw}")
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable |
                          QtCore.Qt.ItemIsEnabled)

            if copy_dir:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)

            item.setData(QtCore.Qt.UserRole, node_parm)
            list_widget.addItem(item)

        list_widget.itemChanged.connect(self.handle_item_checked)

        button = QPushButton("Confrim")
        button.clicked.connect(self.copy)

        # Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel(
            "Copy it's parent directroy or not?"))
        main_layout.addWidget(list_widget)
        main_layout.addWidget(button)
        self.setLayout(main_layout)

        self.setWindowTitle("Organize Export Paths")
        self.setMinimumWidth(1000)

    def handle_item_checked(self, item):
        node_parm = item.data(QtCore.Qt.UserRole)
        if item.checkState() == QtCore.Qt.Checked:
            self.input_path_dict[node_parm]['copy_dir'] = True
        else:
            self.input_path_dict[node_parm]['copy_dir'] = False

        item.setText(self.get_change_str(node_parm))

    def get_change_str(self, node_parm):
        input_path_raw: str = self.input_path_dict[node_parm]['input_path_raw']
        changed_path_raw: str = self.get_changed_path_raw(node_parm)

        return f"{node_parm}: {input_path_raw} => {changed_path_raw}"

    def get_changed_path_raw(self, node_parm, copy_dir=None):
        copy_dir = copy_dir or self.input_path_dict[node_parm]['copy_dir']
        input_path_raw: str = self.input_path_dict[node_parm]['input_path_raw']
        input_path_eval: str = self.input_path_dict[node_parm]['input_path_eval']

        parent_str: str = Path(input_path_eval).parent.name
        end_str: str = Path(input_path_raw).name

        if not self.is_in_omoospace(node_parm):
            return f"$JOB/ExternalData/Collected/{parent_str}/{end_str}" \
                if copy_dir else f"$JOB/ExternalData/Collected/{end_str}"
        else:
            input_path_raw_str = Path(input_path_raw).resolve().as_posix()
            return f"$JOB{input_path_raw_str.removeprefix(self.omoospace.root_path.as_posix())}"

    def execute(self):
        changed_node_parms = []
        input_path_dict = self.input_path_dict
        omoospace = self.omoospace

        # copy files and directroies
        with hou.InterruptableOperation(
            "Copy to ExternalData",
            open_interrupt_dialog=True
        ) as operation:
            for index, node_parm in enumerate(input_path_dict.keys()):
                node = input_path_dict[node_parm]['node']
                parm = input_path_dict[node_parm]['parm']
                input_path_eval: str = self.input_path_dict[node_parm]['input_path_eval']

                copy_dir: bool = input_path_dict[node_parm]['copy_dir']
                changed_path_raw: str = self.get_changed_path_raw(node_parm)

                if not self.is_in_omoospace(node_parm):
                    source = Path(input_path_eval)
                    try:
                        copy_to_dir(
                            source.parent if copy_dir else source,
                            omoospace.externaldata_path / 'Collected',
                            exist_ok=True
                        )
                    except:
                        continue

                try:
                    node.parm(parm).set(changed_path_raw)
                    changed_node_parms.append(node_parm)
                except:
                    continue

                percent = float(index) / float(len(input_path_dict.keys()))
                operation.updateProgress(percent)

        # print report
        report_message = ""
        for node_parm in input_path_dict.keys():
            if node_parm in changed_node_parms:
                report_message += f"[√] {self.get_change_str(node_parm)}\n"
            else:
                report_message += f"[×] {self.get_change_str(node_parm)}\n"

        hou.ui.displayMessage(
            report_message,
            title="Report"
        )

        print(report_message)

        input_paths: list[InputPath] = self.input_paths

        def manage_path(path_item):
            # skip
            if not path_item.do_manage:
                return

            corrected_path = correct_input_path(path_item.orig_path,
                                                category=path_item.category,
                                                copy_dir=path_item.copy_dir)

            source = resolve_path(path_item.orig_path)
            target = resolve_path(corrected_path)

            # copy file if not the same path
            if source != target:
                try:
                    if "<UDIM>" in str(source):
                        udims = source.parent.glob(
                            source.name.replace("<UDIM>", "*"))
                        for udim in udims:
                            copy_to_dir(
                                udim.parent if path_item.copy_dir else udim,
                                target.parent.parent if path_item.copy_dir else target.parent,
                                exist_ok=True
                            )
                    else:
                        copy_to_dir(
                            source.parent if path_item.copy_dir else source,
                            target.parent.parent if path_item.copy_dir else target.parent,
                            exist_ok=True
                        )
                except Exception as e:
                    print(e)
                    corrected_path_str = str(resolve_path(corrected_path))
                    if resolve_path(corrected_path).exists():
                        self.report(
                            {"WARNING"}, f"Fail to overwrite, manually delete {corrected_path_str}, then try again.")
                    else:
                        self.report(
                            {"ERROR"}, f"Fail to copy, skip '{str(source)}'.")
                    return

        self.close()


def manage_input_paths(nodes):
    input_path_dict = {}

    def add_to_dict(node, parm_name):
        # check if node does have that parm
        if not node.parm(parm_name):
            raise Exception

        # except expression parms
        try:
            node.parm(parm_name).expressionLanguage()
            return
        except:
            pass

        node_path = node.path()
        input_path_eval = node.evalParm(parm_name)
        input_path_raw = node.parm(parm_name).rawValue()

        if input_path_raw and ("$JOB" not in input_path_raw):
            input_path_dict[f"{node_path}.{parm_name}"] = {
                "node": node,
                "parm": parm_name,
                "input_path_raw": input_path_raw,
                "input_path_eval": input_path_eval
            }

    omoospace = Omoospace(hou.getenv('JOB'))

    for node in collect_nodes(nodes):
        node_type = node.type().name()
        parm_names: list[str] = IMPORT_PARMS.get(node_type) or []

        for parm_name in parm_names:
            # if that parm is a list like filepath1 filepath2 filepath3
            if parm_name.endswith("*"):
                index = 1
                while True:
                    parm_name = parm_name.removesuffix("*") + str(index)
                    try:
                        add_to_dict(node, parm_name)
                    except:
                        break
                    index += 1

            else:
                try:
                    add_to_dict(node, parm_name)
                except:
                    continue

    if len(input_path_dict.keys()) > 0:
        dialog = ManageInputPaths(input_path_dict, omoospace)
        dialog.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
        dialog.show()
    else:
        print("No parms need to change.")


def manage_output_paths(nodes):
    output_path_dict = {}

    def add_to_dict(node, parm_name, parm_value):
        # check if node does have that parm
        if not node.parm(parm_name):
            return
        # except expression parms
        try:
            node.parm(parm_name).expressionLanguage()
            return
        except:
            pass
        node_path = node.path()
        output_path_dict[f"{node_path}.{parm_name}"] = {
            "node": node,
            "parm": parm_name,
            "value": parm_value
        }

    for node in collect_nodes(nodes):
        node_type = node.type().name()
        present = EXPORT_PARMS.get(node_type)
        parm_names: list[str] = present.keys() if present else []

        for parm_name in parm_names:
            parm_value = present[parm_name]
            add_to_dict(node, parm_name, parm_value)

    if len(output_path_dict.keys()) > 0:
        for node_parm in output_path_dict.keys():
            node = output_path_dict[node_parm]['node']
            parm_name = output_path_dict[node_parm]['parm']

            output_path_raw = node.parm(parm_name).rawValue()
            changed_path_raw = output_path_dict[node_parm]['value']

            try:
                node.parm(parm_name).set(changed_path_raw)
                print(
                    f"[√] {node_parm}: {output_path_raw} => {changed_path_raw}")
            except:
                print(
                    f"[×] {node_parm}: {output_path_raw} => {changed_path_raw}")

    else:
        print("No parms need to change.")
