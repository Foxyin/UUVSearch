"""
UUVSearch - DQN 训练器（含训练结束强制保存）
"""
import os
import numpy as np
from algorithms.dqn.agent import DQNAgent
from utils.logger import Logger


class DQNTrainer:
    def __init__(self, env, config, exp_name="dqn"):
        obs_dim = env.observation_space.shape[0]
        action_dim = env.action_space.n
        self.env = env
        self.agent = DQNAgent(obs_dim, action_dim, config["algo"])
        self.max_steps = config["simulation"]["max_steps"]
        self.total_steps = config.get("total_steps", 100000)
        self.save_freq = config.get("save_freq", 50000)
        self.log_freq = config.get("log_freq", 1000)
        self.checkpoint_dir = f"experiments/checkpoints/{exp_name}"
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        self.logger = Logger(log_dir=f"experiments/logs/{exp_name}")

    def train(self):
        obs, info = self.env.reset()
        episode_reward = 0
        episode_len = 0
        episode_count = 0

        for step in range(self.total_steps):
            action = self.agent.select_action(obs)
            next_obs, reward, terminated, truncated, info = self.env.step(action)
            done = terminated or truncated

            self.agent.store_transition(obs, action, reward, next_obs, float(done))
            loss_info = self.agent.update()

            obs = next_obs
            episode_reward += reward
            episode_len += 1

            if done:
                episode_count += 1
                self.logger.log_scalar("train/episode_reward", episode_reward, step)
                self.logger.log_scalar("train/episode_length", episode_len, step)
                if loss_info:
                    self.logger.log_scalar("train/loss", loss_info["loss"], step)
                    self.logger.log_scalar("train/epsilon", loss_info["epsilon"], step)
                obs, info = self.env.reset()
                episode_reward = 0
                episode_len = 0

            if (step + 1) % self.save_freq == 0:
                self.agent.save(os.path.join(self.checkpoint_dir, f"step_{step+1}.pt"))

        # 训练结束时强制保存最终模型
        final_path = os.path.join(self.checkpoint_dir, f"step_{self.total_steps}.pt")
        self.agent.save(final_path)
        self.logger.close()