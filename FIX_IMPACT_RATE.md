# Fixing 100% Impact Rate Problem

## Problem

**Impact Rate: 100%** - Every episode ends with planet impact. The agent is not learning to prevent impacts.

## Root Cause

The agent is learning to:
- ✅ Destroy some asteroids (30% destruction rate)
- ✅ Get positive rewards (75% success rate)
- ❌ But NOT learning to prevent ALL impacts

The reward structure doesn't strongly enough prioritize **survival over destruction**.

## Changes Made

### 1. Increased Urgency Rewards (CRITICAL)

**Before:**
- Urgency reward: 2.0 for close asteroids
- Aiming bonus: 1.0

**After:**
- Urgency reward: **5.0** (2.5x increase)
- Aiming bonus: **2.0** (2x increase)
- **NEW:** Critical reward: **10.0** for asteroids < 3.0 distance

**Why:** Agent needs MUCH stronger incentive to prioritize close/dangerous asteroids.

### 2. Increased Survival Rewards

**Before:**
- Survival reward: 0.2 per step
- Progress reward: 0.2 per asteroid destroyed

**After:**
- Survival reward: **0.5** per step (2.5x increase)
- **NEW:** Survival bonus: (5 - remaining_asteroids) * 0.3
- **NEW:** Episode survival bonus: **30.0** if no impact

**Why:** Agent needs constant reminder that survival is the priority.

### 3. Increased Completion Bonus

**Before:**
- Perfect episode bonus: 50.0

**After:**
- Perfect episode bonus: **100.0** (2x increase)
- Efficiency bonus: **20.0** (2x increase)

**Why:** Agent needs huge reward for actually winning (clearing all asteroids).

## Expected Effects

### Immediate (Next 1000 Episodes)
- Impact rate should start decreasing: 100% → 95-98%
- Agent should prioritize closer asteroids more
- More defensive behavior

### Short-term (5000 Episodes)
- Impact rate: 90-95%
- Better asteroid prioritization
- More consistent survival

### Long-term (10000+ Episodes)
- Impact rate: 70-85%
- Agent learns to prevent impacts
- Better survival strategies

## How to Apply

### Option 1: Continue Training (Recommended)

The changes are already in the environment. Just continue training:

```bash
python training/train_curriculum_a2c.py \
    --episodes 10000 \
    --resume-from models/a2c_curriculum_final.pth
```

The agent will learn with the new reward structure.

### Option 2: Restart Training

If you want to start fresh with the new rewards:

```bash
python training/train_curriculum_a2c.py \
    --episodes 20000
```

## Monitoring

Watch for these changes in evaluations:

```
[Evaluation at Episode X]
  Impact Rate: 100.0%  ← Should decrease over time
  Success Rate: 75.0%  ← Should increase
  Destruction Rate: 30.0%  ← Should increase
```

**Target:** Impact rate should drop to 70-85% after sufficient training.

## Why This Will Work

1. **Stronger Urgency Signals:** Agent will prioritize dangerous asteroids
2. **Constant Survival Reminder:** 0.5 per step keeps survival in focus
3. **Big Survival Bonus:** 30.0 for surviving episode is significant
4. **Huge Victory Reward:** 100.0 for perfect clear is very motivating

The agent should now learn that **survival is more important than destruction**.

## Additional Recommendations

If impact rate still doesn't decrease after 5000 episodes:

1. **Increase survival reward further:** 0.5 → 1.0 per step
2. **Increase critical reward:** 10.0 → 20.0 for < 3.0 distance
3. **Add distance-based firing priority:** Higher reward for firing at closer asteroids

But try the current changes first - they should be sufficient!

