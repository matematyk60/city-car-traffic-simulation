class Range:

    def __init__(self, start, end):
        if start and end and end < start:
            raise ValueError("End date cannot be before start date, %s:%s" % (start, end))
        self.start = start
        self.end = end

    def __repr__(self):
        return '[%s\u2025%s)' % (
            self.start or '-\u221E',
            self.end or '+\u221E'
        )

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end

    def __hash__(self):
        return 31 * hash(self.start) + hash(self.end)

    def __iter__(self):
        cur = self.start
        while cur < self.end:
            yield cur
            cur = cur + self.increment

    def __contains__(self, elem):
        ret = True
        if self.start:
            ret = ret and self.start <= elem
        if self.end:
            ret = ret and elem < self.end
        return ret

    def len(self):
        return self.end - self.start