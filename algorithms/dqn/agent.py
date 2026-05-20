"""
UUVSearch - DQN 智能体（类型安全版）
"""
import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim
from .network import QNetwork
from .replay_buffer import ReplayBuffer

class DQNAgent:
    def __init__(self, obs_dim, action_dim, config):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.action_dim = action_dim
        # 显式类型转换，防止YAML字符串问题
        self.gamma = float(config.get("gamma", 0.99))
        self.epsilon = float(config.get("epsilon_start", 1.0))
        self.epsilon_min = float(config.get("epsilon_min", 0.05))
        self.epsilon_decay = float(config.get("epsilon_decay", 0.995))
        self.batch_size = int(config.get("batch_size", 64))
        self.learn_start = int(config.get("learn_start", 1000))
        lr = float(config.get("lr", 1e-4))
        hidden_dim = int(config.get("hidden_dim", 128))
        buffer_size = int(config.get("buffer_size", 100000))
        self.update_target_every = int(config.get("update_target_every", 1000))

        self.q_net = QNetwork(obs_dim, action_dim, hidden_dim).to(self.device)
        self.target_net = QNetwork(obs_dim, action_dim, hidden_dim).to(self.device)
        self.target_net.load_state_dict(self.q_net.state_dict())
        self.optimizer = optim.Adam(self.q_net.parameters(), lr=lr)

        self.buffer = ReplayBuffer(buffer_size)
        self.steps = 0

    def select_action(self, obs, deterministic=False):
        if not deterministic and np.random.rand() < self.epsilon:
            return np.random.randint(self.action_dim)
        obs_tensor = torch.FloatTensor(obs).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.q_net(obs_tensor)
        return q_values.argmax(dim=1).item()

    def store_transition(self, state, action, reward, next_state, done):
        self.buffer.push(state, action, reward, next_state, done)

    def update(self):
        if len(self.buffer) < self.learn_start:
            return None

        states, actions, rewards, next_states, dones = self.buffer.sample(self.batch_size)
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).unsqueeze(1).to(self.device)

        current_q = self.q_net(states).gather(1, actions)
        with torch.no_grad():
            max_next_q = self.target_net(next_states).max(dim=1, keepdim=True)[0]
            target_q = rewards + self.gamma * (1 - dones) * max_next_q

        loss = F.mse_loss(current_q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        self.steps += 1
        if self.steps % self.update_target_every == 0:
            self.target_net.load_state_dict(self.q_net.state_dict())

        return {"loss": loss.item(), "epsilon": self.epsilon}

    def save(self, path):
        torch.save({
            'q_net': self.q_net.state_dict(),
            'target_net': self.target_net.state_dict(),
            'optimizer': self.optimizer.state_dict(),
        }, path)

    def load(self, path):
        checkpoint = torch.load(path, map_location=self.device)
        self.q_net.load_state_dict(checkpoint['q_net'])
        self.target_net.load_state_dict(checkpoint['target_net'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])