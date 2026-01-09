# Improved State Representation - Add Angle Difference

## Problem

Despite all reward improvements, the agent still fires at terrible angles:
- **Mean Angle Diff: 3.55 rad (203°)** - Still terrible!
- **Required: < 0.25 rad (14.3°)**
- **Hit Rate: 58.7%** (good, but likely luck)

The agent doesn't understand **when it's well-aligned** to fire.

## Root Cause

The observation space only contains:
- `turret_angle`
- `asteroid_angle`
- `asteroid_distance`
- `asteroid_angular_velocity`

**The agent must calculate `angle_diff = |turret_angle - asteroid_angle|` itself!**

This is **very difficult** for a neural network to learn, especially with wrap-around handling.

## Solution: Add Angle Difference to Observation

### Before:
```python
obs = [turret_angle, asteroid_angle, distance, angular_velocity]
```

### After:
```python
obs = [turret_angle, asteroid_angle, distance, angular_velocity, angle_diff]
```

**angle_diff** is now **directly provided** to the agent!

## Benefits

### 1. Direct Information ✅

The agent now receives:
- **angle_diff** directly (no calculation needed)
- **Clear signal** when well-aligned (< 0.25 rad)
- **Easy to learn** when to fire

### 2. Proper Wrap-Around Handling ✅

The angle difference is calculated **correctly** in the environment:
```python
angle_diff = abs(turret_angle - asteroid_angle)
if angle_diff > math.pi:
    angle_diff = 2 * math.pi - angle_diff
```

The agent doesn't need to learn this complex calculation!

### 3. Better Learning Signal ✅

The agent can now directly learn:
- **If angle_diff < 0.25:** Fire! (good alignment)
- **If angle_diff > 0.25:** Don't fire! (bad alignment)

Much easier than learning to calculate the difference!

## Expected Improvements

### Before:
- Mean Angle Diff: **3.55 rad (203°)** - Terrible!
- Agent must learn angle calculation
- Difficult learning problem

### After:
- Mean Angle Diff: **< 0.5 rad (29°)** - Much better!
- Agent receives angle_diff directly
- Easy learning problem

## Training Recommendations

### 1. Continue Training with Improved State

```bash
python training/train_curriculum_a2c.py \
    --episodes 80000 \
    --resume-from models/a2c_curriculum_final.pth
```

**Expected improvements:**
- Mean Angle Diff: 3.55 rad → **< 0.5 rad**
- Hit Rate: 58.7% → **65-75%**
- Firing frequency: 6.1% → **15-25%**
- Better firing decisions

### 2. Monitor Training

Watch for:
- **Angle differences when firing** (should decrease rapidly)
- **Hit rate** (should increase)
- **Firing frequency** (should increase)
- **Better alignment** before firing

### 3. Re-diagnose After Training

```bash
python evaluation/diagnose_agent.py --model models/a2c_curriculum_final.pth --episodes 20
```

**Expected results:**
- ✅ Mean Angle Diff (All): **< 0.5 rad** (was 3.55 rad!)
- ✅ Mean Angle Diff (Hit): **< 0.25 rad** (was 3.98 rad!)
- ✅ Hit Rate: **> 65%** (was 58.7%)
- ✅ Firing frequency: **> 15%** (was 6.1%)

## Technical Details

### Observation Space:

**Before:**
- Size: 7 (1 + 3*2)
- Components: `[turret_angle, a1_angle, a1_dist, a1_vel, a2_angle, a2_dist, a2_vel]`

**After:**
- Size: 9 (1 + 4*2)
- Components: `[turret_angle, a1_angle, a1_dist, a1_vel, a1_angle_diff, a2_angle, a2_dist, a2_vel, a2_angle_diff]`

### Angle Difference Calculation:

```python
angle_diff = abs(turret_angle - asteroid_angle)
if angle_diff > math.pi:
    angle_diff = 2 * math.pi - angle_diff
```

This ensures the **shortest angle** is always used (handles wrap-around correctly).

## Why This Will Work

### Direct Learning Signal

The agent now receives:
- **angle_diff** directly in observation
- **Clear threshold:** < 0.25 rad = good alignment
- **Easy to learn:** Simple comparison, not complex calculation

### Better State Representation

- **More informative:** Agent knows alignment directly
- **Easier to learn:** No need to learn angle calculation
- **Better decisions:** Can directly use angle_diff to decide when to fire

### Combined with Rewards

- **Good alignment (< 0.3 rad):** +1.5 to +2.0 reward
- **Bad alignment (> 0.5 rad):** -2.0 to -10.0 penalty
- **Direct angle_diff in observation:** Easy to learn the connection!

## Conclusion

Adding angle difference to the observation creates a **much easier learning problem**:

- ✅ **Direct information** (no calculation needed)
- ✅ **Clear signal** (angle_diff < 0.25 = fire)
- ✅ **Better learning** (easier to connect to rewards)
- ✅ **Faster convergence** (simpler problem)

**Next Step:** Continue training with the improved state representation! The agent should learn much faster now! 🚀

