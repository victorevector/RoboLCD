class Session_Saver():
    """docstring for Session_Saver"""
    def __init__(self):
        self.saved = {'saved': 'I am a saver'}

    def save_variable(self, name, value):
        self.saved[name] = value

session_saver = Session_Saver()