from config import users

class Authentication:
    def __init__(self):
        self.users = users

    def authenticate(self, username, password):
        if username in self.users and self.users[username]["password"] == password:
            return True
        return False
