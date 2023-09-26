class uQue:
    def __init__(self, capacity,initialVal):
        self.capacity = capacity
        self.buffer = [None] * capacity
        self.size = 0
        self.start_idx = 0
        for i in range(capacity):
            self.buffer[i] = initialVal

    def append(self, value):
        if self.size < self.capacity:
            self.buffer[self.size] = value
            self.size += 1
        else:
            self.buffer[self.start_idx] = value
            self.start_idx = (self.start_idx + 1) % self.capacity

    def __getitem__(self, idx):
        if idx < 0 or idx >= self.capacity:
            raise IndexError("Index out of range")
        real_idx = (self.start_idx + self.size - 1 - idx) % self.capacity
        return self.buffer[real_idx]

    def sum(self):
        return sum(val for val in self.buffer if val is not None)
    
    def average(self):
        return self.sum() / len(self) if self.size != 0 else 0
    
    def __len__(self):
        return self.size