"""
Curriculum Learning A2C Training
Starts with easier settings and gradually increases difficulty
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from environment.orbital_defender_env import OrbitalDefenderEnv
from agents.a2c_agent import A2CAgent
from evaluation.quick_evaluate import quick_evaluate

def train_curriculum_a2c(
    episodes=20000,
    max_steps=300,
    save_freq=1000,
    save_dir='models',
    device='cpu',
    resume_from=None,
    eval_freq=200,
    eval_episodes=20,
    eval_start_episode=1000
):
    """Train A2C with curriculum learning - start easy, get harder"""
    
    env = OrbitalDefenderEnv()
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    # Curriculum phases with IMPROVED learning rates
    phases = [
        {
            'name': 'Phase 1: Easy (Exploration)',
            'episodes': (0, 5000),
            'lr': 0.00005,  # Increased for faster initial learning
            'lr_decay': 0.95,  # Decay by 5% every 1000 episodes
            'entropy_coef': 0.2,  # Very high for exploration
            'value_coef': 0.5,
            'gamma': 0.99
        },
        {
            'name': 'Phase 2: Medium (Learning)',
            'episodes': (5000, 12000),
            'lr': 0.00003,  # Balanced for learning
            'lr_decay': 0.95,  # Decay by 5% every 1000 episodes
            'entropy_coef': 0.15,  # Still high
            'value_coef': 0.7,
            'gamma': 0.99
        },
        {
            'name': 'Phase 3: Hard (Refinement)',
            'episodes': (12000, 20000),
            'lr': 0.00002,  # Lower for refinement
            'lr_decay': 0.97,  # Slower decay (3% every 1000 episodes)
            'entropy_coef': 0.1,  # Moderate
            'value_coef': 0.8,
            'gamma': 0.99
        },
        {
            'name': 'Phase 4: Fine-tuning (Accuracy)',
            'episodes': (20000, 30000),
            'lr': 0.000015,  # Very low for fine-tuning
            'lr_decay': 0.98,  # Very slow decay (2% every 1000 episodes)
            'entropy_coef': 0.05,  # Low for exploitation
            'value_coef': 0.8,
            'gamma': 0.99
        }
    ]
    
    # Start with Phase 1
    current_phase = phases[0]
    agent = None
    start_episode = 0
    
    # Resume from checkpoint if provided
    if resume_from and os.path.exists(resume_from):
        print(f"🔄 Resuming training from checkpoint: {resume_from}")
        # Determine which phase to resume in
        try:
            filename = os.path.basename(resume_from)
            if 'episode_' in filename:
                episode_str = filename.split('episode_')[1].split('.')[0]
                start_episode = int(episode_str)
            elif 'curriculum_final' in filename or 'final' in filename:
                # Try to find the latest episode file to determine actual episode
                models_dir = os.path.dirname(resume_from) if os.path.dirname(resume_from) else 'models'
                import glob
                episode_files = glob.glob(os.path.join(models_dir, 'a2c_curriculum_episode_*.pth'))
                if episode_files:
                    latest = max(episode_files, key=lambda x: int(x.split('episode_')[1].split('.')[0]))
                    episode_str = latest.split('episode_')[1].split('.')[0]
                    start_episode = int(episode_str)
                    print(f"   Detected final model, found latest episode: {start_episode}")
                else:
                    # No episode files found, assume end of last defined phase
                    start_episode = phases[-1]['episodes'][0]  # Start from beginning of last phase
                    print(f"   Detected final model, starting from episode {start_episode}")
            else:
                # Try to find episode number in directory
                models_dir = os.path.dirname(resume_from) if os.path.dirname(resume_from) else 'models'
                # Look for latest episode file
                import glob
                episode_files = glob.glob(os.path.join(models_dir, 'a2c_curriculum_episode_*.pth'))
                if episode_files:
                    latest = max(episode_files, key=lambda x: int(x.split('episode_')[1].split('.')[0]))
                    episode_str = latest.split('episode_')[1].split('.')[0]
                    start_episode = int(episode_str)
                    print(f"   Found latest episode: {start_episode}")
                else:
                    start_episode = phases[-1]['episodes'][0]  # Default to beginning of last phase
            
            # Find appropriate phase
            for phase in phases:
                if phase['episodes'][0] <= start_episode < phase['episodes'][1]:
                    current_phase = phase
                    print(f"   Entering {phase['name']}")
                    break
            else:
                # If past all phases, use last phase
                current_phase = phases[-1]
                print(f"   Past defined phases, using {current_phase['name']}")
        except Exception as e:
            print(f"   Could not determine episode number: {e}")
            print(f"   Starting from beginning of last phase")
            start_episode = phases[-1]['episodes'][0]  # Default to beginning of last phase
            current_phase = phases[-1]  # Use last phase
    
    # Create agent with Phase 1 settings
    if agent is None:
        agent = A2CAgent(
            state_dim=state_dim,
            action_dim=action_dim,
            lr=current_phase['lr'],
            gamma=current_phase['gamma'],
            value_coef=current_phase['value_coef'],
            entropy_coef=current_phase['entropy_coef'],
            device=device
        )
        
        if resume_from and os.path.exists(resume_from):
            agent.load(resume_from)
        
        # Initialize learning rate scheduler for initial phase
        from torch.optim.lr_scheduler import StepLR
        decay_rate = current_phase.get('lr_decay', 0.95)
        agent.lr_scheduler = StepLR(agent.optimizer, step_size=1000, gamma=decay_rate)
    
    os.makedirs(save_dir, exist_ok=True)
    
    # Training metrics
    episode_rewards = []
    episode_lengths = []
    episode_losses = []
    episode_entropies = []
    shots_fired_list = []
    shots_hit_list = []
    hit_rates = []
    rotation_actions = []  # Track rotation vs fire
    
    print("🚀 Starting CURRICULUM A2C Training...")
    print(f"State dimension: {state_dim}, Action dimension: {action_dim}")
    print(f"Device: {device}")
    print(f"Starting from episode: {start_episode}")
    print(f"Target total episodes: {episodes}")
    
    # Check if we have episodes to train
    if start_episode >= episodes:
        print(f"\n⚠️  Warning: Starting episode ({start_episode}) >= Target episodes ({episodes})")
        print(f"   No new episodes to train. Model already at or beyond target.")
        print(f"   To continue training, specify a higher target (e.g., --episodes {start_episode + 10000})")
        return agent, [], []
    
    episodes_to_train = episodes - start_episode
    print(f"Episodes to train: {episodes_to_train}")
    print("-" * 70)
    
    for episode in range(start_episode, episodes):
        # Check if we need to transition to next phase
        for phase in phases:
            if phase['episodes'][0] <= episode < phase['episodes'][1]:
                if phase != current_phase:
                    print(f"\n{'='*70}")
                    print(f"📚 TRANSITIONING TO {phase['name']}")
                    print(f"{'='*70}")
                    print(f"Episodes: {phase['episodes'][0]} - {phase['episodes'][1]}")
                    print(f"Learning Rate: {phase['lr']}")
                    print(f"Entropy Coef: {phase['entropy_coef']}")
                    print(f"Value Coef: {phase['value_coef']}")
                    print(f"{'='*70}\n")
                    
                    # Update agent hyperparameters
                    current_phase = phase
                    # Create new optimizer with phase learning rate
                    agent.optimizer = type(agent.optimizer)(
                        agent.network.parameters(), 
                        lr=phase['lr']
                    )
                    agent.entropy_coef = phase['entropy_coef']
                    agent.value_coef = phase['value_coef']
                    agent.gamma = phase['gamma']
                    
                    # Initialize learning rate scheduler for this phase
                    # Adaptive decay based on phase
                    from torch.optim.lr_scheduler import StepLR
                    decay_rate = phase.get('lr_decay', 0.95)
                    agent.lr_scheduler = StepLR(agent.optimizer, step_size=1000, gamma=decay_rate)
                    print(f"   Learning rate scheduler: decay {decay_rate} every 1000 episodes")
                break
        
        state, _ = env.reset()
        episode_reward = 0
        episode_length = 0
        shots_fired = 0
        shots_hit = 0
        rotations = 0
        fires = 0
        
        agent.reset_episode()
        
        for step in range(max_steps):
            action = agent.select_action(state, training=True)
            
            # Track actions
            if action == 2:
                fires += 1
            else:
                rotations += 1
            
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            # Track shots
            if action == 2:
                shots_fired += 1
                if reward > 5:
                    shots_hit += 1
            
            agent.store_transition(reward, done)
            
            state = next_state
            episode_reward += reward
            episode_length += 1
            
            if done:
                break
        
        # Train agent
        loss_info = agent.train_step()
        
        # Update learning rate scheduler (adaptive LR decay)
        if hasattr(agent, 'lr_scheduler') and agent.lr_scheduler is not None:
            agent.lr_scheduler.step()
        
        # Calculate metrics
        hit_rate = (shots_hit / shots_fired * 100) if shots_fired > 0 else 0.0
        rotation_ratio = rotations / (rotations + fires) if (rotations + fires) > 0 else 0.0
        
        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)
        shots_fired_list.append(shots_fired)
        shots_hit_list.append(shots_hit)
        hit_rates.append(hit_rate)
        rotation_actions.append(rotation_ratio)
        
        if loss_info:
            episode_losses.append(loss_info['total_loss'])
            episode_entropies.append(loss_info['entropy'])
        else:
            episode_losses.append(0)
            episode_entropies.append(0)
        
        # Print progress
        if (episode + 1) % 10 == 0:
            avg_reward = np.mean(episode_rewards[-10:])
            avg_length = np.mean(episode_lengths[-10:])
            avg_loss = np.mean(episode_losses[-10:]) if episode_losses[-10:] else 0
            avg_entropy = np.mean(episode_entropies[-10:]) if episode_entropies[-10:] else 0
            avg_hit_rate = np.mean(hit_rates[-10:]) if hit_rates[-10:] else 0
            avg_rotation = np.mean(rotation_actions[-10:]) if rotation_actions[-10:] else 0
            
            phase_name = current_phase['name'].split(':')[0]
            current_lr = agent.optimizer.param_groups[0]['lr'] if hasattr(agent, 'optimizer') else current_phase['lr']
            print(f"Episode {episode + 1}/{episodes} [{phase_name}] | "
                  f"Reward: {avg_reward:.2f} | "
                  f"Length: {avg_length:.1f} | "
                  f"Hit Rate: {avg_hit_rate:.1f}% | "
                  f"Rotate: {avg_rotation*100:.1f}% | "
                  f"Entropy: {avg_entropy:.4f} | "
                  f"LR: {current_lr:.6f}")
        
        # Periodic evaluation (after eval_start_episode, every eval_freq episodes)
        current_episode_num = episode + 1
        if (eval_freq > 0 and 
            current_episode_num >= eval_start_episode and 
            current_episode_num % eval_freq == 0):
            print(f"\n[Evaluation at Episode {current_episode_num}]")
            eval_results = quick_evaluate(agent, num_episodes=eval_episodes, max_steps=max_steps, device=device)
            
            print(f"  Avg Reward: {eval_results['avg_reward']:.2f} ± {eval_results['std_reward']:.2f}")
            print(f"  Destruction Rate: {eval_results['destruction_rate']:.1f}%")
            print(f"  Success Rate: {eval_results['success_rate']:.1f}%")
            print(f"  Impact Rate: {eval_results['impact_rate']:.1f}%")
            print()
        
        # Save model
        if (episode + 1) % save_freq == 0:
            model_path = os.path.join(save_dir, f'a2c_curriculum_episode_{episode + 1}.pth')
            agent.save(model_path)
            print(f"\n💾 Model saved to {model_path}")
            
            # Performance summary
            recent = min(100, len(episode_rewards))
            recent_hit_rate = np.mean(hit_rates[-recent:]) if hit_rates[-recent:] else 0
            recent_reward = np.mean(episode_rewards[-recent:])
            print(f"   Recent Performance: Reward: {recent_reward:.2f}, Hit Rate: {recent_hit_rate:.1f}%")
            print()
    
    # Save final model
    final_model_path = os.path.join(save_dir, 'a2c_curriculum_final.pth')
    agent.save(final_model_path)
    print(f"\n✅ Final model saved to {final_model_path}")
    
    # Final statistics
    overall_hit_rate = (np.sum(shots_hit_list) / np.sum(shots_fired_list) * 100) if np.sum(shots_fired_list) > 0 else 0.0
    
    print(f"\n{'='*70}")
    print("CURRICULUM TRAINING SUMMARY")
    print(f"{'='*70}")
    print(f"Total Episodes: {episodes}")
    
    # Check if we have any data
    if len(episode_rewards) > 0:
        mean_reward = np.mean(episode_rewards)
        std_reward = np.std(episode_rewards) if len(episode_rewards) > 1 else 0.0
        best_reward = np.max(episode_rewards)
        print(f"Mean Reward: {mean_reward:.2f} ± {std_reward:.2f}")
        print(f"Best Reward: {best_reward:.2f}")
    else:
        print("Mean Reward: No episodes completed")
        print("Best Reward: No episodes completed")
    
    print(f"Overall Hit Rate: {overall_hit_rate:.1f}%")
    
    if len(hit_rates) > 0:
        mean_hit_rate = np.mean(hit_rates)
        print(f"Mean Hit Rate: {mean_hit_rate:.1f}%")
    else:
        print("Mean Hit Rate: No data")
    
    if len(episode_entropies) > 0:
        recent_entropies = episode_entropies[-10:] if len(episode_entropies) >= 10 else episode_entropies
        final_entropy = np.mean(recent_entropies) if len(recent_entropies) > 0 else 0.0
        print(f"Final Entropy: {final_entropy:.4f}")
    else:
        print("Final Entropy: No data")
    
    print(f"{'='*70}\n")
    
    # Plot training curves (only if we have data)
    if len(episode_rewards) > 0:
        plot_curriculum_curves(
            episode_rewards, episode_lengths, episode_losses,
            episode_entropies, hit_rates, rotation_actions,
            phases, save_dir
        )
    else:
        print("⚠️  No training data to plot")
    
    return agent, episode_rewards, episode_lengths

def plot_curriculum_curves(rewards, lengths, losses, entropies, hit_rates, rotations, phases, save_dir):
    """Plot training curves with phase markers"""
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    
    # Add phase markers
    phase_episodes = [p['episodes'][0] for p in phases] + [phases[-1]['episodes'][1]]
    
    # Rewards
    axes[0, 0].plot(rewards, alpha=0.3, color='blue')
    if len(rewards) > 10:
        window = min(50, len(rewards) // 10)
        smoothed = np.convolve(rewards, np.ones(window)/window, mode='valid')
        axes[0, 0].plot(range(window-1, len(rewards)), smoothed, color='red', linewidth=2)
    for ep in phase_episodes:
        if ep < len(rewards):
            axes[0, 0].axvline(x=ep, color='green', linestyle='--', alpha=0.5)
    axes[0, 0].set_xlabel('Episode')
    axes[0, 0].set_ylabel('Reward')
    axes[0, 0].set_title('Episode Rewards (Phase Markers)')
    axes[0, 0].grid(True)
    
    # Hit rates
    valid_hit_rates = [h for h in hit_rates if not np.isnan(h) and h >= 0]
    if valid_hit_rates:
        axes[0, 1].plot(valid_hit_rates, alpha=0.3, color='purple')
        if len(valid_hit_rates) > 10:
            window = min(50, len(valid_hit_rates) // 10)
            smoothed = np.convolve(valid_hit_rates, np.ones(window)/window, mode='valid')
            axes[0, 1].plot(range(window-1, len(valid_hit_rates)), smoothed, color='red', linewidth=2)
        for ep in phase_episodes:
            if ep < len(valid_hit_rates):
                axes[0, 1].axvline(x=ep, color='green', linestyle='--', alpha=0.5)
        axes[0, 1].set_xlabel('Episode')
        axes[0, 1].set_ylabel('Hit Rate (%)')
        axes[0, 1].set_title('Hit Rate Over Training')
        axes[0, 1].grid(True)
    
    # Entropy
    valid_entropies = [e for e in entropies if e > 0]
    if valid_entropies:
        valid_indices = [i for i, e in enumerate(entropies) if e > 0]
        axes[0, 2].plot(valid_indices, valid_entropies, alpha=0.3, color='teal')
        for ep in phase_episodes:
            if ep < len(entropies):
                axes[0, 2].axvline(x=ep, color='green', linestyle='--', alpha=0.5)
        axes[0, 2].set_xlabel('Episode')
        axes[0, 2].set_ylabel('Entropy')
        axes[0, 2].set_title('Policy Entropy')
        axes[0, 2].grid(True)
    
    # Rotation ratio
    valid_rotations = [r for r in rotations if not np.isnan(r)]
    if valid_rotations:
        axes[1, 0].plot(valid_rotations, alpha=0.3, color='orange')
        if len(valid_rotations) > 10:
            window = min(50, len(valid_rotations) // 10)
            smoothed = np.convolve(valid_rotations, np.ones(window)/window, mode='valid')
            axes[1, 0].plot(range(window-1, len(valid_rotations)), smoothed, color='red', linewidth=2)
        axes[1, 0].set_xlabel('Episode')
        axes[1, 0].set_ylabel('Rotation Ratio')
        axes[1, 0].set_title('Rotation vs Fire Ratio')
        axes[1, 0].grid(True)
    
    # Episode lengths
    axes[1, 1].plot(lengths, alpha=0.3, color='green')
    if len(lengths) > 10:
        window = min(50, len(lengths) // 10)
        smoothed = np.convolve(lengths, np.ones(window)/window, mode='valid')
        axes[1, 1].plot(range(window-1, len(lengths)), smoothed, color='red', linewidth=2)
    axes[1, 1].set_xlabel('Episode')
    axes[1, 1].set_ylabel('Steps')
    axes[1, 1].set_title('Episode Lengths')
    axes[1, 1].grid(True)
    
    # Loss
    valid_losses = [l for l in losses if l > 0]
    if valid_losses:
        valid_indices = [i for i, l in enumerate(losses) if l > 0]
        axes[1, 2].plot(valid_indices, valid_losses, alpha=0.3, color='orange')
        if len(valid_losses) > 10:
            window = min(50, len(valid_losses) // 10)
            smoothed = np.convolve(valid_losses, np.ones(window)/window, mode='valid')
            axes[1, 2].plot(valid_indices[window-1:], smoothed, color='red', linewidth=2)
        axes[1, 2].set_xlabel('Episode')
        axes[1, 2].set_ylabel('Loss')
        axes[1, 2].set_title('Training Loss')
        axes[1, 2].grid(True)
    
    plt.tight_layout()
    plot_path = os.path.join(save_dir, 'a2c_curriculum_training_curves.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"📊 Training curves saved to {plot_path}")
    plt.close()

if __name__ == "__main__":
    import argparse
    import torch
    
    parser = argparse.ArgumentParser(description='Train A2C with curriculum learning')
    parser.add_argument('--episodes', type=int, default=20000, help='Total training episodes')
    parser.add_argument('--max-steps', type=int, default=300, help='Max steps per episode')
    parser.add_argument('--save-freq', type=int, default=1000, help='Save frequency')
    parser.add_argument('--save-dir', type=str, default='models', help='Save directory')
    parser.add_argument('--device', type=str, default='auto', help='Device (auto/cpu/cuda)')
    parser.add_argument('--resume-from', type=str, default=None, help='Resume from checkpoint')
    parser.add_argument('--eval-freq', type=int, default=200, help='Evaluation frequency in episodes (default: 200, set to 0 to disable)')
    parser.add_argument('--eval-episodes', type=int, default=20, help='Number of episodes for evaluation (default: 20)')
    parser.add_argument('--eval-start-episode', type=int, default=1000, help='Start evaluation after this episode (default: 1000)')
    
    args = parser.parse_args()
    
    if args.device == 'auto':
        args.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    train_curriculum_a2c(
        episodes=args.episodes,
        max_steps=args.max_steps,
        save_freq=args.save_freq,
        save_dir=args.save_dir,
        device=args.device,
        resume_from=args.resume_from,
        eval_freq=args.eval_freq,
        eval_episodes=args.eval_episodes,
        eval_start_episode=args.eval_start_episode
    )

