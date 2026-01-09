"""
Improved A2C Training Script
Optimized for better learning with focus on aiming accuracy
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from environment.orbital_defender_env import OrbitalDefenderEnv
from agents.a2c_agent import A2CAgent

def train_improved_a2c(
    episodes=10000,
    max_steps=300,
    save_freq=500,
    save_dir='models',
    device='cpu',
    resume_from=None
):
    """Train A2C agent with improved hyperparameters for better aiming"""
    
    # Create environment
    env = OrbitalDefenderEnv()
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    # IMPROVED HYPERPARAMETERS for better learning
    # Lower learning rate for stability
    lr = 0.00005
    # Higher entropy for more exploration (critical for learning to aim)
    entropy_coef = 0.1
    # Higher value coefficient for better value learning
    value_coef = 0.8
    # Standard discount factor
    gamma = 0.99
    
    # Create agent
    agent = A2CAgent(
        state_dim=state_dim,
        action_dim=action_dim,
        lr=lr,
        gamma=gamma,
        value_coef=value_coef,
        entropy_coef=entropy_coef,
        device=device
    )
    
    # Resume from checkpoint if provided
    start_episode = 0
    if resume_from and os.path.exists(resume_from):
        print(f"🔄 Resuming training from checkpoint: {resume_from}")
        agent.load(resume_from)
        try:
            filename = os.path.basename(resume_from)
            if 'episode_' in filename:
                episode_str = filename.split('episode_')[1].split('.')[0]
                start_episode = int(episode_str)
                print(f"   Starting from episode {start_episode + 1}")
        except:
            print("   Could not determine episode number, starting from 0")
    
    # Create save directory
    os.makedirs(save_dir, exist_ok=True)
    
    # Training metrics
    episode_rewards = []
    episode_lengths = []
    episode_losses = []
    episode_policy_losses = []
    episode_value_losses = []
    episode_entropies = []
    
    # NEW: Track aiming performance
    shots_fired_list = []
    shots_hit_list = []
    hit_rates = []
    
    if start_episode > 0:
        print(f"📊 Continuing training from episode {start_episode + 1} to {start_episode + episodes}")
    else:
        print("🚀 Starting IMPROVED A2C training...")
    print(f"State dimension: {state_dim}, Action dimension: {action_dim}")
    print(f"Device: {device}")
    print(f"Hyperparameters: lr={lr}, gamma={gamma}, value_coef={value_coef}, entropy_coef={entropy_coef}")
    print(f"Focus: Better aiming accuracy and exploration")
    print("-" * 50)
    
    for episode in range(episodes):
        state, _ = env.reset()
        episode_reward = 0
        episode_length = 0
        shots_fired = 0
        shots_hit = 0
        
        agent.reset_episode()
        
        for step in range(max_steps):
            # Select action
            action = agent.select_action(state, training=True)
            
            # Take step
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            # Track shots
            if action == 2:  # Fire
                shots_fired += 1
                if reward > 5:  # Hit
                    shots_hit += 1
            
            # Store transition
            agent.store_transition(reward, done)
            
            state = next_state
            episode_reward += reward
            episode_length += 1
            
            if done:
                break
        
        # Train agent on collected episode
        loss_info = agent.train_step()
        
        # Calculate hit rate
        hit_rate = (shots_hit / shots_fired * 100) if shots_fired > 0 else 0.0
        
        # Store metrics
        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)
        shots_fired_list.append(shots_fired)
        shots_hit_list.append(shots_hit)
        hit_rates.append(hit_rate)
        
        if loss_info:
            episode_losses.append(loss_info['total_loss'])
            episode_policy_losses.append(loss_info['policy_loss'])
            episode_value_losses.append(loss_info['value_loss'])
            episode_entropies.append(loss_info['entropy'])
        else:
            episode_losses.append(0)
            episode_policy_losses.append(0)
            episode_value_losses.append(0)
            episode_entropies.append(0)
        
        # Print progress with hit rate
        current_episode_num = start_episode + episode + 1
        total_episodes = start_episode + episodes
        
        if (episode + 1) % 10 == 0:
            avg_reward = np.mean(episode_rewards[-10:])
            avg_length = np.mean(episode_lengths[-10:])
            avg_loss = np.mean(episode_losses[-10:]) if episode_losses[-10:] else 0
            avg_entropy = np.mean(episode_entropies[-10:]) if episode_entropies[-10:] else 0
            avg_hit_rate = np.mean(hit_rates[-10:]) if hit_rates[-10:] else 0
            
            print(f"Episode {current_episode_num}/{total_episodes} | "
                  f"Avg Reward: {avg_reward:.2f} | "
                  f"Avg Length: {avg_length:.1f} | "
                  f"Avg Loss: {avg_loss:.4f} | "
                  f"Avg Entropy: {avg_entropy:.4f} | "
                  f"Hit Rate: {avg_hit_rate:.1f}%")
        
        # Save model
        if current_episode_num % save_freq == 0:
            model_path = os.path.join(save_dir, f'a2c_model_episode_{current_episode_num}.pth')
            agent.save(model_path)
            print(f"💾 Model saved to {model_path}")
            
            # Print recent performance summary
            recent_episodes = min(50, len(episode_rewards))
            recent_hit_rate = np.mean(hit_rates[-recent_episodes:]) if hit_rates[-recent_episodes:] else 0
            recent_avg_reward = np.mean(episode_rewards[-recent_episodes:])
            print(f"   Recent Performance: Avg Reward: {recent_avg_reward:.2f}, Hit Rate: {recent_hit_rate:.1f}%")
    
    # Save final model
    final_model_path = os.path.join(save_dir, 'a2c_model_final.pth')
    agent.save(final_model_path)
    print(f"\nFinal model saved to {final_model_path}")
    
    # Final statistics
    overall_hit_rate = (np.sum(shots_hit_list) / np.sum(shots_fired_list) * 100) if np.sum(shots_fired_list) > 0 else 0.0
    print(f"\n{'='*60}")
    print("TRAINING SUMMARY")
    print(f"{'='*60}")
    print(f"Total Episodes: {total_episodes}")
    print(f"Mean Reward: {np.mean(episode_rewards):.2f} ± {np.std(episode_rewards):.2f}")
    print(f"Best Reward: {np.max(episode_rewards):.2f}")
    print(f"Overall Hit Rate: {overall_hit_rate:.1f}%")
    print(f"Mean Hit Rate: {np.mean(hit_rates):.1f}%")
    print(f"Final Entropy: {np.mean(episode_entropies[-10:]):.4f}")
    print(f"{'='*60}\n")
    
    # Plot training curves with hit rate
    plot_training_curves(
        episode_rewards, 
        episode_lengths, 
        episode_losses,
        episode_policy_losses,
        episode_value_losses,
        episode_entropies,
        hit_rates,
        save_dir
    )
    
    return agent, episode_rewards, episode_lengths, episode_losses

def plot_training_curves(rewards, lengths, losses, policy_losses, value_losses, entropies, hit_rates, save_dir):
    """Plot training curves including hit rate"""
    fig, axes = plt.subplots(2, 4, figsize=(24, 10))
    
    # Rewards
    axes[0, 0].plot(rewards, alpha=0.3, color='blue', label='Episode Reward')
    if len(rewards) > 10:
        window = min(50, len(rewards) // 10)
        smoothed = np.convolve(rewards, np.ones(window)/window, mode='valid')
        axes[0, 0].plot(range(window-1, len(rewards)), smoothed, color='red', label='Smoothed')
    axes[0, 0].set_xlabel('Episode')
    axes[0, 0].set_ylabel('Reward')
    axes[0, 0].set_title('Episode Rewards')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # Episode lengths
    axes[0, 1].plot(lengths, alpha=0.3, color='green', label='Episode Length')
    if len(lengths) > 10:
        window = min(50, len(lengths) // 10)
        smoothed = np.convolve(lengths, np.ones(window)/window, mode='valid')
        axes[0, 1].plot(range(window-1, len(lengths)), smoothed, color='red', label='Smoothed')
    axes[0, 1].set_xlabel('Episode')
    axes[0, 1].set_ylabel('Steps')
    axes[0, 1].set_title('Episode Lengths')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    # Hit rates (NEW)
    valid_hit_rates = [h for h in hit_rates if not np.isnan(h) and h >= 0]
    if valid_hit_rates:
        axes[0, 2].plot(valid_hit_rates, alpha=0.3, color='purple', label='Hit Rate')
        if len(valid_hit_rates) > 10:
            window = min(50, len(valid_hit_rates) // 10)
            smoothed = np.convolve(valid_hit_rates, np.ones(window)/window, mode='valid')
            axes[0, 2].plot(range(window-1, len(valid_hit_rates)), smoothed, color='red', label='Smoothed')
        axes[0, 2].set_xlabel('Episode')
        axes[0, 2].set_ylabel('Hit Rate (%)')
        axes[0, 2].set_title('Hit Rate Over Training')
        axes[0, 2].legend()
        axes[0, 2].grid(True)
    
    # Total losses
    if losses and any(l > 0 for l in losses):
        valid_losses = [l for l in losses if l > 0]
        valid_indices = [i for i, l in enumerate(losses) if l > 0]
        axes[0, 3].plot(valid_indices, valid_losses, alpha=0.3, color='orange', label='Total Loss')
        if len(valid_losses) > 10:
            window = min(50, len(valid_losses) // 10)
            smoothed = np.convolve(valid_losses, np.ones(window)/window, mode='valid')
            axes[0, 3].plot(valid_indices[window-1:], smoothed, color='red', label='Smoothed')
        axes[0, 3].set_xlabel('Episode')
        axes[0, 3].set_ylabel('Loss')
        axes[0, 3].set_title('Total Loss')
        axes[0, 3].legend()
        axes[0, 3].grid(True)
    
    # Policy losses
    if policy_losses and any(l > 0 for l in policy_losses):
        valid_losses = [l for l in policy_losses if l > 0]
        valid_indices = [i for i, l in enumerate(policy_losses) if l > 0]
        axes[1, 0].plot(valid_indices, valid_losses, alpha=0.3, color='purple', label='Policy Loss')
        if len(valid_losses) > 10:
            window = min(50, len(valid_losses) // 10)
            smoothed = np.convolve(valid_losses, np.ones(window)/window, mode='valid')
            axes[1, 0].plot(valid_indices[window-1:], smoothed, color='red', label='Smoothed')
        axes[1, 0].set_xlabel('Episode')
        axes[1, 0].set_ylabel('Loss')
        axes[1, 0].set_title('Policy Loss')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
    
    # Value losses
    if value_losses and any(l > 0 for l in value_losses):
        valid_losses = [l for l in value_losses if l > 0]
        valid_indices = [i for i, l in enumerate(value_losses) if l > 0]
        axes[1, 1].plot(valid_indices, valid_losses, alpha=0.3, color='brown', label='Value Loss')
        if len(valid_losses) > 10:
            window = min(50, len(valid_losses) // 10)
            smoothed = np.convolve(valid_losses, np.ones(window)/window, mode='valid')
            axes[1, 1].plot(valid_indices[window-1:], smoothed, color='red', label='Smoothed')
        axes[1, 1].set_xlabel('Episode')
        axes[1, 1].set_ylabel('Loss')
        axes[1, 1].set_title('Value Loss')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
    
    # Entropies
    if entropies and any(e > 0 for e in entropies):
        valid_entropies = [e for e in entropies if e > 0]
        valid_indices = [i for i, e in enumerate(entropies) if e > 0]
        axes[1, 2].plot(valid_indices, valid_entropies, alpha=0.3, color='teal', label='Entropy')
        if len(valid_entropies) > 10:
            window = min(50, len(valid_entropies) // 10)
            smoothed = np.convolve(valid_entropies, np.ones(window)/window, mode='valid')
            axes[1, 2].plot(valid_indices[window-1:], smoothed, color='red', label='Smoothed')
        axes[1, 2].set_xlabel('Episode')
        axes[1, 2].set_ylabel('Entropy')
        axes[1, 2].set_title('Policy Entropy')
        axes[1, 2].legend()
        axes[1, 2].grid(True)
    
    # Reward vs Hit Rate correlation
    if valid_hit_rates and len(valid_hit_rates) == len(rewards):
        axes[1, 3].scatter(valid_hit_rates, rewards, alpha=0.3, s=10)
        axes[1, 3].set_xlabel('Hit Rate (%)')
        axes[1, 3].set_ylabel('Reward')
        axes[1, 3].set_title('Reward vs Hit Rate')
        axes[1, 3].grid(True)
    
    plt.tight_layout()
    plot_path = os.path.join(save_dir, 'a2c_training_curves_improved.png')
    plt.savefig(plot_path)
    print(f"Training curves saved to {plot_path}")
    plt.close()

if __name__ == "__main__":
    import argparse
    import torch
    
    parser = argparse.ArgumentParser(description='Train A2C agent with improved hyperparameters')
    parser.add_argument('--episodes', type=int, default=10000, help='Number of training episodes')
    parser.add_argument('--max-steps', type=int, default=300, help='Maximum steps per episode')
    parser.add_argument('--save-freq', type=int, default=500, help='Model save frequency')
    parser.add_argument('--save-dir', type=str, default='models', help='Directory to save models')
    
    default_device = 'cuda' if torch.cuda.is_available() else 'cpu'
    parser.add_argument('--device', type=str, default=default_device, 
                       help=f'Device to use (cpu/cuda). Default: {default_device}')
    parser.add_argument('--resume-from', type=str, default=None,
                       help='Resume training from a checkpoint file')
    
    args = parser.parse_args()
    
    if args.device == 'cuda' and not torch.cuda.is_available():
        print("CUDA not available, using CPU")
        args.device = 'cpu'
    elif args.device == 'cuda':
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("Using CPU")
    
    train_improved_a2c(
        episodes=args.episodes,
        max_steps=args.max_steps,
        save_freq=args.save_freq,
        save_dir=args.save_dir,
        device=args.device,
        resume_from=args.resume_from
    )

