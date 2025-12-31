print("Starting environment test...")

from environment.orbital_defender_env import OrbitalDefenderEnv

env = OrbitalDefenderEnv()

obs, _ = env.reset()
print("Initial observation:", obs)

for i in range(10):
    action = env.action_space.sample()
    obs, reward, done, _, _ = env.step(action)
    print(f"Step {i} | Action: {action} | Reward: {reward}")
    if done:
        print("Episode finished")
        break
