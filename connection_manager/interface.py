from . graphics import mvc_interface, git_app, main_frame
from utils import logger


class UI(mvc_interface.MVCInterface, main_frame.ConnectionFrame, logger.Logger):

    name = "UI"
    app_name = "Connection Manager"

    def __init__(self, model):
        super().__init__(model=model)

    # ------------------ from controller ------------------------------------------ # 

    def controller_update_users(self, users, passwords):

        self.update_users(users, passwords)

    def controller_update_waiting_list(self, users):
            
        self.update_waiting_list(users)

    # -------------------------- ask to controller -------------------------------  #

    def register_waiting_list(self, users):
        self.ask_controller("ui_register_waiting_list", arg=(users, ))

    def register_users(self, users, passwords):
        self.ask_controller("ui_register_users", arg=(users, passwords))

    def ask_for_erasing_tables(self, tables):
        self.ask_controller("ui_ask_for_erasing_tables", arg=tables)
