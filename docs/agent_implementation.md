# Agent Implementation

## Overview

This project implements two reinforcement learning agents for the Orbital Defender environment:
1. **DQN (Deep Q-Network)** - Value-based method
2. **A2C (Advantage Actor-Critic)** - Policy-based method

This document focuses on the **DQN agent** as it is the primary agent used in training and evaluation.

---

## DQN Agent Architecture

### Network Architecture

The DQN agent uses a **Deep Q-Network** to approximate the Q-function `Q(s, a)`, which estimates the expected return for taking action `a` in state `s`.

#### Network Structure

```
Input (7) → FC1 (256) → ReLU → Dropout (0.1)
         → FC2 (256) → ReLU → Dropout (0.1)
         → FC3 (128) → ReLU
         → FC4 (3) → Output (Q-values for each action)
```

**Layer Details:**
- **Input Layer:** 7 neurons (state dimension)
- **Hidden Layer 1:** 256 neurons with ReLU activation
- **Dropout:** 0.1 (regularization)
- **Hidden Layer 2:** 256 neurons with ReLU activation
- **Dropout:** 0.1 (regularization)
- **Hidden Layer 3:** 128 neurons with ReLU activation
- **Output Layer:** 3 neurons (one Q-value per action)

**Design Rationale:**
- **Deep Network:** 3 hidden layers provide sufficient capacity for complex Q-function approximation
- **Dropout:** Prevents overfitting during training
- **ReLU Activation:** Non-linear activation for learning complex patterns
- **Progressive Sizing:** 256 → 256 → 128 reduces dimensionality gradually

### Double DQN

The implementation uses **Double DQN** to reduce overestimation bias:

- **Main Network:** Selects the best action
- **Target Network:** Evaluates the selected action

This decoupling prevents the agent from overestimating Q-values, leading to more stable learning.

---

## Key Components

### 1. Experience Replay Buffer

**Purpose:** Store and sample past experiences for training

**Implementation:**
```python
class ReplayBuffer:
    def __init__(self, capacity=10000):
        self.buffer = deque(maxlen=capacity)
```

**Features:**
- **Fixed Capacity:** 10,000-100,000 experiences (configurable)
- **Uniform Sampling:** Random sampling breaks correlation between consecutive experiences
- **FIFO:** Oldest experiences are automatically removed when buffer is full

**Benefits:**
- **Data Efficiency:** Reuse past experiences
- **Stability:** Breaks temporal correlation
- **Diversity:** Sample from wide range of experiences

### 2. Target Network

**Purpose:** Provide stable Q-value targets during training

**Implementation:**
- Separate network with identical architecture
- Updated periodically (every 5-10 episodes) from main network
- Used only for computing target Q-values (not trained)

**Benefits:**
- **Stability:** Prevents moving target problem
- **Convergence:** More stable learning updates

### 3. Epsilon-Greedy Exploration

**Purpose:** Balance exploration and exploitation

**Strategy:**
- **Exploration:** Random action with probability `ε`
- **Exploitation:** Greedy action (max Q-value) with probability `1-ε`

**Epsilon Decay:**
```
ε(t) = max(ε_end, ε_start * decay^t)
```

**Parameters:**
- **ε_start:** 1.0 (100% exploration initially)
- **ε_end:** 0.05-0.01 (5-1% exploration at end)
- **ε_decay:** 0.9998 (slow decay for extended exploration)

**Design Rationale:**
- Start with full exploration to discover environment
- Gradually shift to exploitation as agent learns
- Maintain small exploration to avoid getting stuck

---

## Training Process

### 1. Action Selection

```python
def select_action(self, state, training=True):
    if training and random.random() < self.epsilon:
        return random.randrange(self.action_dim)  # Explore
    
    with torch.no_grad():
        q_values = self.q_network(state)
        return q_values.argmax().item()  # Exploit
```

### 2. Experience Storage

After each step:
```python
agent.remember(state, action, reward, next_state, done)
```

Stores experience tuple `(s, a, r, s', done)` in replay buffer.

### 3. Training Step

**Process:**
1. **Sample Batch:** Randomly sample `batch_size` experiences from buffer
2. **Compute Current Q-values:** `Q(s, a)` using main network
3. **Compute Target Q-values:** 
   - Double DQN: `r + γ * Q_target(s', argmax(Q_main(s')))`
   - Standard DQN: `r + γ * max(Q_target(s'))`
4. **Compute Loss:** Mean Squared Error between current and target
5. **Backpropagation:** Update main network weights
6. **Epsilon Decay:** Reduce exploration rate

**Loss Function:**
```
L = MSE(Q(s, a), r + γ * Q_target(s', a'))
```

**Optimizer:** Adam with learning rate 0.001 (optimized from 0.0005)

### 4. Target Network Update

Updated every 5 episodes (configurable):
```python
def update_target_network(self):
    self.target_network.load_state_dict(self.q_network.state_dict())
```

---

## Hyperparameters

### Optimized Hyperparameters (Current)

| Parameter | Value | Description |
|-----------|-------|-------------|
| Learning Rate | 0.001 | Optimizer step size (increased from 0.0005) |
| Gamma (γ) | 0.99 | Discount factor for future rewards |
| Epsilon Start | 1.0 | Initial exploration rate |
| Epsilon End | 0.05 | Final exploration rate |
| Epsilon Decay | 0.9998 | Decay rate per step |
| Batch Size | 64 | Training batch size (reduced from 128) |
| Memory Size | 50,000 | Replay buffer capacity |
| Target Update Freq | 5 | Episodes between target network updates |
| Double DQN | True | Use Double DQN algorithm |

### Hyperparameter Rationale

#### Learning Rate (0.001)
- **Increased from 0.0005** for faster learning
- Still stable enough to avoid divergence
- Allows agent to adapt quickly to environment changes

#### Batch Size (64)
- **Reduced from 128** for more frequent updates
- Smaller batches provide more gradient updates per episode
- Better for faster learning

#### Epsilon Decay (0.9998)
- **Faster decay** than initial 0.9995
- Reaches ε_end around episode 1500
- Balances exploration and exploitation

#### Memory Size (50,000)
- Sufficient for diverse experience storage
- Not too large to avoid stale experiences
- Balanced between diversity and recency

---

## Training Strategy

### Training Frequency

**Multiple Updates Per Step:**
- Train 4 times per environment step
- Provides more learning opportunities
- Faster convergence

**Condition:**
```python
if len(agent.memory) > agent.batch_size:
    for _ in range(4):  # Train 4 times
        loss = agent.train_step()
```

### Adaptive Epsilon Decay

**Performance-Based Decay:**
```python
if episode > 100:
    recent_avg = np.mean(episode_rewards[-50:])
    if recent_avg > 10:
        agent.epsilon *= 0.9999  # Faster decay if doing well
```

**Rationale:** Decay exploration faster when agent is performing well.

### Learning Rate Scheduling

**Gradual Reduction:**
```python
if episode > 500 and episode % 500 == 0:
    new_lr = initial_lr * (0.95 ** (episode // 500))
```

**Purpose:** Reduce learning rate over time for fine-tuning.

---

## Algorithm: Double DQN

### Standard DQN Update

```
Q(s, a) ← Q(s, a) + α[r + γ * max Q_target(s', a') - Q(s, a)]
```

**Problem:** Overestimates Q-values due to max operator.

### Double DQN Update

```
a* = argmax Q_main(s', a')
Q(s, a) ← Q(s, a) + α[r + γ * Q_target(s', a*) - Q(s, a)]
```

**Solution:** Use main network to select action, target network to evaluate.

**Benefits:**
- Reduces overestimation bias
- More stable learning
- Better final performance

---

## Network Architecture Details

### Forward Pass

```python
def forward(self, x):
    x = self.relu(self.fc1(x))      # 7 → 256
    x = self.dropout(x)              # Regularization
    x = self.relu(self.fc2(x))       # 256 → 256
    x = self.dropout(x)              # Regularization
    x = self.relu(self.fc3(x))       # 256 → 128
    return self.fc4(x)               # 128 → 3
```

### Activation Functions

- **ReLU:** `f(x) = max(0, x)`
  - Non-linear activation
  - Prevents vanishing gradients
  - Computationally efficient

- **Linear (Output):** No activation
  - Q-values can be any real number
  - Represents expected return

### Regularization

- **Dropout (0.1):** Randomly zero 10% of activations
  - Prevents overfitting
  - Forces network to learn robust features

---

## Model Persistence

### Saving

```python
torch.save({
    'q_network': self.q_network.state_dict(),
    'target_network': self.target_network.state_dict(),
    'optimizer': self.optimizer.state_dict(),
    'epsilon': self.epsilon,
}, filepath)
```

**Saves:**
- Network weights
- Optimizer state
- Current epsilon value

### Loading

```python
checkpoint = torch.load(filepath)
self.q_network.load_state_dict(checkpoint['q_network'])
self.target_network.load_state_dict(checkpoint['target_network'])
self.optimizer.load_state_dict(checkpoint['optimizer'])
self.epsilon = checkpoint['epsilon']
```

**Enables:**
- Resuming training from checkpoints
- Loading best models for evaluation
- Transfer learning

---

## Training Workflow

### Complete Training Loop

```python
for episode in range(episodes):
    state, _ = env.reset()
    
    for step in range(max_steps):
        # 1. Select action
        action = agent.select_action(state, training=True)
        
        # 2. Take step
        next_state, reward, done, _, _ = env.step(action)
        
        # 3. Store experience
        agent.remember(state, action, reward, next_state, done)
        
        # 4. Train (multiple times)
        if len(agent.memory) > batch_size:
            for _ in range(4):
                loss = agent.train_step()
        
        state = next_state
        if done:
            break
    
    # 5. Update target network
    if episode % target_update_freq == 0:
        agent.update_target_network()
```

### Training Metrics Tracked

- **Episode Rewards:** Total reward per episode
- **Episode Lengths:** Steps per episode
- **Training Loss:** Q-value prediction error
- **Asteroids Destroyed:** Success metric
- **Epsilon Value:** Exploration rate

---

## Evaluation Mode

### Action Selection

```python
def select_action(self, state, training=False):
    if training:
        # Epsilon-greedy (exploration)
        if random.random() < self.epsilon:
            return random.randrange(self.action_dim)
    
    # Greedy (exploitation only)
    with torch.no_grad():
        q_values = self.q_network(state)
        return q_values.argmax().item()
```

**Evaluation Settings:**
- `epsilon = 0.0` (no exploration)
- Greedy action selection only
- Deterministic behavior

---

## Implementation Optimizations

### 1. GPU Support

```python
device = 'cuda' if torch.cuda.is_available() else 'cpu'
agent = DQNAgent(..., device=device)
```

**Benefits:**
- Faster training on GPU
- Automatic CPU fallback

### 2. Gradient Clipping (Optional)

Can be added for stability:
```python
torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), max_norm=1.0)
```

### 3. Efficient Tensor Operations

- Batch processing for Q-value computation
- In-place operations where possible
- Gradient computation only when needed

---

## Comparison: DQN vs A2C

### DQN (Implemented)

**Type:** Value-based
**Method:** Learn Q-function, derive policy
**Advantages:**
- Sample efficient (experience replay)
- Stable learning
- Good for discrete actions

**Disadvantages:**
- Requires discrete action space
- Can overestimate Q-values (mitigated by Double DQN)

### A2C (Also Implemented)

**Type:** Policy-based
**Method:** Learn policy directly
**Advantages:**
- Can handle continuous actions
- Direct policy optimization
- Lower variance with advantage

**Disadvantages:**
- Less sample efficient
- More hyperparameters to tune

**Note:** A2C is implemented but DQN is the primary agent used.

---

## Code Structure

```
agents/
├── __init__.py
├── dqn_agent.py          # DQN implementation
│   ├── DQN (nn.Module)   # Neural network
│   ├── ReplayBuffer      # Experience buffer
│   └── DQNAgent          # Main agent class
└── a2c_agent.py          # A2C implementation (optional)
```

---

## Usage Example

### Creating Agent

```python
from agents.dqn_agent import DQNAgent

agent = DQNAgent(
    state_dim=7,
    action_dim=3,
    lr=0.001,
    gamma=0.99,
    epsilon_start=1.0,
    epsilon_end=0.05,
    epsilon_decay=0.9998,
    batch_size=64,
    memory_size=50000,
    device='cuda',
    use_double_dqn=True
)
```

### Training

```python
state, _ = env.reset()
action = agent.select_action(state, training=True)
next_state, reward, done, _, _ = env.step(action)
agent.remember(state, action, reward, next_state, done)
loss = agent.train_step()
```

### Evaluation

```python
agent.epsilon = 0.0  # No exploration
action = agent.select_action(state, training=False)
```

### Saving/Loading

```python
agent.save('models/dqn_model.pth')
agent.load('models/dqn_model.pth')
```

---

## Performance Characteristics

### Training Time

- **CPU:** ~2-4 hours for 3000 episodes
- **GPU:** ~1-2 hours for 3000 episodes
- **Per Episode:** ~2-5 seconds

### Memory Usage

- **Replay Buffer:** ~50,000 experiences × ~100 bytes ≈ 5 MB
- **Networks:** 2 × ~500 KB ≈ 1 MB
- **Total:** ~6-10 MB

### Convergence

- **Initial Learning:** Episodes 0-500 (exploration phase)
- **Rapid Improvement:** Episodes 500-1500
- **Fine-tuning:** Episodes 1500-3000+
- **Stable Performance:** After episode 2000+

---

## Design Decisions

### 1. Double DQN Over Standard DQN

**Decision:** Use Double DQN
**Rationale:** Reduces overestimation bias, more stable learning

### 2. Experience Replay

**Decision:** Use replay buffer with uniform sampling
**Rationale:** Breaks temporal correlation, improves sample efficiency

### 3. Target Network

**Decision:** Update every 5 episodes
**Rationale:** Balance between stability and adaptability

### 4. Multiple Training Steps

**Decision:** Train 4 times per environment step
**Rationale:** Faster learning, better sample efficiency

### 5. Adaptive Epsilon

**Decision:** Performance-based epsilon decay
**Rationale:** Faster convergence when agent is learning well

---

## Future Improvements

### Potential Enhancements

1. **Prioritized Experience Replay**
   - Sample important experiences more frequently
   - Faster learning from critical moments

2. **Dueling DQN**
   - Separate value and advantage streams
   - Better value estimation

3. **Rainbow DQN**
   - Combine multiple DQN improvements
   - State-of-the-art performance

4. **Curriculum Learning**
   - Start with easier scenarios
   - Gradually increase difficulty

---

## References

- **DQN Paper:** Mnih et al., "Human-level control through deep reinforcement learning" (2015)
- **Double DQN Paper:** van Hasselt et al., "Deep Reinforcement Learning with Double Q-learning" (2016)
- **Implementation:** `agents/dqn_agent.py`
- **Training:** `training/train_dqn.py`

---

## Summary

The DQN agent implementation uses:
- **Deep neural network** (256-256-128) for Q-function approximation
- **Double DQN** for stable learning
- **Experience replay** for sample efficiency
- **Target network** for stable targets
- **Epsilon-greedy** exploration
- **Optimized hyperparameters** for best performance

The agent successfully learns to defend the planet by destroying asteroids while avoiding impacts.

