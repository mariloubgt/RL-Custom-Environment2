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
        # 2 closest asteroids (angle, distance, angular_velocity)
        self.observation_space = gym.spaces.Box(
            low=np.array([-math.pi] + [-math.pi, 0.0, -1.0] * 2),
            high=np.array([ math.pi] + [ math.pi, 10.0,  1.0] * 2),
            dtype=np.float32
        )

        self.planet_radius = 2.0
        self.max_asteroids = 5
        self.consecutive_hits = 0  # Track consecutive hits for bonus
        self.curriculum_level = None  # For curriculum learning
        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.turret_angle = 0.0
        self.steps = 0
        self.consecutive_hits = 0  # Reset consecutive hits counter
        self.asteroids_destroyed_this_episode = 0  # Track total destroyed

        # Create asteroids (support curriculum learning)
        num_asteroids = self.curriculum_level if self.curriculum_level is not None else self.max_asteroids
        self.asteroids = []
        for _ in range(num_asteroids):
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
                obs.extend([asts[i]["angle"], asts[i]["distance"], asts[i]["angular_velocity"]])
            else:
                # Pad with default values: angle=0, distance=10.0 (far away), angular_velocity=0
                obs.extend([0.0, 10.0, 0.0])

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
            a["distance"] -= 0.015  # Even slower (was 0.02) - gives agent even more time to react

            # Track closest asteroid for reward shaping
            if a["distance"] < min_distance:
                min_distance = a["distance"]
                closest_asteroid = a
            
            # Track dangerous asteroids (close to planet)
            if a["distance"] < 5.0:
                dangerous_asteroids.append(a)
            
            # PROGRESSIVE DISTANCE PENALTY: Penalize asteroids getting too close (NEW)
            # This teaches agent to destroy asteroids BEFORE they get dangerous
            if a["distance"] < 3.0 and a["distance"] > self.planet_radius:
                distance_penalty = -10.0 * (3.0 - a["distance"]) / 1.0  # Up to -10 penalty
                reward += distance_penalty

            # Planet impact - CRITICAL FAILURE
            if a["distance"] <= self.planet_radius:
                reward = -500.0  # Much stronger penalty (was -200) - make it REALLY hurt
                terminated = True
                self.consecutive_hits = 0  # Reset streak on failure
                return self._get_obs(), reward, terminated, False, {}

        # ========== ENHANCED REWARD SHAPING ==========
        
        # 1. Reward for good positioning and aiming (stronger signal)
        if closest_asteroid and not terminated:
            angle_diff = abs(self.turret_angle - closest_asteroid["angle"])
            # Normalize angle difference to [0, 1]
            normalized_angle_diff = min(angle_diff / math.pi, 1.0)
            
            # Stronger reward for good aim (encourage precise aiming)
            if normalized_angle_diff < 0.15:  # Very close to target
                aim_reward = 0.5 * (1.0 - normalized_angle_diff / 0.15)
                reward += aim_reward
            elif normalized_angle_diff < 0.3:  # Getting close
                aim_reward = 0.2 * (1.0 - (normalized_angle_diff - 0.15) / 0.15)
                reward += aim_reward
            
            # 2. URGENCY REWARD: Strong reward for tracking dangerous asteroids
            if closest_asteroid["distance"] < 5.0:  # Very close!
                urgency_reward = 2.0 * (5.0 - closest_asteroid["distance"]) / 3.0  # Increased from 1.0
                reward += urgency_reward
                
                # Extra bonus if also aiming at it
                if normalized_angle_diff < 0.25:  # More forgiving
                    reward += 1.0  # Increased from 0.5
            
            # 3. EARLY DESTRUCTION REWARD: Encourage destroying asteroids early
            if closest_asteroid["distance"] > 7.0:  # Far away
                early_bonus = 0.5 * (closest_asteroid["distance"] - 7.0) / 3.0  # Increased from 0.3
                reward += early_bonus
        
        # 4. EFFICIENCY REWARD: Small reward for each step without planet impact
        if not terminated and len(self.asteroids) > 0:
            reward += 0.5  # Increased from 0.2 - much stronger signal for survival
            
            # 4b. SAFETY REWARD: Strong reward for keeping asteroids at safe distance
            if closest_asteroid:
                safe_distance = closest_asteroid["distance"]
                if safe_distance > 5.0:  # Safe zone
                    safety_reward = 0.3 * (safe_distance - 5.0) / 3.0
                    reward += safety_reward
                elif safe_distance < 4.0:  # Danger zone - small penalty
                    danger_penalty = -0.5 * (4.0 - safe_distance) / 2.0
                    reward += danger_penalty
        
        # 5. PROGRESS REWARD: Reward for reducing asteroid count
        initial_count = self.curriculum_level if self.curriculum_level is not None else self.max_asteroids
        remaining_asteroids = len(self.asteroids)
        if remaining_asteroids < initial_count:
            progress_reward = 1.0 * (initial_count - remaining_asteroids)  # Increased from 0.5
            reward += progress_reward
            
            # Progressive completion bonus: Extra reward for each asteroid destroyed
            destroyed_count = initial_count - remaining_asteroids
            # Stronger bonus for each asteroid destroyed (encourages completion)
            completion_bonus = 5.0 * destroyed_count  # Increased from 2.0 - 5 points per asteroid
            reward += completion_bonus

        # ========== FIRE ACTION WITH ENHANCED REWARDS ==========
        if action == 2:
            hit = False
            hit_asteroid = None
            
            for a in self.asteroids:
                angle_diff = abs(self.turret_angle - a["angle"])
                # Increased firing range and angle tolerance (more forgiving)
                if angle_diff < 0.35 and a["distance"] < 9.5:  # Even wider angle (0.3→0.35), longer range (9.0→9.5)
                    hit_asteroid = a
                    hit = True
                    break
            
            if hit and hit_asteroid:
                # Base hit reward
                base_reward = 30.0
                
                # Distance bonus: More reward for hitting closer asteroids (urgency)
                # BUT: Less reward for hitting VERY close asteroids (encourage early hits)
                if hit_asteroid["distance"] > 6.0:  # Far asteroid - big bonus
                    distance_factor = (9.0 - hit_asteroid["distance"]) / 3.0
                    distance_bonus = 25.0 * distance_factor  # Big bonus for early hits
                else:  # Close asteroid - smaller bonus (should have hit it earlier)
                    distance_factor = (hit_asteroid["distance"] - 3.0) / 3.0
                    distance_bonus = 10.0 * distance_factor  # Smaller bonus
                
                # Accuracy bonus: More reward for precise hits
                angle_factor = 1.0 - (angle_diff / 0.25)  # Updated for new tolerance
                accuracy_bonus = 5.0 * angle_factor  # 0-5 bonus
                
                # Progressive hit bonus: Reward for consecutive hits
                self.consecutive_hits += 1
                streak_bonus = min(self.consecutive_hits * 2.0, 10.0)  # Max 10 bonus
                
                # Early destruction bonus: Extra reward for hitting far asteroids
                if hit_asteroid["distance"] > 8.5:
                    early_destruction_bonus = 20.0  # Increased from 10.0 - much stronger incentive
                elif hit_asteroid["distance"] > 7.5:
                    early_destruction_bonus = 10.0  # Increased from 5.0
                elif hit_asteroid["distance"] > 6.5:
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
                # Miss penalty (but not too harsh to encourage trying)
                reward -= 0.3  # Reduced from 0.5
                self.consecutive_hits = 0  # Reset streak on miss
        
        # Remove destroyed asteroids
        for a in asteroids_to_remove:
            if a in self.asteroids:
                self.asteroids.remove(a)
        
        # ========== EPISODE COMPLETION BONUSES ==========
        
        # Bonus for clearing all asteroids (PERFECT EPISODE)
        if len(self.asteroids) == 0 and not terminated:
            completion_bonus = 50.0  # Reduced from 100.0 to reduce variance
            efficiency_bonus = max(0, 15.0 - self.steps * 0.05)  # Reduced from 20.0
            reward += completion_bonus + efficiency_bonus
            terminated = True
        
        # Episode limit reached (timeout)
        if self.steps >= 300:
            # Small penalty for timeout, but reward for surviving
            if len(self.asteroids) > 0:
                reward -= 5.0  # Penalty for not clearing
            terminated = True

        return self._get_obs(), reward, terminated, False, {}
