class TranslationException(BaseException):
    def __init__(self, message: str, node):
        self.message = message
        self.node = node

    def get_error_msg(self):
        return self.message
    
    def get_causing_node(self):
        return self.node