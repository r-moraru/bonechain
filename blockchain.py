from block import Block

class Blockchain:
    def __init__(self):
        self._blocks = [self.create_genesis()]

    def create_genesis(self) -> Block:
        Block("", [])