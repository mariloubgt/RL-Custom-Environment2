# Diagnostic Tool Fix

## Problem

The diagnostic tool was showing **0.0° turret movement** even though:
- Agent uses rotation actions (32.6% + 32.9% = 65.5%)
- Training shows rotation is happening
- Code logic appears correct

## Root Cause

The diagnostic was calculating angle change **BEFORE** the step, not after:

```python
# WRONG: Calculated before step
if prev_turret_angle is not None:
    angle_change = abs(env.turret_angle - prev_turret_angle)  # Before step!
    turret_angle_changes.append(angle_change)

next_state, reward, terminated, truncated, _ = env.step(action)  # Turret moves here
```

This compared the current angle with the previous angle, but the current angle hadn't changed yet!

## Fix

Changed to calculate angle change **AFTER** the step:

```python
# Store angle before step
turret_angle_before = env.turret_angle

# Take step (turret moves here)
next_state, reward, terminated, truncated, _ = env.step(action)

# Calculate change AFTER step
if prev_turret_angle is not None:
    angle_change = abs(env.turret_angle - prev_turret_angle)
    # Handle wrap-around (angles can wrap from -pi to +pi)
    if angle_change > math.pi:
        angle_change = 2 * math.pi - angle_change
    turret_angle_changes.append(angle_change)
```

## Additional Improvements

1. **Wrap-around handling**: Angles can wrap from -π to +π, so we handle this correctly
2. **Proper timing**: Angle change is now calculated after the turret actually moves

## Expected Results

After this fix, the diagnostic should show:
- ✅ **Mean Angle Change: > 0.0 rad** (turret is moving!)
- ✅ Accurate movement tracking
- ✅ Correct angle difference calculations

## Testing

Run the diagnostic again:

```bash
python evaluation/diagnose_agent.py --model models/a2c_curriculum_final.pth --episodes 20
```

You should now see:
- Turret movement > 0.0°
- Accurate angle change measurements
- Better diagnosis of agent behavior

