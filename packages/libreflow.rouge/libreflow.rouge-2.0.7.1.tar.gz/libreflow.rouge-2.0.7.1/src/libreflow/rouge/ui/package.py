from enum import Enum
from kabaret.app.ui.gui.widgets.flow.flow_view import QtCore, QtGui, QtWidgets, CustomPageWidget
from kabaret.app import resources
from libreflow.resources.icons import libreflow as _

from ..flow.film import ShotState


class ShotSelectWidget(QtWidgets.QWidget):

    def __init__(self, shot_item, shot_name):
        super(ShotSelectWidget, self).__init__()
        self._shot_item = shot_item
        self._shot_name_label = QtWidgets.QLabel(shot_name)
        self.checkbox_select = QtWidgets.QCheckBox()

        hlo = QtWidgets.QHBoxLayout()
        hlo.addWidget(self.checkbox_select)
        hlo.addWidget(self._shot_name_label)
        hlo.setContentsMargins(0, 0, 0, 0)
        hlo.setSpacing(0)

        self.setLayout(hlo)
    
    def set_label_color(self, color):
        self.setStyleSheet('QLabel { color : %s; }' % color)
    
    def sizeHint(self):
        return QtCore.QSize(150, 30)


class ShotToSendItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, tree, oid, custom_widget, session):
        super(ShotToSendItem, self).__init__(tree)
        self._custom_widget = custom_widget
        self._session = session
        self._oid = oid
        self._state = None

        self._select_widget = ShotSelectWidget(self, self.get_shot_name())
        self._button_choose_take = QtWidgets.QPushButton('...')
        self._checkbox_pack = QtWidgets.QCheckBox()
        self.treeWidget().setItemWidget(self, 0, self._select_widget)
        self.treeWidget().setItemWidget(self, 2, self._checkbox_pack)
        self.setTextAlignment(1, QtCore.Qt.AlignCenter)
        
        self.initialise()

        # Install widget callbacks after their initialisation
        self._select_widget.checkbox_select.stateChanged.connect(self._on_checkbox_select_state_changed)
        self._checkbox_pack.stateChanged.connect(self._on_checkbox_pack_state_changed)
        self._button_choose_take.clicked.connect(self._on_button_choose_clicked)
    
    def initialise(self):
        self.setText(2, '')
        init_state = self._session.cmds.Flow.call(self._oid, 'get_init_state', [], {})

        if init_state == ShotState.MISSING_FILE:
            self._get_checkbox_select().setCheckState(QtCore.Qt.Unchecked)
            self._get_checkbox_pack().setCheckState(QtCore.Qt.Unchecked)
            self.set_selected(False)
            self.set_send_pack(False)
            self.set_new_take(False)
        elif init_state == ShotState.FIRST_DELIVERY:
            self._get_checkbox_select().setCheckState(QtCore.Qt.Checked)
            self._get_checkbox_pack().setCheckState(QtCore.Qt.Checked)
            self.set_selected(True)
            self.set_send_pack(True)
            self.set_new_take(True)
        elif init_state == ShotState.NEW_TAKE_PACK_UNSELECTED:
            self._get_checkbox_select().setCheckState(QtCore.Qt.Checked)
            self._get_checkbox_pack().setCheckState(QtCore.Qt.Unchecked)
            self.set_selected(True)
            self.set_send_pack(False)
            self.set_new_take(True)
        elif init_state == ShotState.ALREADY_DELIVERED:
            self._get_checkbox_select().setCheckState(QtCore.Qt.Unchecked)
            self._get_checkbox_pack().setCheckState(QtCore.Qt.Unchecked)
            self.set_selected(False)
            self.set_send_pack(False)
            self.set_new_take(False)
        elif init_state == ShotState.ALREADY_RECEIVED:
            self._get_checkbox_select().setCheckState(QtCore.Qt.Unchecked)
            self._get_checkbox_pack().setCheckState(QtCore.Qt.Unchecked)
            self.set_selected(False)
            self.set_send_pack(False)
            self.set_new_take(True)
        
        self.update_state(init_state)
    
    def get_shot_name(self):
        return self._session.cmds.Flow.call(self._oid, 'name', [], {})
    
    def get_target_take_name(self):
        return self._session.cmds.Flow.get_value(self._oid+'/target_take')
    
    def get_state(self):
        return self._state
    
    def update_state(self, state):
        self._state = state
        self._activate(self._state)
    
    def set_selected(self, b):
        self._session.cmds.Flow.set_value(self._oid+'/selected', b)
    
    def set_new_take(self, b):
        self._session.cmds.Flow.set_value(self._oid+'/new_take', b)
    
    def set_send_pack(self, b):
        self._session.cmds.Flow.set_value(self._oid+'/send_pack', b)
    
    def _activate(self, state):
        if state == ShotState.MISSING_FILE:
            self._get_checkbox_select().setEnabled(False)
            self._get_checkbox_pack().setEnabled(False)
            
            self._select_widget.set_label_color('#d5000d')
            self.setForeground(3, QtGui.QBrush(QtGui.QColor('#d5000d')))
            
            self.setText(1, '')
            self.setText(3, 'Missing working file')
            self.treeWidget().setItemWidget(self, 1, QtWidgets.QWidget())
        elif state == ShotState.FIRST_DELIVERY:
            self._get_checkbox_select().setEnabled(True)
            self._get_checkbox_pack().setEnabled(False)

            self._select_widget.set_label_color('#b9c2c8')
            self.setForeground(1, QtGui.QBrush(QtGui.QColor('#b9c2c8')))
            self.setForeground(3, QtGui.QBrush(QtGui.QColor('#3b9800')))
            
            self.setText(1, self.get_target_take_name())
            self.setText(3, 'First delivery')
            self.treeWidget().setItemWidget(self, 1, QtWidgets.QWidget())
        elif state == ShotState.NEW_TAKE_PACK_SELECTED:
            self._get_checkbox_select().setEnabled(True)
            self._get_checkbox_pack().setEnabled(True)

            self._select_widget.set_label_color('#b9c2c8')
            self.setForeground(1, QtGui.QBrush(QtGui.QColor('#b9c2c8')))
            self.setForeground(3, QtGui.QBrush(QtGui.QColor('#b9c2c8')))
            
            self.setText(1, self.get_target_take_name())
            self.setText(3, 'Pack will be sent again')
            self.treeWidget().setItemWidget(self, 1, QtWidgets.QWidget())
        elif state == ShotState.NEW_TAKE_PACK_UNSELECTED:
            self._get_checkbox_select().setEnabled(True)
            self._get_checkbox_pack().setEnabled(True)

            self._select_widget.set_label_color('#b9c2c8')
            self.setForeground(1, QtGui.QBrush(QtGui.QColor('#b9c2c8')))
            
            self.setText(1, self.get_target_take_name())
            self.setText(3, '')
            self.treeWidget().setItemWidget(self, 1, QtWidgets.QWidget())
        elif state == ShotState.RESEND_TAKE_PACK_SELECTED:
            self._get_checkbox_select().setEnabled(True)
            self._get_checkbox_pack().setEnabled(True)

            self._select_widget.set_label_color('#b9c2c8')
            self.setForeground(1, QtGui.QBrush(QtGui.QColor('#d5000d')))
            self.setForeground(3, QtGui.QBrush(QtGui.QColor('#b9c2c8')))
            
            self.setText(1, self.get_target_take_name())
            self.setText(3, 'Pack will be sent again')
            self.treeWidget().setItemWidget(self, 1, QtWidgets.QWidget())
        elif state == ShotState.RESEND_TAKE_PACK_UNSELECTED:
            self._get_checkbox_select().setEnabled(True)
            self._get_checkbox_pack().setEnabled(True)

            self._select_widget.set_label_color('#b9c2c8')
            self.setForeground(1, QtGui.QBrush(QtGui.QColor('#d5000d')))
            
            self.setText(1, self.get_target_take_name())
            self.setText(3, '')
            self.treeWidget().setItemWidget(self, 1, QtWidgets.QWidget())
        elif state == ShotState.ALREADY_DELIVERED:
            self._get_checkbox_select().setEnabled(False)
            self._get_checkbox_pack().setEnabled(False)

            self._select_widget.set_label_color('#d66700')
            self.setForeground(3, QtGui.QBrush(QtGui.QColor('#d66700')))
            
            self.setText(1, '')
            self.setText(3, 'Already delivered')
            self.treeWidget().setItemWidget(self, 1, self._button_choose_take)
            
            self._get_checkbox_select().setEnabled(False)
        elif state == ShotState.ALREADY_RECEIVED:
            self._get_checkbox_select().setEnabled(False)
            self._get_checkbox_pack().setEnabled(False)

            self._select_widget.set_label_color('#d66700')
            self.setForeground(3, QtGui.QBrush(QtGui.QColor('#d66700')))
            
            self.setText(1, '')
            self.setText(3, 'Already received')
            self.treeWidget().setItemWidget(self, 1, self._button_choose_take)
    
    def _get_checkbox_select(self):
        return self._select_widget.checkbox_select
    
    def _get_checkbox_pack(self):
        return self._checkbox_pack
    
    def _on_checkbox_select_state_changed(self, checkstate):
        if self._state == ShotState.FIRST_DELIVERY:
            self.set_selected(checkstate == QtCore.Qt.Checked)
        elif self._state == ShotState.NEW_TAKE_PACK_SELECTED:
            self.set_selected(checkstate == QtCore.Qt.Checked)
        elif self._state == ShotState.NEW_TAKE_PACK_UNSELECTED:
            self.set_selected(checkstate == QtCore.Qt.Checked)
        elif self._state == ShotState.RESEND_TAKE_PACK_SELECTED:
            self.set_selected(checkstate == QtCore.Qt.Checked)
        elif self._state == ShotState.RESEND_TAKE_PACK_UNSELECTED:
            self.set_selected(checkstate == QtCore.Qt.Checked)
    
    def _on_checkbox_pack_state_changed(self, checkstate):
        if self._state == ShotState.NEW_TAKE_PACK_SELECTED:
            if checkstate == QtCore.Qt.Unchecked:
                self.update_state(ShotState.NEW_TAKE_PACK_UNSELECTED)
                self.set_send_pack(False)
        elif self._state == ShotState.NEW_TAKE_PACK_UNSELECTED:
            if checkstate == QtCore.Qt.Checked:
                self.update_state(ShotState.NEW_TAKE_PACK_SELECTED)
                self.set_send_pack(True)
        elif self._state == ShotState.RESEND_TAKE_PACK_SELECTED:
            if checkstate == QtCore.Qt.Unchecked:
                self.update_state(ShotState.NEW_TAKE_PACK_UNSELECTED)
                self.set_send_pack(False)
        elif self._state == ShotState.RESEND_TAKE_PACK_UNSELECTED:
            if checkstate == QtCore.Qt.Checked:
                self.update_state(ShotState.RESEND_TAKE_PACK_SELECTED)
                self.set_send_pack(True)
    
    def _on_button_choose_clicked(self, checked=False):
        if self._state == ShotState.ALREADY_DELIVERED:
            res = self._custom_widget.dialog_choose_take.show_dialog(self._state)

            if res == QtWidgets.QDialog.Accepted:
                new_take = self._custom_widget.dialog_choose_take.get_new_take()
                self.set_new_take(new_take)

                if new_take:
                    self.update_state(ShotState.NEW_TAKE_PACK_UNSELECTED)
                else:
                    self.update_state(ShotState.RESEND_TAKE_PACK_UNSELECTED)
        elif self._state == ShotState.ALREADY_RECEIVED:
            res = self._custom_widget.dialog_choose_take.show_dialog(self._state)

            if res == QtWidgets.QDialog.Accepted:
                self.set_new_take(True)
                self.update_state(ShotState.NEW_TAKE_PACK_UNSELECTED)


class SelectAllWidget(QtWidgets.QWidget):

    def __init__(self):
        super(SelectAllWidget, self).__init__()
        self._label = QtWidgets.QLabel('Select all')
        self.checkbox = QtWidgets.QCheckBox()

        self.setStyleSheet('QLabel { font-weight : 600; }')

        hlo = QtWidgets.QHBoxLayout()
        hlo.addWidget(self.checkbox)
        hlo.addWidget(self._label)
        hlo.setContentsMargins(0, 0, 0, 0)
        hlo.setSpacing(0)

        self.setLayout(hlo)
    
    def sizeHint(self):
        return QtCore.QSize(60, 30)


class SelectAllItem(QtWidgets.QTreeWidgetItem):
    
    def __init__(self, tree):
        super(SelectAllItem, self).__init__(tree)
        self._widget_select = SelectAllWidget()
        self._widget_pack = SelectAllWidget()
        self.treeWidget().setItemWidget(self, 0, self._widget_select)
        self.treeWidget().setItemWidget(self, 2, self._widget_pack)
        
        for i in range(self.treeWidget().columnCount()):
            self.setBackground(i, QtGui.QBrush(QtGui.QColor('#311215')))
        
        self._widget_select.checkbox.stateChanged.connect(self._on_checkbox_select_state_changed)
        self._widget_pack.checkbox.stateChanged.connect(self._on_checkbox_pack_state_changed)
    
    def _on_checkbox_select_state_changed(self, checkstate):
        for i in range(1, self.treeWidget().topLevelItemCount()):
            item = self.treeWidget().topLevelItem(i)
            if (
                    item.get_state() != ShotState.MISSING_FILE
                and item.get_state() != ShotState.ALREADY_DELIVERED
                and item.get_state() != ShotState.ALREADY_RECEIVED
            ):
                item._get_checkbox_select().setCheckState(
                    QtCore.Qt.CheckState(checkstate)
                )

    def _on_checkbox_pack_state_changed(self, checkstate):
        for i in range(1, self.treeWidget().topLevelItemCount()):
            item = self.treeWidget().topLevelItem(i)
            if (
                    item.get_state() != ShotState.MISSING_FILE
                and item.get_state() != ShotState.FIRST_DELIVERY
                and item.get_state() != ShotState.ALREADY_DELIVERED
                and item.get_state() != ShotState.ALREADY_RECEIVED
            ):
                item._get_checkbox_pack().setCheckState(
                    QtCore.Qt.CheckState(checkstate)
                )


class ShotToSendList(QtWidgets.QTreeWidget):
    
    def __init__(self, custom_widget, session):
        super(ShotToSendList, self).__init__()
        self.custom_widget = custom_widget
        self.session = session

        self.setHeaderLabels(self.get_header_labels())
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.update()
        self.header().resizeSections(QtWidgets.QHeaderView.ResizeToContents)
    
    def get_header_labels(self):
        return ['Shots', 'Delivered take', 'Send pack', 'Info']
    
    def update(self):
        self.clear()
        SelectAllItem(self)

        oids = self.session.cmds.Flow.get_mapped_oids(
            self.custom_widget.oid+'/shots',
        )
        for oid in oids:
            ShotToSendItem(self, oid, self.custom_widget, self.session)


class ChooseTakeWidget(QtWidgets.QWidget):

    def __init__(self):
        super(ChooseTakeWidget, self).__init__()
        self._radiobutton_new_take = QtWidgets.QRadioButton('Create a new take')
        self._radiobutton_resend = QtWidgets.QRadioButton('Resend the last take')
        self._new_take_mandatory_label = QtWidgets.QLabel('Last take already received: create a new take ?')
        self.setStyleSheet('QLabel { color : #d66700; }')

        vlo = QtWidgets.QVBoxLayout()
        vlo.addWidget(self._radiobutton_new_take)
        vlo.addWidget(self._radiobutton_resend)
        vlo.addWidget(self._new_take_mandatory_label)

        vlo.setContentsMargins(0, 0, 0, 0)
        vlo.setSpacing(0)

        self.setLayout(vlo)
    
    def update(self, state):
        if state == ShotState.ALREADY_DELIVERED:
            self._radiobutton_new_take.setVisible(True)
            self._radiobutton_resend.setVisible(True)
            self._new_take_mandatory_label.setVisible(False)

            self._radiobutton_new_take.setChecked(True)
        elif state == ShotState.ALREADY_RECEIVED:
            self._radiobutton_new_take.setVisible(False)
            self._radiobutton_resend.setVisible(False)
            self._new_take_mandatory_label.setVisible(True)
            
            self._radiobutton_new_take.setChecked(True)


class ChooseTakeDialog(QtWidgets.QDialog):

    def __init__(self, parent):
        super(ChooseTakeDialog, self).__init__(parent)
        self._widget_choose_take = ChooseTakeWidget()
        self._button_confirm = QtWidgets.QPushButton('Confirm')
        self._button_cancel = QtWidgets.QPushButton('Cancel')

        glo = QtWidgets.QGridLayout()
        glo.addWidget(self._widget_choose_take, 0, 0, 1, 2)
        glo.addWidget(self._button_confirm, 1, 0)
        glo.addWidget(self._button_cancel, 1, 1)

        self.setLayout(glo)

        self.setWindowTitle('')
        self.resize(200, 100)

        self._button_confirm.clicked.connect(lambda checked=False: self.accept())
        self._button_cancel.clicked.connect(lambda checked=False: self.reject())
    
    def get_new_take(self):
        return self._widget_choose_take._radiobutton_new_take.isChecked()
    
    def show_dialog(self, state):
        self._widget_choose_take.update(state)
        return self.exec()


class SendShotsForValidationWidget(CustomPageWidget):

    def build(self):
        self._shot_list = ShotToSendList(self, self.session)
        self._combobox_task = QtWidgets.QComboBox()
        self._combobox_task.addItems(self.get_task_names())
        self._combobox_task.setCurrentText(self.get_target_task())
        refresh_icon = QtGui.QIcon(resources.get_icon(('icons.libreflow', 'refresh')))
        self._button_send = QtWidgets.QPushButton('Send')
        self._button_send.setFixedSize(50, 30)
        self._button_close = QtWidgets.QPushButton('Close')
        self._button_close.setFixedSize(50, 30)
        self._label_shot_count = QtWidgets.QLabel(f'{self._shot_list.topLevelItemCount() - 1} shot(s)')

        self.dialog_choose_take = ChooseTakeDialog(self)

        glo = QtWidgets.QGridLayout()
        glo.addWidget(self._combobox_task, 0, 0, 1, 5)
        glo.addWidget(self._shot_list, 1, 0, 1, 5)
        glo.addWidget(self._button_close, 2, 0)
        glo.addWidget(self._label_shot_count, 2, 2, QtCore.Qt.AlignCenter)
        glo.addWidget(self._button_send, 2, 4)
        glo.setContentsMargins(0, 0, 0, 0)
        glo.setSpacing(0)
        self.setLayout(glo)
    
        # Install callbacks
        self._button_send.clicked.connect(self._on_button_send_clicked)
        self._button_close.clicked.connect(self._on_button_close_clicked)
        self._combobox_task.currentTextChanged.connect(self._on_combobox_task_text_changed)
    
    def get_task_names(self):
        return self.session.cmds.Flow.get_value_choices(self.oid+'/task')
    
    def get_target_task(self):
        return self.session.cmds.Flow.get_value(self.oid+'/task')

    def set_target_task(self, task_name):
        self.session.cmds.Flow.set_value(self.oid+'/task', task_name)
    
    def update_list(self):
        self.session.cmds.Flow.call(self.oid+'/shots', 'touch', [], {})
        self._shot_list.update()
        shot_count = self._shot_list.topLevelItemCount() - 1
        self._label_shot_count.setText(f'{shot_count} shot(s)')

    def _on_button_send_clicked(self):
        self.session.cmds.Flow.run_action(self.oid, None)
        self.update_list()
    
    def _on_button_close_clicked(self):
        self.page.view.close()
    
    def _on_combobox_task_text_changed(self, text):
        self.set_target_task(text)
        self.update_list()
