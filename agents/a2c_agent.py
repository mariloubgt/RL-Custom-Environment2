import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np

class ActorCritic(nn.Module):
    """Enhanced Actor-Critic network for A2C"""
    def __init__(self, state_dim, action_dim, hidden_dim=256):
        super(ActorCritic, self).__init__()
        
        # Larger shared layers
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, hidden_dim // 2)
        
        # Actor head (policy)
        self.actor = nn.Linear(hidden_dim // 2, action_dim)
        
        # Critic head (value)
        self.critic = nn.Linear(hidden_dim // 2, 1)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        
        # Policy distribution
        policy_logits = self.actor(x)
        policy = F.softmax(policy_logits, dim=-1)
        
        # State value
        value = self.critic(x)
        
        return policy, value
    
    def get_action_and_value(self, state, action=None):
        """Get action from policy and value estimate"""
        policy, value = self.forward(state)
        
        # Sample action from policy
        dist = torch.distributions.Categorical(policy)
        if action is None:
            action = dist.sample()
        
        action_log_prob = dist.log_prob(action)
        entropy = dist.entropy()
        
        return action, action_log_prob, entropy, value

class A2CAgent:
    """A2C (Advantage Actor-Critic) Agent implementation"""
    def __init__(
        self,
        state_dim,
        action_dim,
        lr=0.0003,
        gamma=0.99,
        value_coef=0.5,
        entropy_coef=0.02,
        device='cpu'
    ):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef
        self.device = device
        
        # Network
        self.network = ActorCritic(state_dim, action_dim).to(device)
        self.optimizer = optim.Adam(self.network.parameters(), lr=lr)
        
        # Storage for episode data
        self.reset_episode()
    
    def reset_episode(self):
        """Reset episode storage"""
        self.states = []
        self.actions = []
        self.rewards = []
        self.log_probs = []
        self.values = []
        self.entropies = []
        self.dones = []
    
    def select_action(self, state, training=True):
        """Select action using the policy network"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad() if not training else torch.enable_grad():
            action, log_prob, entropy, value = self.network.get_action_and_value(state_tensor)
        
        if training:
            self.states.append(state)
            self.actions.append(action.item())
            self.log_probs.append(log_prob)
            self.values.append(value.squeeze())
            self.entropies.append(entropy)
        
        return action.item()
    
    def store_transition(self, reward, done):
        """Store reward and done flag"""
        self.rewards.append(reward)
        self.dones.append(done)
    
    def compute_returns(self, next_value=0):
        """Compute discounted returns"""
        returns = []
        G = next_value
        for reward, done in zip(reversed(self.rewards), reversed(self.dones)):
            if done:
                G = reward
            else:
                G = reward + self.gamma * G
            returns.insert(0, G)
        return torch.tensor(returns, dtype=torch.float32).to(self.device)
    
    def train_step(self):
        """Perform one training step on collected episode data"""
        if len(self.rewards) == 0:
            return None
        
        # Convert to tensors
        states = torch.FloatTensor(np.array(self.states)).to(self.device)
        actions = torch.LongTensor(self.actions).to(self.device)
        log_probs = torch.stack(self.log_probs).to(self.device)
        values = torch.stack(self.values).squeeze().to(self.device)
        entropies = torch.stack(self.entropies).to(self.device)
        
        # Compute returns
        returns = self.compute_returns()
        
        # Compute advantages
        advantages = returns - values
        
        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        # Get current policy and values
        _, current_values = self.network(states)
        current_values = current_values.squeeze()
        
        # Policy loss (actor)
        policy_loss = -(log_probs * advantages.detach()).mean()
        
        # Value loss (critic)
        value_loss = F.mse_loss(current_values, returns)
        
        # Entropy bonus
        entropy_loss = -entropies.mean()
        
        # Total loss
        total_loss = policy_loss + self.value_coef * value_loss + self.entropy_coef * entropy_loss
        
        # Optimize
        self.optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.network.parameters(), 0.5)
        self.optimizer.step()
        
        # Reset episode storage
        self.reset_episode()
        
        return {
            'total_loss': total_loss.item(),
            'policy_loss': policy_loss.item(),
            'value_loss': value_loss.item(),
            'entropy': -entropy_loss.item()
        }
    
    def save(self, filepath):
        """Save the agent"""
        torch.save({
            'network': self.network.state_dict(),
            'optimizer': self.optimizer.state_dict(),
        }, filepath)
    
    def load(self, filepath):
        """Load the agent"""
        checkpoint = torch.load(filepath)
        self.network.load_state_dict(checkpoint['network'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])

