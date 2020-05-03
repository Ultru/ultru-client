class Scores:
    scores = {
        "MALWARE": [9, 10],
        "MALICIOUS": [8, 9],
        "SUSPICIOUS": [5, 8],
        "BENIGN": [0, 5]
    }

    def __init__(self):
        self.lhv = [0, 0]

    def __getattr__(self, name):
        if name.upper() in self.scores.keys():
            self.lhv = self.scores[name]
        return self

    @classmethod
    def from_score(cls, score):
        c = cls()
        c.lhv = c.scores[score.upper()]
        return c

    def compare(self, rhv):
        return rhv > self.lhv[0] and rhv <= self.lhv[1] 

    def gte(self, rhv):
        return self.lhv[0] >= rhv

    def lt(self, rhv):
        return self.lhv[0] < rhv

    @property
    def low(self):
        return self.lhv[0]

    @property
    def high(self):
        return self.lhv[1]
