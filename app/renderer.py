import pygame
import math
import numpy as np
from typing import List, Tuple, Optional
from collections import deque

class Particle:
    """Enhanced particle for explosion effects"""
    def __init__(self, x, y, vx, vy, color, lifetime=40, size=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size if size else np.random.randint(2, 6)
        self.gravity = 0.1
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.96
        self.vy *= 0.96
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, screen):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        if alpha > 0:
            # Create surface with alpha for better blending
            size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
            color_with_alpha = (*self.color[:3], min(255, alpha))
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

class Bullet:
    """Bullet projectile that travels from turret to target"""
    def __init__(self, start_x, start_y, target_x, target_y, speed=6.0):
        self.x = float(start_x)
        self.y = float(start_y)
        self.target_x = float(target_x)
        self.target_y = float(target_y)
        
        # Calculate direction
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            self.vx = (dx / distance) * speed
            self.vy = (dy / distance) * speed
        else:
            self.vx = 0
            self.vy = 0
        
        self.distance_traveled = 0
        self.total_distance = distance
        self.active = True
        self.trail = deque(maxlen=10)
        self.trail.append((int(start_x), int(start_y)))
    
    def update(self):
        """Update bullet position"""
        if not self.active:
            return False
        
        old_x, old_y = self.x, self.y
        self.x += self.vx
        self.y += self.vy
        self.distance_traveled += math.sqrt(self.vx*self.vx + self.vy*self.vy)
        self.trail.append((int(old_x), int(old_y)))
        
        # Check if reached target or gone too far
        distance_to_target = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)
        if distance_to_target < 8 or self.distance_traveled > self.total_distance * 1.3:
            self.active = False
            return False
        
        return True
    
    def draw(self, screen, colors):
        """Draw bullet with trail"""
        if not self.active:
            return
        
        # Draw trail
        if len(self.trail) > 1:
            points = list(self.trail)
            for i in range(len(points) - 1):
                alpha = int(200 * (i / len(points)))
                pygame.draw.line(screen, colors['projectile_trail'],
                               points[i], points[i + 1], 4)
        
        # Draw bullet glow
        glow_radius = 12
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*colors['projectile_glow'], 200),
                         (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surface, (int(self.x) - glow_radius, int(self.y) - glow_radius))
        
        # Draw bullet core
        pygame.draw.circle(screen, colors['projectile'], (int(self.x), int(self.y)), 7)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 4)

class Trail:
    """Trail effect for moving objects"""
    def __init__(self, max_length=10):
        self.positions = deque(maxlen=max_length)
        self.max_length = max_length
    
    def add(self, x, y):
        self.positions.append((x, y))
    
    def draw(self, screen, color, width=2):
        if len(self.positions) < 2:
            return
        
        points = list(self.positions)
        for i in range(len(points) - 1):
            alpha = int(255 * (i / len(points)))
            color_with_alpha = (*color[:3], min(255, alpha))
            pygame.draw.line(screen, color, points[i], points[i + 1], width)

class Star:
    """Star for starfield background"""
    def __init__(self, x, y, brightness):
        self.x = x
        self.y = y
        self.brightness = brightness
        self.twinkle = np.random.uniform(0, 2 * math.pi)
        self.twinkle_speed = np.random.uniform(0.02, 0.05)
    
    def update(self):
        self.twinkle += self.twinkle_speed
    
    def draw(self, screen):
        twinkle_brightness = int(self.brightness * (0.7 + 0.3 * math.sin(self.twinkle)))
        color = (twinkle_brightness, twinkle_brightness, twinkle_brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 1)

class OrbitalDefenderRenderer:
    """Professional 2D renderer for Orbital Defender environment"""
    
    def __init__(self, width=1400, height=900, scale=45, fullscreen=False, fps=60):
        pygame.init()
        pygame.mixer.init()  # For potential sound effects
        
        self.width = width
        self.height = height
        self.scale = scale
        self.center_x = width // 2
        self.center_y = height // 2
        self.fps = fps
        
        # Display setup
        flags = pygame.FULLSCREEN if fullscreen else 0
        self.screen = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption("Orbital Defender - RL Agent Visualization")
        pygame.display.set_icon(pygame.Surface((32, 32)))
        
        # Enhanced color palette
        self.colors = {
            'background': (8, 8, 16),
            'space': (5, 5, 12),
            'planet': (65, 105, 225),  # Royal blue
            'planet_dark': (25, 25, 112),  # Midnight blue
            'planet_ring': (70, 130, 180),  # Steel blue
            'planet_highlight': (176, 196, 222),  # Light steel blue
            'planet_atmosphere': (135, 206, 250),  # Light sky blue
            'turret': (255, 255, 255),
            'turret_base': (192, 192, 192),
            'turret_glow': (0, 191, 255),  # Deep sky blue
            'turret_shadow': (64, 64, 64),
            'asteroid': (169, 169, 169),  # Dark gray
            'asteroid_highlight': (211, 211, 211),  # Light gray
            'asteroid_danger': (220, 20, 60),  # Crimson
            'asteroid_trail': (128, 128, 128),
            'projectile': (255, 215, 0),  # Gold
            'projectile_trail': (255, 165, 0),  # Orange
            'projectile_glow': (255, 255, 0),  # Yellow
            'text': (255, 255, 255),
            'text_secondary': (200, 200, 200),
            'text_highlight': (0, 191, 255),
            'success': (50, 205, 50),  # Lime green
            'warning': (255, 215, 0),  # Gold
            'danger': (220, 20, 60),  # Crimson
            'ui_bg': (20, 20, 30),
            'ui_border': (70, 130, 180),
            'ui_shadow': (0, 0, 0),
        }
        
        # Enhanced fonts
        try:
            self.font_large = pygame.font.Font(None, 42)
            self.font_medium = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 20)
            self.font_tiny = pygame.font.Font(None, 16)
        except:
            self.font_large = pygame.font.SysFont('arial', 42)
            self.font_medium = pygame.font.SysFont('arial', 28)
            self.font_small = pygame.font.SysFont('arial', 20)
            self.font_tiny = pygame.font.SysFont('arial', 16)
        
        # Effects
        self.particles: List[Particle] = []
        self.stars: List[Star] = []
        self.asteroid_trails = {}  # Track trails for each asteroid
        self.projectile_trails = deque(maxlen=5)
        self.active_bullets: List[Bullet] = []  # Active bullets in flight
        
        # Initialize starfield
        self._init_starfield()
        
        # Animation state
        self.frame_count = 0
        self.fire_animation_frames = 0
        self.last_fire_time = 0
        self.impact_effects = []  # Store impact positions with timing
        
        # Performance
        self.clock = pygame.time.Clock()
        self.show_fps = False
    
    def _init_starfield(self, num_stars=200):
        """Initialize starfield background"""
        for _ in range(num_stars):
            x = np.random.uniform(0, self.width)
            y = np.random.uniform(0, self.height)
            brightness = np.random.randint(150, 255)
            self.stars.append(Star(x, y, brightness))
    
    def world_to_screen(self, angle: float, distance: float) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        x = self.center_x + math.cos(angle) * distance * self.scale
        y = self.center_y - math.sin(angle) * distance * self.scale
        return int(x), int(y)
    
    def create_explosion(self, x: int, y: int, color: Tuple[int, int, int] = (255, 200, 0), size='large'):
        """Create enhanced particle explosion"""
        num_particles = 30 if size == 'large' else 15
        
        for _ in range(num_particles):
            angle = np.random.uniform(0, 2 * math.pi)
            speed = np.random.uniform(3, 12)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Color variation
            color_variation = np.random.randint(-40, 40)
            particle_color = (
                max(0, min(255, color[0] + color_variation)),
                max(0, min(255, color[1] + color_variation)),
                max(0, min(255, color[2] + color_variation))
            )
            
            lifetime = np.random.randint(30, 50)
            self.particles.append(Particle(x, y, vx, vy, particle_color, lifetime))
        
        # Add impact effect
        self.impact_effects.append({'x': x, 'y': y, 'frame': 0, 'max_frames': 20})
    
    def draw_planet(self):
        """Draw enhanced planet with atmosphere and glow"""
        planet_radius = int(self.scale * 2.0)
        
        # Outer glow
        for i in range(5, 0, -1):
            alpha = 30 - i * 5
            radius = planet_radius + i * 4
            glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.colors['planet_atmosphere'], alpha),
                             (radius, radius), radius)
            self.screen.blit(glow_surface, 
                           (self.center_x - radius, self.center_y - radius))
        
        # Planet shadow (bottom right)
        shadow_offset = 3
        pygame.draw.ellipse(self.screen, (0, 0, 0, 100),
                          (self.center_x - planet_radius + shadow_offset,
                           self.center_y - planet_radius + shadow_offset,
                           planet_radius * 2, planet_radius * 2))
        
        # Planet main body with gradient effect
        pygame.draw.circle(self.screen, self.colors['planet_dark'],
                          (self.center_x, self.center_y), planet_radius)
        pygame.draw.circle(self.screen, self.colors['planet'],
                          (self.center_x, self.center_y), planet_radius - 2)
        
        # Planet highlight (light source from top-left)
        highlight_offset = -planet_radius // 3
        highlight_radius = planet_radius // 2.5
        pygame.draw.circle(self.screen, self.colors['planet_highlight'],
                          (self.center_x + highlight_offset, self.center_y + highlight_offset),
                          highlight_radius)
        
        # Planet surface details (craters/features)
        for _ in range(3):
            crater_x = self.center_x + np.random.randint(-planet_radius//2, planet_radius//2)
            crater_y = self.center_y + np.random.randint(-planet_radius//2, planet_radius//2)
            crater_r = np.random.randint(3, 6)
            pygame.draw.circle(self.screen, self.colors['planet_dark'],
                             (crater_x, crater_y), crater_r)
        
        # Planet ring/orbit indicator
        pygame.draw.circle(self.screen, self.colors['planet_ring'],
                          (self.center_x, self.center_y), planet_radius + 3, 2)
    
    def draw_turret(self, turret_angle: float):
        """Draw enhanced turret with better visuals"""
        turret_length = int(self.scale * 1.5)
        turret_width = 10
        
        # Calculate positions
        end_x = self.center_x + math.cos(turret_angle) * turret_length
        end_y = self.center_y - math.sin(turret_angle) * turret_length
        
        # Turret base shadow
        base_radius = 14
        pygame.draw.circle(self.screen, (0, 0, 0, 150),
                          (self.center_x + 2, self.center_y + 2), base_radius)
        
        # Turret base
        pygame.draw.circle(self.screen, self.colors['turret_base'],
                          (self.center_x, self.center_y), base_radius)
        pygame.draw.circle(self.screen, self.colors['turret'],
                          (self.center_x, self.center_y), base_radius - 3)
        
        # Base highlight
        pygame.draw.circle(self.screen, (255, 255, 255, 100),
                          (self.center_x - 3, self.center_y - 3), base_radius // 2)
        
        # Turret glow when firing
        if self.fire_animation_frames > 0:
            glow_intensity = min(255, self.fire_animation_frames * 25)
            glow_surface = pygame.Surface((turret_length * 3, turret_length * 3), pygame.SRCALPHA)
            glow_color = (*self.colors['turret_glow'], glow_intensity)
            pygame.draw.line(glow_surface, glow_color,
                           (turret_length * 1.5, turret_length * 1.5),
                           (turret_length * 1.5 + math.cos(turret_angle) * turret_length * 1.2,
                            turret_length * 1.5 - math.sin(turret_angle) * turret_length * 1.2),
                           12)
            self.screen.blit(glow_surface,
                           (self.center_x - turret_length * 1.5,
                            self.center_y - turret_length * 1.5))
            self.fire_animation_frames -= 1
        
        # Turret barrel shadow
        shadow_end_x = end_x + 2
        shadow_end_y = end_y + 2
        pygame.draw.line(self.screen, (0, 0, 0, 150),
                        (self.center_x + 2, self.center_y + 2),
                        (shadow_end_x, shadow_end_y), turret_width)
        
        # Turret barrel
        pygame.draw.line(self.screen, self.colors['turret'],
                        (self.center_x, self.center_y),
                        (end_x, end_y), turret_width)
        
        # Turret tip with glow
        tip_radius = turret_width // 2 + 2
        pygame.draw.circle(self.screen, self.colors['turret_glow'],
                          (int(end_x), int(end_y)), tip_radius)
        pygame.draw.circle(self.screen, self.colors['turret'],
                          (int(end_x), int(end_y)), tip_radius - 2)
    
    def draw_asteroid(self, angle: float, distance: float, asteroid_id: str = None,
                     size: float = 1.0, is_danger: bool = False):
        """Draw enhanced asteroid with trail - made bigger and more visible"""
        x, y = self.world_to_screen(angle, distance)
        # Make asteroids bigger - increased from 0.35 to 0.55
        asteroid_radius = int(self.scale * 0.55 * size)
        
        # Update trail
        if asteroid_id:
            if asteroid_id not in self.asteroid_trails:
                self.asteroid_trails[asteroid_id] = Trail(max_length=8)
            self.asteroid_trails[asteroid_id].add(x, y)
            self.asteroid_trails[asteroid_id].draw(self.screen, 
                                                  self.colors['asteroid_trail'], width=1)
        
        # Color based on danger
        if is_danger:
            color = self.colors['asteroid_danger']
            # Pulsing danger effect
            pulse = int(20 * math.sin(self.frame_count * 0.3))
            danger_radius = asteroid_radius + 8 + pulse
            pygame.draw.circle(self.screen, (*self.colors['asteroid_danger'], 100),
                            (x, y), danger_radius, 2)
        else:
            color = self.colors['asteroid']
        
        # Asteroid shadow
        pygame.draw.circle(self.screen, (0, 0, 0, 120),
                          (x + 3, y + 3), asteroid_radius)
        
        # Draw asteroid outline for better visibility
        outline_width = 3
        pygame.draw.circle(self.screen, (255, 255, 255, 200), (x, y), asteroid_radius + outline_width, outline_width)
        
        # Asteroid body (irregular shape for realism) - made brighter
        points = []
        num_points = 10
        for i in range(num_points):
            angle_offset = (2 * math.pi * i / num_points) + self.frame_count * 0.02
            radius_variation = asteroid_radius + np.random.randint(-3, 4)
            px = x + math.cos(angle_offset) * radius_variation
            py = y + math.sin(angle_offset) * radius_variation
            points.append((px, py))
        
        # Brighter asteroid color
        bright_color = tuple(min(255, c + 40) for c in color) if not is_danger else color
        pygame.draw.polygon(self.screen, bright_color, points)
        
        # Asteroid highlight - brighter
        highlight_offset = -asteroid_radius // 3
        highlight_radius = asteroid_radius // 2
        pygame.draw.circle(self.screen, (255, 255, 255, 180),
                          (x + highlight_offset, y + highlight_offset),
                          highlight_radius)
        
        # Surface details - more visible
        for _ in range(3):
            detail_x = x + np.random.randint(-asteroid_radius//2, asteroid_radius//2)
            detail_y = y + np.random.randint(-asteroid_radius//2, asteroid_radius//2)
            detail_color = (255, 100, 100) if is_danger else (200, 200, 200)
            pygame.draw.circle(self.screen, detail_color, (detail_x, detail_y), 3)
    
    def draw_projectile(self, angle: float, distance: float, progress: float = 0.5):
        """Draw enhanced projectile with trail"""
        start_dist = 2.0
        end_dist = distance * progress + start_dist
        
        start_x, start_y = self.world_to_screen(angle, start_dist)
        end_x, end_y = self.world_to_screen(angle, end_dist)
        
        # Add to trail
        self.projectile_trails.append((end_x, end_y))
        
        # Draw trail
        if len(self.projectile_trails) > 1:
            points = list(self.projectile_trails)
            for i in range(len(points) - 1):
                alpha = int(200 * (i / len(points)))
                pygame.draw.line(self.screen, self.colors['projectile_trail'],
                               points[i], points[i + 1], 4)
        
        # Projectile glow
        glow_radius = 8
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.colors['projectile_glow'], 150),
                         (glow_radius, glow_radius), glow_radius)
        self.screen.blit(glow_surface, (end_x - glow_radius, end_y - glow_radius))
        
        # Projectile core
        pygame.draw.circle(self.screen, self.colors['projectile'],
                          (end_x, end_y), 5)
        pygame.draw.circle(self.screen, (255, 255, 255),
                          (end_x, end_y), 2)
    
    def draw_ui(self, episode: int, step: int, reward: float, total_reward: float,
                asteroids_destroyed: int, agent_type: str = "", fps: float = 0):
        """Draw enhanced UI panel"""
        panel_width = 280
        panel_height = 240
        panel_x = self.width - panel_width - 25
        panel_y = 25
        
        # UI shadow
        shadow_offset = 3
        shadow_surface = pygame.Surface((panel_width, panel_height))
        shadow_surface.fill(self.colors['ui_shadow'])
        shadow_surface.set_alpha(150)
        self.screen.blit(shadow_surface, (panel_x + shadow_offset, panel_y + shadow_offset))
        
        # UI background with gradient effect
        ui_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        for y in range(panel_height):
            alpha = int(220 - (y / panel_height) * 20)
            color = (*self.colors['ui_bg'], alpha)
            pygame.draw.line(ui_surface, color, (0, y), (panel_width, y))
        self.screen.blit(ui_surface, (panel_x, panel_y))
        
        # UI border with glow
        pygame.draw.rect(self.screen, self.colors['ui_border'],
                        (panel_x, panel_y, panel_width, panel_height), 3)
        pygame.draw.rect(self.screen, (*self.colors['ui_border'], 100),
                        (panel_x - 1, panel_y - 1, panel_width + 2, panel_height + 2), 1)
        
        # Title
        title = self.font_medium.render("STATISTICS", True, self.colors['text_highlight'])
        self.screen.blit(title, (panel_x + 10, panel_y + 10))
        
        # Content
        y_offset = panel_y + 45
        line_height = 28
        
        if agent_type:
            text = self.font_small.render(f"Agent: {agent_type}", True, self.colors['text'])
            self.screen.blit(text, (panel_x + 15, y_offset))
            y_offset += line_height
        
        text = self.font_small.render(f"Episode: {episode}", True, self.colors['text_secondary'])
        self.screen.blit(text, (panel_x + 15, y_offset))
        y_offset += line_height
        
        text = self.font_small.render(f"Step: {step}", True, self.colors['text_secondary'])
        self.screen.blit(text, (panel_x + 15, y_offset))
        y_offset += line_height
        
        # Reward with color coding
        reward_color = self.colors['success'] if reward > 0 else (
            self.colors['danger'] if reward < -5 else self.colors['text_secondary']
        )
        text = self.font_small.render(f"Reward: {reward:.2f}", True, reward_color)
        self.screen.blit(text, (panel_x + 15, y_offset))
        y_offset += line_height
        
        text = self.font_small.render(f"Total: {total_reward:.2f}", True, self.colors['text'])
        self.screen.blit(text, (panel_x + 15, y_offset))
        y_offset += line_height
        
        text = self.font_small.render(f"Destroyed: {asteroids_destroyed}", True, self.colors['success'])
        self.screen.blit(text, (panel_x + 15, y_offset))
        
        # FPS counter
        if self.show_fps and fps > 0:
            fps_text = self.font_tiny.render(f"FPS: {fps:.1f}", True, self.colors['text_secondary'])
            self.screen.blit(fps_text, (panel_x + panel_width - 60, panel_y + panel_height - 20))
    
    def update_starfield(self):
        """Update and draw starfield"""
        for star in self.stars:
            star.update()
            star.draw(self.screen)
    
    def update_particles(self):
        """Update and draw particles"""
        self.particles = [p for p in self.particles if p.update()]
        for particle in self.particles:
            particle.draw(self.screen)
    
    def create_bullet(self, turret_angle: float, target_angle: float, target_distance: float):
        """Create a bullet from turret to target asteroid"""
        # Calculate start position (turret tip)
        turret_length = int(self.scale * 1.5)
        start_x = self.center_x + math.cos(turret_angle) * turret_length
        start_y = self.center_y - math.sin(turret_angle) * turret_length
        
        # Calculate target position
        target_x, target_y = self.world_to_screen(target_angle, target_distance)
        
        # Create bullet with slower speed for visibility
        bullet = Bullet(start_x, start_y, target_x, target_y, speed=5.0)
        self.active_bullets.append(bullet)
    
    def update_bullets(self):
        """Update all active bullets"""
        self.active_bullets = [b for b in self.active_bullets if b.update()]
        for bullet in self.active_bullets:
            bullet.draw(self.screen, self.colors)
    
    def update_impact_effects(self):
        """Update impact visual effects"""
        active_effects = []
        for effect in self.impact_effects:
            effect['frame'] += 1
            if effect['frame'] < effect['max_frames']:
                active_effects.append(effect)
                # Draw impact flash
                alpha = int(255 * (1 - effect['frame'] / effect['max_frames']))
                radius = int(30 * (effect['frame'] / effect['max_frames']))
                flash_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(flash_surface, (255, 255, 255, alpha),
                                 (radius, radius), radius)
                self.screen.blit(flash_surface,
                               (effect['x'] - radius, effect['y'] - radius))
        self.impact_effects = active_effects
    
    def render(self, env, action: Optional[int] = None, stats: Optional[dict] = None):
        """Main enhanced render function"""
        self.frame_count += 1
        
        # Clear screen
        self.screen.fill(self.colors['background'])
        
        # Update and draw starfield
        self.update_starfield()
        
        # Draw planet
        self.draw_planet()
        
        # Draw turret
        self.draw_turret(env.turret_angle)
        
        # Draw asteroids with trails
        asteroid_id = 0
        for asteroid in env.asteroids:
            is_danger = asteroid["distance"] < 4.0
            self.draw_asteroid(
                asteroid["angle"],
                asteroid["distance"],
                asteroid_id=f"ast_{asteroid_id}",
                size=1.0,
                is_danger=is_danger
            )
            asteroid_id += 1
        
        # Create bullet if firing
        if action == 2:
            self.fire_animation_frames = 5
            if env.asteroids:
                # Find closest asteroid in firing range
                closest = None
                for a in env.asteroids:
                    angle_diff = abs(env.turret_angle - a["angle"])
                    if angle_diff < 0.15 and a["distance"] < 6.0:
                        if closest is None or a["distance"] < closest["distance"]:
                            closest = a
                
                if closest:
                    self.create_bullet(env.turret_angle, closest["angle"], closest["distance"])
        
        # Update and draw bullets
        self.update_bullets()
        
        # Update and draw particles
        self.update_particles()
        
        # Update impact effects
        self.update_impact_effects()
        
        # Draw UI
        if stats:
            fps = self.clock.get_fps()
            self.draw_ui(
                episode=stats.get('episode', 0),
                step=stats.get('step', 0),
                reward=stats.get('reward', 0),
                total_reward=stats.get('total_reward', 0),
                asteroids_destroyed=stats.get('asteroids_destroyed', 0),
                agent_type=stats.get('agent_type', ''),
                fps=fps
            )
        
        pygame.display.flip()
        self.clock.tick(self.fps)
    
    def handle_events(self) -> bool:
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_F11:
                    # Toggle fullscreen (if needed)
                    pass
                elif event.key == pygame.K_F3:
                    # Toggle FPS display
                    self.show_fps = not self.show_fps
        return True
    
    def quit(self):
        """Clean up"""
        pygame.quit()
