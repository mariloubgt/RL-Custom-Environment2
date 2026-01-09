# Start Fresh Training - Fix Broken Agent

## Current Status: CRITICAL FAILURE

The agent has learned a completely broken policy:
- **100% rotate left** (only one action)
- **0% fire** (never fires)
- **0% rotate right** (never rotates right)

This is a degenerate policy that must be fixed.

## Solution: Curriculum Learning

I've fixed the reward function to be less discouraging. Now start fresh training:

### Step 1: Start Curriculum Training

```bash
python training/train_curriculum_a2c.py --episodes 20000
```

This will:
- **Phase 1 (0-5000 episodes):** High entropy (0.2) forces exploration
  - Agent will try ALL actions including firing
  - Prevents degenerate policies
- **Phase 2 (5000-12000 episodes):** Medium entropy (0.15)
  - Agent refines policy while still exploring
- **Phase 3 (12000+ episodes):** Lower entropy (0.1)
  - Agent optimizes for consistency

### Step 2: Monitor Progress

Watch for these indicators:

**Early Training (Episodes 0-1000):**
- Rotation vs Fire ratio should be ~60% rotation, 40% fire
- Hit rate should start appearing (even if 0-2%)
- Entropy should stay high (>0.15)

**Mid Training (Episodes 1000-5000):**
- Hit rate should increase to 2-5%
- Success rate should start appearing
- Agent should be firing regularly

**Late Training (Episodes 5000+):**
- Hit rate should reach 10-20%+
- Success rate should be 30-50%+
- Agent should be defending effectively

### Step 3: Re-evaluate After Training

```bash
python evaluation/evaluate_a2c.py \
    --model models/a2c_curriculum_final.pth \
    --episodes 100
```

## What Changed

### Reward Function Fixes:
1. **Reduced miss penalty:** -0.3 → -0.1 (less discouraging)
2. **Added firing attempt reward:** +0.2 for firing at close asteroids (encourages defense)

These changes make firing less risky and more rewarding, preventing the "never fire" policy.

## Why This Will Work

1. **High Entropy (0.2) in Phase 1:**
   - Forces agent to explore all actions
   - Prevents convergence to degenerate policies
   - Agent will try firing even if it misses initially

2. **Gradual Difficulty Increase:**
   - Starts with high exploration
   - Gradually reduces as agent learns
   - Prevents overfitting to bad policies

3. **Better Reward Structure:**
   - Less penalty for missing
   - Reward for attempting to defend
   - Encourages active defense

## Expected Timeline

- **Episodes 0-1000:** Agent starts firing (hit rate 0-2%)
- **Episodes 1000-3000:** Agent learns basic aiming (hit rate 2-5%)
- **Episodes 3000-5000:** Agent improves (hit rate 5-10%)
- **Episodes 5000+:** Agent refines (hit rate 10-20%+)

## Important Notes

- **Discard current model:** The current `a2c_model_final.pth` is broken
- **Start fresh:** Don't resume from broken model
- **Be patient:** Curriculum learning takes time but prevents broken policies
- **Monitor closely:** Watch rotation vs fire ratio in early episodes

## Quick Start Command

```bash
# Start curriculum training (will take several hours)
python training/train_curriculum_a2c.py --episodes 20000

# In another terminal, you can monitor progress by checking:
# - Rotation vs Fire ratio in output
# - Hit rate appearing in evaluation
# - Entropy staying high in Phase 1
```

The curriculum learning approach is specifically designed to prevent this exact problem by forcing exploration in early phases.

