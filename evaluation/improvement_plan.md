# Agent Performance Improvement Plan

## Current Performance (Critical Issues)

- **Hit Rate: 2.1%** - Agent misses 97.9% of shots
- **Failure Rate: 100%** - Every episode ends with planet impact
- **Mean Asteroids Destroyed: 1.45/5** - Very poor performance
- **No Perfect Episodes** - Never cleared all asteroids

## Root Cause Analysis

### Problem 1: Agent Not Learning to Aim
The 2.1% hit rate indicates the agent is essentially firing randomly. The agent hasn't learned the relationship between:
- Turret angle
- Asteroid position
- When to fire

### Problem 2: Insufficient Exploration
With such low hit rate, the agent likely:
- Explored too little during training
- Converged to a poor policy too early
- Needs higher entropy to explore more

### Problem 3: Weak Reward Signal
The reward for aiming (0.5 max) may be too small compared to:
- Miss penalty (-0.3)
- Other rewards in the environment

## Immediate Action Plan

### Step 1: Run Diagnostic
```bash
python evaluation/diagnose_agent.py --episodes 20
```
This will show:
- Action distribution
- Firing behavior
- Angle differences when firing
- Specific issues

### Step 2: Retrain with Improved Settings

#### Option A: Easy Mode Training (Recommended First)
Create a training script with:
- **Much higher entropy**: 0.15-0.2 (encourage exploration)
- **Lower learning rate**: 0.00003 (more stable)
- **More forgiving firing**: Temporarily increase angle tolerance
- **Longer training**: 15,000+ episodes

#### Option B: Curriculum Learning
1. **Phase 1 (Episodes 0-5000)**: Easy mode
   - Wider firing angle (0.4 rad instead of 0.25)
   - Longer range (10.0 instead of 8.0)
   - Higher entropy (0.15)

2. **Phase 2 (Episodes 5000-10000)**: Medium mode
   - Normal firing angle (0.3 rad)
   - Normal range (8.0)
   - Medium entropy (0.1)

3. **Phase 3 (Episodes 10000+)**: Hard mode
   - Tight firing angle (0.25 rad)
   - Normal range (8.0)
   - Lower entropy (0.05)

### Step 3: Improve Reward Function

**Current Issues:**
- Aiming reward too small (0.5 max)
- Miss penalty may discourage firing

**Proposed Changes:**
```python
# Increase aiming reward
if normalized_angle_diff < 0.15:
    aim_reward = 1.0 * (1.0 - normalized_angle_diff / 0.15)  # Increased from 0.5

# Decrease miss penalty
reward -= 0.1  # Decreased from 0.3

# Add reward for attempting to fire at close asteroids
if action == 2 and closest_asteroid["distance"] < 6.0:
    reward += 0.2  # Reward for trying
```

### Step 4: Improve State Representation

Consider adding:
- Normalized angle difference to closest asteroid
- Distance to closest asteroid (already present)
- Binary indicator: "can fire now" (angle_diff < 0.25 and distance < 8.0)

## Training Commands

### Quick Retrain (Easy Mode)
```bash
python training/train_improved_a2c.py \
    --episodes 15000 \
    --resume-from models/a2c_model_final.pth
```

### Full Retrain from Scratch
```bash
python training/train_improved_a2c.py \
    --episodes 15000
```

## Expected Improvements

After implementing these changes:
- **Hit Rate**: Should reach 15-30% (from 2.1%)
- **Success Rate**: Should reach 60-70% (from 50%)
- **Mean Asteroids**: Should reach 2.5-3.5/5 (from 1.45)
- **Failure Rate**: Should drop to 30-40% (from 100%)

## Monitoring Progress

During training, monitor:
1. **Hit Rate** - Should increase over time
2. **Entropy** - Should stay above 0.05 for exploration
3. **Reward** - Should trend upward
4. **Loss** - Should decrease and stabilize

## Next Steps

1. ✅ Run diagnostic to identify specific issues
2. ⏳ Retrain with improved hyperparameters
3. ⏳ Re-evaluate after training
4. ⏳ Iterate based on results

