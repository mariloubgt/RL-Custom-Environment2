import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from environment.orbital_defender_env import OrbitalDefenderEnv
from agents.a2c_agent import A2CAgent

def train_a2c(
    episodes=1000,
    max_steps=300,
    save_freq=100,
    save_dir='models',
    device='cpu'
):
    """Train A2C agent on OrbitalDefenderEnv"""
    
    # Create environment
    env = OrbitalDefenderEnv()
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    # Create agent with improved hyperparameters
    agent = A2CAgent(
        state_dim=state_dim,
        action_dim=action_dim,
        lr=0.0003,
        gamma=0.99,
        value_coef=0.5,
        entropy_coef=0.02,
        device=device
    )
    
    # Create save directory
    os.makedirs(save_dir, exist_ok=True)
    
    # Training metrics
    episode_rewards = []
    episode_lengths = []
    episode_losses = []
    episode_policy_losses = []
    episode_value_losses = []
    episode_entropies = []
    
    print("Starting A2C training...")
    print(f"State dimension: {state_dim}, Action dimension: {action_dim}")
    print(f"Device: {device}")
    print("-" * 50)
    
    for episode in range(episodes):
        state, _ = env.reset()
        episode_reward = 0
        episode_length = 0
        
        agent.reset_episode()
        
        for step in range(max_steps):
            # Select action
            action = agent.select_action(state, training=True)
            
            # Take step
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            # Store transition
            agent.store_transition(reward, done)
            
            state = next_state
            episode_reward += reward
            episode_length += 1
            
            if done:
                break
        
        # Train agent on collected episode
        loss_info = agent.train_step()
        
        # Store metrics
        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)
        
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
        
        # Print progress
        if (episode + 1) % 10 == 0:
            avg_reward = np.mean(episode_rewards[-10:])
            avg_length = np.mean(episode_lengths[-10:])
            avg_loss = np.mean(episode_losses[-10:]) if episode_losses[-10:] else 0
            avg_entropy = np.mean(episode_entropies[-10:]) if episode_entropies[-10:] else 0
            print(f"Episode {episode + 1}/{episodes} | "
                  f"Avg Reward: {avg_reward:.2f} | "
                  f"Avg Length: {avg_length:.1f} | "
                  f"Avg Loss: {avg_loss:.4f} | "
                  f"Avg Entropy: {avg_entropy:.4f}")
        
        # Save model
        if (episode + 1) % save_freq == 0:
            model_path = os.path.join(save_dir, f'a2c_model_episode_{episode + 1}.pth')
            agent.save(model_path)
            print(f"Model saved to {model_path}")
    
    # Save final model
    final_model_path = os.path.join(save_dir, 'a2c_model_final.pth')
    agent.save(final_model_path)
    print(f"\nFinal model saved to {final_model_path}")
    
    # Plot training curves
    plot_training_curves(
        episode_rewards, 
        episode_lengths, 
        episode_losses,
        episode_policy_losses,
        episode_value_losses,
        episode_entropies,
        save_dir
    )
    
    return agent, episode_rewards, episode_lengths, episode_losses

def plot_training_curves(rewards, lengths, losses, policy_losses, value_losses, entropies, save_dir):
    """Plot training curves"""
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    
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
    
    # Total losses
    if losses and any(l > 0 for l in losses):
        valid_losses = [l for l in losses if l > 0]
        valid_indices = [i for i, l in enumerate(losses) if l > 0]
        axes[0, 2].plot(valid_indices, valid_losses, alpha=0.3, color='orange', label='Total Loss')
        if len(valid_losses) > 10:
            window = min(50, len(valid_losses) // 10)
            smoothed = np.convolve(valid_losses, np.ones(window)/window, mode='valid')
            axes[0, 2].plot(valid_indices[window-1:], smoothed, color='red', label='Smoothed')
        axes[0, 2].set_xlabel('Episode')
        axes[0, 2].set_ylabel('Loss')
        axes[0, 2].set_title('Total Loss')
        axes[0, 2].legend()
        axes[0, 2].grid(True)
    
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
    
    plt.tight_layout()
    plot_path = os.path.join(save_dir, 'a2c_training_curves.png')
    plt.savefig(plot_path)
    print(f"Training curves saved to {plot_path}")
    plt.close()

if __name__ == "__main__":
    import argparse
    import torch
    
    parser = argparse.ArgumentParser(description='Train A2C agent')
    parser.add_argument('--episodes', type=int, default=1000, help='Number of training episodes')
    parser.add_argument('--max-steps', type=int, default=300, help='Maximum steps per episode')
    parser.add_argument('--save-freq', type=int, default=100, help='Model save frequency')
    parser.add_argument('--save-dir', type=str, default='models', help='Directory to save models')
    
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
    
    train_a2c(
        episodes=args.episodes,
        max_steps=args.max_steps,
        save_freq=args.save_freq,
        save_dir=args.save_dir,
        device=args.device
    )

