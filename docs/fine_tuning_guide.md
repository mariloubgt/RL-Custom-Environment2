# Fine-Tuning Guide for Adapted Model

## Problem

When resuming training, the script interprets `--episodes` as the **total target episodes**, not additional episodes.

If your model is at episode 70000 and you specify `--episodes 10000`, it thinks you want to train to 10000 total, which is already passed.

## Solution

Specify the **total target episodes** you want to reach:

### Example: Continue to 80000 Episodes

```bash
python training/train_curriculum_a2c.py --episodes 80000 --resume-from models/a2c_curriculum_final_adapted.pth
```

This will train from episode 70000 to 80000 (10,000 additional episodes).

### Example: Continue to 100000 Episodes

```bash
python training/train_curriculum_a2c.py --episodes 100000 --resume-from models/a2c_curriculum_final_adapted.pth
```

This will train from episode 70000 to 100000 (30,000 additional episodes).

## Recommended Fine-Tuning

For the adapted model, I recommend:

```bash
python training/train_curriculum_a2c.py --episodes 80000 --resume-from models/a2c_curriculum_final_adapted.pth
```

This gives 10,000 episodes to fine-tune the new dimensions (angle_diff).

## Expected Improvements

After fine-tuning (10,000 episodes):

- **Mean Angle Diff:** 3.39 rad → **< 0.5 rad**
- **Hit Rate:** 34.7% → **50-65%**
- **Firing Frequency:** 11.9% → **15-25%**
- **Better use of angle_diff** information

## How It Works

The `--episodes` argument specifies the **total target episodes**, not additional episodes:

- Current episode: 70000
- `--episodes 80000` → Train from 70000 to 80000 (10,000 new episodes)
- `--episodes 100000` → Train from 70000 to 100000 (30,000 new episodes)

## Quick Start

```bash
# Fine-tune for 10,000 additional episodes
python training/train_curriculum_a2c.py --episodes 80000 --resume-from models/a2c_curriculum_final_adapted.pth
```

The model will learn to use the new `angle_diff` dimensions effectively! 🚀

