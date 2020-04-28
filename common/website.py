class Website:
    def __init__(self, url: str, depth: int, content: str):
        self.url = url
        self.depth = depth
        self.content = content

    def __eq__(self, other):
        return self.url.__eq__(other)

    def __hash__(self):
        return self.url.__hash__()

    def __str__(self):
        return self.url
