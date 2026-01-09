"""
Adapt existing model from old state representation (7 dims) to new (9 dims)

The new state representation adds angle_diff for each asteroid:
- Old: [turret_angle, a1_angle, a1_dist, a1_vel, a2_angle, a2_dist, a2_vel] (7 dims)
- New: [turret_angle, a1_angle, a1_dist, a1_vel, a1_angle_diff, a2_angle, a2_dist, a2_vel, a2_angle_diff] (9 dims)
"""

import torch
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from agents.a2c_agent import ActorCritic

def adapt_model(old_model_path, new_model_path, old_state_dim=7, new_state_dim=9, action_dim=3):
    """
    Adapt model from old state dimension to new state dimension
    
    Strategy:
    - Keep existing weights for dimensions 0-6 (same in both)
    - Initialize new dimensions (7, 8) with small random weights
    - This allows the model to work immediately, and can be fine-tuned
    """
    
    print(f"🔄 Adapting model from {old_state_dim}D to {new_state_dim}D...")
    
    # Load old model
    print(f"📂 Loading old model: {old_model_path}")
    old_checkpoint = torch.load(old_model_path, map_location='cpu')
    
    # Create new network with new state dimension
    print(f"🏗️  Creating new network with {new_state_dim} dimensions...")
    new_network = ActorCritic(new_state_dim, action_dim)
    
    # Get old network state dict
    old_state_dict = old_checkpoint['network']
    new_state_dict = new_network.state_dict()
    
    # Adapt fc1 layer (input layer)
    print("🔧 Adapting input layer (fc1)...")
    old_fc1_weight = old_state_dict['fc1.weight']  # Shape: [256, 7]
    old_fc1_bias = old_state_dict['fc1.bias']      # Shape: [256]
    
    # Create new weight matrix: [256, 9]
    new_fc1_weight = torch.zeros(256, new_state_dim)
    
    # Copy old weights for dimensions 0-6
    new_fc1_weight[:, :old_state_dim] = old_fc1_weight
    
    # Initialize new dimensions (7, 8) with small random values
    # These correspond to a1_angle_diff and a2_angle_diff
    # Use small values so they don't disrupt existing behavior too much
    torch.nn.init.normal_(new_fc1_weight[:, old_state_dim:], mean=0.0, std=0.01)
    
    new_state_dict['fc1.weight'] = new_fc1_weight
    new_state_dict['fc1.bias'] = old_fc1_bias  # Bias stays the same
    
    # Copy all other layers (they don't change)
    for key in new_state_dict:
        if key not in ['fc1.weight', 'fc1.bias']:
            if key in old_state_dict:
                new_state_dict[key] = old_state_dict[key]
    
    # Load adapted state dict
    new_network.load_state_dict(new_state_dict)
    
    # Create new checkpoint
    # NOTE: Don't copy optimizer - it has state tied to old model dimensions
    # The optimizer will be recreated when training resumes
    new_checkpoint = {
        'network': new_network.state_dict(),
        'episode': old_checkpoint.get('episode', 0),
        # Optimizer not included - will be recreated with correct dimensions
    }
    
    # Save new model
    print(f"💾 Saving adapted model: {new_model_path}")
    torch.save(new_checkpoint, new_model_path)
    
    print("✅ Model adaptation complete!")
    print(f"   Old model: {old_state_dim} dimensions")
    print(f"   New model: {new_state_dim} dimensions")
    print(f"   New dimensions initialized with small random weights")
    print(f"   Model can now be used, but fine-tuning recommended")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Adapt model from old to new state representation')
    parser.add_argument('--old-model', type=str, default='models/a2c_curriculum_final.pth',
                       help='Path to old model (7 dimensions)')
    parser.add_argument('--new-model', type=str, default='models/a2c_curriculum_final_adapted.pth',
                       help='Path to save adapted model (9 dimensions)')
    parser.add_argument('--old-dims', type=int, default=7, help='Old state dimension')
    parser.add_argument('--new-dims', type=int, default=9, help='New state dimension')
    
    args = parser.parse_args()
    
    adapt_model(
        old_model_path=args.old_model,
        new_model_path=args.new_model,
        old_state_dim=args.old_dims,
        new_state_dim=args.new_dims
    )

