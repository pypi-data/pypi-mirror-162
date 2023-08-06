import os
import random
from abc import ABC, abstractmethod
import time
import gym
import torch
import torch.nn
from maslourl.trackers.average_tracker import AverageRewardTracker
from maslourl.models.replay_buffer import ReplayBuffer
import numpy as np
from torch.utils.tensorboard import SummaryWriter


class DDQDiscrete(ABC):
    def __init__(self, cuda=True, seed=1, torch_deterministic=True):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.backends.cudnn.deterministic = torch_deterministic
        self.device = torch.device("cuda" if torch.cuda.is_available() and cuda else "cpu")

        self.env = self.build_env(seed, False, 0)
        self.input_shape = self.env.observation_space.shape
        self.n_actions = self.env.action_space.n
        self.action_space = [i for i in range(self.n_actions)]

        self.memory = None
        self.Q_eval = self.build_model().to(self.device)
        self.Q_target = self.build_model().to(self.device)
        self.update_target_model()
        self.epsilon = 0

    @abstractmethod
    def build_env(self, seed, capture_video, capture_every_n_video) -> gym.Env:
        pass

    def train(self, episodes, max_steps_for_episode=1000,
              starting_epsilon=1, epsilon_min=0.01, epsilon_decay=0.01,
              target_network_replace_frequency_steps=1000,
              training_batch_size=128, discount_factor=0.99,
              episodes_for_average_tracking=100, replay_buffer_size=100000,
              learning_rate=1e-3, run_name="ddqn_run_name", verbose=True,
              save_2_wandb=False, capture_video=False, capture_every_n_video=20, config=None):

        self.memory = ReplayBuffer(replay_buffer_size, input_shape=self.input_shape, n_actions=self.n_actions)
        self.Q_eval.optimizer = torch.optim.Adam(self.Q_eval.parameters(), lr=learning_rate)
        self.Q_eval.loss = torch.nn.MSELoss()
        average_tracker = AverageRewardTracker(episodes_for_average_tracking)
        self.epsilon = starting_epsilon
        self.target_network_replace_frequency_steps = target_network_replace_frequency_steps
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.run_name = run_name
        self.writer = SummaryWriter(f"runs/{self.run_name}")
        if config is not None:
            self.writer.add_text("hyperparameters",
                                 "|param|value|\n|-|-|\n%s" % (
                                     "\n".join([f"|{key}|{value}" for key, value in vars(config).items()])))
        self.env = self.build_env(self.seed, capture_video=capture_video, capture_every_n_video=capture_every_n_video)
        global_step = 0
        best_reward = -np.inf
        for episode in range(episodes):
            episode_reward = 0
            state = self.env.reset()
            episode_start_time = time.time()
            for step in range(max_steps_for_episode):
                global_step += 1
                action = self.choose_action(state)
                new_state, reward, done, info = self.env.step(action)
                episode_reward += reward
                self.remember(state, action, reward, new_state, done)
                state = new_state
                self.learn(training_batch_size, discount_factor)
                if done:
                    break
            average_tracker.add(episode_reward)
            average = average_tracker.get_average()
            if average > best_reward:
                best_reward = average
                self.save_agent("./models/best_model.pt", save_2_wandb)
            if verbose:
                print(
                    f"episode {episode} finished in {step + 1} steps with reward {episode_reward:.2f}. "
                    f"Average reward over last {episodes_for_average_tracking}: {average:.2f} "
                    f"And took: {(time.time() - episode_start_time):.2f} seconds. "
                    f"Eps: {self.epsilon}")
            self.writer.add_scalar("charts/episodic_return", episode_reward, global_step)
            self.writer.add_scalar("charts/episodic_length", step + 1, global_step)
            self.writer.add_scalar("charts/epsilon", self.epsilon, global_step)
        self.writer.add_scalar("best_avg_reward", best_reward)
        self.writer.add_scalar("length_avg_reward", episodes_for_average_tracking)
        self.epsilon = 0

    def remember(self, state, action, reward, state_, done):
        self.memory.store_transition(state, action, reward, state_, done)

    def choose_action(self, observation):
        if np.random.random() > self.epsilon:
            state = torch.tensor([observation], dtype=torch.float).to(self.device)
            advantage = self.Q_eval.forward(state)
            action = torch.argmax(advantage).item()
        else:
            action = np.random.choice(self.action_space)
        return action

    def learn(self, batch_size, discount_factor):
        if self.memory.mem_cntr < batch_size:
            return

        self.Q_eval.optimizer.zero_grad()
        state, action, reward, new_state, done = self.memory.sample_buffer(batch_size)

        states = torch.tensor(state, dtype=torch.float32).to(self.device)
        rewards = torch.tensor(reward, dtype=torch.float32).to(self.device)
        dones = torch.tensor(done, dtype=torch.bool).to(self.device)
        actions = torch.tensor(action, dtype=torch.long).to(self.device)
        states_ = torch.tensor(new_state, dtype=torch.float32).to(self.device)

        indices = np.arange(batch_size)

        q_pred = self.Q_eval(states)[indices, actions]
        q_next = self.Q_target(states_)
        q_eval = self.Q_eval(states_)
        max_actions = torch.argmax(q_eval, dim=1)

        q_next[dones] = 0.0
        q_target = rewards + discount_factor * q_next[indices, max_actions]

        loss = self.Q_eval.loss(q_target, q_pred).to(self.device)
        loss.backward()
        self.Q_eval.optimizer.step()

        self.epsilon = self.epsilon - self.epsilon_decay if self.epsilon > self.epsilon_min else self.epsilon_min

        if self.memory.mem_cntr % self.target_network_replace_frequency_steps == 0:
            self.update_target_model()

    def update_target_model(self):
        self.Q_target.load_state_dict(self.Q_eval.state_dict())

    def load_agent(self, model_file):
        path = model_file.split(".")
        path_without_ext = ".".join(path[:-1])
        self.Q_eval = torch.load(path_without_ext + "." + path[-1]).to(self.device)
        self.Q_eval.eval()

    @abstractmethod
    def build_model(self) -> torch.nn.Module:
        raise NotImplementedError("build model must be implemented in child")

    def save_agent(self, path, save_2_wandb=False):
        dir_name = "/".join(path.split("/")[:-1])
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        torch.save(self.Q_eval, path)
        if save_2_wandb:
            import wandb
            if not os.path.exists(os.path.join(wandb.run.dir, "models/")):
                os.makedirs(os.path.join(wandb.run.dir, "models/"))
            torch.save(self.Q_eval, os.path.join(wandb.run.dir, "models/model.pt"))