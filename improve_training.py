"""
Quick Start Script for Improved DQN Training

This script provides an easy way to start training with optimized settings.
"""

import sys
from pathlib import Path

# Add training directory to path
sys.path.insert(0, str(Path(__file__).parent))

from training.train_dqn import train_dqn
import torch

def main():
    print("=" * 70)
    print("DQN AGENT IMPROVEMENT TRAINING")
    print("=" * 70)
    print()
    print("This will train your DQN agent with optimized hyperparameters:")
    print("  - Increased learning rate (0.001)")
    print("  - Better epsilon decay schedule")
    print("  - More frequent target network updates")
    print("  - Enhanced reward shaping")
    print("  - Automatic evaluation and checkpointing")
    print()
    print("Recommended: Train for 3000 episodes for best results")
    print()
    
    # Auto-detect device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    if device == 'cuda':
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("Using CPU")
    print()
    
    # Start training with improved settings
    train_dqn(
        episodes=3000,  # Train for 3000 episodes
        max_steps=300,
        target_update_freq=5,  # Update target network every 5 episodes
        save_freq=100,  # Save checkpoint every 100 episodes
        eval_freq=200,  # Evaluate every 200 episodes
        eval_episodes=20,  # Use 20 episodes for evaluation
        save_dir='models',
        device=device
    )
    
    print()
    print("=" * 70)
    print("TRAINING COMPLETE!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Evaluate the trained model:")
    print("   python -m evaluation.evaluate_dqn --model-path models/dqn_model_best.pth --episodes 100")
    print()
    print("2. Visualize the agent:")
    print("   python visualize.py --agent dqn --model-path models/dqn_model_best.pth")
    print()
    print("3. Check training curves:")
    print("   Open: models/dqn_training_curves_improved.png")
    print()

if __name__ == "__main__":
    main()

