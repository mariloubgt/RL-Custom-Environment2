# Fixing the Broken Agent

## Critical Issues Confirmed

### Diagnostic Results:
- **Action Distribution:** 100% rotate left, 0% fire, 0% rotate right
- **Firing Behavior:** Agent NEVER fires
- **Policy:** Completely broken - learned "only rotate left" policy

## Root Cause

The agent has converged to a degenerate policy:
1. **No exploration** - Entropy too low during training
2. **Reward structure** - Miss penalty discourages firing
3. **Local minimum** - Agent found a "safe" policy (do nothing)

## Solution: Immediate Retraining

### Option 1: Curriculum Learning (RECOMMENDED)

Start fresh with curriculum learning that forces exploration:

```bash
python training/train_curriculum_a2c.py --episodes 20000
```

**Why this works:**
- Phase 1: High entropy (0.2) forces agent to try ALL actions
- Prevents convergence to degenerate policies
- Gradually reduces entropy as agent learns

### Option 2: High Exploration Retraining

Retrain with very high entropy from the start:

```bash
python training/train_improved_a2c.py \
    --episodes 15000 \
    --resume-from models/a2c_model_final.pth
```

But you need to modify the script to use:
- `entropy_coef = 0.2` (very high)
- `lr = 0.00005` (lower for stability)

### Option 3: Fix Reward Function First

Before retraining, adjust the environment to encourage firing:

**In `orbital_defender_env.py`, modify the miss penalty:**

```python
# Line ~187: Change miss penalty
else:
    # Miss penalty (but not too harsh to encourage trying)
    reward -= 0.1  # Reduced from 0.3 - less discouraging
    self.consecutive_hits = 0
```

**Add reward for attempting to fire:**

```python
# After line 141 (in the fire action block)
if action == 2:
    # Add small reward just for attempting to fire at close asteroids
    if closest_asteroid and closest_asteroid["distance"] < 6.0:
        reward += 0.2  # Reward for trying to defend
```

## Recommended Action Plan

### Step 1: Fix Environment (Optional but Recommended)
Modify the reward function to be less discouraging:
- Reduce miss penalty from -0.3 to -0.1
- Add small reward for firing attempts

### Step 2: Start Curriculum Training
```bash
python training/train_curriculum_a2c.py --episodes 20000
```

### Step 3: Monitor Progress
Watch for:
- **Rotation vs Fire Ratio:** Should be ~60% rotation, 40% fire
- **Hit Rate:** Should start appearing (even if low)
- **Entropy:** Should stay high (>0.1) in Phase 1

### Step 4: Re-evaluate After Training
```bash
python evaluation/evaluate_a2c.py \
    --model models/a2c_curriculum_final.pth \
    --episodes 100
```

## Expected Recovery Timeline

- **Episodes 0-1000:** Agent starts firing (hit rate 0-2%)
- **Episodes 1000-3000:** Agent learns basic aiming (hit rate 2-5%)
- **Episodes 3000-5000:** Agent improves (hit rate 5-10%)
- **Episodes 5000+:** Agent refines (hit rate 10-20%+)

## Why Curriculum Learning is Best

1. **Forces Exploration:** High entropy in Phase 1 prevents degenerate policies
2. **Gradual Learning:** Reduces entropy as agent improves
3. **Tracks Progress:** Monitors rotation vs fire ratio
4. **Prevents Overfitting:** Gradual difficulty increase

The current model is completely broken and should be discarded. Start fresh with curriculum learning.

