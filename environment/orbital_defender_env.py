import gymnasium as gym
import numpy as np
import math

class OrbitalDefenderEnv(gym.Env):
    def __init__(self):
        super().__init__()

        # Actions: rotate left, rotate right, fire
        self.action_space = gym.spaces.Discrete(3)

        # Observation:
        # turret_angle +
        # 2 closest asteroids (angle, distance, angular_velocity, angle_diff)
        # angle_diff = shortest angle difference between turret and asteroid
        self.observation_space = gym.spaces.Box(
            low=np.array([-math.pi] + [-math.pi, 0.0, -1.0, 0.0] * 2),
            high=np.array([ math.pi] + [ math.pi, 10.0,  1.0, math.pi] * 2),
            dtype=np.float32
        )

        self.planet_radius = 2.0
        self.max_asteroids = 5
        self.consecutive_hits = 0  # Track consecutive hits for bonus
        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.turret_angle = 0.0
        self.steps = 0
        self.consecutive_hits = 0  # Reset consecutive hits counter
        self.asteroids_destroyed_this_episode = 0  # Track total destroyed
        self.prev_angle_diff = math.pi  # Initialize previous angle difference

        # Create asteroids
        self.asteroids = []
        for _ in range(self.max_asteroids):
            self.asteroids.append({
                "angle": np.random.uniform(-math.pi, math.pi),
                "distance": np.random.uniform(6.0, 10.0),
                "angular_velocity": np.random.uniform(-0.2, 0.2)
            })

        return self._get_obs(), {}

    def _get_obs(self):
        # Sort asteroids by distance (closest first)
        asts = sorted(self.asteroids, key=lambda a: a["distance"])[:2]

        obs = [self.turret_angle]

        # Always include 2 asteroids (pad with default values if fewer exist)
        for i in range(2):
            if i < len(asts):
                # Calculate angle difference with wrap-around
                angle_diff = abs(self.turret_angle - asts[i]["angle"])
                if angle_diff > math.pi:
                    angle_diff = 2 * math.pi - angle_diff
                
                obs.extend([
                    asts[i]["angle"], 
                    asts[i]["distance"], 
                    asts[i]["angular_velocity"],
                    angle_diff  # Add angle difference directly!
                ])
            else:
                # Pad with default values: angle=0, distance=10.0 (far away), angular_velocity=0, angle_diff=pi (max)
                obs.extend([0.0, 10.0, 0.0, math.pi])

        return np.array(obs, dtype=np.float32)

    def step(self, action):
        self.steps += 1
        reward = 0.0  # Start with zero, build up rewards
        terminated = False

        # Rotate turret
        if action == 0:
            self.turret_angle -= 0.1
        elif action == 1:
            self.turret_angle += 0.1

        self.turret_angle = (self.turret_angle + math.pi) % (2 * math.pi) - math.pi

        # Move asteroids
        asteroids_to_remove = []
        closest_asteroid = None
        min_distance = float('inf')
        dangerous_asteroids = []  # Track asteroids getting too close
        
        for a in self.asteroids:
            a["angle"] += a["angular_velocity"]
            a["distance"] -= 0.03  # Slower movement (was 0.05) - gives agent more time

            # Track closest asteroid for reward shaping
            if a["distance"] < min_distance:
                min_distance = a["distance"]
                closest_asteroid = a
            
            # Track dangerous asteroids (close to planet)
            if a["distance"] < 5.0:
                dangerous_asteroids.append(a)

            # Planet impact - CRITICAL FAILURE
            if a["distance"] <= self.planet_radius:
                # MUCH stronger penalty for impact
                reward = -500.0  # Increased from -200.0 to -500.0
                terminated = True
                self.consecutive_hits = 0  # Reset streak on failure
                return self._get_obs(), reward, terminated, False, {}

        # ========== ENHANCED REWARD SHAPING ==========
        
        # Track previous angle difference for movement reward
        if not hasattr(self, 'prev_angle_diff'):
            self.prev_angle_diff = math.pi  # Initialize to max difference
        
        # 1. TURRET MOVEMENT REWARD: Reward for moving turret TOWARD closest asteroid
        if closest_asteroid and not terminated:
            angle_diff = abs(self.turret_angle - closest_asteroid["angle"])
            
            # Reward for REDUCING angle difference (moving toward target)
            if angle_diff < self.prev_angle_diff:
                # Calculate improvement
                improvement = self.prev_angle_diff - angle_diff
                # Strong reward for moving toward target
                movement_reward = 2.0 * improvement / math.pi  # Scale by improvement
                reward += movement_reward
                
                # Extra bonus for getting very close
                if angle_diff < 0.3:  # Within 17 degrees
                    tracking_bonus = 1.0 * (0.3 - angle_diff) / 0.3
                    reward += tracking_bonus
            
            # Penalty for moving AWAY from target (but small to not discourage exploration)
            elif angle_diff > self.prev_angle_diff:
                penalty = -0.1 * (angle_diff - self.prev_angle_diff) / math.pi
                reward += penalty
            
            # Update previous angle difference
            self.prev_angle_diff = angle_diff
            
            # Normalize angle difference to [0, 1]
            normalized_angle_diff = min(angle_diff / math.pi, 1.0)
            
            # 2. AIMING REWARD: Stronger reward for good aim (encourage precise aiming)
            if normalized_angle_diff < 0.15:  # Very close to target (< 27°)
                aim_reward = 1.5 * (1.0 - normalized_angle_diff / 0.15)  # Increased from 0.5
                reward += aim_reward
            elif normalized_angle_diff < 0.3:  # Getting close (< 54°)
                aim_reward = 0.8 * (1.0 - (normalized_angle_diff - 0.15) / 0.15)  # Increased from 0.2
                reward += aim_reward
            elif normalized_angle_diff < 0.5:  # Moderate alignment (< 90°)
                aim_reward = 0.3 * (1.0 - (normalized_angle_diff - 0.3) / 0.2)
                reward += aim_reward
            
            # 3. URGENCY REWARD: MUCH stronger reward for tracking dangerous asteroids
            if closest_asteroid["distance"] < 5.0:  # Very close!
                urgency_reward = 5.0 * (5.0 - closest_asteroid["distance"]) / 3.0  # Increased from 2.0 to 5.0
                reward += urgency_reward
                
                # Extra bonus if also aiming at it
                if normalized_angle_diff < 0.25:  # More forgiving
                    reward += 2.0  # Increased from 1.0 to 2.0
                
                # CRITICAL: Extra reward if very close (distance < 3.0)
                if closest_asteroid["distance"] < 3.0:
                    critical_reward = 10.0 * (3.0 - closest_asteroid["distance"]) / 2.0
                    reward += critical_reward
                    
                    # Extra bonus for being well-aimed at critical asteroid
                    if normalized_angle_diff < 0.25:  # Well-aimed at critical target
                        critical_aim_bonus = 5.0
                        reward += critical_aim_bonus
            
            # 3. EARLY DESTRUCTION REWARD: Encourage destroying asteroids early
            if closest_asteroid["distance"] > 7.0:  # Far away
                early_bonus = 0.5 * (closest_asteroid["distance"] - 7.0) / 3.0  # Increased from 0.3
                reward += early_bonus
        
        # 4. EFFICIENCY REWARD: MUCH stronger reward for each step without planet impact
        if not terminated and len(self.asteroids) > 0:
            reward += 1.0  # Increased from 0.5 to 1.0 - VERY strong signal for survival
            
            # Bonus for surviving with fewer asteroids (closer to victory)
            survival_bonus = (5.0 - len(self.asteroids)) * 0.5  # Increased from 0.3 to 0.5
            reward += survival_bonus
            
            # EXTRA bonus for preventing close asteroids from impacting
            if dangerous_asteroids:
                # Reward for each dangerous asteroid that hasn't hit yet
                danger_prevention_bonus = len(dangerous_asteroids) * 2.0  # 2.0 per dangerous asteroid
                reward += danger_prevention_bonus
        
        # 5. PROGRESS REWARD: Reward for reducing asteroid count
        remaining_asteroids = len(self.asteroids)
        if remaining_asteroids < self.max_asteroids:
            progress_reward = 0.2 * (self.max_asteroids - remaining_asteroids)
            reward += progress_reward

        # ========== FIRE ACTION WITH ENHANCED REWARDS ==========
        if action == 2:
            hit = False
            hit_asteroid = None
            closest_asteroid_for_fire = None
            min_angle_diff = float('inf')
            
            # Find closest asteroid and calculate angle difference
            for a in self.asteroids:
                # Calculate angle difference with proper wrap-around handling
                angle_diff = abs(self.turret_angle - a["angle"])
                # Handle wrap-around (shortest angle difference)
                if angle_diff > math.pi:
                    angle_diff = 2 * math.pi - angle_diff
                
                if angle_diff < min_angle_diff:
                    min_angle_diff = angle_diff
                    closest_asteroid_for_fire = a
                
                # Check if this asteroid can be hit
                if angle_diff < 0.25 and a["distance"] < 8.0:  # Within tolerance and range
                    hit_asteroid = a
                    hit = True
                    break
            
            # BALANCED PENALTY/REWARD for firing based on alignment
            if not hit and closest_asteroid_for_fire:
                # Calculate how bad the aim is (normalize to 0-1)
                normalized_bad_aim = min(min_angle_diff / math.pi, 1.0)
                
                # If well-aligned but missed (encourage good attempts)
                if min_angle_diff < 0.3:  # Within 17 degrees - good attempt!
                    good_attempt_reward = 2.0 * (0.3 - min_angle_diff) / 0.3  # Reward for good aim attempt
                    reward += good_attempt_reward
                    # Small miss penalty (much less discouraging)
                    reward -= 0.5  # Reduced from -0.1 to -0.5 for well-aimed misses
                
                # Moderate penalty for moderately bad aim
                elif min_angle_diff < 0.5:  # 17-29 degrees off
                    moderate_penalty = -2.0 * (min_angle_diff - 0.3) / 0.2
                    reward += moderate_penalty
                
                # Strong penalty for bad aim
                elif min_angle_diff < 1.0:  # 29-57 degrees off
                    bad_aim_penalty = -5.0 * (min_angle_diff - 0.5) / 0.5
                    reward += bad_aim_penalty
                
                # Severe penalty for very bad aim
                else:  # More than 57 degrees off
                    severe_penalty = -10.0 * min(normalized_bad_aim, 1.0)
                    reward += severe_penalty
            
            if hit and hit_asteroid:
                # Base hit reward (increased to make good hits more attractive)
                base_reward = 50.0  # Increased from 30.0 to 50.0
                
                # Distance bonus: More reward for hitting closer asteroids (urgency)
                distance_factor = (8.0 - hit_asteroid["distance"]) / 6.0  # Adjusted for new range
                distance_bonus = 20.0 * distance_factor  # Increased from 15.0 to 20.0
                
                # Calculate angle difference with wrap-around for accuracy bonus
                angle_diff_for_bonus = abs(self.turret_angle - hit_asteroid["angle"])
                if angle_diff_for_bonus > math.pi:
                    angle_diff_for_bonus = 2 * math.pi - angle_diff_for_bonus
                
                # Accuracy bonus: More reward for precise hits
                angle_factor = 1.0 - (angle_diff_for_bonus / 0.25)  # Updated for new tolerance
                accuracy_bonus = 5.0 * angle_factor  # 0-5 bonus
                
                # Progressive hit bonus: Reward for consecutive hits
                self.consecutive_hits += 1
                streak_bonus = min(self.consecutive_hits * 2.0, 10.0)  # Max 10 bonus
                
                # Early destruction bonus: Extra reward for hitting far asteroids
                if hit_asteroid["distance"] > 8.5:
                    early_destruction_bonus = 10.0  # Increased from 5.0
                elif hit_asteroid["distance"] > 7.5:
                    early_destruction_bonus = 5.0
                else:
                    early_destruction_bonus = 0.0
                
                # Total hit reward
                total_hit_reward = (base_reward + distance_bonus + accuracy_bonus + 
                                    streak_bonus + early_destruction_bonus)
                reward = total_hit_reward
                
                asteroids_to_remove.append(hit_asteroid)
                self.asteroids_destroyed_this_episode += 1
                
            else:
                # This case is handled above with alignment-based rewards/penalties
                # Only handle case where no asteroids exist
                if not closest_asteroid_for_fire:
                    reward -= 0.1  # Small penalty if firing with no targets
                self.consecutive_hits = 0  # Reset streak on miss
        
        # Remove destroyed asteroids
        for a in asteroids_to_remove:
            if a in self.asteroids:
                self.asteroids.remove(a)
        
        # ========== EPISODE COMPLETION BONUSES ==========
        
        # Bonus for clearing all asteroids (PERFECT EPISODE)
        if len(self.asteroids) == 0 and not terminated:
            completion_bonus = 100.0  # Increased from 50.0 - MUCH larger bonus
            efficiency_bonus = max(0, 20.0 - self.steps * 0.05)  # Increased from 10.0
            reward += completion_bonus + efficiency_bonus
            terminated = True
        
        # Episode limit reached (timeout)
        if self.steps >= 300:
            # CRITICAL: Bonus for surviving episode without impact (even if asteroids remain)
            if not terminated:  # Episode ended by max steps, no impact
                survival_bonus = 100.0  # Increased from 30.0 to 100.0 - MUCH larger bonus
                remaining_penalty = len(self.asteroids) * 10.0  # Increased from 5.0 to 10.0
                reward += survival_bonus - remaining_penalty
            else:
                # Small penalty for timeout with impact
                if len(self.asteroids) > 0:
                    reward -= 5.0  # Penalty for not clearing
            terminated = True

        return self._get_obs(), reward, terminated, False, {}
