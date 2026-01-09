# Balanced Firing Rewards - Encourage Good Attempts

## Problem

After adding strong penalties, the agent became **too conservative**:
- ❌ **Fires only 4.7% of actions** (too rare!)
- ❌ **Rotates 95.3% of time** (too much!)
- ❌ **Still fires at bad angles** (3.8 rad = 218°)
- ✅ **Hit rate: 47.2%** (good, but due to luck)

The penalties were **too strong**, making the agent afraid to fire!

## Root Cause

The penalty structure was:
- **Well-aimed miss:** -0.1 (small)
- **Badly-aimed miss:** -5.0 to -30.0 (very strong!)

The agent learned: "Firing is risky! Better just rotate and avoid penalties!"

## Solution: Balanced Reward/Penalty System

### New Structure: Reward Good Attempts, Penalize Bad Ones

| Angle Difference | Reward/Penalty | Behavior Encouraged |
|-----------------|----------------|---------------------|
| **< 0.3 rad (17°)** | **+2.0 to +0.5** | ✅ **Reward good attempts!** |
| **0.3-0.5 rad (17-29°)** | **-0.5 to -2.0** | ⚠️ Small penalty |
| **0.5-1.0 rad (29-57°)** | **-2.0 to -5.0** | ❌ Moderate penalty |
| **> 1.0 rad (57°+)** | **-5.0 to -10.0** | ❌ Strong penalty |

### Key Changes:

1. **Reward Well-Aimed Attempts** ✅
   - If angle < 0.3 rad: **+2.0 to +0.5 reward** (was -0.1 penalty)
   - Encourages firing when well-aligned
   - Even if miss, good attempt is rewarded!

2. **Graduated Penalties** ✅
   - Small penalty for moderate misalignment (-0.5 to -2.0)
   - Moderate penalty for bad aim (-2.0 to -5.0)
   - Strong penalty only for very bad aim (-5.0 to -10.0)

3. **Removed Extreme Penalties** ✅
   - No more -15.0 or -30.0 penalties
   - Maximum penalty: -10.0 (still strong, but not catastrophic)

## Expected Improvements

### Before Balanced Rewards:
- Firing frequency: **4.7%** (too low!)
- Rotation frequency: **95.3%** (too high!)
- Mean angle diff: **3.8 rad (218°)** (terrible!)

### After Balanced Rewards:
- Firing frequency: **15-25%** (much better!)
- Rotation frequency: **75-85%** (more balanced)
- Mean angle diff: **< 0.5 rad (29°)** (much better!)

## Why This Will Work

### Positive Reinforcement

- **Well-aimed attempts:** +2.0 reward (even if miss!)
- **Agent learns:** "Good aiming = reward, even if I miss!"

### Graduated Penalties

- **Small misalignment:** Small penalty (-0.5 to -2.0)
- **Bad misalignment:** Moderate penalty (-2.0 to -5.0)
- **Very bad misalignment:** Strong penalty (-5.0 to -10.0)

### Clear Signal

- **Good attempt:** +2.0
- **Bad attempt:** -5.0 to -10.0
- **Difference:** 12.0 to 12.0 (clear, but not extreme)

## Training Recommendations

### 1. Continue Training with Balanced Rewards

```bash
python training/train_curriculum_a2c.py \
    --episodes 70000 \
    --resume-from models/a2c_curriculum_final.pth
```

**Expected improvements:**
- Firing frequency: 4.7% → **15-25%**
- Mean angle diff: 3.8 rad → **< 0.5 rad**
- Hit rate: 47.2% → **50-70%**
- Better balance between rotation and firing

### 2. Monitor Training

Watch for:
- **Firing frequency** (should increase)
- **Angle differences** (should decrease)
- **Hit rate** (should improve)
- **Balance** between rotation and firing

### 3. Re-diagnose After Training

```bash
python evaluation/diagnose_agent.py --model models/a2c_curriculum_final.pth --episodes 20
```

**Expected results:**
- ✅ Firing frequency: **15-25%** (was 4.7%)
- ✅ Mean Angle Diff: **< 0.5 rad** (was 3.8 rad)
- ✅ Hit Rate: **> 50%** (was 47.2%)
- ✅ Better balance between actions

## Technical Details

### Reward Calculation (Well-Aimed Misses):

```python
if min_angle_diff < 0.3:  # Within 17 degrees
    good_attempt_reward = 2.0 * (0.3 - min_angle_diff) / 0.3
    reward += good_attempt_reward
    reward -= 0.5  # Small miss penalty
```

**Result:** +1.5 to +2.0 reward for well-aimed attempts (even if miss!)

### Penalty Calculation (Badly-Aimed Misses):

```python
elif min_angle_diff < 0.5:  # 17-29 degrees
    moderate_penalty = -2.0 * (min_angle_diff - 0.3) / 0.2
elif min_angle_diff < 1.0:  # 29-57 degrees
    bad_aim_penalty = -5.0 * (min_angle_diff - 0.5) / 0.5
else:  # > 57 degrees
    severe_penalty = -10.0
```

**Result:** Graduated penalties based on how bad the aim is.

## Comparison

### Old System:
- Well-aimed miss: **-0.1** (small penalty)
- Badly-aimed miss: **-5.0 to -30.0** (extreme penalty)
- **Result:** Agent afraid to fire!

### New System:
- Well-aimed miss: **+1.5 to +2.0** (reward!)
- Badly-aimed miss: **-0.5 to -10.0** (graduated penalty)
- **Result:** Agent encouraged to fire when well-aligned!

## Conclusion

The balanced reward system creates a **much better learning signal**:

- ✅ **Rewards good attempts** (even if miss)
- ✅ **Graduated penalties** (not too harsh)
- ✅ **Encourages firing** when well-aligned
- ✅ **Discourages firing** when badly-aligned

**Next Step:** Continue training with the balanced reward system! The agent should fire more frequently and with better aim! 🚀

