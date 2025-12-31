"""
Orbital Defender Visualization Application

Professional visualization tool for trained RL agents.
Can be run as a module: python -m app.app
"""

import sys
import os
import argparse
import torch
import numpy as np
import time
from pathlib import Path

# Add parent directory to path for imports
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from environment.orbital_defender_env import OrbitalDefenderEnv
from agents.dqn_agent import DQNAgent
from agents.a2c_agent import A2CAgent
from app.renderer import OrbitalDefenderRenderer

def load_agent(agent_type: str, model_path: str, device: str = 'cpu'):
    """Load a trained agent from a model file"""
    env = OrbitalDefenderEnv()
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    if agent_type.lower() == 'dqn':
        agent = DQNAgent(
            state_dim=state_dim,
            action_dim=action_dim,
            device=device
        )
        agent.load(model_path)
        agent.epsilon = 0.0  # No exploration during visualization
        return agent, 'DQN'
    
    elif agent_type.lower() == 'a2c':
        agent = A2CAgent(
            state_dim=state_dim,
            action_dim=action_dim,
            device=device
        )
        agent.load(model_path)
        return agent, 'A2C'
    
    else:
        raise ValueError(f"Unknown agent type: {agent_type}. Use 'dqn' or 'a2c'")

def visualize_agent(
    agent_type: str = 'dqn',
    model_path: str = None,
    episodes: int = 5,
    steps_per_episode: int = 300,
    fps: int = 60,
    device: str = 'auto',
    speed: float = 1.0
):
    """Visualize a trained agent playing the game"""
    
    # Auto-detect device
    if device == 'auto':
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # Default model path
    if model_path is None:
        models_dir = Path(__file__).parent.parent / 'models'
        if agent_type.lower() == 'dqn':
            model_path = models_dir / 'dqn_model_final.pth'
        else:
            model_path = models_dir / 'a2c_model_final.pth'
        
        if not model_path.exists():
            print(f"❌ Error: Model file not found at {model_path}")
            print("   Please train an agent first or specify a model path with --model-path")
            print(f"   Available models in {models_dir}:")
            if models_dir.exists():
                for f in sorted(models_dir.glob(f"{agent_type.lower()}_model*.pth")):
                    print(f"     - {f.name}")
            return
    
    # Load agent
    print(f"🔄 Loading {agent_type.upper()} agent from {model_path}...")
    try:
        agent, agent_name = load_agent(agent_type, str(model_path), device)
        print(f"✅ Agent loaded successfully!")
        if device == 'cuda':
            print(f"   Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            print(f"   Using CPU")
    except Exception as e:
        print(f"❌ Error loading agent: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Create environment and renderer
    env = OrbitalDefenderEnv()
    renderer = OrbitalDefenderRenderer(fps=fps)
    
    print(f"\n🚀 Starting visualization...")
    print(f"   Press ESC or close window to exit")
    print(f"   Press F3 to toggle FPS display")
    print(f"   Running {episodes} episodes\n")
    print("=" * 60)
    
    # Statistics
    total_episodes = 0
    total_rewards = []
    total_asteroids_destroyed = 0
    episode_times = []
    
    running = True
    current_episode = 0
    
    try:
        while running and current_episode < episodes:
            state, _ = env.reset()
            episode_reward = 0
            episode_steps = 0
            asteroids_destroyed_this_episode = 0
            initial_asteroid_count = len(env.asteroids)
            episode_start_time = time.time()
            
            episode_done = False
            
            while running and not episode_done:
                # Handle events
                running = renderer.handle_events()
                if not running:
                    break
                
                # Agent selects action
                action = agent.select_action(state, training=False)
                
                # Take step
                next_state, reward, terminated, truncated, _ = env.step(action)
                done = terminated or truncated
                
                episode_reward += reward
                episode_steps += 1
                
                # Check if asteroid was destroyed
                if action == 2 and reward > 5:  # Fire action with positive reward
                    asteroids_destroyed_this_episode += 1
                    total_asteroids_destroyed += 1
                    # Create explosion effect at asteroid position
                    if env.asteroids:
                        # Find the destroyed asteroid (closest one that was hit)
                        closest = min(env.asteroids, key=lambda a: a["distance"])
                        x, y = renderer.world_to_screen(closest["angle"], closest["distance"])
                        renderer.create_explosion(x, y, color=(255, 100, 0), size='large')
                
                # Render multiple frames per step for smooth animation
                for _ in range(3):  # Render 3 frames per step for smoother animation
                    stats = {
                        'episode': current_episode + 1,
                        'step': episode_steps,
                        'reward': reward,
                        'total_reward': episode_reward,
                        'asteroids_destroyed': asteroids_destroyed_this_episode,
                        'agent_type': agent_name
                    }
                    renderer.render(env, action=action, stats=stats)
                    time.sleep(0.05)  # Slow down animation - 50ms delay per frame
                
                state = next_state
                
                if done:
                    episode_done = True
                    current_episode += 1
                    total_episodes += 1
                    total_rewards.append(episode_reward)
                    episode_time = time.time() - episode_start_time
                    episode_times.append(episode_time)
                    
                    print(f"Episode {current_episode}/{episodes} | "
                          f"Steps: {episode_steps:3d} | "
                          f"Reward: {episode_reward:7.2f} | "
                          f"Destroyed: {asteroids_destroyed_this_episode}/{initial_asteroid_count} | "
                          f"Time: {episode_time:.2f}s")
                    
                    # Wait a bit before next episode
                    time.sleep(1.5)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Visualization interrupted by user")
    
    finally:
        # Print summary
        if total_episodes > 0:
            avg_reward = np.mean(total_rewards)
            std_reward = np.std(total_rewards)
            avg_time = np.mean(episode_times)
            print("\n" + "=" * 60)
            print("📊 VISUALIZATION SUMMARY")
            print("=" * 60)
            print(f"Episodes Completed:     {total_episodes}")
            print(f"Average Reward:          {avg_reward:.2f} ± {std_reward:.2f}")
            print(f"Best Reward:             {max(total_rewards):.2f}")
            print(f"Worst Reward:            {min(total_rewards):.2f}")
            print(f"Total Asteroids Destroyed: {total_asteroids_destroyed}")
            print(f"Average Episode Time:    {avg_time:.2f}s")
            print(f"Total Time:              {sum(episode_times):.2f}s")
            print("=" * 60)
        
        renderer.quit()

def visualize_human():
    """Allow human to play the game manually"""
    import pygame
    
    env = OrbitalDefenderEnv()
    renderer = OrbitalDefenderRenderer()
    
    print("\n" + "=" * 60)
    print("🎮 HUMAN PLAY MODE")
    print("=" * 60)
    print("Controls:")
    print("  ← LEFT ARROW / A  - Rotate turret left")
    print("  → RIGHT ARROW / D - Rotate turret right")
    print("  SPACE             - Fire")
    print("  ESC               - Exit")
    print("  F3                - Toggle FPS display")
    print("=" * 60 + "\n")
    
    state, _ = env.reset()
    episode_reward = 0
    episode_steps = 0
    asteroids_destroyed = 0
    episode_num = 1
    
    running = True
    
    try:
        while running:
            running = renderer.handle_events()
            if not running:
                break
            
            # Get keyboard input
            keys = pygame.key.get_pressed()
            action = None
            
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                action = 0  # Rotate left
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                action = 1  # Rotate right
            elif keys[pygame.K_SPACE]:
                action = 2  # Fire
            
            if action is not None:
                next_state, reward, terminated, truncated, _ = env.step(action)
                done = terminated or truncated
                
                episode_reward += reward
                episode_steps += 1
                
                if action == 2 and reward > 5:
                    asteroids_destroyed += 1
                    if env.asteroids:
                        closest = min(env.asteroids, key=lambda a: a["distance"])
                        x, y = renderer.world_to_screen(closest["angle"], closest["distance"])
                        renderer.create_explosion(x, y, color=(255, 100, 0), size='large')
                
                state = next_state
                
                if done:
                    print(f"Episode {episode_num} ended! "
                          f"Steps: {episode_steps}, "
                          f"Reward: {episode_reward:.2f}, "
                          f"Asteroids Destroyed: {asteroids_destroyed}")
                    state, _ = env.reset()
                    episode_reward = 0
                    episode_steps = 0
                    asteroids_destroyed = 0
                    episode_num += 1
                    time.sleep(1.0)
            
            stats = {
                'episode': episode_num,
                'step': episode_steps,
                'reward': 0,
                'total_reward': episode_reward,
                'asteroids_destroyed': asteroids_destroyed,
                'agent_type': 'Human'
            }
            renderer.render(env, action=action, stats=stats)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Game interrupted by user")
    
    finally:
        renderer.quit()

def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(
        description='Orbital Defender - RL Agent Visualization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m app.app --agent dqn --episodes 5
  python -m app.app --agent a2c --model-path models/a2c_model_episode_1000.pth
  python -m app.app --agent human
        """
    )
    parser.add_argument('--agent', type=str, default='dqn', 
                       choices=['dqn', 'a2c', 'human'],
                       help='Agent type to visualize (default: dqn)')
    parser.add_argument('--model-path', type=str, default=None,
                       help='Path to model file (default: models/{agent}_model_final.pth)')
    parser.add_argument('--episodes', type=int, default=5,
                       help='Number of episodes to visualize (default: 5)')
    parser.add_argument('--fps', type=int, default=60,
                       help='Frames per second (default: 60)')
    parser.add_argument('--device', type=str, default='auto',
                       choices=['auto', 'cpu', 'cuda'],
                       help='Device to use (default: auto)')
    parser.add_argument('--speed', type=float, default=1.0,
                       help='Playback speed multiplier (default: 1.0)')
    
    args = parser.parse_args()
    
    if args.agent == 'human':
        visualize_human()
    else:
        visualize_agent(
            agent_type=args.agent,
            model_path=args.model_path,
            episodes=args.episodes,
            fps=args.fps,
            device=args.device,
            speed=args.speed
        )

if __name__ == "__main__":
    main()
