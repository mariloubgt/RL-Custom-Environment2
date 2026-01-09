"""
Evaluate DQN Agent Performance

Comprehensive evaluation script to test the trained DQN agent.
"""

import sys
import os
import torch
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from environment.orbital_defender_env import OrbitalDefenderEnv
from agents.dqn_agent import DQNAgent

def evaluate_agent(
    model_path: str,
    num_episodes: int = 100,
    device: str = 'cpu',
    verbose: bool = True
):
    """Evaluate agent performance over multiple episodes"""
    
    # Create environment
    env = OrbitalDefenderEnv()
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    # Load agent
    agent = DQNAgent(
        state_dim=state_dim,
        action_dim=action_dim,
        device=device
    )
    agent.load(model_path)
    agent.epsilon = 0.0  # No exploration during evaluation
    
    # Statistics
    episode_rewards = []
    episode_lengths = []
    asteroids_destroyed = []
    success_rate = []  # Episodes where all asteroids destroyed
    impact_rate = []   # Episodes where planet was hit
    avg_reward_per_step = []
    
    print(f"Evaluating DQN agent from {model_path}")
    print(f"Running {num_episodes} evaluation episodes...")
    print("=" * 70)
    
    for episode in range(num_episodes):
        state, _ = env.reset()
        episode_reward = 0
        episode_steps = 0
        asteroids_destroyed_this_episode = 0
        initial_asteroid_count = len(env.asteroids)
        planet_hit = False
        all_destroyed = False
        
        while True:
            action = agent.select_action(state, training=False)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            episode_reward += reward
            episode_steps += 1
            
            # Track asteroid destruction
            if action == 2 and reward > 5:
                asteroids_destroyed_this_episode += 1
            
            # Check for planet impact
            if reward < -10:
                planet_hit = True
            
            # Check if all asteroids destroyed
            if len(env.asteroids) == 0:
                all_destroyed = True
            
            state = next_state
            
            if done:
                break
        
        # Record statistics
        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_steps)
        asteroids_destroyed.append(asteroids_destroyed_this_episode)
        success_rate.append(1.0 if all_destroyed else 0.0)
        impact_rate.append(1.0 if planet_hit else 0.0)
        avg_reward_per_step.append(episode_reward / episode_steps if episode_steps > 0 else 0)
        
        # Progress update
        if verbose and (episode + 1) % 10 == 0:
            print(f"Episode {episode + 1}/{num_episodes} | "
                  f"Reward: {episode_reward:.2f} | "
                  f"Steps: {episode_steps} | "
                  f"Destroyed: {asteroids_destroyed_this_episode}/{initial_asteroid_count}")
    
    # Calculate statistics
    stats = {
        'episodes': num_episodes,
        'avg_reward': np.mean(episode_rewards),
        'std_reward': np.std(episode_rewards),
        'min_reward': np.min(episode_rewards),
        'max_reward': np.max(episode_rewards),
        'avg_length': np.mean(episode_lengths),
        'avg_asteroids_destroyed': np.mean(asteroids_destroyed),
        'success_rate': np.mean(success_rate) * 100,  # Percentage
        'impact_rate': np.mean(impact_rate) * 100,     # Percentage
        'avg_reward_per_step': np.mean(avg_reward_per_step),
        'total_asteroids_destroyed': np.sum(asteroids_destroyed),
        'total_possible_asteroids': num_episodes * 5,  # 5 asteroids per episode
        'destruction_rate': (np.sum(asteroids_destroyed) / (num_episodes * 5)) * 100
    }
    
    # Print results
    print("\n" + "=" * 70)
    print("EVALUATION RESULTS")
    print("=" * 70)
    print(f"Episodes Evaluated:        {stats['episodes']}")
    print(f"\nReward Statistics:")
    print(f"  Average Reward:           {stats['avg_reward']:.2f} ± {stats['std_reward']:.2f}")
    print(f"  Min Reward:               {stats['min_reward']:.2f}")
    print(f"  Max Reward:               {stats['max_reward']:.2f}")
    print(f"  Average Reward/Step:      {stats['avg_reward_per_step']:.4f}")
    print(f"\nEpisode Statistics:")
    print(f"  Average Episode Length:  {stats['avg_length']:.1f} steps")
    print(f"  Average Asteroids Destroyed: {stats['avg_asteroids_destroyed']:.2f} per episode")
    print(f"\nSuccess Metrics:")
    print(f"  Success Rate (All Destroyed): {stats['success_rate']:.1f}%")
    print(f"  Impact Rate (Planet Hit):      {stats['impact_rate']:.1f}%")
    print(f"  Overall Destruction Rate:     {stats['destruction_rate']:.1f}%")
    print(f"  Total Asteroids Destroyed:    {stats['total_asteroids_destroyed']}/{stats['total_possible_asteroids']}")
    print("=" * 70)
    
    # Performance rating
    print("\nPerformance Rating:")
    if stats['success_rate'] >= 80:
        rating = "[EXCELLENT]"
    elif stats['success_rate'] >= 60:
        rating = "[VERY GOOD]"
    elif stats['success_rate'] >= 40:
        rating = "[GOOD]"
    elif stats['success_rate'] >= 20:
        rating = "[FAIR]"
    else:
        rating = "[NEEDS IMPROVEMENT]"
    
    print(f"  {rating}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    
    if stats['impact_rate'] < 10:
        print(f"  [OK] Low impact rate ({stats['impact_rate']:.1f}%) - Good defense!")
    else:
        print(f"  [WARNING] Impact rate: {stats['impact_rate']:.1f}% - Needs improvement")
    
    return stats

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate DQN agent performance')
    parser.add_argument('--model-path', type=str, default='models/dqn_model_final.pth',
                       help='Path to model file')
    parser.add_argument('--episodes', type=int, default=100,
                       help='Number of evaluation episodes')
    parser.add_argument('--device', type=str, default='auto',
                       choices=['auto', 'cpu', 'cuda'],
                       help='Device to use')
    
    args = parser.parse_args()
    
    # Auto-detect device
    if args.device == 'auto':
        args.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    evaluate_agent(
        model_path=args.model_path,
        num_episodes=args.episodes,
        device=args.device,
        verbose=True
    )

