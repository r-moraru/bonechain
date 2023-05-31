from block import Block

class Blockchain:
    def __init__(self):
        self._blocks = []

    def add_block(self, block: Block):
        self._blocks.append(block)

    def get_blocks(self) -> list[Block]:
        return self._blocks