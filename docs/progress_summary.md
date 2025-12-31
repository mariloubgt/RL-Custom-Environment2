# 28/12/2025

# Orbital Defender, Project Progress Summary

This document explains **everything implemented so far** so that you can understand the project structure, design choices, and current status.

---

## 1. Project Goal

The goal of this project is to build a **custom Reinforcement Learning (RL) environment** where an agent controls a **turret on a planet** and must **defend it against incoming asteroids**.

The agent learns a policy to:

* Rotate the turret
* Decide when to shoot
* Prioritize the most dangerous asteroids

This environment is later used to **train an RL agent (DQN)** and optionally visualize it as a **mini-game**.

---

## 2. Technologies Used

* **Python 3**
* **Gymnasium** (custom RL environment)
* **NumPy** (math & vectors)
* **Git & GitHub** (version control)
* Virtual environment (`.venv`)

---

## 3. Project Structure

```
RL-Custom-Environment/
│
├── environment/
│   ├── __init__.py
│   ├── orbital_defender_env.py   # Main RL environment
│   └── test_env.py               # Environment testing script
│
├── docs/                          # Documentation
├── notebooks/                     # Future experiments / training
├── app/                           # (Future) visual game
└── .venv/                         # Virtual environment
```

---

## 4. Environment Design (Orbital Defender)

### 4.1 Core Idea

* The **planet** is fixed at the center
* A **turret** rotates around the planet using an **angle (θ)**
* **Asteroids** approach the planet using **angular motion**

Everything is modeled using **angular physics**, not Cartesian coordinates.

---

## 5. Action Space

The agent has **3 discrete actions**:

| Action | Meaning             |
| ------ | ------------------- |
| 0      | Rotate turret left  |
| 1      | Rotate turret right |
| 2      | Fire projectile     |

---

## 6. Observation Space (State Representation)

To keep the state **fixed-size and stable**, only the **two closest asteroids** are observed.

### State Vector (7 values)

```
[
  turret_angle,
  asteroid1_angle,
  asteroid1_distance,
  asteroid1_angular_velocity,
  asteroid2_angle,
  asteroid2_distance,
  asteroid2_angular_velocity
]
```

### Why only the closest asteroids?

* Prevents variable-length states
* Improves learning stability
* Forces the agent to **prioritize threats**

---

## 7. Multi-Asteroid Logic

* Internally, the environment manages **5 asteroids**
* Each asteroid has:

  * angle
  * distance from planet
  * angular velocity
* At every step:

  * Asteroids move closer to the planet
  * The two closest are selected for observation

---

## 8. Reward Function

| Situation            | Reward |
| -------------------- | ------ |
| Each timestep        | -0.01  |
| Successful hit       | +10    |
| Asteroid hits planet | -10    |

### Reward shaping purpose:

* Encourage efficiency
* Penalize passive behavior
* Strongly discourage planet impact

---

## 9. Episode Termination

An episode ends if:

* An asteroid hits the planet
* A successful hit occurs
* Maximum number of steps is reached

---

## 10. Testing the Environment

A dedicated test script verifies the environment behavior.

### How to run the test (IMPORTANT)

From the **project root**, run:

```
python -m environment.test_env
```

This confirms:

* Environment loads correctly
* Observation shape is valid `(7,)`
* Actions and rewards behave as expected

---

## 11. Current Status

✅ Custom Gym environment implemented
✅ Multi-asteroid support
✅ Stable observation space
✅ Tested and working
✅ Clean Python package structure

---

## 12. Next Steps (Planned)

1. Train a **DQN agent** on this environment
2. Plot learning curves and evaluate performance
3. Add **Pygame rendering** for visualization
4. Compare random agent vs trained agent

---

## 13. Key Takeaway

This project is **not just a game**, but a complete **Reinforcement Learning system** including:

* Environment design
* Physics modeling
* Reward shaping
* Agent training

It follows professional ML engineering practices.
