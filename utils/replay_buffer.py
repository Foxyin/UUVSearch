"""经验回放缓冲区（DQN/SAC 共用）"""
import numpy as np


class ReplayBuffer:
    def __init__(self, capacity=100000):
        self.capacity = capacity
        self.buffer = []
        self.position = 0
        self._rng = np.random.RandomState()

    def push(self, state, action, reward, next_state, done):
        if len(self.buffer) < self.capacity:
            self.buffer.append(None)
        self.buffer[self.position] = (state, action, reward, next_state, done)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        indices = self._rng.choice(len(self.buffer), batch_size, replace=False)
        batch = [self.buffer[i] for i in indices]
        state, action, reward, next_state, done = map(np.array, zip(*batch))
        return state, action, reward, next_state, done

    def seed(self, s):
        self._rng = np.random.RandomState(s)

    def __len__(self):
        return len(self.buffer)
