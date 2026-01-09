# Orbital Defender Environment Design

## Overview

**Orbital Defender** is a custom reinforcement learning environment where an agent controls a turret on a planet to defend against incoming asteroids. The agent must learn to rotate the turret, aim accurately, and fire projectiles to destroy asteroids before they impact the planet.

### Core Mechanics

- **Planet:** Fixed at the center with radius 2.0
- **Turret:** Rotates around the planet using angular position (θ)
- **Asteroids:** Approach the planet using angular motion
- **Physics:** Everything modeled using angular coordinates, not Cartesian

---

## Action Space

The agent has **3 discrete actions**:

| Action | ID | Description | Effect |
|--------|----|----|----|
| Rotate Left | 0 | Rotate turret counter-clockwise | `turret_angle -= 0.1` radians |
| Rotate Right | 1 | Rotate turret clockwise | `turret_angle += 0.1` radians |
| Fire | 2 | Fire projectile | Destroys asteroid if within range and angle tolerance |

**Action Space Type:** `gym.spaces.Discrete(3)`

---

## Observation Space

The observation space is a **fixed-size vector** containing information about the turret and the two closest asteroids.

### Observation Vector (7 values)

```
[
  turret_angle,                    # Current turret angle [-π, π]
  asteroid1_angle,                 # Angle of closest asteroid [-π, π]
  asteroid1_distance,               # Distance of closest asteroid [0, 10]
  asteroid1_angular_velocity,       # Angular velocity of closest asteroid [-1, 1]
  asteroid2_angle,                  # Angle of second closest asteroid [-π, π]
  asteroid2_distance,               # Distance of second closest asteroid [0, 10]
  asteroid2_angular_velocity        # Angular velocity of second closest asteroid [-1, 1]
]
```

**Observation Space Type:** `gym.spaces.Box(low=[-π, -π, 0, -1, -π, 0, -1], high=[π, π, 10, 1, π, 10, 1])`

### Design Rationale

- **Fixed-size:** Prevents variable-length states, improves learning stability
- **Two closest asteroids:** Forces agent to prioritize threats
- **Angular representation:** Matches the physics model (circular motion)

---

## Environment Dynamics

### Asteroid Initialization

At episode start, **5 asteroids** are created with:
- **Angle:** Random uniform distribution `[-π, π]`
- **Distance:** Random uniform distribution `[6.0, 10.0]` from planet center
- **Angular Velocity:** Random uniform distribution `[-0.2, 0.2]` radians per step

### Asteroid Movement

Each step, asteroids:
- **Rotate:** `angle += angular_velocity`
- **Approach:** `distance -= 0.02` (moves 0.02 units closer per step)

**Design Note:** The movement speed (0.02) was optimized through iteration to give the agent sufficient time to react while maintaining challenge.

### Turret Rotation

- **Rotation Speed:** 0.1 radians per action
- **Angle Wrapping:** Angles are normalized to `[-π, π]` range

### Firing Mechanics

A projectile hits an asteroid if:
- **Angle Difference:** `|turret_angle - asteroid_angle| < 0.3` radians (17.2° tolerance)
- **Distance:** `asteroid_distance < 9.0` units

**Design Rationale:** These values were tuned to balance difficulty - wide enough to be learnable, narrow enough to require skill.

---

## Reward Function

The reward function uses **comprehensive reward shaping** to guide the agent toward desired behaviors. Rewards are accumulated throughout the step.

### 1. Aiming and Positioning Rewards

#### Precise Aim Reward
- **Condition:** Angle difference < 0.15 radians
- **Reward:** `0.5 * (1.0 - normalized_angle_diff / 0.15)`
- **Purpose:** Encourage precise turret positioning

#### Good Aim Reward
- **Condition:** Angle difference < 0.3 radians
- **Reward:** `0.2 * (1.0 - (normalized_angle_diff - 0.15) / 0.15)`
- **Purpose:** Reward getting close to target

### 2. Urgency and Safety Rewards

#### Urgency Reward
- **Condition:** Closest asteroid distance < 5.0
- **Reward:** `2.0 * (5.0 - distance) / 3.0`
- **Additional:** +1.0 if also aiming at it (angle_diff < 0.25)
- **Purpose:** Strong signal for dangerous situations

#### Safety Reward
- **Safe Zone (distance > 5.0):** `+0.3 * (distance - 5.0) / 3.0`
- **Danger Zone (distance < 4.0):** `-0.5 * (4.0 - distance) / 2.0`
- **Purpose:** Encourage keeping asteroids at safe distance

### 3. Early Destruction Rewards

#### Early Tracking Bonus
- **Condition:** Closest asteroid distance > 7.0
- **Reward:** `0.5 * (distance - 7.0) / 3.0`
- **Purpose:** Encourage proactive defense

### 4. Survival and Progress Rewards

#### Survival Reward
- **Reward:** `+0.5` per step (when asteroids remain)
- **Purpose:** Strong positive signal for staying alive

#### Progress Reward
- **Reward:** `0.2 * (5 - remaining_asteroids)`
- **Purpose:** Reward for reducing asteroid count

### 5. Hit Rewards (Fire Action)

When an asteroid is successfully hit, the reward is calculated as:

#### Base Hit Reward
- **Base:** `30.0` points

#### Distance Bonus
- **Early Hit (distance > 6.0):** `25.0 * (9.0 - distance) / 3.0` (up to 25 points)
- **Late Hit (distance ≤ 6.0):** `10.0 * (distance - 3.0) / 3.0` (up to 10 points)
- **Purpose:** Encourage destroying asteroids early, before they get dangerous

#### Accuracy Bonus
- **Reward:** `5.0 * (1.0 - angle_diff / 0.3)`
- **Range:** 0-5 points
- **Purpose:** Reward precise aiming

#### Progressive Hit Bonus (Streak)
- **Reward:** `min(consecutive_hits * 2.0, 10.0)`
- **Maximum:** 10 points
- **Purpose:** Encourage consistent performance

#### Early Destruction Bonus
- **Distance > 8.5:** `+10.0` points
- **Distance > 7.5:** `+5.0` points
- **Purpose:** Extra incentive for proactive defense

**Total Hit Reward Range:** 30-80 points (depending on distance, accuracy, and streak)

### 6. Episode Completion Bonuses

#### Perfect Clear Bonus
- **Condition:** All asteroids destroyed
- **Reward:** `+50.0` points
- **Purpose:** Strong incentive for complete success

#### Efficiency Bonus
- **Reward:** `max(0, 10.0 - steps * 0.05)`
- **Purpose:** Encourage quick completion

### 7. Penalties

#### Planet Impact Penalty
- **Penalty:** `-500.0` points
- **Condition:** Any asteroid reaches planet (distance ≤ 2.0)
- **Purpose:** Very strong negative signal to prevent impacts
- **Note:** Episode terminates immediately

#### Miss Penalty
- **Penalty:** `-0.3` points
- **Condition:** Fire action with no hit
- **Purpose:** Mild discouragement of random firing

#### Timeout Penalty
- **Penalty:** `-5.0` points
- **Condition:** Episode reaches 300 steps with asteroids remaining
- **Purpose:** Encourage efficiency

---

## Episode Termination

An episode terminates when:

1. **Planet Impact:** Any asteroid reaches the planet (distance ≤ 2.0)
   - **Reward:** -500.0
   - **Status:** Terminated (failure)

2. **Perfect Clear:** All asteroids destroyed
   - **Reward:** +50.0 (completion bonus) + efficiency bonus
   - **Status:** Terminated (success)

3. **Maximum Steps:** Episode reaches 300 steps
   - **Reward:** -5.0 (if asteroids remain)
   - **Status:** Terminated (timeout)

---

## Design Decisions and Rationale

### 1. Fixed-Size Observation Space
- **Decision:** Only observe 2 closest asteroids
- **Rationale:** Prevents variable-length states, improves learning stability, forces prioritization

### 2. Angular Physics Model
- **Decision:** Use angular coordinates instead of Cartesian
- **Rationale:** Matches the circular nature of the problem, simplifies calculations

### 3. Slower Asteroid Movement
- **Decision:** 0.02 units per step (optimized from 0.05)
- **Rationale:** Gives agent sufficient time to react and learn

### 4. Forgiving Firing Mechanics
- **Decision:** 0.3 radian angle tolerance, 9.0 unit range
- **Rationale:** Balance between learnability and skill requirement

### 5. Comprehensive Reward Shaping
- **Decision:** Multiple reward components (aiming, safety, hits, etc.)
- **Rationale:** Provides clear learning signals for complex behaviors

### 6. Strong Impact Penalty
- **Decision:** -500.0 penalty for planet impact
- **Rationale:** Critical failure should have strong negative signal

### 7. Progressive Rewards
- **Decision:** Streak bonuses, early hit bonuses, distance-based rewards
- **Rationale:** Encourages optimal strategies (early destruction, consistency)

### 8. Safety Reward System
- **Decision:** Reward for safe distance, penalty for danger zone
- **Rationale:** Explicitly teaches agent to prevent impacts, not just destroy asteroids

---

## Reward Function Summary Table

| Component | Reward Range | Purpose |
|-----------|--------------|---------|
| Precise Aim | 0-0.5 | Encourage precision |
| Good Aim | 0-0.2 | Reward getting close |
| Urgency | 0-2.0 | Prioritize threats |
| Safety (Safe) | 0-0.3 | Keep distance |
| Safety (Danger) | -0.5-0 | Avoid close asteroids |
| Early Tracking | 0-0.5 | Proactive defense |
| Survival | +0.5/step | Stay alive |
| Progress | 0-1.0 | Reduce count |
| Hit (Base) | 30.0 | Successful destruction |
| Hit (Distance) | 0-25 | Early hits preferred |
| Hit (Accuracy) | 0-5 | Precision |
| Hit (Streak) | 0-10 | Consistency |
| Hit (Early Bonus) | 0-10 | Far asteroid bonus |
| Perfect Clear | +50.0 | Complete success |
| Efficiency | 0-10 | Speed bonus |
| Planet Impact | -500.0 | Critical failure |
| Miss | -0.3 | Mild discouragement |
| Timeout | -5.0 | Efficiency |

**Total Possible Reward Range:** Approximately -500 to +150 per episode

---

## Environment Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `planet_radius` | 2.0 | Planet size |
| `max_asteroids` | 5 | Asteroids per episode |
| `asteroid_speed` | 0.02 | Distance reduction per step |
| `turret_rotation` | 0.1 | Radians per rotation action |
| `firing_angle_tolerance` | 0.3 | Radians (17.2°) |
| `firing_range` | 9.0 | Maximum distance for hit |
| `max_steps` | 300 | Episode length limit |
| `asteroid_start_distance` | [6.0, 10.0] | Initial distance range |
| `asteroid_angular_velocity` | [-0.2, 0.2] | Radians per step |

---

## Evolution of Design

This environment has been iteratively improved based on training results:

1. **Initial Design:** Basic reward structure, faster asteroids (0.05 speed)
2. **First Improvement:** Enhanced rewards, slower asteroids (0.03 speed)
3. **Second Improvement:** Safety rewards, stronger penalties, even slower (0.02 speed)
4. **Current Design:** Comprehensive reward shaping, optimized parameters

The final design balances:
- **Learnability:** Easy enough for agent to learn
- **Challenge:** Hard enough to require skill
- **Clear Signals:** Rewards guide agent toward optimal behavior

---

## Usage Example

```python
import gymnasium as gym
from environment.orbital_defender_env import OrbitalDefenderEnv

env = OrbitalDefenderEnv()
state, info = env.reset()

for step in range(300):
    action = agent.select_action(state)  # 0, 1, or 2
    next_state, reward, terminated, truncated, info = env.step(action)
    
    if terminated or truncated:
        break
    
    state = next_state
```

---

## References

- See `environment/orbital_defender_env.py` for implementation
- See `docs/reward_function_enhancements.md` for reward design details
- See `docs/critical_fixes.md` for optimization history

