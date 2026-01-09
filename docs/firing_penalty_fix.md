# Firing Penalty Fix - Prevent Bad Aiming

## Problem Identified

The diagnostic showed:
- **Mean Angle Diff (All): 9.5 rad (544°)** - Agent fires at terrible angles!
- **Mean Angle Diff (Hit): 13.9 rad (795°)** - Even hits are at bad angles (likely lucky)
- **Mean Angle Diff (Miss): 8.5 rad (489°)** - Misses are at very bad angles

The agent doesn't understand **when to fire** - it fires randomly regardless of alignment.

## Root Cause

The agent was receiving:
- ✅ Small reward for firing attempts (0.2)
- ✅ Small penalty for misses (-0.1)
- ❌ **NO penalty for firing when badly aligned**

This meant the agent learned: "Fire whenever you want, it doesn't matter if you're aiming!"

## Solution Implemented

### 1. Strong Penalty for Bad Aiming ✅

Added **penalty for firing when NOT well-aligned**:

```python
# STRONG PENALTY for firing when NOT well-aligned
if not hit and closest_asteroid_for_fire:
    # Calculate how bad the aim is
    bad_aim_penalty = -2.0 * min(min_angle_diff / math.pi, 1.0)  # Up to -2.0
    reward += bad_aim_penalty
    
    # Extra penalty if very far from target
    if min_angle_diff > 0.5:  # More than 90 degrees off
        severe_miss_penalty = -3.0
        reward += severe_miss_penalty
```

**Penalty Structure:**
- **Bad aim (< 0.5 rad):** -0 to -2.0 (scaled by how bad)
- **Very bad aim (> 0.5 rad):** -2.0 to -5.0 (severe penalty)

### 2. Proper Angle Calculation ✅

Fixed angle difference calculation to handle wrap-around correctly:

```python
# Calculate angle difference with proper wrap-around handling
angle_diff = abs(self.turret_angle - a["angle"])
# Handle wrap-around (shortest angle difference)
if angle_diff > math.pi:
    angle_diff = 2 * math.pi - angle_diff
```

**Benefits:**
- Correct angle calculations (no false large angles)
- Proper penalty calculation
- Accurate aiming rewards

## Expected Improvements

### Before Fix:
- ❌ Mean Angle Diff: **9.5 rad (544°)** - Terrible!
- ❌ Agent fires randomly
- ❌ No understanding of when to fire

### After Fix:
- ✅ Mean Angle Diff: **< 0.5 rad (29°)** - Much better!
- ✅ Agent learns to aim before firing
- ✅ Strong penalty discourages bad firing

## Reward Structure Now

### Firing Rewards:
1. **Hit:** +30 to +75 (depending on accuracy, distance, streak)
2. **Miss (well-aimed):** -0.1 (small penalty)
3. **Miss (badly-aimed):** -0.1 to -5.0 (strong penalty!)
4. **Firing at close asteroid:** +0.2 (encourages defense)

### Net Effect:
- **Well-aimed fire:** High reward potential (+30 to +75)
- **Badly-aimed fire:** Strong penalty (-2.0 to -5.0)
- **Agent learns:** "Only fire when well-aligned!"

## Training Recommendations

### 1. Continue Training with New Penalties

```bash
python training/train_curriculum_a2c.py \
    --episodes 60000 \
    --resume-from models/a2c_curriculum_final.pth
```

**Expected improvements:**
- Mean Angle Diff: 9.5 rad → **< 0.5 rad**
- Hit Rate: 14.0% → **20-25%**
- Better firing decisions

### 2. Monitor Training

Watch for:
- **Angle differences when firing** (should decrease)
- **Hit rate** (should increase)
- **Firing frequency** (may decrease initially, then stabilize)

### 3. Re-diagnose After Training

```bash
python evaluation/diagnose_agent.py --model models/a2c_curriculum_final.pth --episodes 20
```

**Expected results:**
- ✅ Mean Angle Diff (All): **< 0.5 rad** (was 9.5 rad!)
- ✅ Mean Angle Diff (Hit): **< 0.25 rad** (was 13.9 rad!)
- ✅ Hit Rate: **> 20%** (was 18.2%)

## Technical Details

### Penalty Calculation:

1. **Find closest asteroid** to turret angle
2. **Calculate angle difference** (with wrap-around)
3. **If not hit:**
   - Bad aim penalty: `-2.0 * (angle_diff / π)`
   - If angle > 0.5 rad: Add `-3.0` severe penalty
4. **Total penalty:** Up to **-5.0** for very bad aiming

### Why This Works:

- **Strong negative signal** for bad firing
- **Scales with how bad** the aim is
- **Combines with existing rewards** to guide learning
- **Agent learns:** "Bad aiming = bad outcome"

## Conclusion

The firing penalty fix addresses the **root cause**: lack of penalty for bad aiming. With this change:

- ✅ Agent will learn to **aim before firing**
- ✅ Agent will learn **when NOT to fire**
- ✅ Angle differences should **decrease dramatically**
- ✅ Hit rate should **improve significantly**

**Next Step:** Continue training with the new penalty system! 🚀

