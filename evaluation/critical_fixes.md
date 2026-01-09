# Critical Issues and Fixes

## Diagnostic Results Analysis

### Critical Problems Identified:

1. **Mean Angle Difference: 619.4°** (needs <14.3°)
   - Agent fires when completely misaligned
   - Has NO understanding of aiming
   - Fires randomly without rotating turret

2. **Turret Movement: 0.0°**
   - Turret is NOT rotating at all
   - Agent is not learning to aim
   - This is the ROOT CAUSE

3. **Hit Rate: 2.1%**
   - Only 30 hits out of 1433 shots
   - Agent is essentially firing randomly

## Root Cause

The agent has learned a policy that:
- Fires 42.5% of the time (reasonable)
- BUT fires without rotating the turret first
- Has no understanding of the relationship between:
  - Turret angle
  - Asteroid angle  
  - When to fire

## Why This Happened

1. **Insufficient Exploration**: Entropy was too low (0.02-0.08)
2. **Weak Reward Signal**: Aiming rewards (0.5 max) too small
3. **No Curriculum**: Started with full difficulty
4. **State Representation**: May not clearly show angle relationships

## Solutions

### Solution 1: Curriculum Learning (RECOMMENDED)

Use `train_curriculum_a2c.py` which:
- **Phase 1 (0-5000 episodes)**: High entropy (0.2) for exploration
- **Phase 2 (5000-12000)**: Medium entropy (0.15) for learning
- **Phase 3 (12000+)**: Lower entropy (0.1) for refinement

**Command:**
```bash
python training/train_curriculum_a2c.py --episodes 20000
```

### Solution 2: Increase Exploration

Retrain with much higher entropy:
```bash
python training/train_improved_a2c.py \
    --episodes 15000 \
    --resume-from models/a2c_model_final.pth
```

But modify the script to use:
- `entropy_coef = 0.2` (instead of 0.1)
- `lr = 0.00003` (lower for stability)

### Solution 3: Improve Reward Function

The environment needs stronger rewards for:
1. **Rotating toward asteroids** (currently missing!)
2. **Good aiming** (currently 0.5, should be 1.0+)
3. **Not firing when misaligned** (add penalty)

### Solution 4: Modify Environment (Advanced)

Add explicit reward for rotating toward closest asteroid:
```python
# In orbital_defender_env.py step() function
if action in [0, 1]:  # Rotation action
    if closest_asteroid:
        angle_to_asteroid = closest_asteroid["angle"]
        current_angle = self.turret_angle
        
        # Calculate shortest rotation direction
        angle_diff = (angle_to_asteroid - current_angle + math.pi) % (2 * math.pi) - math.pi
        
        # Reward for rotating in correct direction
        if action == 0 and angle_diff < 0:  # Rotating left toward target
            reward += 0.3
        elif action == 1 and angle_diff > 0:  # Rotating right toward target
            reward += 0.3
```

## Immediate Action Plan

### Step 1: Start Curriculum Training
```bash
python training/train_curriculum_a2c.py --episodes 20000
```

This will:
- Start with high exploration (entropy 0.2)
- Gradually reduce entropy as agent learns
- Track rotation vs fire ratio
- Monitor hit rate improvement

### Step 2: Monitor Progress

Watch for:
- **Hit Rate**: Should increase from 2% to 10%+ in Phase 1
- **Rotation Ratio**: Should be >50% (agent rotating more than firing)
- **Entropy**: Should stay high (>0.1) in early phases

### Step 3: Re-evaluate After Training

```bash
python evaluation/evaluate_a2c.py \
    --model models/a2c_curriculum_final.pth \
    --episodes 100
```

## Expected Improvements

After curriculum training:
- **Hit Rate**: 15-30% (from 2.1%)
- **Rotation Ratio**: 60-70% (agent learns to aim first)
- **Success Rate**: 60-70% (from 50%)
- **Mean Asteroids**: 2.5-3.5/5 (from 1.45)

## Why Curriculum Learning Works

1. **Phase 1 (High Exploration)**: Agent explores action space, learns to rotate
2. **Phase 2 (Learning)**: Agent refines policy, learns when to fire
3. **Phase 3 (Refinement)**: Agent optimizes for consistency

The high entropy in Phase 1 forces the agent to try different actions, including rotating the turret, which it's currently not doing.

