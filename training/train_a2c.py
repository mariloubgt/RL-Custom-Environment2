import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from environment.orbital_defender_env import OrbitalDefenderEnv
from agents.a2c_agent import A2CAgent
from evaluation.quick_evaluate import quick_evaluate

def train_a2c(
    episodes=1000,
    max_steps=300,
    save_freq=100,
    save_dir='models',
    device='cpu',
    resume_from=None,
    lr=0.0003,
    gamma=0.99,
    value_coef=0.5,
    entropy_coef=0.02,
    eval_freq=200,
    eval_episodes=20
):
    """Train A2C agent on OrbitalDefenderEnv"""
    
    # Create environment
    env = OrbitalDefenderEnv()
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    # Create agent with hyperparameters
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
    best_performance = None  # Track best performance for saving best model
    if resume_from and os.path.exists(resume_from):
        print(f"🔄 Resuming training from checkpoint: {resume_from}")
        agent.load(resume_from)
        # Try to extract episode number from filename
        try:
            # Extract episode number from filename like "a2c_model_episode_1000.pth"
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
    
    if start_episode > 0:
        print(f"📊 Continuing training from episode {start_episode + 1} to {start_episode + episodes}")
    else:
        print("🚀 Starting A2C training...")
    print(f"State dimension: {state_dim}, Action dimension: {action_dim}")
    print(f"Device: {device}")
    print(f"Hyperparameters: lr={lr}, gamma={gamma}, value_coef={value_coef}, entropy_coef={entropy_coef}")
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
        current_episode_num = start_episode + episode + 1
        total_episodes = start_episode + episodes
        if (episode + 1) % 10 == 0:
            avg_reward = np.mean(episode_rewards[-10:])
            avg_length = np.mean(episode_lengths[-10:])
            avg_loss = np.mean(episode_losses[-10:]) if episode_losses[-10:] else 0
            avg_entropy = np.mean(episode_entropies[-10:]) if episode_entropies[-10:] else 0
            print(f"Episode {current_episode_num}/{total_episodes} | "
                  f"Avg Reward: {avg_reward:.2f} | "
                  f"Avg Length: {avg_length:.1f} | "
                  f"Avg Loss: {avg_loss:.4f} | "
                  f"Avg Entropy: {avg_entropy:.4f}")
        
        # Evaluate agent periodically
        if eval_freq > 0 and current_episode_num % eval_freq == 0:
            print(f"\n[Evaluation at Episode {current_episode_num}]")
            eval_results = quick_evaluate(agent, num_episodes=eval_episodes, max_steps=max_steps, device=device)
            
            print(f"  Avg Reward: {eval_results['avg_reward']:.2f} ± {eval_results['std_reward']:.2f}")
            print(f"  Destruction Rate: {eval_results['destruction_rate']:.1f}%")
            print(f"  Success Rate: {eval_results['success_rate']:.1f}%")
            print(f"  Impact Rate: {eval_results['impact_rate']:.1f}%")
            
            # Check if this is the best model so far
            # Use a combination of metrics to determine best model
            # Priority: success_rate > destruction_rate > avg_reward
            is_best = False
            if best_performance is None:
                is_best = True
            else:
                # Compare: higher success rate is better, then destruction rate, then reward
                if eval_results['success_rate'] > best_performance['success_rate']:
                    is_best = True
                elif (eval_results['success_rate'] == best_performance['success_rate'] and
                      eval_results['destruction_rate'] > best_performance['destruction_rate']):
                    is_best = True
                elif (eval_results['success_rate'] == best_performance['success_rate'] and
                      eval_results['destruction_rate'] == best_performance['destruction_rate'] and
                      eval_results['avg_reward'] > best_performance['avg_reward']):
                    is_best = True
            
            if is_best:
                best_performance = eval_results.copy()
                best_model_path = os.path.join(save_dir, 'a2c_model_best.pth')
                agent.save(best_model_path)
                print(f"  [NEW BEST MODEL] Saved to {best_model_path}")
            print()
        
        # Save model
        if current_episode_num % save_freq == 0:
            model_path = os.path.join(save_dir, f'a2c_model_episode_{current_episode_num}.pth')
            agent.save(model_path)
            print(f"💾 Model saved to {model_path}")
    
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
    parser.add_argument('--resume-from', type=str, default=None,
                       help='Resume training from a checkpoint file (e.g., models/a2c_model_episode_1000.pth)')
    
    # Hyperparameters
    parser.add_argument('--lr', type=float, default=0.0003,
                       help='Learning rate (default: 0.0003)')
    parser.add_argument('--gamma', type=float, default=0.99,
                       help='Discount factor (default: 0.99)')
    parser.add_argument('--value-coef', type=float, default=0.5,
                       help='Value loss coefficient (default: 0.5)')
    parser.add_argument('--entropy-coef', type=float, default=0.02,
                       help='Entropy bonus coefficient (default: 0.02)')
    parser.add_argument('--eval-freq', type=int, default=200,
                       help='Evaluation frequency in episodes (default: 200, set to 0 to disable)')
    parser.add_argument('--eval-episodes', type=int, default=20,
                       help='Number of episodes for evaluation (default: 20)')
    
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
        device=args.device,
        resume_from=args.resume_from,
        lr=args.lr,
        gamma=args.gamma,
        value_coef=args.value_coef,
        entropy_coef=args.entropy_coef,
        eval_freq=args.eval_freq,
        eval_episodes=args.eval_episodes
    )

