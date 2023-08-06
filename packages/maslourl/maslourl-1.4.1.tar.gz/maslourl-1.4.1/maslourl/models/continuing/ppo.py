import os

from torch.distributions import Normal
from torch.utils.tensorboard import SummaryWriter
import time
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import gym
from maslourl.trackers.average_tracker import AverageRewardTracker
from abc import ABC, abstractmethod


class PPOContinuing(ABC):

    def __init__(self, cuda=True, seed=1, torch_deterministic=True):
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.backends.cudnn.deterministic = torch_deterministic
        temp_env = self.make_env(0, 0, False, 0, "")()
        self.observation_shape = temp_env.observation_space.shape
        self.n_actions = np.prod(temp_env.action_space.shape)
        self.device = torch.device("cuda" if torch.cuda.is_available() and cuda else "cpu")
        self.model = self.build_model().to(self.device)

    @abstractmethod
    def make_env(self, seed, idx, capture_video, capture_every_n_episode, run_name):
        pass

    @abstractmethod
    def build_model(self) -> nn.Module:
        pass

    def save_agent(self, path, save_2_wandb=False):
        dir_name = "/".join(path.split("/")[:-1])
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        torch.save(self.model, path)
        if save_2_wandb:
            import wandb
            if not os.path.exists(os.path.join(wandb.run.dir, "models/")):
                os.makedirs(os.path.join(wandb.run.dir, "models/"))
            torch.save(self.model, os.path.join(wandb.run.dir, "models/best_model.pt"))

    def get_value(self, x):
        actions_mean, value = self.model(x)
        return value

    def get_action_and_value(self, x, action=None):
        action_mean, value = self.model(x)
        action_logstd = self.model.actor_logstd.expand_as(action_mean)
        action_std = torch.exp(action_logstd)
        dist = Normal(loc=action_mean, scale=action_std)
        if action is None:
            action = dist.sample()
        return action, dist.log_prob(action).sum(1), dist.entropy().sum(1), value

    def get_action_greedy(self, x):
        action_probs, value = self.model(torch.tensor(x))
        return torch.argmax(action_probs, dim=1)

    def load_agent(self, path, train=False):
        self.model = torch.load(path)
        if train:
            self.model.train()
        else:
            self.model.eval()

    def track_info(self, info, average_reward_tracker, save_2_wandb, verbose, global_step, ckpt_path):
        for item in info:
            if "episode" in item.keys():
                if verbose:
                    print(f"global_step={global_step}, episodic_return={item['episode']['r']}")
                self.writer.add_scalar("charts/episodic_return", item["episode"]["r"], global_step)
                self.writer.add_scalar("charts/episodic_length", item["episode"]["l"], global_step)
                average_reward_tracker.add(item["episode"]["r"])
                avg = average_reward_tracker.get_average()
                if avg > self.best_reward:
                    self.best_reward = avg
                    self.save_agent(ckpt_path, save_2_wandb=save_2_wandb)
                break
    def train(self, learning_rate=2.5e-4, num_steps=128,
              num_envs=4, seed=42, capture_video=True,
              capture_every_n_video=50, run_name="PPO_run_name",
              total_timesteps=1000000, anneal_lr=True, gae=True,
              discount_gamma=0.99, gae_lambda=0.95, update_epochs=4,
              minibatches=4, norm_adv=True, clip_coef=0.2, clip_vloss=True,
              ent_coef=0.01, vf_coef=0.5,max_grad_norm=0.5, average_reward_2_save=20,
              verbose=True, ckpt_path="./models/model.pt",
              save_2_wandb=False, config=None):

        self.run_name = run_name
        self.envs = gym.vector.SyncVectorEnv(
            [self.make_env(seed + i, i, capture_video, capture_every_n_video, self.run_name)
             for i in
             range(num_envs)])

        self.writer = SummaryWriter(f"runs/{self.run_name}")
        self.writer.add_text("hyperparameters",
                             "|param|value|\n|-|-|\n%s" % (
                                 "\n".join([f"|{key}|{value}" for key, value in vars(config).items()])))
        batch_size = num_steps * num_envs

        average_reward_tracker = AverageRewardTracker(average_reward_2_save)
        self.best_reward = -np.inf
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate, eps=1e-5)
        obs = torch.zeros((num_steps, num_envs) + self.envs.single_observation_space.shape).to(
            self.device)
        actions = torch.zeros((num_steps, num_envs) + self.envs.single_action_space.shape).to(
            self.device)
        logprobs = torch.zeros((num_steps, num_envs)).to(self.device)
        rewards = torch.zeros((num_steps, num_envs)).to(self.device)
        dones = torch.zeros((num_steps, num_envs)).to(self.device)
        values = torch.zeros((num_steps, num_envs)).to(self.device)

        global_step = 0
        start_time = time.time()
        next_obs = torch.Tensor(self.envs.reset()).to(self.device)
        next_done = torch.zeros(num_envs).to(self.device)
        num_updates = total_timesteps // batch_size

        for update in range(1, num_updates + 1):
            if anneal_lr:
                frac = 1.0 - (update - 1) / num_updates
                lrnow = frac * learning_rate
                optimizer.param_groups[0]["lr"] = lrnow
            for step in range(0, num_steps):
                global_step += 1 * num_envs
                obs[step] = next_obs
                dones[step] = next_done

                with torch.no_grad():
                    action, logprob, entropy, value = self.get_action_and_value(next_obs)
                    values[step] = value.flatten()
                    actions[step] = action
                    logprobs[step] = logprob

                next_obs, reward, done, info = self.envs.step(action.cpu().numpy())

                rewards[step] = torch.tensor(reward).to(self.device).view(-1)
                next_obs, next_done = torch.Tensor(next_obs).to(self.device), torch.Tensor(done).to(self.device)
                self.track_info(info, average_reward_tracker, save_2_wandb, verbose, global_step, ckpt_path)

            with torch.no_grad():
                next_value = self.get_value(next_obs).reshape(1, -1)

                if gae:
                    advantages = torch.zeros_like(rewards).to(self.device)
                    lastgaelam = 0
                    for t in reversed(range(num_steps)):
                        if t == num_steps - 1:
                            nextnonterminal = 1.0 - next_done
                            nextvalues = next_value
                        else:
                            nextnonterminal = 1.0 - dones[t + 1]
                            nextvalues = values[t + 1]
                        delta = rewards[t] + discount_gamma * nextvalues * nextnonterminal - values[t]
                        advantages[
                            t] = lastgaelam = delta + discount_gamma * gae_lambda * nextnonterminal * lastgaelam
                    returns = advantages + values

                else:
                    returns = torch.zeros_like(rewards).to(self.device)
                    for t in reversed(range(num_steps)):
                        if t == num_steps - 1:
                            nextnonterminal = 1.0 - next_done
                            next_return = next_value
                        else:
                            nextnonterminal = 1.0 - dones[t + 1]
                            next_return = returns[t + 1]
                        returns[t] = rewards[t] + discount_gamma * nextnonterminal * next_return
                    advantages = returns - values

            # flatten the batch
            b_obs = obs.reshape((-1,) + self.envs.single_observation_space.shape)
            b_logprobs = logprobs.reshape(-1)
            b_actions = actions.reshape((-1,) + self.envs.single_action_space.shape)
            b_advantages = advantages.reshape(-1)
            b_returns = returns.reshape(-1)
            b_values = values.reshape(-1)

            b_inds = np.arange(batch_size)
            minibatch_size = batch_size // minibatches
            for epoch in range(update_epochs):
                np.random.shuffle(b_inds)
                for start in range(0, batch_size, minibatch_size):
                    end = start + minibatch_size

                    mb_inds = b_inds[start: end]

                    _, newlogprob, entropy, newvalue = self.get_action_and_value(b_obs[mb_inds],
                                                                                 b_actions[mb_inds])

                    log_ratio = newlogprob - b_logprobs[mb_inds]
                    ratio = log_ratio.exp()

                    mb_advantages = b_advantages[mb_inds]
                    if norm_adv:
                        mb_advantages = (mb_advantages - mb_advantages.mean()) / (mb_advantages.std() + 1e-8)

                    pg_loss1 = - mb_advantages * ratio
                    pg_loss2 = -mb_advantages * torch.clip(ratio, 1 - clip_coef, 1 + clip_coef)
                    pg_loss = torch.max(pg_loss1, pg_loss2).mean()

                    newvalue = newvalue.view(-1)
                    if clip_vloss:
                        v_loss_unclipped = (newvalue - b_returns[mb_inds]) ** 2
                        v_clipped = b_values[mb_inds] + torch.clamp(newvalue - b_returns[mb_inds],
                                                                    -clip_coef,
                                                                    clip_coef)
                        v_loss_clipped = (v_clipped - b_returns[mb_inds]) ** 2
                        v_loss_max = torch.max(v_loss_unclipped, v_loss_clipped)
                        v_loss = 0.5 * v_loss_max.mean()

                    else:
                        v_loss = 0.5 * ((newvalue - b_returns[mb_inds]) ** 2).mean()
                    entropy_loss = entropy.mean()

                    loss = pg_loss - ent_coef * entropy_loss + v_loss * vf_coef
                    optimizer.zero_grad()
                    loss.backward()
                    nn.utils.clip_grad_norm_(self.model.parameters(), max_grad_norm)
                    optimizer.step()

            y_pred, y_true = b_values.cpu().numpy(), b_returns.cpu().numpy()
            var_y = np.var(y_true)
            explained_var = np.nan if var_y == 0 else 1 - np.var(y_true - y_pred) / var_y

            self.writer.add_scalar("charts/learning_rate", optimizer.param_groups[0]["lr"], global_step)
            self.writer.add_scalar("losses/value_loss", v_loss.item(), global_step)
            self.writer.add_scalar("losses/policy_loss", pg_loss.item(), global_step)
            self.writer.add_scalar("losses/entropy_loss", entropy_loss.item(), global_step)
            self.writer.add_scalar("losses/explained_variance", explained_var, global_step)
            self.writer.add_scalar("charts/SPS", int(global_step / (time.time() - start_time)), global_step)
        self.writer.add_scalar("best_avg_reward", self.best_reward)
        self.writer.add_scalar("length_avg_reward", average_reward_2_save)
        self.envs.close()
        self.writer.close()
