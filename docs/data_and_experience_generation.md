# Data and Experience Generation in Reinforcement Learning

## Overview

Unlike supervised learning projects that use pre-existing datasets (images, text, etc.), **reinforcement learning projects generate their own data** through interaction with the environment. This project follows that paradigm.

## No Traditional Dataset

**This project does NOT use a pre-existing dataset.**

Instead:
- **Data is generated dynamically** through agent-environment interaction
- **Experiences are collected** during training
- **The environment itself** serves as the data generator

## How Data is Generated

### 1. Environment Interaction

The agent interacts with the `OrbitalDefenderEnv` environment:

```python
state, _ = env.reset()           # Initial state
action = agent.select_action(state)
next_state, reward, done, _, _ = env.step(action)  # New data point
```

**Each step generates:**
- Current state (observation)
- Action taken
- Reward received
- Next state
- Done flag (episode termination)

### 2. Experience Tuple

Each interaction creates an **experience tuple**:

```
(s, a, r, s', done)
```

Where:
- **s**: Current state (7-dimensional vector)
- **a**: Action taken (0, 1, or 2)
- **r**: Reward received (scalar)
- **s'**: Next state (7-dimensional vector)
- **done**: Episode termination flag (boolean)

### 3. Experience Replay Buffer

For DQN, experiences are stored in a **replay buffer**:

```python
class ReplayBuffer:
    def __init__(self, capacity=50000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
```

**Characteristics:**
- **Capacity:** 50,000 experiences (configurable)
- **Storage:** In-memory deque (FIFO)
- **Sampling:** Random uniform sampling for training

## Data Generation Process

### Training Phase

1. **Episode Start:**
   ```python
   state = env.reset()  # Generate initial state
   ```

2. **Step-by-Step Interaction:**
   ```python
   for step in range(max_steps):
       action = agent.select_action(state)
       next_state, reward, done, _, _ = env.step(action)
       
       # Store experience
       agent.remember(state, action, reward, next_state, done)
       
       state = next_state
   ```

3. **Experience Collection:**
   - Each step generates one experience tuple
   - Stored in replay buffer
   - Used for training

### Data Volume

**Per Episode:**
- Average: ~100-150 steps
- Experiences generated: 100-150 tuples
- Data size: ~100-150 KB per episode

**Total Training (5000 episodes):**
- Total experiences: ~500,000-750,000
- Replay buffer: Stores last 50,000
- Total data generated: ~50-75 MB

## State Space (Input Data)

### Observation Vector

Each state is a **7-dimensional vector**:

```python
[
  turret_angle,                    # [-π, π]
  asteroid1_angle,                 # [-π, π]
  asteroid1_distance,              # [0, 10]
  asteroid1_angular_velocity,       # [-1, 1]
  asteroid2_angle,                 # [-π, π]
  asteroid2_distance,              # [0, 10]
  asteroid2_angular_velocity        # [-1, 1]
]
```

**Data Type:** `numpy.ndarray`, `dtype=np.float32`

**Size:** 7 floats × 4 bytes = 28 bytes per state

## Action Space (Output Data)

### Discrete Actions

**3 possible actions:**
- `0`: Rotate left
- `1`: Rotate right
- `2`: Fire

**Data Type:** Integer (0, 1, or 2)

## Reward Signal (Training Signal)

### Reward Range

- **Positive rewards:** 0 to ~150 (hits, completions)
- **Negative rewards:** -500 (planet impact)
- **Typical range:** -500 to +150 per episode

**Data Type:** Float

## Data Flow

```
Environment
    ↓
[State] → Agent → [Action]
    ↓                    ↓
[Reward, Next State] ← Environment
    ↓
Experience Buffer
    ↓
Training Batch (64 samples)
    ↓
Neural Network Update
```

## Comparison: RL vs Supervised Learning

| Aspect | Supervised Learning | This RL Project |
|--------|-------------------|-----------------|
| **Dataset** | Pre-existing (images, text, etc.) | Generated during training |
| **Data Source** | External files/databases | Environment interaction |
| **Data Size** | Fixed, known in advance | Dynamic, grows during training |
| **Labels** | Provided in dataset | Rewards from environment |
| **Data Collection** | One-time, before training | Continuous, during training |
| **Storage** | Files/databases | In-memory replay buffer |

## Experience Replay Buffer Details

### Storage

```python
# DQN Agent
self.memory = ReplayBuffer(capacity=50000)
```

**Structure:**
- **Type:** `collections.deque`
- **Capacity:** 50,000 experiences
- **Memory:** ~5-10 MB
- **Access:** O(1) append, O(1) random sample

### Sampling

```python
def sample(self, batch_size):
    batch = random.sample(self.buffer, batch_size)
    return states, actions, rewards, next_states, dones
```

**Process:**
- Random uniform sampling
- Batch size: 64 experiences
- Used for each training step

## Data Characteristics

### State Distribution

- **Turret angle:** Uniform distribution (exploration)
- **Asteroid positions:** Random initialization each episode
- **Asteroid velocities:** Random uniform [-0.2, 0.2]

### Reward Distribution

- **Sparse rewards:** Most steps have small rewards
- **Large spikes:** Hit rewards (30-80), impact penalties (-500)
- **Completion bonuses:** +50 for perfect clear

### Episode Length Distribution

- **Typical:** 100-150 steps
- **Early termination:** Impact (short episodes)
- **Maximum:** 300 steps (timeout)

## Data Augmentation (Not Used)

Unlike supervised learning, this project does **NOT** use:
- Data augmentation
- Synthetic data generation
- Pre-processing pipelines
- Data normalization (states are already normalized)

**Why?** RL learns directly from environment interaction, which naturally provides diverse experiences.

## Data Persistence

### Saved Data

**Model Checkpoints:**
```python
torch.save({
    'q_network': ...,
    'target_network': ...,
    'optimizer': ...,
    'epsilon': ...
}, 'models/dqn_model.pth')
```

**Training Progress:**
```python
{
    'episode_rewards': [...],
    'episode_lengths': [...],
    'asteroids_destroyed': [...],
    'evaluation_results': [...]
}
```

**NOT Saved:**
- Individual experiences (too large)
- Replay buffer contents (regenerated each training run)

## Summary

### Key Points

1. **No pre-existing dataset** - Data is generated through environment interaction
2. **Experience replay buffer** - Stores 50,000 recent experiences
3. **Dynamic generation** - New data created every training step
4. **State-action-reward tuples** - The "data points" in RL
5. **7-dimensional states** - Input to the neural network
6. **3 discrete actions** - Output from the agent
7. **Reward signal** - The "label" that guides learning

### Data Statistics

- **Experiences per episode:** ~100-150
- **Total experiences (5000 episodes):** ~500,000-750,000
- **Replay buffer size:** 50,000 experiences
- **State size:** 7 floats (28 bytes)
- **Experience size:** ~100 bytes
- **Total buffer memory:** ~5-10 MB

## Conclusion

This project uses **reinforcement learning**, which means:
- **No traditional dataset** is required
- **Data is generated** through agent-environment interaction
- **Experiences are collected** in a replay buffer
- **Training uses** randomly sampled batches from the buffer

The "dataset" is essentially the **stream of experiences** collected during training, stored temporarily in the replay buffer, and used to update the agent's policy.

