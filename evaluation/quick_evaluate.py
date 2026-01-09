"""
Quick Evaluation Function
Fast evaluation during training to check agent performance
"""

import numpy as np
from environment.orbital_defender_env import OrbitalDefenderEnv

def quick_evaluate(agent, num_episodes=20, max_steps=300, device='cpu'):
    """
    Quick evaluation of agent during training
    
    Returns:
        dict with metrics: avg_reward, std_reward, destruction_rate, 
        success_rate, impact_rate, mean_asteroids_destroyed
    """
    env = OrbitalDefenderEnv()
    
    episode_rewards = []
    asteroids_destroyed_list = []
    success_episodes = 0
    failure_episodes = 0
    total_asteroids_possible = 0
    
    for episode in range(num_episodes):
        state, _ = env.reset()
        episode_reward = 0
        asteroids_destroyed = 0
        initial_asteroid_count = len(env.asteroids)
        total_asteroids_possible += initial_asteroid_count
        episode_ended_with_impact = False
        
        for step in range(max_steps):
            # Select action (no exploration during evaluation)
            action = agent.select_action(state, training=False)
            
            # Take step
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            episode_reward += reward
            
            # Track asteroids destroyed (check if asteroid was hit)
            if action == 2:  # Fire action
                if reward > 5:  # Hit reward is positive and > 5
                    asteroids_destroyed += 1
            
            # Check if planet was hit (terminated with large negative reward)
            if terminated and reward < -50:
                episode_ended_with_impact = True
            
            state = next_state
            
            if done:
                break
        
        episode_rewards.append(episode_reward)
        asteroids_destroyed_list.append(asteroids_destroyed)
        
        if episode_ended_with_impact:
            failure_episodes += 1
        
        if episode_reward > 0:
            success_episodes += 1
    
    # Calculate metrics
    avg_reward = np.mean(episode_rewards)
    std_reward = np.std(episode_rewards)
    
    total_asteroids_destroyed = np.sum(asteroids_destroyed_list)
    destruction_rate = (total_asteroids_destroyed / total_asteroids_possible * 100) if total_asteroids_possible > 0 else 0.0
    
    success_rate = (success_episodes / num_episodes * 100)
    impact_rate = (failure_episodes / num_episodes * 100)
    mean_asteroids_destroyed = np.mean(asteroids_destroyed_list)
    
    return {
        'avg_reward': avg_reward,
        'std_reward': std_reward,
        'destruction_rate': destruction_rate,
        'success_rate': success_rate,
        'impact_rate': impact_rate,
        'mean_asteroids_destroyed': mean_asteroids_destroyed,
        'total_asteroids_destroyed': total_asteroids_destroyed,
        'total_asteroids_possible': total_asteroids_possible
    }

