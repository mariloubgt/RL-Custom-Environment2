"""
Quick Performance Analysis Script

Analyzes DQN agent evaluation results and provides recommendations.
"""

def analyze_performance(
    episodes=5,
    avg_reward=5.00,
    std_reward=16.50,
    best_reward=30.94,
    worst_reward=-19.50,
    asteroids_destroyed=8,
    total_asteroids=25
):
    """Analyze and print performance assessment"""
    
    asteroids_per_episode = asteroids_destroyed / episodes
    destruction_rate = (asteroids_destroyed / total_asteroids) * 100
    variance_ratio = std_reward / abs(avg_reward) if avg_reward != 0 else float('inf')
    
    print("=" * 70)
    print("DQN AGENT PERFORMANCE ANALYSIS")
    print("=" * 70)
    print(f"\n[Evaluation Metrics]")
    print(f"   Episodes:              {episodes}")
    print(f"   Average Reward:        {avg_reward:.2f} ± {std_reward:.2f}")
    print(f"   Best Reward:           {best_reward:.2f}")
    print(f"   Worst Reward:          {worst_reward:.2f}")
    print(f"   Asteroids Destroyed:   {asteroids_destroyed}/{total_asteroids} ({destruction_rate:.1f}%)")
    print(f"   Per Episode:           {asteroids_per_episode:.2f} asteroids")
    
    print(f"\n[Analysis]")
    
    # Destruction rate assessment
    if destruction_rate >= 80:
        destruction_status = "[OK] EXCELLENT"
    elif destruction_rate >= 60:
        destruction_status = "[!] GOOD"
    elif destruction_rate >= 40:
        destruction_status = "[!] FAIR"
    else:
        destruction_status = "[X] POOR"
    
    print(f"   Destruction Rate:      {destruction_status} ({destruction_rate:.1f}%)")
    print(f"                        Target: >80%, Current: {destruction_rate:.1f}%")
    
    # Variance assessment
    if variance_ratio < 0.5:
        variance_status = "[OK] STABLE"
    elif variance_ratio < 1.0:
        variance_status = "[!] MODERATE VARIANCE"
    else:
        variance_status = "[X] HIGH VARIANCE (UNSTABLE)"
    
    print(f"   Consistency:           {variance_status}")
    print(f"                        Std/Mean ratio: {variance_ratio:.2f}")
    
    # Planet impact check
    if worst_reward <= -19:
        impact_status = "[X] PLANET IMPACTS OCCURRING"
        print(f"   Defense:                {impact_status}")
        print(f"                        Worst reward ({worst_reward:.2f}) indicates planet hits")
    else:
        impact_status = "[OK] NO IMPACTS DETECTED"
        print(f"   Defense:                {impact_status}")
    
    # Overall rating
    print(f"\n[Overall Performance Rating]")
    
    score = 0
    if destruction_rate >= 80:
        score += 40
    elif destruction_rate >= 60:
        score += 30
    elif destruction_rate >= 40:
        score += 20
    else:
        score += 10
    
    if variance_ratio < 1.0:
        score += 30
    elif variance_ratio < 2.0:
        score += 20
    else:
        score += 10
    
    if worst_reward > -19:
        score += 30
    elif worst_reward > -10:
        score += 20
    else:
        score += 10
    
    if best_reward > 25:
        score += 10
    
    if score >= 80:
        rating = "[GREEN] EXCELLENT"
        recommendation = "Agent is performing well! Consider fine-tuning for even better results."
    elif score >= 60:
        rating = "[YELLOW] GOOD"
        recommendation = "Agent shows promise but needs more training and optimization."
    elif score >= 40:
        rating = "[ORANGE] FAIR"
        recommendation = "Agent needs significant improvement. Continue training with hyperparameter tuning."
    else:
        rating = "[RED] NEEDS IMPROVEMENT"
        recommendation = "Agent requires substantial training and optimization. See recommendations below."
    
    print(f"   {rating} (Score: {score}/100)")
    print(f"\n[Recommendation] {recommendation}")
    
    print(f"\n[Performance Targets]")
    print(f"   Current Destruction Rate:  {destruction_rate:.1f}%")
    print(f"   Target Destruction Rate:    >80%")
    print(f"   Current Avg Reward:          {avg_reward:.2f}")
    print(f"   Target Avg Reward:          >15.00")
    print(f"   Current Std/Mean:           {variance_ratio:.2f}")
    print(f"   Target Std/Mean:            <1.00")
    
    print(f"\n[Key Issues Identified]")
    issues = []
    
    if destruction_rate < 60:
        issues.append(f"[X] Low destruction rate ({destruction_rate:.1f}% < 80% target)")
    if variance_ratio > 1.5:
        issues.append(f"[X] High variance (std/mean = {variance_ratio:.2f})")
    if worst_reward <= -19:
        issues.append("[X] Planet impacts occurring (worst reward = -19.50)")
    if episodes < 20:
        issues.append(f"[!] Small sample size ({episodes} episodes - need 50+ for reliable stats)")
    
    if not issues:
        print("   [OK] No major issues detected!")
    else:
        for issue in issues:
            print(f"   {issue}")
    
    print(f"\n[Recommended Actions]")
    print("   1. Continue training for 2000-5000 more episodes")
    print("   2. Re-evaluate on 50-100 episodes for reliable metrics")
    print("   3. Tune hyperparameters (learning rate, epsilon decay)")
    print("   4. Monitor training curves to ensure learning progress")
    print("   5. Consider reward shaping improvements")
    
    print("\n" + "=" * 70)
    
    return {
        'rating': rating,
        'score': score,
        'destruction_rate': destruction_rate,
        'variance_ratio': variance_ratio,
        'has_impacts': worst_reward <= -19
    }

if __name__ == "__main__":
    # Your evaluation results
    results = analyze_performance(
        episodes=5,
        avg_reward=5.00,
        std_reward=16.50,
        best_reward=30.94,
        worst_reward=-19.50,
        asteroids_destroyed=8,
        total_asteroids=25  # 5 episodes × 5 asteroids
    )

