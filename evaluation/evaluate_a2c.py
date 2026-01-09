"""
A2C Agent Evaluation Script
Comprehensive evaluation of A2C agent performance
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

def evaluate_a2c(
    model_path=None,
    num_episodes=100,
    max_steps=300,
    device='cpu',
    save_dir='evaluation'
):
    """Evaluate A2C agent and generate comprehensive report"""
    
    # Create environment
    env = OrbitalDefenderEnv()
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    # Default model path
    if model_path is None:
        models_dir = Path(__file__).parent.parent / 'models'
        model_path = models_dir / 'a2c_model_final.pth'
    
    if not os.path.exists(model_path):
        print(f"❌ Error: Model file not found at {model_path}")
        print(f"   Available models in {models_dir}:")
        if models_dir.exists():
            for f in sorted(models_dir.glob("a2c_model*.pth")):
                print(f"     - {f.name}")
        return
    
    # Load agent
    print(f"\n🔄 Loading A2C agent from {model_path}...")
    agent = A2CAgent(state_dim=state_dim, action_dim=action_dim, device=device)
    agent.load(str(model_path))
    print("✅ Agent loaded successfully!")
    
    print(f"\n{'='*60}")
    print("A2C AGENT EVALUATION")
    print(f"{'='*60}")
    print(f"Episodes: {num_episodes}")
    print(f"Max steps per episode: {max_steps}")
    print(f"Device: {device}")
    print(f"{'='*60}\n")
    
    # Evaluation metrics
    episode_rewards = []
    episode_lengths = []
    asteroids_destroyed_list = []
    shots_fired_list = []
    shots_hit_list = []
    hit_rates = []
    success_episodes = 0
    perfect_episodes = 0  # All asteroids destroyed
    failure_episodes = 0  # Planet impact
    
    # Per-episode detailed tracking
    episode_details = []
    
    for episode in range(num_episodes):
        state, _ = env.reset()
        episode_reward = 0
        episode_length = 0
        asteroids_destroyed = 0
        shots_fired = 0
        shots_hit = 0
        initial_asteroid_count = len(env.asteroids)
        episode_start_asteroids = initial_asteroid_count
        
        for step in range(max_steps):
            # Select action (no exploration)
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
                # Check if planet was hit (negative reward)
                if reward < -50:
                    failure_episodes += 1
                break
        
        # Check for perfect episode
        if asteroids_destroyed == initial_asteroid_count:
            perfect_episodes += 1
        
        # Calculate hit rate
        hit_rate = (shots_hit / shots_fired * 100) if shots_fired > 0 else 0.0
        
        # Store metrics
        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)
        asteroids_destroyed_list.append(asteroids_destroyed)
        shots_fired_list.append(shots_fired)
        shots_hit_list.append(shots_hit)
        hit_rates.append(hit_rate)
        
        if episode_reward > 0:
            success_episodes += 1
        
        # Store episode details
        episode_details.append({
            'episode': episode + 1,
            'reward': episode_reward,
            'length': episode_length,
            'asteroids_destroyed': asteroids_destroyed,
            'initial_asteroids': initial_asteroid_count,
            'shots_fired': shots_fired,
            'shots_hit': shots_hit,
            'hit_rate': hit_rate,
            'success': episode_reward > 0,
            'perfect': asteroids_destroyed == initial_asteroid_count,
            'failure': episode_reward < -50
        })
        
        # Print progress
        if (episode + 1) % 10 == 0:
            avg_reward = np.mean(episode_rewards[-10:])
            avg_hit_rate = np.mean(hit_rates[-10:])
            avg_asteroids = np.mean(asteroids_destroyed_list[-10:])
            print(f"Episode {episode + 1}/{num_episodes} | "
                  f"Avg Reward: {avg_reward:.2f} | "
                  f"Avg Hit Rate: {avg_hit_rate:.1f}% | "
                  f"Avg Asteroids: {avg_asteroids:.2f}")
    
    # Calculate overall statistics
    overall_hit_rate = (np.sum(shots_hit_list) / np.sum(shots_fired_list) * 100) if np.sum(shots_fired_list) > 0 else 0.0
    
    # Print summary
    print(f"\n{'='*60}")
    print("EVALUATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total Episodes:              {num_episodes}")
    print(f"Success Episodes:            {success_episodes} ({success_episodes/num_episodes*100:.1f}%)")
    print(f"Perfect Episodes:            {perfect_episodes} ({perfect_episodes/num_episodes*100:.1f}%)")
    print(f"Failure Episodes:            {failure_episodes} ({failure_episodes/num_episodes*100:.1f}%)")
    print(f"\nReward Statistics:")
    print(f"  Mean Reward:                {np.mean(episode_rewards):.2f}")
    print(f"  Std Reward:                 {np.std(episode_rewards):.2f}")
    print(f"  Best Reward:                {np.max(episode_rewards):.2f}")
    print(f"  Worst Reward:               {np.min(episode_rewards):.2f}")
    print(f"  Median Reward:              {np.median(episode_rewards):.2f}")
    print(f"\nPerformance Statistics:")
    print(f"  Mean Asteroids Destroyed:   {np.mean(asteroids_destroyed_list):.2f}")
    print(f"  Total Asteroids Destroyed:  {np.sum(asteroids_destroyed_list)}")
    print(f"  Mean Episode Length:        {np.mean(episode_lengths):.1f}")
    print(f"\nAccuracy Statistics:")
    print(f"  Total Shots Fired:          {np.sum(shots_fired_list)}")
    print(f"  Total Shots Hit:            {np.sum(shots_hit_list)}")
    print(f"  Overall Hit Rate:           {overall_hit_rate:.1f}%")
    print(f"  Mean Hit Rate per Episode:   {np.mean(hit_rates):.1f}%")
    print(f"  Std Hit Rate:                {np.std(hit_rates):.1f}%")
    print(f"{'='*60}\n")
    
    # Create visualizations
    os.makedirs(save_dir, exist_ok=True)
    plot_evaluation_results(
        episode_rewards, episode_lengths, asteroids_destroyed_list,
        hit_rates, shots_fired_list, shots_hit_list,
        save_dir
    )
    
    # Save detailed results
    save_evaluation_csv(episode_details, save_dir)
    
    print(f"✅ Evaluation complete! Results saved to {save_dir}/")
    
    return {
        'episode_rewards': episode_rewards,
        'episode_lengths': episode_lengths,
        'asteroids_destroyed': asteroids_destroyed_list,
        'hit_rates': hit_rates,
        'overall_hit_rate': overall_hit_rate,
        'success_rate': success_episodes / num_episodes * 100,
        'perfect_rate': perfect_episodes / num_episodes * 100,
        'failure_rate': failure_episodes / num_episodes * 100
    }

def plot_evaluation_results(
    rewards, lengths, asteroids, hit_rates, shots_fired, shots_hit, save_dir
):
    """Create comprehensive evaluation plots"""
    fig, axes = plt.subplots(3, 3, figsize=(18, 15))
    
    # 1. Reward over episodes
    axes[0, 0].plot(rewards, alpha=0.3, color='blue', label='Episode Reward')
    if len(rewards) > 10:
        window = min(20, len(rewards) // 5)
        smoothed = np.convolve(rewards, np.ones(window)/window, mode='valid')
        axes[0, 0].plot(range(window-1, len(rewards)), smoothed, color='red', linewidth=2, label='Smoothed')
    axes[0, 0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    axes[0, 0].set_xlabel('Episode')
    axes[0, 0].set_ylabel('Reward')
    axes[0, 0].set_title('Episode Rewards')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Hit rate over episodes
    axes[0, 1].plot(hit_rates, alpha=0.3, color='green', label='Hit Rate')
    if len(hit_rates) > 10:
        window = min(20, len(hit_rates) // 5)
        smoothed = np.convolve(hit_rates, np.ones(window)/window, mode='valid')
        axes[0, 1].plot(range(window-1, len(hit_rates)), smoothed, color='red', linewidth=2, label='Smoothed')
    axes[0, 1].set_xlabel('Episode')
    axes[0, 1].set_ylabel('Hit Rate (%)')
    axes[0, 1].set_title('Hit Rate per Episode')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Asteroids destroyed over episodes
    axes[0, 2].plot(asteroids, alpha=0.3, color='orange', label='Asteroids Destroyed')
    if len(asteroids) > 10:
        window = min(20, len(asteroids) // 5)
        smoothed = np.convolve(asteroids, np.ones(window)/window, mode='valid')
        axes[0, 2].plot(range(window-1, len(asteroids)), smoothed, color='red', linewidth=2, label='Smoothed')
    axes[0, 2].axhline(y=5, color='green', linestyle='--', alpha=0.5, label='Perfect (5)')
    axes[0, 2].set_xlabel('Episode')
    axes[0, 2].set_ylabel('Asteroids Destroyed')
    axes[0, 2].set_title('Asteroids Destroyed per Episode')
    axes[0, 2].legend()
    axes[0, 2].grid(True, alpha=0.3)
    
    # 4. Reward distribution
    axes[1, 0].hist(rewards, bins=30, color='blue', alpha=0.7, edgecolor='black')
    axes[1, 0].axvline(x=np.mean(rewards), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(rewards):.2f}')
    axes[1, 0].axvline(x=0, color='black', linestyle='-', alpha=0.5)
    axes[1, 0].set_xlabel('Reward')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_title('Reward Distribution')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # 5. Hit rate distribution
    valid_hit_rates = [h for h in hit_rates if not np.isnan(h)]
    if valid_hit_rates:
        axes[1, 1].hist(valid_hit_rates, bins=30, color='green', alpha=0.7, edgecolor='black')
        axes[1, 1].axvline(x=np.mean(valid_hit_rates), color='red', linestyle='--', linewidth=2, 
                          label=f'Mean: {np.mean(valid_hit_rates):.1f}%')
        axes[1, 1].set_xlabel('Hit Rate (%)')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].set_title('Hit Rate Distribution')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    # 6. Asteroids destroyed distribution
    axes[1, 2].hist(asteroids, bins=6, color='orange', alpha=0.7, edgecolor='black', align='left')
    axes[1, 2].set_xlabel('Asteroids Destroyed')
    axes[1, 2].set_ylabel('Frequency')
    axes[1, 2].set_title('Asteroids Destroyed Distribution')
    axes[1, 2].set_xticks(range(6))
    axes[1, 2].grid(True, alpha=0.3, axis='y')
    
    # 7. Reward vs Hit Rate scatter
    axes[2, 0].scatter(hit_rates, rewards, alpha=0.5, s=20)
    axes[2, 0].set_xlabel('Hit Rate (%)')
    axes[2, 0].set_ylabel('Reward')
    axes[2, 0].set_title('Reward vs Hit Rate')
    axes[2, 0].grid(True, alpha=0.3)
    
    # 8. Reward vs Asteroids Destroyed scatter
    axes[2, 1].scatter(asteroids, rewards, alpha=0.5, s=20, color='orange')
    axes[2, 1].set_xlabel('Asteroids Destroyed')
    axes[2, 1].set_ylabel('Reward')
    axes[2, 1].set_title('Reward vs Asteroids Destroyed')
    axes[2, 1].grid(True, alpha=0.3)
    
    # 9. Episode length distribution
    axes[2, 2].hist(lengths, bins=30, color='purple', alpha=0.7, edgecolor='black')
    axes[2, 2].axvline(x=np.mean(lengths), color='red', linestyle='--', linewidth=2, 
                      label=f'Mean: {np.mean(lengths):.1f}')
    axes[2, 2].set_xlabel('Episode Length (steps)')
    axes[2, 2].set_ylabel('Frequency')
    axes[2, 2].set_title('Episode Length Distribution')
    axes[2, 2].legend()
    axes[2, 2].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plot_path = os.path.join(save_dir, 'a2c_evaluation_results.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"📊 Evaluation plots saved to {plot_path}")
    plt.close()

def save_evaluation_csv(episode_details, save_dir):
    """Save detailed evaluation results to CSV"""
    df = pd.DataFrame(episode_details)
    csv_path = os.path.join(save_dir, 'a2c_evaluation_detailed.csv')
    df.to_csv(csv_path, index=False)
    print(f"📄 Detailed results saved to {csv_path}")
    
    # Create summary statistics
    summary = {
        'Metric': [
            'Total Episodes',
            'Success Episodes',
            'Perfect Episodes',
            'Failure Episodes',
            'Mean Reward',
            'Std Reward',
            'Best Reward',
            'Worst Reward',
            'Median Reward',
            'Mean Asteroids Destroyed',
            'Total Asteroids Destroyed',
            'Mean Episode Length',
            'Total Shots Fired',
            'Total Shots Hit',
            'Overall Hit Rate (%)',
            'Mean Hit Rate (%)',
            'Std Hit Rate (%)'
        ],
        'Value': [
            len(episode_details),
            df['success'].sum(),
            df['perfect'].sum(),
            df['failure'].sum(),
            df['reward'].mean(),
            df['reward'].std(),
            df['reward'].max(),
            df['reward'].min(),
            df['reward'].median(),
            df['asteroids_destroyed'].mean(),
            df['asteroids_destroyed'].sum(),
            df['length'].mean(),
            df['shots_fired'].sum(),
            df['shots_hit'].sum(),
            (df['shots_hit'].sum() / df['shots_fired'].sum() * 100) if df['shots_fired'].sum() > 0 else 0,
            df['hit_rate'].mean(),
            df['hit_rate'].std()
        ]
    }
    
    df_summary = pd.DataFrame(summary)
    summary_path = os.path.join(save_dir, 'a2c_evaluation_summary.csv')
    df_summary.to_csv(summary_path, index=False)
    print(f"📄 Summary statistics saved to {summary_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluate A2C agent')
    parser.add_argument('--model', type=str, default=None,
                       help='Path to A2C model (default: models/a2c_model_final.pth)')
    parser.add_argument('--episodes', type=int, default=100,
                       help='Number of evaluation episodes (default: 100)')
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
    
    evaluate_a2c(
        model_path=args.model,
        num_episodes=args.episodes,
        max_steps=args.max_steps,
        device=args.device,
        save_dir=args.save_dir
    )

