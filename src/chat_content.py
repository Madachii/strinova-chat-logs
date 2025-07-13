class ChatContent:
    def __init__(self, user: str = "", to: str = "", messages: list = None):
        self.user = user
        self.to = to
        self.messages = list(messages) if messages is not None else []
        