from PyQt5 import QtCore, QtWidgets, Qt
import sys


class MouseClick(Qt.QObject):

    """
    filter used in order to select 
    one table at a time: if one table is selected
    then we check if another is as well. In 
    that case we disable the latter.
    """
    
    def __init__(self):
        super().__init__()

    def eventFilter(self, obj, event):

        if event.type() == QtCore.QEvent.MouseButtonPress:

            obj.parent().parent().parent().disable_focus(obj.parent())

        return False


class AbstractTable(QtWidgets.QTableWidget):

    """
    Model class for QTables
    """

    def __init__(self, parent, headers):

        super().__init__(parent=parent)

        self.columns_headers = headers

        self.data = [[] for i in range(len(headers))]
        
        # in order to filter clicks
        self.filter = MouseClick()
        self.viewport().installEventFilter(self.filter)

        # needs to be replaced by params["game"]["n_customers"] + n_firms
        self.n_player = 21

        self.setup()

    def setup(self):

          # set height and width
        self.setColumnCount(len(self.columns_headers))
        self.setRowCount(self.n_player)

        # fit the widget
        self.horizontalHeader().setSectionResizeMode(Qt.QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(Qt.QHeaderView.Stretch)
        
        # readonly
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # select whole rows when clicking
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        # remove grid
        self.setShowGrid(False)

        # enable drag and drop
        self.setDragEnabled(True);
        self.setDragDropOverwriteMode(True);
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop);
        self.setDefaultDropAction(QtCore.Qt.CopyAction);

        # set names
        for i, name in enumerate(self.columns_headers):
            self.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(name))

    def update(self, *data):
        
        self.clearContents()

        if data:
            self.fill_table(columns=data)

    def fill_table(self, columns):
        
        for y, items in enumerate(columns):
            
            for x, item in enumerate(items):
                self.setItem(x, y, QtWidgets.QTableWidgetItem(str(item)))

    def is_already_in_table(self, item):

        return any([item in col for col in self.get_data()])

    def insert(self, *data):

        x = len(self.get_data()[0])

        for y, item in enumerate(data):
            self.setItem(x, y, QtWidgets.QTableWidgetItem(str(item)))

    def remove_selected_row(self):

        self.removeRow(self.currentRow())
        self.insertRow(self.rowCount())

    def get_data(self):

        return [[self.item(x, y).text() for x in range(self.rowCount()) if self.item(x, y)] 
                for y in range(self.columnCount())]


class UsersTable(AbstractTable):
    
    """
    Table containing a list of users and corresponding 
    passwords
    """

    name = "users"

    def __init__(self, parent, headers):

        super().__init__(parent=parent, headers=headers)

    def add_user(self, user, password):
       
        cond0 = self.is_already_in_table(user)
        cond1 = self.is_already_in_table(password)

        if not cond0 and not cond1:

            self.insert(user, password)

        else:
            
            return "User '{}' or password '{}' already registered!".format(user, password)

    def remove_selected_user(self):

        self.remove_selected_row()


class WaitingListTable(AbstractTable):

    """
    Table containing a list of users waiting after 
    a valid connection (username and password matching)
    """
    
    name = "waiting_list"

    def __init__(self, parent, headers):

        super().__init__(parent=parent, headers=headers)
    
    def remove_selected_user(self):
        
        self.remove_selected_row()


class AddUserWindow(QtWidgets.QDialog):

    """
    window used in order to add a new player
    """
    
    def __init__(self, parent):

        super().__init__(parent=parent)

        self.setWindowTitle("Add user")

        self.layout = QtWidgets.QVBoxLayout()
        
        self.ok_button = QtWidgets.QPushButton("Ok")
        self.cancel_button = QtWidgets.QPushButton("Cancel")

        self.forms = {"user": QtWidgets.QLineEdit(), 
                      "password": QtWidgets.QLineEdit()}

        self.setup()

    def setup(self):

        self.fill_layout()

        # noinspection PyUnresolvedReferences
        self.ok_button.clicked.connect(self.push_ok_button)
        self.ok_button.setFocus(True)
        # noinspection PyUnresolvedReferences
        self.cancel_button.clicked.connect(self.push_cancel_button)

    def fill_layout(self):

        form_layout = QtWidgets.QFormLayout()

        for label, value in self.forms.items():
            form_layout.addRow(QtWidgets.QLabel(label), value)

        horizontal_layout = QtWidgets.QHBoxLayout()

        horizontal_layout.addWidget(self.cancel_button, alignment=QtCore.Qt.AlignRight)
        horizontal_layout.addWidget(self.ok_button, alignment=QtCore.Qt.AlignRight)

        self.layout.addLayout(form_layout)
        self.layout.addLayout(horizontal_layout)

        self.setLayout(self.layout) 

    def push_ok_button(self):
        
        self.parent().add_user_to_user_table(user=self.forms["user"].text(), 
                                        password=self.forms["password"].text())

        self.hide()

    def push_cancel_button(self):
        self.hide()


class ConnectionFrame(QtWidgets.QWidget):

    name = "ConnectionFrame"

    def __init__(self, parent):

        super().__init__()

        self.layout = QtWidgets.QVBoxLayout()

        self.remove_button = QtWidgets.QPushButton("Remove")
        self.add_button = QtWidgets.QPushButton("Add user")
        self.update_tables_button = QtWidgets.QPushButton("Update tables online")

        self.left_group = QtWidgets.QGroupBox("Users")
        self.left_table = UsersTable(parent=self, headers=("Username", "Password"))

        self.right_group = QtWidgets.QGroupBox("Waiting list")
        self.right_table = WaitingListTable(parent=self, headers=("Username", ))

        self.add_window = AddUserWindow(parent=self)

        self.set_up()

    def set_up(self):

        self.fill_layout()

        # noinspection PyUnresolvedReferences
        self.remove_button.clicked.connect(self.push_remove_button)
        # noinspection PyUnresolvedReferences
        self.add_button.clicked.connect(self.push_add_button)
        # noinspection PyUnresolvedReferences
        self.update_tables_button.clicked.connect(self.push_update_tables_button)

    def fill_layout(self):

        # ------ add first row ------------ # 

        horizontal_layout_first_row = QtWidgets.QHBoxLayout()

        left_table_layout = QtWidgets.QHBoxLayout()
        right_table_layout = QtWidgets.QHBoxLayout()

        left_table_layout.addWidget(self.left_table)
        right_table_layout.addWidget(self.right_table)

        # add groups 
        self.left_group.setLayout(left_table_layout)
        self.right_group.setLayout(right_table_layout)

        horizontal_layout_first_row.addWidget(self.left_group)
        horizontal_layout_first_row.addWidget(self.right_group)

        self.layout.addLayout(horizontal_layout_first_row)

        # ------ add second row ------------ # 

        vertical_layout_second_row = QtWidgets.QVBoxLayout()

        vertical_layout_second_row.addWidget(self.add_button, alignment=QtCore.Qt.AlignCenter)
        vertical_layout_second_row.addWidget(self.remove_button, alignment=QtCore.Qt.AlignCenter)
        vertical_layout_second_row.addWidget(self.update_tables_button, alignment=QtCore.Qt.AlignCenter)

        self.layout.addLayout(vertical_layout_second_row)

        self.setLayout(self.layout)

    # ----- Update tables ------------------------ # 

    def update_waiting_list(self, users):

        self.right_table.update(users)

    def update_users(self, users, passwords):

        self.left_table.update(users, passwords)

    def get_selected_table(self):

        if self.right_table.selectedItems() or self.left_table.selectedItems():
            return (self.right_table, self.left_table)[bool(self.left_table.selectedItems())]

    # ----- Push Buttons  ------------------------ # 

    def push_add_button(self):

        self.add_window.show()

    def push_remove_button(self):
        
        table = self.get_selected_table()

        if table:

            table.remove_selected_user()
                
        else:
            self.show_warning(msg="Please select a user to remove.")

    def push_update_tables_button(self):

        users, passwords = self.left_table.get_data()
        self.register_users(users, passwords)
        
        users, = self.right_table.get_data()
        self.register_waiting_list(users)

    def add_user_to_user_table(self, user, password):

        err = self.left_table.add_user(user, password)

        if err:
            self.show_warning(msg=err)

    # ----- Method used in order to defocus another table in order to remove users  -------- # 

    def disable_focus(self, obj):

        table_are_focused = self.left_table.selectedItems() \
                or self.right_table.selectedItems()

        if table_are_focused:

            to_defocus = (self.left_table, self.right_table)[self.left_table == obj]

            to_defocus.clearSelection()


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = ConnectionFrame(parent="lol")
    window.setFixedSize(1000, 600)
    data = {"waiting_list": ["mickael"], 
            "users": [("test", "pass") for i in range(21)]}
    window.update(data)
    window.show()
    sys.exit(app.exec_())
