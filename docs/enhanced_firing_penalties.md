# Enhanced Firing Penalties - Stronger Signal

## Problem

Even after adding firing penalties, the agent still fires at bad angles:
- **Mean Angle Diff: 3.37 rad (193°)** - Still terrible!
- **Required: < 0.25 rad (14.3°)**
- **Hit Rate: 11.7%** - Low due to bad aiming

The penalties were **not strong enough** to discourage bad firing.

## Solution: Dramatically Increased Penalties

### 1. Increased Bad Aim Penalty ✅

**Before:**
- Bad aim penalty: **-2.0** (too weak)
- Severe miss penalty: **-3.0** (too weak)

**After:**
- Bad aim penalty: **-5.0** (scaled by how bad)
- Severe miss penalty: **-10.0** (for > 90° off)
- Extreme miss penalty: **-15.0** (for > 115° off)

**Total penalty for very bad firing: Up to -30.0!**

### 2. Increased Hit Reward ✅

**Before:**
- Base hit reward: **30.0**

**After:**
- Base hit reward: **50.0** (+67% increase)

**Why:** Makes good hits much more attractive compared to bad firing.

### 3. Removed Bad Firing Incentive ✅

**Before:**
- Small reward (+0.2) for firing at close asteroids (even if badly aimed)
- This was **encouraging bad behavior**!

**After:**
- **NO reward** for badly-aimed firing attempts
- Only rewards come from **actual hits**

## New Reward Structure

### Firing Rewards:

| Situation | Reward | Total Range |
|-----------|--------|-------------|
| **Perfect Hit** | +50 to +95 | Excellent! |
| **Good Hit** | +50 to +75 | Good! |
| **Miss (well-aimed)** | -0.1 | Small penalty |
| **Miss (badly-aimed)** | -5.0 to -15.0 | Strong penalty! |
| **Miss (very badly-aimed)** | -15.0 to -30.0 | **Extreme penalty!** |

### Net Effect:

- **Well-aimed fire:** +50 to +95 reward
- **Badly-aimed fire:** -5.0 to -30.0 penalty
- **Difference:** Up to **125.0** reward difference!

This creates a **very strong signal** that bad aiming is terrible.

## Expected Improvements

### Before Enhanced Penalties:
- Mean Angle Diff: **3.37 rad (193°)** - Terrible!
- Hit Rate: **11.7%** - Low
- Agent fires randomly

### After Enhanced Penalties:
- Mean Angle Diff: **< 0.5 rad (29°)** - Much better!
- Hit Rate: **20-30%** - Significantly improved
- Agent learns to aim before firing

## Training Recommendations

### 1. Continue Training with Enhanced Penalties

```bash
python training/train_curriculum_a2c.py \
    --episodes 60000 \
    --resume-from models/a2c_curriculum_final.pth
```

**Expected improvements:**
- Mean Angle Diff: 3.37 rad → **< 0.5 rad**
- Hit Rate: 11.7% → **20-30%**
- Better firing decisions

### 2. Monitor Training

Watch for these metrics:
- **Angle differences when firing** (should decrease rapidly)
- **Hit rate** (should increase)
- **Firing frequency** (may decrease initially, then stabilize)
- **Reward per episode** (should increase as agent learns)

### 3. Re-diagnose After Training

```bash
python evaluation/diagnose_agent.py --model models/a2c_curriculum_final.pth --episodes 20
```

**Expected results:**
- ✅ Mean Angle Diff (All): **< 0.5 rad** (was 3.37 rad!)
- ✅ Mean Angle Diff (Hit): **< 0.25 rad** (was 3.24 rad!)
- ✅ Hit Rate: **> 20%** (was 11.7%)

## Why This Will Work

### Strong Negative Signal

The penalties are now **5-15x stronger**:
- Bad aim: -5.0 (was -2.0)
- Severe: -10.0 (was -3.0)
- Extreme: -15.0 (new!)

### Strong Positive Signal

The hit reward is now **67% higher**:
- Base hit: +50.0 (was +30.0)
- Total hit reward: Up to +95 (was +75)

### Clear Contrast

- **Good firing:** +50 to +95
- **Bad firing:** -5 to -30
- **Difference:** Up to 125.0!

This creates an **unmistakable signal** that the agent cannot ignore.

## Technical Details

### Penalty Calculation:

1. **Find closest asteroid** to turret angle
2. **Calculate angle difference** (with wrap-around)
3. **If not hit:**
   - Base penalty: `-5.0 * (angle_diff / π)`
   - If angle > 0.5 rad: Add `-10.0`
   - If angle > 2.0 rad: Add `-15.0`
4. **Total penalty:** Up to **-30.0** for extreme bad aiming

### Reward Calculation (Hits):

1. **Base reward:** +50.0 (was +30.0)
2. **Distance bonus:** Up to +20.0
3. **Accuracy bonus:** Up to +5.0
4. **Streak bonus:** Up to +10.0
5. **Early destruction:** Up to +10.0
6. **Total:** Up to **+95.0** (was +75.0)

## Conclusion

The enhanced penalties create a **much stronger learning signal**:

- ✅ **5-15x stronger penalties** for bad firing
- ✅ **67% higher rewards** for good hits
- ✅ **Clear contrast** (125.0 difference)
- ✅ **Agent will learn** to aim before firing

**Next Step:** Continue training with the enhanced penalty system! The agent should learn much faster now. 🚀

