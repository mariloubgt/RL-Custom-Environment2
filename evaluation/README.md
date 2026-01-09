# Evaluation Scripts

This folder contains scripts for evaluating and comparing reinforcement learning agents.

## Files

- **`compare_algorithms.py`**: Compares A2C and DQN algorithms side-by-side
- **`evaluate_a2c.py`**: Comprehensive evaluation of A2C agent performance

## Usage

### Compare Algorithms

Compare A2C and DQN agents:

```bash
python evaluation/compare_algorithms.py --episodes 100
```

**Options:**
- `--a2c-model`: Path to A2C model (default: models/a2c_model_final.pth)
- `--dqn-model`: Path to DQN model (default: models/dqn_model_final.pth)
- `--episodes`: Number of evaluation episodes per agent (default: 100)
- `--max-steps`: Maximum steps per episode (default: 300)
- `--device`: Device to use (auto/cpu/cuda, default: auto)
- `--save-dir`: Directory to save results (default: evaluation)

**Output:**
- Comparison table in console
- `comparison_summary.csv`: Summary statistics
- `comparison_detailed.csv`: Episode-by-episode results
- `algorithm_comparison.png`: Visualization plots

### Evaluate A2C Agent

Evaluate A2C agent performance:

```bash
python evaluation/evaluate_a2c.py --episodes 100
```

**Options:**
- `--model`: Path to A2C model (default: models/a2c_model_final.pth)
- `--episodes`: Number of evaluation episodes (default: 100)
- `--max-steps`: Maximum steps per episode (default: 300)
- `--device`: Device to use (auto/cpu/cuda, default: auto)
- `--save-dir`: Directory to save results (default: evaluation)

**Output:**
- Detailed statistics in console
- `a2c_evaluation_summary.csv`: Summary statistics
- `a2c_evaluation_detailed.csv`: Episode-by-episode results
- `a2c_evaluation_results.png`: Comprehensive visualization plots

## Example Commands

```bash
# Compare both algorithms with 200 episodes each
python evaluation/compare_algorithms.py --episodes 200

# Evaluate specific A2C model
python evaluation/evaluate_a2c.py --model models/a2c_model_episode_3000.pth --episodes 50

# Compare with custom model paths
python evaluation/compare_algorithms.py \
    --a2c-model models/a2c_model_episode_3000.pth \
    --dqn-model models/dqn_model_episode_2000.pth \
    --episodes 100
```

## Metrics Tracked

- **Reward**: Episode cumulative reward
- **Hit Rate**: Percentage of shots that hit asteroids
- **Asteroids Destroyed**: Number of asteroids destroyed per episode
- **Success Rate**: Percentage of episodes with positive reward
- **Perfect Episodes**: Episodes where all asteroids were destroyed
- **Failure Episodes**: Episodes where planet was hit
- **Episode Length**: Number of steps per episode

