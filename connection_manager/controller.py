from connection_manager.control import mvc_controller


class Controller(mvc_controller.MVCController):
    name = "Controller"

    def __init__(self, model):

        super().__init__(model=model)

    def ui_register_users(self, users, passwords):

        self.log("Got new request from ui: register users: {}".format(users))
        self.server.register_users(usernames=users, passwords=passwords)
        self.server_get_users()

    def ui_register_waiting_list(self, users):

        self.log("Got new request from ui: register users: {}".format(users))
        self.server.register_waiting_list(usernames=users)
        self.server_get_waiting_list()

    def ui_ready(self):

        super().ui_ready()

        self.server_get_waiting_list()
        self.server_get_users()

    def server_get_waiting_list(self):

        users = self.server.get_waiting_list()
        self.ask_interface("controller_update_waiting_list", (users, ))

    def server_get_users(self):
        
        users, passwords = self.server.get_users()
        self.ask_interface("controller_update_users", (users, passwords))
