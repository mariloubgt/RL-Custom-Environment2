# Continuing Training - Phase 4: Fine-tuning

## Current Status

You're continuing training from episode 20,000 with:
- **Current Performance:** 72% success rate, 3.1% hit rate
- **Goal:** Improve hit rate to 5-10%+ and success rate to 75-80%+

## What's Happening

The training script will automatically:
1. ✅ Load the model from episode 20,000
2. ✅ Enter **Phase 4: Fine-tuning** (episodes 20,000-30,000)
3. ✅ Use lower entropy (0.05) for better exploitation
4. ✅ Focus on refining aiming accuracy

## Phase 4 Settings

- **Entropy:** 0.05 (low - focuses on exploitation)
- **Learning Rate:** 0.00003 (stable)
- **Value Coefficient:** 0.8 (strong value learning)
- **Episodes:** 20,000 → 30,000

## What to Expect

### During Training

Watch for these indicators in the output:

**Good Signs:**
- Hit rate gradually increasing (from 3.1% → 4-6%+)
- Rotation vs Fire ratio stabilizing (~60% rotation, 40% fire)
- Entropy decreasing (showing policy convergence)
- Average reward increasing

**Progress Checkpoints:**
- Episode 22,000: Hit rate should be ~3.5-4%
- Episode 25,000: Hit rate should be ~4-5%
- Episode 28,000: Hit rate should be ~5-6%
- Episode 30,000: Hit rate should be ~6-8%

### After Training

Run evaluation to see improvements:

```bash
python evaluation/evaluate_a2c.py \
    --model models/a2c_curriculum_final.pth \
    --episodes 100
```

**Expected Results:**
- Hit rate: 5-8% (from 3.1%)
- Success rate: 75-80% (from 72%)
- Mean asteroids: 2.0-2.5/5 (from 1.64)
- More consistent performance

## Monitoring Tips

1. **Check hit rate** in training output every 10 episodes
2. **Watch entropy** - should decrease gradually
3. **Monitor rotation ratio** - should stay balanced
4. **Track average reward** - should trend upward

## If Training Stalls

If hit rate doesn't improve after 5,000 episodes:
- Try even lower entropy (0.03)
- Increase value coefficient (0.9)
- Consider adjusting learning rate

## Next Steps After This Training

1. **Evaluate** the model
2. **Visualize** agent behavior
3. **Continue training** if needed (Phase 5)
4. **Compare** with previous models

Good luck with the training! The agent should improve its aiming accuracy during this phase.

