"""
UUVSearch - SAC 网络结构（离散动作）
"""
import torch
import torch.nn as nn
import torch.nn.functional as F

class Actor(nn.Module):
    """策略网络，输出动作概率分布"""
    def __init__(self, obs_dim, action_dim, hidden_dim=128):
        super().__init__()
        self.fc1 = nn.Linear(obs_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.out = nn.Linear(hidden_dim, action_dim)

    def forward(self, obs):
        x = F.relu(self.fc1(obs))
        x = F.relu(self.fc2(x))
        return F.softmax(self.out(x), dim=-1)

class Critic(nn.Module):
    """双 Q 网络"""
    def __init__(self, obs_dim, action_dim, hidden_dim=128):
        super().__init__()
        self.fc1 = nn.Linear(obs_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.out = nn.Linear(hidden_dim, action_dim)  # 每个动作的 Q 值

    def forward(self, obs):
        x = F.relu(self.fc1(obs))
        x = F.relu(self.fc2(x))
        return self.out(x)