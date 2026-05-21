"""
UUVSearch - 离散 SAC 智能体（修复α张量）
"""
import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim
from .network import Actor, Critic
from utils.replay_buffer import ReplayBuffer

class SACAgent:
    def __init__(self, obs_dim, action_dim, config):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.action_dim = action_dim
        self.gamma = float(config.get("gamma", 0.99))
        self.tau = float(config.get("tau", 0.005))
        self.batch_size = int(config.get("batch_size", 64))
        self.learn_start = int(config.get("learn_start", 1000))
        hidden_dim = int(config.get("hidden_dim", 128))

        # 熵温度系数（使用可学习参数 log_alpha）
        init_alpha = float(config.get("alpha", 0.2))
        self.auto_alpha = bool(config.get("auto_alpha", True))
        self.target_entropy = -np.log(1.0 / action_dim) * float(config.get("target_entropy_scale", 1.0))
        self.log_alpha = torch.tensor(np.log(init_alpha), requires_grad=True, device=self.device)
        self.alpha_optimizer = optim.Adam([self.log_alpha], lr=float(config.get("lr_alpha", 3e-4)))
        # 始终保持当前 α 的浮点数快照（用于日志或外部查询）
        self.alpha = self.log_alpha.exp().item()

        # 网络
        self.actor = Actor(obs_dim, action_dim, hidden_dim).to(self.device)
        self.critic1 = Critic(obs_dim, action_dim, hidden_dim).to(self.device)
        self.critic2 = Critic(obs_dim, action_dim, hidden_dim).to(self.device)
        self.target_critic1 = Critic(obs_dim, action_dim, hidden_dim).to(self.device)
        self.target_critic2 = Critic(obs_dim, action_dim, hidden_dim).to(self.device)
        self.target_critic1.load_state_dict(self.critic1.state_dict())
        self.target_critic2.load_state_dict(self.critic2.state_dict())

        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=float(config.get("lr_actor", 1e-4)))
        self.critic_optimizer = optim.Adam(
            list(self.critic1.parameters()) + list(self.critic2.parameters()),
            lr=float(config.get("lr_critic", 1e-4))
        )

        self.buffer = ReplayBuffer(int(config.get("buffer_size", 100000)))
        self.steps = 0

    def select_action(self, obs, deterministic=False):
        obs_tensor = torch.FloatTensor(obs).unsqueeze(0).to(self.device)
        with torch.no_grad():
            probs = self.actor(obs_tensor)
        if deterministic:
            return probs.argmax(dim=1).item()
        else:
            return torch.multinomial(probs, 1).item()

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

        # 当前 alpha 张量（不参与梯度）
        alpha_tensor = self.log_alpha.exp().detach()

        # 更新 Critic
        with torch.no_grad():
            next_probs = self.actor(next_states)
            next_log_probs = torch.log(next_probs + 1e-8)
            next_q1 = self.target_critic1(next_states)
            next_q2 = self.target_critic2(next_states)
            next_min_q = torch.min(next_q1, next_q2)
            next_v = (next_probs * (next_min_q - alpha_tensor * next_log_probs)).sum(dim=1, keepdim=True)
            target_q = rewards + self.gamma * (1 - dones) * next_v

        current_q1 = self.critic1(states).gather(1, actions)
        current_q2 = self.critic2(states).gather(1, actions)
        critic_loss = F.mse_loss(current_q1, target_q) + F.mse_loss(current_q2, target_q)

        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()

        # 更新 Actor
        probs = self.actor(states)
        log_probs = torch.log(probs + 1e-8)
        with torch.no_grad():
            q1 = self.critic1(states)
            q2 = self.critic2(states)
            min_q = torch.min(q1, q2)
        # 使用 alpha_tensor（已 detach），确保梯度只流向 actor
        actor_loss = (probs * (alpha_tensor * log_probs - min_q)).sum(dim=1).mean()

        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()

        # 自动调整 alpha（基于策略熵与目标熵的差距）
        if self.auto_alpha:
            policy_entropy = -(probs * log_probs).sum(dim=1).mean()  # H(π) = -E[log π]
            alpha_loss = self.log_alpha * (policy_entropy.detach() - self.target_entropy)
            self.alpha_optimizer.zero_grad()
            alpha_loss.backward()
            self.alpha_optimizer.step()
            self.alpha = self.log_alpha.exp().item()
        else:
            # 即使不自动调整，也同步一下浮点值
            self.alpha = self.log_alpha.exp().item()

        # 软更新目标网络
        for target_param, param in zip(self.target_critic1.parameters(), self.critic1.parameters()):
            target_param.data.copy_(target_param.data * (1.0 - self.tau) + param.data * self.tau)
        for target_param, param in zip(self.target_critic2.parameters(), self.critic2.parameters()):
            target_param.data.copy_(target_param.data * (1.0 - self.tau) + param.data * self.tau)

        self.steps += 1
        return {
            "loss_critic": critic_loss.item(),
            "loss_actor": actor_loss.item(),
            "alpha": self.alpha
        }

    def save(self, path):
        torch.save({
            'actor': self.actor.state_dict(),
            'critic1': self.critic1.state_dict(),
            'critic2': self.critic2.state_dict(),
            'target_critic1': self.target_critic1.state_dict(),
            'target_critic2': self.target_critic2.state_dict(),
            'log_alpha': self.log_alpha.detach(),
            'alpha_optimizer': self.alpha_optimizer.state_dict(),
            'actor_optimizer': self.actor_optimizer.state_dict(),
            'critic_optimizer': self.critic_optimizer.state_dict(),
        }, path)

    def load(self, path):
        checkpoint = torch.load(path, map_location=self.device, weights_only=True)
        self.actor.load_state_dict(checkpoint['actor'])
        self.critic1.load_state_dict(checkpoint['critic1'])
        self.critic2.load_state_dict(checkpoint['critic2'])
        self.target_critic1.load_state_dict(checkpoint['target_critic1'])
        self.target_critic2.load_state_dict(checkpoint['target_critic2'])
        self.log_alpha = checkpoint['log_alpha'].to(self.device).requires_grad_()
        self.alpha_optimizer.load_state_dict(checkpoint['alpha_optimizer'])
        self.actor_optimizer.load_state_dict(checkpoint['actor_optimizer'])
        self.critic_optimizer.load_state_dict(checkpoint['critic_optimizer'])
        self.alpha = self.log_alpha.exp().item()