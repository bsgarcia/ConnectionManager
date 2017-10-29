from multiprocessing import Event
from threading import Thread

from utils.logger import Logger

from multiprocessing import Queue, Event
import requests as rq
import json


class Server(Logger):

    name = "Server"
    time_between_requests = 2

    def __init__(self, controller):

        Thread.__init__(self)

        self.controller = controller
        self.param = self.controller.get_parameters("network")

        self.shutdown_event = Event()
        self.waiting_event = Event()

        self.queue = Queue()

        self.server_address = self.param["website"] + "/server_request_with_id.php"

    def shutdown(self):

        self.log("I'm shutting down...")
        self.shutdown_event.set()
        self.waiting_event.set()

    def get_waiting_list(self):

        while True and not self.shutdown_event.is_set():

            self.log("I will ask the distant server to the 'waiting_list' table.")

            response = self.send_request(
                demand_type="reading",
                table="waiting_list"
            )

            if response.text and response.text.split("&")[0] == "waiting_list":
            

                participants = [i for i in response.text.split("&")[1:] if i]
                break

        return participants

    def get_users(self):

        while True and not self.shutdown_event.is_set():

            self.log("I will ask the distant server to the 'users' table.")

            response = self.send_request(
                demand_type="reading",
                table="users"
            )

            if response.text and response.text.split("&")[0] == "name_password":
            
                users_and_passwords = [i.split("#") for i in response.text.split("&")[1:] if i]
                users = [username for (username, password) in users_and_passwords]
                passwords = [password for (username, password) in users_and_passwords]

                break

        return users, passwords

    def register_users(self, usernames, passwords):

        while True and not self.shutdown_event.is_set():

            self.log("I will ask the distant server to write the 'users' table with data {}".format(usernames +
                passwords))

            response = self.send_request(
                demand_type="writing",
                table="users",
                names=json.dumps(usernames),
                passwords=json.dumps(passwords)
            )

            self.log("I got the response '{}' from the distant server.".format(response.text))

            if response.text == "I inserted users in 'users' table.":
                break

    def register_waiting_list(self, usernames):


        while True and not self.shutdown_event.is_set():

            self.log("I will ask the distant server to write the 'waiting_list' table.")

            print(usernames)
            response = self.send_request(
                demand_type="writing",
                table="waiting_list",
                names=json.dumps(usernames),
            )

            self.log("I got the response '{}' from the distant server.".format(response.text))


            if response.text == "I inserted names in 'waiting_list' table.":
                break

    def send_request(self, **kwargs):

        return rq.get(self.server_address, params=kwargs)
