import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from environment.orbital_defender_env import OrbitalDefenderEnv
from agents.dqn_agent import DQNAgent

def train_dqn(
    episodes=3000,  # Increased from 1000 for better performance
    max_steps=300,
    target_update_freq=5,  # More frequent updates (was 10)
    save_freq=100,
    eval_freq=200,  # New: Evaluate every 200 episodes
    eval_episodes=20,  # New: Episodes for evaluation
    save_dir='models',
    device='cpu',
    resume_from=None  # New: Resume from checkpoint
):
    """Train DQN agent on OrbitalDefenderEnv"""
    
    # Create environment
    env = OrbitalDefenderEnv()
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    # Create agent with OPTIMIZED hyperparameters
    agent = DQNAgent(
        state_dim=state_dim,
        action_dim=action_dim,
        lr=0.001,  # Increased from 0.0005 for faster learning
        gamma=0.99,
        epsilon_start=1.0,
        epsilon_end=0.05,  # Slightly higher for continued exploration
        epsilon_decay=0.9998,  # Faster decay - reaches 0.05 around episode 1500
        batch_size=64,  # Smaller batch for more frequent updates (was 128)
        memory_size=50000,  # Smaller but still sufficient (was 100000)
        device=device,
        use_double_dqn=True  # Double DQN for better stability
    )
    
    # Resume from checkpoint if provided
    start_episode = 0
    if resume_from and os.path.exists(resume_from):
        print(f"Loading checkpoint from {resume_from}...")
        agent.load(resume_from)
        try:
            start_episode = int(resume_from.split('_')[-1].split('.')[0])
            print(f"Resuming from episode {start_episode}")
        except:
            print("Could not determine episode number, starting from 0")
    
    # Create save directory
    os.makedirs(save_dir, exist_ok=True)
    os.makedirs(os.path.join(save_dir, 'checkpoints'), exist_ok=True)
    
    # Training metrics
    episode_rewards = []
    episode_lengths = []
    episode_losses = []
    asteroids_destroyed_per_episode = []
    evaluation_results = []
    
    # Best model tracking
    best_avg_reward = float('-inf')
    best_model_path = None
    
    print("=" * 70)
    print("DQN TRAINING (IMPROVED)")
    print("=" * 70)
    print(f"Episodes: {episodes}")
    print(f"State dimension: {state_dim}, Action dimension: {action_dim}")
    print(f"Device: {device}")
    print(f"Learning Rate: {agent.initial_lr}")
    print(f"Epsilon Decay: {agent.epsilon_decay}")
    print(f"Batch Size: {agent.batch_size}")
    print("=" * 70)
    print()
    
    for episode in range(start_episode, episodes):
        state, _ = env.reset()
        episode_reward = 0
        episode_length = 0
        episode_loss = 0
        loss_count = 0
        asteroids_destroyed = 0
        initial_asteroid_count = len(env.asteroids)
        
        for step in range(max_steps):
            # Select action
            action = agent.select_action(state, training=True)
            
            # Take step
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            # Track asteroid destruction
            if action == 2 and reward > 10:  # Successful hit
                asteroids_destroyed += 1
            
            # Store experience
            agent.remember(state, action, reward, next_state, done)
            
            # Train agent (train more frequently for faster learning)
            if len(agent.memory) > agent.batch_size:
                # Train 4 times per step for faster learning (was 2)
                for _ in range(4):
                    loss = agent.train_step()
                    if loss is not None:
                        episode_loss += loss
                        loss_count += 1
            
            state = next_state
            episode_reward += reward
            episode_length += 1
            
            if done:
                break
        
        # Update target network
        if episode % target_update_freq == 0:
            agent.update_target_network()
        
        # Adaptive epsilon decay (faster if performing well)
        if episode > 100:
            recent_avg = np.mean(episode_rewards[-50:]) if len(episode_rewards) >= 50 else 0
            if recent_avg > 10:
                # Decay epsilon faster if doing well
                agent.epsilon = max(agent.epsilon_end, agent.epsilon * 0.9999)
        
        # Learning rate scheduling
        if episode > 500 and episode % 500 == 0:
            new_lr = agent.initial_lr * (0.95 ** (episode // 500))
            for param_group in agent.optimizer.param_groups:
                param_group['lr'] = new_lr
        
        # Calculate average loss
        avg_loss = episode_loss / loss_count if loss_count > 0 else 0
        
        # Store metrics
        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)
        episode_losses.append(avg_loss)
        asteroids_destroyed_per_episode.append(asteroids_destroyed)
        
        # Print progress with more detailed stats
        if (episode + 1) % 10 == 0:
            window = min(50, len(episode_rewards))
            avg_reward = np.mean(episode_rewards[-window:])
            avg_length = np.mean(episode_lengths[-window:])
            avg_loss = np.mean(episode_losses[-window:]) if episode_losses[-window:] else 0
            max_reward = np.max(episode_rewards[-window:]) if len(episode_rewards) >= window else 0
            avg_asteroids = np.mean(asteroids_destroyed_per_episode[-window:])
            
            # Calculate success metrics
            recent_rewards = episode_rewards[-window:]
            positive_episodes = sum(1 for r in recent_rewards if r > 0)
            success_pct = (positive_episodes / len(recent_rewards)) * 100 if recent_rewards else 0
            
            print(f"Episode {episode + 1:5d}/{episodes} | "
                  f"Avg Reward: {avg_reward:7.2f} | "
                  f"Max: {max_reward:6.2f} | "
                  f"Success: {success_pct:5.1f}% | "
                  f"Asteroids: {avg_asteroids:.2f} | "
                  f"Loss: {avg_loss:.4f} | "
                  f"Epsilon: {agent.epsilon:.3f}")
        
        # Periodic evaluation
        if (episode + 1) % eval_freq == 0:
            eval_stats = evaluate_agent(agent, env, eval_episodes)
            evaluation_results.append({
                'episode': episode + 1,
                'stats': eval_stats
            })
            
            print(f"\n[Evaluation at Episode {episode + 1}]")
            print(f"  Avg Reward: {eval_stats['avg_reward']:.2f} ± {eval_stats['std_reward']:.2f}")
            print(f"  Destruction Rate: {eval_stats['destruction_rate']:.1f}%")
            print(f"  Success Rate: {eval_stats['success_rate']:.1f}%")
            print(f"  Impact Rate: {eval_stats['impact_rate']:.1f}%")
            
            # Save best model
            if eval_stats['avg_reward'] > best_avg_reward:
                best_avg_reward = eval_stats['avg_reward']
                best_model_path = os.path.join(save_dir, 'dqn_model_best.pth')
                agent.save(best_model_path)
                print(f"  [NEW BEST MODEL] Saved to {best_model_path}")
            print()
        
        # Save checkpoint
        if (episode + 1) % save_freq == 0:
            checkpoint_path = os.path.join(save_dir, 'checkpoints', f'dqn_checkpoint_episode_{episode + 1}.pth')
            agent.save(checkpoint_path)
            
            # Also save regular checkpoint
            model_path = os.path.join(save_dir, f'dqn_model_episode_{episode + 1}.pth')
            agent.save(model_path)
            
            # Save training progress
            progress = {
                'episode': episode + 1,
                'episode_rewards': episode_rewards[-1000:],  # Last 1000 episodes
                'episode_lengths': episode_lengths[-1000:],
                'asteroids_destroyed': asteroids_destroyed_per_episode[-1000:],
                'evaluation_results': evaluation_results
            }
            progress_path = os.path.join(save_dir, 'training_progress.json')
            with open(progress_path, 'w') as f:
                json.dump(progress, f, indent=2)
    
    # Save final model
    final_model_path = os.path.join(save_dir, 'dqn_model_final.pth')
    agent.save(final_model_path)
    print(f"\nFinal model saved to {final_model_path}")
    
    if best_model_path:
        print(f"Best model (avg reward: {best_avg_reward:.2f}) saved to {best_model_path}")
    
    # Plot training curves
    plot_training_curves(episode_rewards, episode_lengths, episode_losses, 
                        asteroids_destroyed_per_episode, evaluation_results, save_dir)
    
    return agent, episode_rewards, episode_lengths, episode_losses

def evaluate_agent(agent, env, num_episodes=20):
    """Quick evaluation of agent performance"""
    episode_rewards = []
    asteroids_destroyed = []
    success_count = 0
    impact_count = 0
    
    original_epsilon = agent.epsilon
    agent.epsilon = 0.0  # No exploration during evaluation
    
    for _ in range(num_episodes):
        state, _ = env.reset()
        episode_reward = 0
        asteroids_destroyed_ep = 0
        initial_count = len(env.asteroids)
        planet_hit = False
        
        while True:
            action = agent.select_action(state, training=False)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            if action == 2 and reward > 10:
                asteroids_destroyed_ep += 1
            
            if reward < -10:
                planet_hit = True
            
            episode_reward += reward
            state = next_state
            
            if done:
                break
        
        episode_rewards.append(episode_reward)
        asteroids_destroyed.append(asteroids_destroyed_ep)
        
        if asteroids_destroyed_ep == initial_count:
            success_count += 1
        if planet_hit:
            impact_count += 1
    
    agent.epsilon = original_epsilon
    
    total_asteroids = num_episodes * 5
    total_destroyed = sum(asteroids_destroyed)
    
    return {
        'avg_reward': np.mean(episode_rewards),
        'std_reward': np.std(episode_rewards),
        'min_reward': np.min(episode_rewards),
        'max_reward': np.max(episode_rewards),
        'destruction_rate': (total_destroyed / total_asteroids) * 100,
        'success_rate': (success_count / num_episodes) * 100,
        'impact_rate': (impact_count / num_episodes) * 100,
        'avg_asteroids_per_episode': np.mean(asteroids_destroyed)
    }

def plot_training_curves(rewards, lengths, losses, asteroids=None, evaluations=None, save_dir='models'):
    """Plot comprehensive training curves"""
    if asteroids is None:
        asteroids = []
    if evaluations is None:
        evaluations = []
    
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # Rewards
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(rewards, alpha=0.2, color='blue', label='Episode Reward')
    if len(rewards) > 50:
        window = 50
        smoothed = np.convolve(rewards, np.ones(window)/window, mode='valid')
        ax1.plot(range(window-1, len(rewards)), smoothed, color='red', linewidth=2, label='Smoothed (50)')
    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Reward')
    ax1.set_title('Episode Rewards')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Asteroids destroyed
    ax2 = fig.add_subplot(gs[0, 1])
    if asteroids:
        ax2.plot(asteroids, alpha=0.2, color='green', label='Asteroids Destroyed')
        if len(asteroids) > 50:
            window = 50
            smoothed = np.convolve(asteroids, np.ones(window)/window, mode='valid')
            ax2.plot(range(window-1, len(asteroids)), smoothed, color='red', linewidth=2, label='Smoothed (50)')
        ax2.axhline(y=5, color='orange', linestyle='--', label='Target (5 per episode)')
    ax2.set_xlabel('Episode')
    ax2.set_ylabel('Asteroids Destroyed')
    ax2.set_title('Asteroids Destroyed per Episode')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Episode lengths
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(lengths, alpha=0.2, color='purple', label='Episode Length')
    if len(lengths) > 50:
        window = 50
        smoothed = np.convolve(lengths, np.ones(window)/window, mode='valid')
        ax3.plot(range(window-1, len(lengths)), smoothed, color='red', linewidth=2, label='Smoothed (50)')
    ax3.set_xlabel('Episode')
    ax3.set_ylabel('Steps')
    ax3.set_title('Episode Lengths')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Losses
    ax4 = fig.add_subplot(gs[1, 1])
    if losses and any(l > 0 for l in losses):
        valid_losses = [l for l in losses if l > 0]
        valid_indices = [i for i, l in enumerate(losses) if l > 0]
        ax4.plot(valid_indices, valid_losses, alpha=0.2, color='orange', label='Loss')
        if len(valid_losses) > 50:
            window = 50
            smoothed = np.convolve(valid_losses, np.ones(window)/window, mode='valid')
            ax4.plot(valid_indices[window-1:], smoothed, color='red', linewidth=2, label='Smoothed (50)')
    ax4.set_xlabel('Episode')
    ax4.set_ylabel('Loss')
    ax4.set_title('Training Loss')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Evaluation metrics
    if evaluations:
        ax5 = fig.add_subplot(gs[2, :])
        episodes = [e['episode'] for e in evaluations]
        avg_rewards = [e['stats']['avg_reward'] for e in evaluations]
        destruction_rates = [e['stats']['destruction_rate'] for e in evaluations]
        success_rates = [e['stats']['success_rate'] for e in evaluations]
        
        ax5_twin = ax5.twinx()
        
        line1 = ax5.plot(episodes, avg_rewards, 'o-', color='blue', label='Avg Reward', linewidth=2)
        line2 = ax5_twin.plot(episodes, destruction_rates, 's-', color='green', label='Destruction Rate %', linewidth=2)
        line3 = ax5_twin.plot(episodes, success_rates, '^-', color='purple', label='Success Rate %', linewidth=2)
        
        ax5.set_xlabel('Episode')
        ax5.set_ylabel('Average Reward', color='blue')
        ax5_twin.set_ylabel('Rate (%)', color='green')
        ax5.set_title('Evaluation Metrics Over Training')
        ax5.grid(True, alpha=0.3)
        
        # Combine legends
        lines = line1 + line2 + line3
        labels = [l.get_label() for l in lines]
        ax5.legend(lines, labels, loc='upper left')
    
    plt.suptitle('DQN Training Progress', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plot_path = os.path.join(save_dir, 'dqn_training_curves.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"Training curves saved to {plot_path}")
    plt.close()

if __name__ == "__main__":
    import argparse
    import torch
    
    parser = argparse.ArgumentParser(description='Train DQN agent')
    parser.add_argument('--episodes', type=int, default=3000, help='Number of training episodes')
    parser.add_argument('--max-steps', type=int, default=300, help='Maximum steps per episode')
    parser.add_argument('--target-update-freq', type=int, default=5, help='Target network update frequency')
    parser.add_argument('--save-freq', type=int, default=100, help='Model save frequency')
    parser.add_argument('--eval-freq', type=int, default=200, help='Evaluation frequency')
    parser.add_argument('--eval-episodes', type=int, default=20, help='Episodes for evaluation')
    parser.add_argument('--save-dir', type=str, default='models', help='Directory to save models')
    parser.add_argument('--resume-from', type=str, default=None, help='Resume from checkpoint')
    
    # Auto-detect device: use GPU if available, otherwise CPU
    default_device = 'cuda' if torch.cuda.is_available() else 'cpu'
    parser.add_argument('--device', type=str, default=default_device, 
                       help=f'Device to use (cpu/cuda). Default: {default_device}')
    
    args = parser.parse_args()
    
    # Validate device selection
    if args.device == 'cuda' and not torch.cuda.is_available():
        print("CUDA not available, using CPU")
        args.device = 'cpu'
    elif args.device == 'cuda':
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("Using CPU")
    
    train_dqn(
        episodes=args.episodes,
        max_steps=args.max_steps,
        target_update_freq=args.target_update_freq,
        save_freq=args.save_freq,
        eval_freq=args.eval_freq,
        eval_episodes=args.eval_episodes,
        save_dir=args.save_dir,
        device=args.device,
        resume_from=args.resume_from
    )

