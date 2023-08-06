class GameError(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return self.message

class ImplementationError(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return self.message

class GameOver(Exception):
    def __init__(self, status):
        self.win = status
        
    def __str__(self):
        return "You lost the game!" if not self.win else "You won the game!"