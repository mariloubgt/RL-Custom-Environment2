import os
import sys
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from environment.orbital_defender_env import OrbitalDefenderEnv
from agents.a2c_agent import A2CAgent

def test_agent(model_path, num_episodes=10, render=False):
    """Test a trained A2C agent"""
    
    # Create environment
    env = OrbitalDefenderEnv()
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    # Create agent
    agent = A2CAgent(
        state_dim=state_dim,
        action_dim=action_dim,
        device='cpu'
    )
    
    # Load trained model
    if not os.path.exists(model_path):
        print(f"Error: Model file not found: {model_path}")
        return
    
    agent.load(model_path)
    print(f"Loaded model from: {model_path}")
    print("-" * 50)
    
    # Test episodes
    episode_rewards = []
    episode_lengths = []
    asteroids_destroyed = []
    
    for episode in range(num_episodes):
        state, _ = env.reset()
        episode_reward = 0
        episode_length = 0
        
        for step in range(300):
            # Select action (no exploration during testing)
            action = agent.select_action(state, training=False)
            
            # Take step
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            state = next_state
            episode_reward += reward
            episode_length += 1
            
            if done:
                break
        
        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)
        
        # Get asteroids destroyed (from environment if available)
        asteroids_destroyed.append(env.asteroids_destroyed_this_episode if hasattr(env, 'asteroids_destroyed_this_episode') else 0)
        
        print(f"Episode {episode + 1}/{num_episodes} | "
              f"Reward: {episode_reward:.2f} | "
              f"Length: {episode_length} | "
              f"Asteroids Destroyed: {asteroids_destroyed[-1]}")
    
    # Print statistics
    print("-" * 50)
    print("Test Results:")
    print(f"Average Reward: {np.mean(episode_rewards):.2f} ± {np.std(episode_rewards):.2f}")
    print(f"Average Episode Length: {np.mean(episode_lengths):.1f} ± {np.std(episode_lengths):.1f}")
    print(f"Average Asteroids Destroyed: {np.mean(asteroids_destroyed):.1f} ± {np.std(asteroids_destroyed):.1f}")
    print(f"Best Episode Reward: {np.max(episode_rewards):.2f}")
    print(f"Worst Episode Reward: {np.min(episode_rewards):.2f}")
    print(f"Success Rate (Positive Reward): {np.mean(np.array(episode_rewards) > 0) * 100:.1f}%")
    
    return episode_rewards, episode_lengths, asteroids_destroyed

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test trained A2C agent')
    parser.add_argument('--model', type=str, default='models/a2c_model_final.pth',
                       help='Path to trained model')
    parser.add_argument('--episodes', type=int, default=10,
                       help='Number of test episodes')
    
    args = parser.parse_args()
    
    test_agent(args.model, args.episodes)

