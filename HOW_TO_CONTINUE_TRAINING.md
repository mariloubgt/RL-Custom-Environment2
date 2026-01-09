# How to Continue Training

## Problem

When resuming from `a2c_curriculum_final.pth`, the script detects you're at episode 20000, but if you specify `--episodes 10000`, it thinks you want to train until episode 10000 total, which is less than where you are.

## Solution

**Specify the TOTAL number of episodes you want to reach**, not the number of additional episodes.

### Example

If you're at episode 20000 and want to train 10000 more episodes:

```bash
# ❌ WRONG - This will stop immediately
python training/train_curriculum_a2c.py --episodes 10000 --resume-from models/a2c_curriculum_final.pth

# ✅ CORRECT - Train until episode 30000 total
python training/train_curriculum_a2c.py --episodes 30000 --resume-from models/a2c_curriculum_final.pth
```

## Quick Reference

| Current Episode | Episodes to Add | Total Episodes to Specify |
|----------------|-----------------|---------------------------|
| 20000 | 5000 | `--episodes 25000` |
| 20000 | 10000 | `--episodes 30000` |
| 20000 | 20000 | `--episodes 40000` |
| 10000 | 10000 | `--episodes 20000` |

## For Your Current Situation

You're at episode 20000. To continue training:

```bash
# Train 10000 more episodes (until 30000 total)
python training/train_curriculum_a2c.py --episodes 30000 --resume-from models/a2c_curriculum_final.pth

# Or train 20000 more episodes (until 40000 total)
python training/train_curriculum_a2c.py --episodes 40000 --resume-from models/a2c_curriculum_final.pth
```

The script will automatically:
1. Detect you're at episode 20000
2. Train from 20000 to your target (30000 or 40000)
3. Apply the correct phase settings
4. Run evaluations every 200 episodes

## Note

The `--episodes` parameter specifies the **total target**, not additional episodes. This is consistent with how most training scripts work.

