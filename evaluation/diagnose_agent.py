"""
Agent Diagnostic Tool
Analyzes why the agent is performing poorly and suggests fixes
"""

import os
import sys
import numpy as np
import math
from pathlib import Path
import argparse
import torch

sys.path.append(str(Path(__file__).parent.parent))

from environment.orbital_defender_env import OrbitalDefenderEnv
from agents.a2c_agent import A2CAgent

def diagnose_agent(model_path=None, num_episodes=20, device='cpu'):
    """Diagnose agent behavior to understand why performance is poor"""
    
    env = OrbitalDefenderEnv()
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    if model_path is None:
        models_dir = Path(__file__).parent.parent / 'models'
        model_path = models_dir / 'a2c_model_final.pth'
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        return
    
    agent = A2CAgent(state_dim=state_dim, action_dim=action_dim, device=device)
    agent.load(str(model_path))
    
    print(f"\n{'='*70}")
    print("AGENT DIAGNOSTIC ANALYSIS")
    print(f"{'='*70}\n")
    
    # Track detailed statistics
    action_distribution = {0: 0, 1: 0, 2: 0}  # Rotate left, right, fire
    firing_angles = []  # Angle differences when firing
    firing_distances = []  # Distances when firing
    hit_angles = []  # Angle differences when hitting
    miss_angles = []  # Angle differences when missing
    closest_asteroid_distances = []
    turret_angle_changes = []
    
    for episode in range(num_episodes):
        state, _ = env.reset()
        prev_turret_angle = None
        
        for step in range(300):
            # Get closest asteroid info
            if env.asteroids:
                closest = min(env.asteroids, key=lambda a: a["distance"])
                closest_asteroid_distances.append(closest["distance"])
                angle_to_closest = abs(env.turret_angle - closest["angle"])
            else:
                angle_to_closest = None
            
            # Select action
            action = agent.select_action(state, training=False)
            action_distribution[action] += 1
            
            # Store turret angle BEFORE step
            turret_angle_before = env.turret_angle
            
            # Take step
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            # Track turret movement AFTER step (calculate change)
            if prev_turret_angle is not None:
                # Calculate angle change (handle wrap-around)
                angle_change = abs(env.turret_angle - prev_turret_angle)
                # Handle wrap-around (angles can wrap from -pi to +pi)
                if angle_change > math.pi:
                    angle_change = 2 * math.pi - angle_change
                turret_angle_changes.append(angle_change)
            
            # Analyze firing behavior
            if action == 2:  # Fire
                if env.asteroids:
                    closest = min(env.asteroids, key=lambda a: a["distance"])
                    angle_diff = abs(env.turret_angle - closest["angle"])
                    firing_angles.append(angle_diff)
                    firing_distances.append(closest["distance"])
                    
                    if reward > 5:  # Hit
                        hit_angles.append(angle_diff)
                    else:  # Miss
                        miss_angles.append(angle_diff)
            
            state = next_state
            prev_turret_angle = env.turret_angle  # Update for next iteration
            
            if done:
                break
    
    # Print diagnostics
    print("1. ACTION DISTRIBUTION")
    print("-" * 70)
    total_actions = sum(action_distribution.values())
    for action, count in action_distribution.items():
        action_name = ["Rotate Left", "Rotate Right", "Fire"][action]
        percentage = (count / total_actions * 100) if total_actions > 0 else 0
        print(f"   {action_name:15s}: {count:5d} ({percentage:5.1f}%)")
    print()
    
    print("2. FIRING BEHAVIOR")
    print("-" * 70)
    if firing_angles:
        print(f"   Total Shots Fired:     {len(firing_angles)}")
        print(f"   Shots Hit:             {len(hit_angles)}")
        print(f"   Shots Missed:          {len(miss_angles)}")
        print(f"   Hit Rate:              {len(hit_angles)/len(firing_angles)*100:.1f}%")
        print()
        print(f"   Mean Angle Diff (All):  {np.mean(firing_angles):.4f} rad ({np.degrees(np.mean(firing_angles)):.1f}°)")
        print(f"   Mean Angle Diff (Hit): {np.mean(hit_angles) if hit_angles else 0:.4f} rad ({np.degrees(np.mean(hit_angles)) if hit_angles else 0:.1f}°)")
        print(f"   Mean Angle Diff (Miss): {np.mean(miss_angles) if miss_angles else 0:.4f} rad ({np.degrees(np.mean(miss_angles)) if miss_angles else 0:.1f}°)")
        print()
        print(f"   Required Tolerance:    < 0.25 rad ({np.degrees(0.25):.1f}°)")
        print(f"   Mean Distance (All):    {np.mean(firing_distances):.2f}")
        print(f"   Max Firing Range:       8.0")
    else:
        print("   ⚠️  Agent never fired!")
    print()
    
    print("3. TURRET MOVEMENT")
    print("-" * 70)
    if turret_angle_changes:
        print(f"   Mean Angle Change:      {np.mean(turret_angle_changes):.4f} rad ({np.degrees(np.mean(turret_angle_changes)):.1f}°)")
        print(f"   Max Angle Change:       {np.max(turret_angle_changes):.4f} rad ({np.degrees(np.max(turret_angle_changes)):.1f}°)")
        print(f"   Min Angle Change:       {np.min(turret_angle_changes):.4f} rad ({np.degrees(np.min(turret_angle_changes)):.1f}°)")
    print()
    
    print("4. ASTEROID TRACKING")
    print("-" * 70)
    if closest_asteroid_distances:
        print(f"   Mean Closest Distance:  {np.mean(closest_asteroid_distances):.2f}")
        print(f"   Min Closest Distance:   {np.min(closest_asteroid_distances):.2f}")
        print(f"   Max Closest Distance:   {np.max(closest_asteroid_distances):.2f}")
    print()
    
    # Diagnose problems
    print("5. DIAGNOSIS")
    print("-" * 70)
    issues = []
    recommendations = []
    
    if firing_angles:
        mean_angle_diff = np.mean(firing_angles)
        if mean_angle_diff > 0.25:
            issues.append(f"❌ Agent fires when angle difference is too large ({mean_angle_diff:.3f} > 0.25)")
            recommendations.append("   → Agent doesn't understand when to fire")
            recommendations.append("   → Increase reward for good aiming")
            recommendations.append("   → Make firing tolerance more forgiving during early training")
        
        if len(hit_angles) / len(firing_angles) < 0.1:
            issues.append(f"❌ Hit rate is very low ({len(hit_angles)/len(firing_angles)*100:.1f}%)")
            recommendations.append("   → Agent needs more exploration (increase entropy)")
            recommendations.append("   → Agent needs more training episodes")
            recommendations.append("   → Consider curriculum learning (start with easier settings)")
        
        if np.std(firing_angles) < 0.1:
            issues.append("❌ Agent fires at very similar angles (low variance)")
            recommendations.append("   → Increase entropy coefficient for more exploration")
    else:
        issues.append("❌ Agent never fires")
        recommendations.append("   → Agent is too conservative")
        recommendations.append("   → Increase reward for firing attempts")
        recommendations.append("   → Decrease penalty for misses")
    
    if action_distribution[2] / total_actions < 0.1:
        issues.append(f"❌ Agent fires too rarely ({action_distribution[2]/total_actions*100:.1f}% of actions)")
        recommendations.append("   → Increase reward for firing")
        recommendations.append("   → Decrease miss penalty")
    
    if action_distribution[0] + action_distribution[1] > action_distribution[2] * 10:
        issues.append("❌ Agent rotates much more than it fires")
        recommendations.append("   → Agent may be confused about when to fire")
        recommendations.append("   → Improve state representation")
    
    if issues:
        print("   Issues Found:")
        for issue in issues:
            print(f"   {issue}")
        print()
        print("   Recommendations:")
        for rec in set(recommendations):  # Remove duplicates
            print(f"   {rec}")
    else:
        print("   ✅ No obvious issues detected")
    
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Diagnose agent behavior')
    parser.add_argument('--model', type=str, default=None,
                       help='Path to model (default: models/a2c_model_final.pth)')
    parser.add_argument('--episodes', type=int, default=20,
                       help='Number of diagnostic episodes (default: 20)')
    parser.add_argument('--device', type=str, default='auto',
                       choices=['auto', 'cpu', 'cuda'],
                       help='Device to use (default: auto)')
    
    args = parser.parse_args()
    
    if args.device == 'auto':
        args.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    diagnose_agent(
        model_path=args.model,
        num_episodes=args.episodes,
        device=args.device
    )

