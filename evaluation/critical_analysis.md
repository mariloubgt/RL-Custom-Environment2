# Critical Performance Analysis

## Current Status: CRITICAL FAILURE

### Evaluation Results
- **Success Rate: 0%** - No episodes with positive reward
- **Failure Rate: 100%** - Every episode ends with planet impact
- **Asteroids Destroyed: 0** - Agent destroyed nothing
- **Shots Fired: 0** - **AGENT NEVER FIRES**
- **Hit Rate: 0%** - Cannot calculate (no shots)

### Root Cause Analysis

The agent has learned a policy that **NEVER FIRES**. This is worse than the previous 2.1% hit rate because:
1. The agent is completely passive
2. It's not even attempting to defend
3. It's essentially doing nothing until impact

## Possible Causes

### 1. Reward Structure Issue
The miss penalty (-0.3) might be discouraging firing attempts, especially if:
- The agent learned that firing and missing is worse than not firing
- The reward for aiming is too small compared to miss penalty
- The agent converged to a "do nothing" policy

### 2. Training Issue
- Agent may have been trained with too low entropy
- Agent converged to a deterministic "never fire" policy
- Insufficient exploration during training

### 3. Action Selection Bug
- Possible issue with action selection during evaluation
- Policy might be outputting wrong action probabilities

## Immediate Actions Required

### Step 1: Verify Agent Behavior
Run diagnostic to see what actions the agent is taking:

```bash
python evaluation/diagnose_agent.py --episodes 10
```

This will show:
- Action distribution (should show if agent is only rotating)
- Why it's not firing
- Current policy behavior

### Step 2: Check Model
The current model appears to be completely broken. Options:

**Option A: Retrain from Scratch**
```bash
python training/train_curriculum_a2c.py --episodes 20000
```

**Option B: Retrain with Higher Entropy**
```bash
python training/train_improved_a2c.py \
    --episodes 15000 \
    --resume-from models/a2c_model_final.pth
```

But modify the script to use:
- `entropy_coef = 0.2` (very high)
- `lr = 0.00005` (lower for stability)

### Step 3: Fix Reward Function
The environment reward function may need adjustment:

**Current Issues:**
- Miss penalty: -0.3 (might be too discouraging)
- Aiming reward: 0.5 max (might be too small)

**Proposed Changes:**
```python
# In orbital_defender_env.py
# Reduce miss penalty
if action == 2 and not hit:
    reward -= 0.1  # Reduced from 0.3

# Increase aiming reward
if normalized_angle_diff < 0.15:
    aim_reward = 1.0  # Increased from 0.5

# Add reward for attempting to fire at close asteroids
if action == 2 and closest_asteroid["distance"] < 6.0:
    reward += 0.3  # Reward for trying
```

### Step 4: Force Exploration
Create a training script that forces firing:

```python
# Add to training loop
if episode < 1000:  # First 1000 episodes
    # Force fire action occasionally
    if random.random() < 0.1:  # 10% chance
        action = 2  # Force fire
```

## Expected Recovery Path

After implementing fixes:

1. **Phase 1 (Episodes 0-2000):** Agent starts firing
   - Hit rate: 0-5%
   - Success rate: 0-10%

2. **Phase 2 (Episodes 2000-5000):** Agent learns to aim
   - Hit rate: 5-15%
   - Success rate: 10-30%

3. **Phase 3 (Episodes 5000+):** Agent improves
   - Hit rate: 15-30%
   - Success rate: 30-60%

## Recommended Immediate Action

**Start fresh with curriculum learning:**

```bash
python training/train_curriculum_a2c.py --episodes 20000
```

This will:
- Start with very high entropy (0.2) to force exploration
- Gradually reduce entropy as agent learns
- Track rotation vs fire ratio
- Monitor hit rate improvement

The curriculum learning approach is designed to prevent this exact problem by forcing exploration in early phases.

