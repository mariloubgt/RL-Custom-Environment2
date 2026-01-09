"""
Algorithm Comparison Script
Compares A2C and DQN agents on the Orbital Defender environment
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import argparse
import torch

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from environment.orbital_defender_env import OrbitalDefenderEnv
from agents.a2c_agent import A2CAgent
from agents.dqn_agent import DQNAgent

def evaluate_agent(agent, env, num_episodes=100, max_steps=300, agent_name="Agent"):
    """Evaluate an agent and return statistics"""
    print(f"\n{'='*60}")
    print(f"Evaluating {agent_name}")
    print(f"{'='*60}")
    
    episode_rewards = []
    episode_lengths = []
    asteroids_destroyed_list = []
    shots_fired_list = []
    shots_hit_list = []
    hit_rates = []
    success_episodes = 0  # Episodes with positive reward
    
    for episode in range(num_episodes):
        state, _ = env.reset()
        episode_reward = 0
        episode_length = 0
        asteroids_destroyed = 0
        shots_fired = 0
        shots_hit = 0
        initial_asteroid_count = len(env.asteroids)
        
        for step in range(max_steps):
            # Select action (no exploration during evaluation)
            action = agent.select_action(state, training=False)
            
            # Take step
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            episode_reward += reward
            episode_length += 1
            
            # Track shots
            if action == 2:  # Fire action
                shots_fired += 1
                if reward > 5:  # Hit
                    shots_hit += 1
                    asteroids_destroyed += 1
            
            state = next_state
            
            if done:
                break
        
        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)
        asteroids_destroyed_list.append(asteroids_destroyed)
        shots_fired_list.append(shots_fired)
        shots_hit_list.append(shots_hit)
        
        # Calculate hit rate for this episode
        hit_rate = (shots_hit / shots_fired * 100) if shots_fired > 0 else 0.0
        hit_rates.append(hit_rate)
        
        if episode_reward > 0:
            success_episodes += 1
        
        # Print progress
        if (episode + 1) % 10 == 0:
            avg_reward = np.mean(episode_rewards[-10:])
            avg_hit_rate = np.mean(hit_rates[-10:])
            print(f"Episode {episode + 1}/{num_episodes} | "
                  f"Avg Reward: {avg_reward:.2f} | "
                  f"Avg Hit Rate: {avg_hit_rate:.1f}%")
    
    # Calculate overall statistics
    overall_hit_rate = (np.sum(shots_hit_list) / np.sum(shots_fired_list) * 100) if np.sum(shots_fired_list) > 0 else 0.0
    
    results = {
        'agent_name': agent_name,
        'episode_rewards': episode_rewards,
        'episode_lengths': episode_lengths,
        'asteroids_destroyed': asteroids_destroyed_list,
        'shots_fired': shots_fired_list,
        'shots_hit': shots_hit_list,
        'hit_rates': hit_rates,
        'overall_hit_rate': overall_hit_rate,
        'success_rate': (success_episodes / num_episodes * 100),
        'mean_reward': np.mean(episode_rewards),
        'std_reward': np.std(episode_rewards),
        'mean_asteroids_destroyed': np.mean(asteroids_destroyed_list),
        'mean_episode_length': np.mean(episode_lengths),
        'best_reward': np.max(episode_rewards),
        'worst_reward': np.min(episode_rewards),
        'total_asteroids_destroyed': np.sum(asteroids_destroyed_list),
        'total_shots_fired': np.sum(shots_fired_list),
        'total_shots_hit': np.sum(shots_hit_list)
    }
    
    return results

def print_comparison_table(a2c_results, dqn_results):
    """Print a comparison table of the results"""
    print("\n" + "="*80)
    print("ALGORITHM COMPARISON RESULTS")
    print("="*80)
    
    metrics = [
        ('Metric', 'A2C', 'DQN', 'Winner'),
        ('-'*20, '-'*20, '-'*20, '-'*20),
        ('Mean Reward', f"{a2c_results['mean_reward']:.2f}", 
         f"{dqn_results['mean_reward']:.2f}",
         'A2C' if a2c_results['mean_reward'] > dqn_results['mean_reward'] else 'DQN'),
        ('Std Reward', f"{a2c_results['std_reward']:.2f}",
         f"{dqn_results['std_reward']:.2f}",
         'A2C' if a2c_results['std_reward'] < dqn_results['std_reward'] else 'DQN'),
        ('Best Reward', f"{a2c_results['best_reward']:.2f}",
         f"{dqn_results['best_reward']:.2f}",
         'A2C' if a2c_results['best_reward'] > dqn_results['best_reward'] else 'DQN'),
        ('Worst Reward', f"{a2c_results['worst_reward']:.2f}",
         f"{dqn_results['worst_reward']:.2f}",
         'A2C' if a2c_results['worst_reward'] > dqn_results['worst_reward'] else 'DQN'),
        ('Success Rate', f"{a2c_results['success_rate']:.1f}%",
         f"{dqn_results['success_rate']:.1f}%",
         'A2C' if a2c_results['success_rate'] > dqn_results['success_rate'] else 'DQN'),
        ('Mean Asteroids Destroyed', f"{a2c_results['mean_asteroids_destroyed']:.2f}",
         f"{dqn_results['mean_asteroids_destroyed']:.2f}",
         'A2C' if a2c_results['mean_asteroids_destroyed'] > dqn_results['mean_asteroids_destroyed'] else 'DQN'),
        ('Overall Hit Rate', f"{a2c_results['overall_hit_rate']:.1f}%",
         f"{dqn_results['overall_hit_rate']:.1f}%",
         'A2C' if a2c_results['overall_hit_rate'] > dqn_results['overall_hit_rate'] else 'DQN'),
        ('Mean Episode Length', f"{a2c_results['mean_episode_length']:.1f}",
         f"{dqn_results['mean_episode_length']:.1f}",
         'A2C' if a2c_results['mean_episode_length'] < dqn_results['mean_episode_length'] else 'DQN'),
        ('Total Asteroids Destroyed', f"{a2c_results['total_asteroids_destroyed']}",
         f"{dqn_results['total_asteroids_destroyed']}",
         'A2C' if a2c_results['total_asteroids_destroyed'] > dqn_results['total_asteroids_destroyed'] else 'DQN'),
    ]
    
    # Print table
    for row in metrics:
        print(f"{row[0]:<25} | {row[1]:<15} | {row[2]:<15} | {row[3]}")
    
    print("="*80)

def plot_comparison(a2c_results, dqn_results, save_dir='evaluation'):
    """Create comparison plots"""
    os.makedirs(save_dir, exist_ok=True)
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # 1. Reward comparison
    axes[0, 0].plot(a2c_results['episode_rewards'], alpha=0.3, color='blue', label='A2C')
    axes[0, 0].plot(dqn_results['episode_rewards'], alpha=0.3, color='red', label='DQN')
    
    # Smoothed curves
    window = 10
    if len(a2c_results['episode_rewards']) >= window:
        a2c_smooth = np.convolve(a2c_results['episode_rewards'], np.ones(window)/window, mode='valid')
        dqn_smooth = np.convolve(dqn_results['episode_rewards'], np.ones(window)/window, mode='valid')
        axes[0, 0].plot(range(window-1, len(a2c_results['episode_rewards'])), a2c_smooth, 
                        color='blue', linewidth=2, label='A2C (smoothed)')
        axes[0, 0].plot(range(window-1, len(dqn_results['episode_rewards'])), dqn_smooth, 
                        color='red', linewidth=2, label='DQN (smoothed)')
    
    axes[0, 0].set_xlabel('Episode')
    axes[0, 0].set_ylabel('Reward')
    axes[0, 0].set_title('Episode Rewards Comparison')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Hit rate comparison
    axes[0, 1].plot(a2c_results['hit_rates'], alpha=0.3, color='blue', label='A2C')
    axes[0, 1].plot(dqn_results['hit_rates'], alpha=0.3, color='red', label='DQN')
    
    if len(a2c_results['hit_rates']) >= window:
        a2c_hit_smooth = np.convolve(a2c_results['hit_rates'], np.ones(window)/window, mode='valid')
        dqn_hit_smooth = np.convolve(dqn_results['hit_rates'], np.ones(window)/window, mode='valid')
        axes[0, 1].plot(range(window-1, len(a2c_results['hit_rates'])), a2c_hit_smooth, 
                        color='blue', linewidth=2, label='A2C (smoothed)')
        axes[0, 1].plot(range(window-1, len(dqn_results['hit_rates'])), dqn_hit_smooth, 
                        color='red', linewidth=2, label='DQN (smoothed)')
    
    axes[0, 1].set_xlabel('Episode')
    axes[0, 1].set_ylabel('Hit Rate (%)')
    axes[0, 1].set_title('Hit Rate Comparison')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Asteroids destroyed comparison
    axes[0, 2].plot(a2c_results['asteroids_destroyed'], alpha=0.3, color='blue', label='A2C')
    axes[0, 2].plot(dqn_results['asteroids_destroyed'], alpha=0.3, color='red', label='DQN')
    
    if len(a2c_results['asteroids_destroyed']) >= window:
        a2c_ast_smooth = np.convolve(a2c_results['asteroids_destroyed'], np.ones(window)/window, mode='valid')
        dqn_ast_smooth = np.convolve(dqn_results['asteroids_destroyed'], np.ones(window)/window, mode='valid')
        axes[0, 2].plot(range(window-1, len(a2c_results['asteroids_destroyed'])), a2c_ast_smooth, 
                        color='blue', linewidth=2, label='A2C (smoothed)')
        axes[0, 2].plot(range(window-1, len(dqn_results['asteroids_destroyed'])), dqn_ast_smooth, 
                        color='red', linewidth=2, label='DQN (smoothed)')
    
    axes[0, 2].set_xlabel('Episode')
    axes[0, 2].set_ylabel('Asteroids Destroyed')
    axes[0, 2].set_title('Asteroids Destroyed Comparison')
    axes[0, 2].legend()
    axes[0, 2].grid(True, alpha=0.3)
    
    # 4. Reward distribution
    axes[1, 0].hist(a2c_results['episode_rewards'], bins=30, alpha=0.6, color='blue', label='A2C')
    axes[1, 0].hist(dqn_results['episode_rewards'], bins=30, alpha=0.6, color='red', label='DQN')
    axes[1, 0].set_xlabel('Reward')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_title('Reward Distribution')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # 5. Hit rate distribution
    axes[1, 1].hist(a2c_results['hit_rates'], bins=30, alpha=0.6, color='blue', label='A2C')
    axes[1, 1].hist(dqn_results['hit_rates'], bins=30, alpha=0.6, color='red', label='DQN')
    axes[1, 1].set_xlabel('Hit Rate (%)')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].set_title('Hit Rate Distribution')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    # 6. Summary statistics bar chart
    metrics = ['Mean Reward', 'Success Rate', 'Hit Rate', 'Mean Asteroids']
    a2c_values = [
        a2c_results['mean_reward'],
        a2c_results['success_rate'],
        a2c_results['overall_hit_rate'],
        a2c_results['mean_asteroids_destroyed'] * 20  # Scale for visibility
    ]
    dqn_values = [
        dqn_results['mean_reward'],
        dqn_results['success_rate'],
        dqn_results['overall_hit_rate'],
        dqn_results['mean_asteroids_destroyed'] * 20
    ]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    axes[1, 2].bar(x - width/2, a2c_values, width, label='A2C', color='blue', alpha=0.7)
    axes[1, 2].bar(x + width/2, dqn_values, width, label='DQN', color='red', alpha=0.7)
    axes[1, 2].set_xlabel('Metrics')
    axes[1, 2].set_ylabel('Value')
    axes[1, 2].set_title('Summary Statistics Comparison')
    axes[1, 2].set_xticks(x)
    axes[1, 2].set_xticklabels(metrics, rotation=45, ha='right')
    axes[1, 2].legend()
    axes[1, 2].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plot_path = os.path.join(save_dir, 'algorithm_comparison.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"\n📊 Comparison plots saved to {plot_path}")
    plt.close()

def save_results_csv(a2c_results, dqn_results, save_dir='evaluation'):
    """Save results to CSV files"""
    os.makedirs(save_dir, exist_ok=True)
    
    # Create summary DataFrame
    summary_data = {
        'Metric': [
            'Mean Reward', 'Std Reward', 'Best Reward', 'Worst Reward',
            'Success Rate (%)', 'Mean Asteroids Destroyed', 'Overall Hit Rate (%)',
            'Mean Episode Length', 'Total Asteroids Destroyed', 'Total Shots Fired',
            'Total Shots Hit'
        ],
        'A2C': [
            a2c_results['mean_reward'],
            a2c_results['std_reward'],
            a2c_results['best_reward'],
            a2c_results['worst_reward'],
            a2c_results['success_rate'],
            a2c_results['mean_asteroids_destroyed'],
            a2c_results['overall_hit_rate'],
            a2c_results['mean_episode_length'],
            a2c_results['total_asteroids_destroyed'],
            a2c_results['total_shots_fired'],
            a2c_results['total_shots_hit']
        ],
        'DQN': [
            dqn_results['mean_reward'],
            dqn_results['std_reward'],
            dqn_results['best_reward'],
            dqn_results['worst_reward'],
            dqn_results['success_rate'],
            dqn_results['mean_asteroids_destroyed'],
            dqn_results['overall_hit_rate'],
            dqn_results['mean_episode_length'],
            dqn_results['total_asteroids_destroyed'],
            dqn_results['total_shots_fired'],
            dqn_results['total_shots_hit']
        ]
    }
    
    df_summary = pd.DataFrame(summary_data)
    summary_path = os.path.join(save_dir, 'comparison_summary.csv')
    df_summary.to_csv(summary_path, index=False)
    print(f"📄 Summary saved to {summary_path}")
    
    # Create detailed episode-by-episode DataFrame
    max_episodes = max(len(a2c_results['episode_rewards']), len(dqn_results['episode_rewards']))
    detailed_data = {
        'Episode': range(1, max_episodes + 1),
        'A2C_Reward': a2c_results['episode_rewards'] + [np.nan] * (max_episodes - len(a2c_results['episode_rewards'])),
        'A2C_Length': a2c_results['episode_lengths'] + [np.nan] * (max_episodes - len(a2c_results['episode_lengths'])),
        'A2C_Asteroids': a2c_results['asteroids_destroyed'] + [np.nan] * (max_episodes - len(a2c_results['asteroids_destroyed'])),
        'A2C_HitRate': a2c_results['hit_rates'] + [np.nan] * (max_episodes - len(a2c_results['hit_rates'])),
        'DQN_Reward': dqn_results['episode_rewards'] + [np.nan] * (max_episodes - len(dqn_results['episode_rewards'])),
        'DQN_Length': dqn_results['episode_lengths'] + [np.nan] * (max_episodes - len(dqn_results['episode_lengths'])),
        'DQN_Asteroids': dqn_results['asteroids_destroyed'] + [np.nan] * (max_episodes - len(dqn_results['asteroids_destroyed'])),
        'DQN_HitRate': dqn_results['hit_rates'] + [np.nan] * (max_episodes - len(dqn_results['hit_rates']))
    }
    
    df_detailed = pd.DataFrame(detailed_data)
    detailed_path = os.path.join(save_dir, 'comparison_detailed.csv')
    df_detailed.to_csv(detailed_path, index=False)
    print(f"📄 Detailed results saved to {detailed_path}")

def compare_algorithms(
    a2c_model_path=None,
    dqn_model_path=None,
    num_episodes=100,
    max_steps=300,
    device='cpu',
    save_dir='evaluation'
):
    """Main function to compare A2C and DQN algorithms"""
    
    # Create environment
    env = OrbitalDefenderEnv()
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    # Default model paths
    models_dir = Path(__file__).parent.parent / 'models'
    if a2c_model_path is None:
        a2c_model_path = models_dir / 'a2c_model_final.pth'
    if dqn_model_path is None:
        dqn_model_path = models_dir / 'dqn_model_final.pth'
    
    # Check if models exist
    if not os.path.exists(a2c_model_path):
        print(f"❌ Error: A2C model not found at {a2c_model_path}")
        return
    
    if not os.path.exists(dqn_model_path):
        print(f"❌ Error: DQN model not found at {dqn_model_path}")
        return
    
    # Load A2C agent
    print(f"\n🔄 Loading A2C agent from {a2c_model_path}...")
    a2c_agent = A2CAgent(state_dim=state_dim, action_dim=action_dim, device=device)
    a2c_agent.load(str(a2c_model_path))
    print("✅ A2C agent loaded")
    
    # Load DQN agent
    print(f"\n🔄 Loading DQN agent from {dqn_model_path}...")
    dqn_agent = DQNAgent(state_dim=state_dim, action_dim=action_dim, device=device)
    dqn_agent.load(str(dqn_model_path))
    dqn_agent.epsilon = 0.0  # No exploration
    print("✅ DQN agent loaded")
    
    # Evaluate both agents
    a2c_results = evaluate_agent(a2c_agent, env, num_episodes, max_steps, "A2C")
    dqn_results = evaluate_agent(dqn_agent, env, num_episodes, max_steps, "DQN")
    
    # Print comparison
    print_comparison_table(a2c_results, dqn_results)
    
    # Create plots
    plot_comparison(a2c_results, dqn_results, save_dir)
    
    # Save results
    save_results_csv(a2c_results, dqn_results, save_dir)
    
    print("\n✅ Comparison complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compare A2C and DQN algorithms')
    parser.add_argument('--a2c-model', type=str, default=None,
                       help='Path to A2C model (default: models/a2c_model_final.pth)')
    parser.add_argument('--dqn-model', type=str, default=None,
                       help='Path to DQN model (default: models/dqn_model_final.pth)')
    parser.add_argument('--episodes', type=int, default=100,
                       help='Number of evaluation episodes per agent (default: 100)')
    parser.add_argument('--max-steps', type=int, default=300,
                       help='Maximum steps per episode (default: 300)')
    parser.add_argument('--device', type=str, default='auto',
                       choices=['auto', 'cpu', 'cuda'],
                       help='Device to use (default: auto)')
    parser.add_argument('--save-dir', type=str, default='evaluation',
                       help='Directory to save results (default: evaluation)')
    
    args = parser.parse_args()
    
    # Auto-detect device
    if args.device == 'auto':
        args.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    compare_algorithms(
        a2c_model_path=args.a2c_model,
        dqn_model_path=args.dqn_model,
        num_episodes=args.episodes,
        max_steps=args.max_steps,
        device=args.device,
        save_dir=args.save_dir
    )

