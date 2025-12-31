from environment.orbital_defender import OrbitalDefenderEnv
import numpy as np

print("Testing Orbital Defender Environment...")
env = OrbitalDefenderEnv()

# Test 1: Reset
obs, info = env.reset()
print(f"✓ Reset successful")
print(f"  Observation shape: {obs.shape}")
print(f"  Observation: {obs}")

# Test 2: Random actions
total_reward = 0
for i in range(10):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    total_reward += reward
    print(f"  Step {i}: action={action}, reward={reward:.2f}")
    if terminated or truncated:
        print("  Episode ended early")
        break

print(f"✓ Random actions test: Total reward = {total_reward:.2f}")
print("\n✅ All tests passed! Environment is working.")
