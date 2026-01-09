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
        glow_color_rgb = colors['projectile_glow'][:3]  # RGB only
        pygame.draw.circle(glow_surface, (*glow_color_rgb, 200),
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
        
        # Enhanced color palette with modern styling
        self.colors = {
            'background': (5, 5, 15),  # Deeper space
            'space': (2, 2, 8),
            'planet': (70, 130, 255),  # Brighter blue
            'planet_dark': (20, 40, 120),  # Darker blue
            'planet_ring': (100, 150, 255),  # Bright ring
            'planet_highlight': (200, 220, 255),  # Bright highlight
            'planet_atmosphere': (150, 220, 255),  # Glowing atmosphere
            'planet_core': (255, 255, 255),  # White core
            'turret': (255, 255, 255),
            'turret_base': (220, 220, 220),
            'turret_glow': (0, 200, 255),  # Cyan glow
            'turret_shadow': (40, 40, 40),
            'turret_energy': (100, 200, 255),  # Energy effect
            'asteroid': (180, 180, 200),  # Brighter gray
            'asteroid_highlight': (240, 240, 255),  # Very light
            'asteroid_danger': (255, 50, 50),  # Bright red
            'asteroid_critical': (255, 0, 0),  # Pure red
            'asteroid_trail': (150, 150, 180),
            'projectile': (255, 230, 0),  # Bright gold
            'projectile_trail': (255, 180, 0),  # Orange
            'projectile_glow': (255, 255, 150),  # Yellow glow
            'projectile_core': (255, 255, 255),  # White core
            'text': (255, 255, 255),
            'text_secondary': (180, 200, 220),
            'text_highlight': (100, 200, 255),  # Cyan
            'text_title': (255, 255, 255),
            'success': (100, 255, 100),  # Bright green
            'warning': (255, 220, 0),  # Bright gold
            'danger': (255, 80, 80),  # Bright red
            'ui_bg': (15, 20, 35),  # Darker UI
            'ui_bg_light': (25, 30, 45),
            'ui_border': (100, 150, 255),  # Blue border
            'ui_border_glow': (150, 200, 255),  # Glowing border
            'ui_shadow': (0, 0, 0),
            'ui_accent': (100, 200, 255),  # Accent color
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
        self.show_radar = True
        self.show_distance_rings = True
        self.show_targeting_line = True
    
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
        """Create enhanced particle explosion with modern effects"""
        num_particles = 80 if size == 'large' else 40
        
        # Outer explosion layer (fast particles) - enhanced
        for _ in range(num_particles):
            angle = np.random.uniform(0, 2 * math.pi)
            speed = np.random.uniform(8, 20)  # Faster particles
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Enhanced color variation - more vibrant
            color_variation = np.random.randint(-40, 60)
            particle_color = (
                max(0, min(255, color[0] + color_variation)),
                max(0, min(255, color[1] + color_variation)),
                max(0, min(255, color[2] + color_variation))
            )
            
            lifetime = np.random.randint(50, 70)  # Longer lifetime
            particle_size = np.random.randint(3, 7)  # Varied sizes
            self.particles.append(Particle(x, y, vx, vy, particle_color, lifetime, size=particle_size))
        
        # Middle explosion layer (medium speed particles)
        for _ in range(num_particles // 2):
            angle = np.random.uniform(0, 2 * math.pi)
            speed = np.random.uniform(4, 10)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Orange/red gradient
            brightness = np.random.randint(180, 255)
            particle_color = (brightness, brightness // 2, brightness // 4)
            
            lifetime = np.random.randint(35, 50)
            self.particles.append(Particle(x, y, vx, vy, particle_color, lifetime, size=5))
        
        # Inner explosion layer (slow, bright particles) - enhanced
        for _ in range(num_particles // 2):
            angle = np.random.uniform(0, 2 * math.pi)
            speed = np.random.uniform(2, 8)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Bright white/yellow center with variation
            brightness = np.random.randint(220, 255)
            particle_color = (brightness, brightness, max(150, brightness - 30))
            
            lifetime = np.random.randint(25, 40)
            self.particles.append(Particle(x, y, vx, vy, particle_color, lifetime, size=6))
        
        # Core explosion (very bright, slow particles)
        for _ in range(num_particles // 4):
            angle = np.random.uniform(0, 2 * math.pi)
            speed = np.random.uniform(1, 4)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Pure white core
            particle_color = (255, 255, 255)
            
            lifetime = np.random.randint(15, 25)
            self.particles.append(Particle(x, y, vx, vy, particle_color, lifetime, size=7))
        
        # Add enhanced impact effect with multiple flashes
        self.impact_effects.append({'x': x, 'y': y, 'frame': 0, 'max_frames': 40, 'type': 'explosion'})
    
    def draw_planet(self):
        """Draw enhanced planet with modern styling and effects"""
        planet_radius = int(self.scale * 2.0)
        
        # Draw distance rings if enabled - enhanced styling
        if self.show_distance_rings:
            for ring_idx, ring_dist in enumerate([4.0, 6.0, 8.0]):
                ring_radius = int(ring_dist * self.scale)
                # Pulsing effect for rings
                pulse = int(3 * math.sin(self.frame_count * 0.1 + ring_idx))
                ring_radius += pulse
                
                # Draw glowing ring
                num_segments = 48
                ring_color_intensity = 100 + ring_idx * 20
                for i in range(num_segments):
                    if i % 4 < 2:  # Create dashed effect
                        angle1 = 2 * math.pi * i / num_segments
                        angle2 = 2 * math.pi * (i + 1) / num_segments
                        x1 = self.center_x + math.cos(angle1) * ring_radius
                        y1 = self.center_y - math.sin(angle1) * ring_radius
                        x2 = self.center_x + math.cos(angle2) * ring_radius
                        y2 = self.center_y - math.sin(angle2) * ring_radius
                        # Glowing ring segments
                        color = (ring_color_intensity, ring_color_intensity + 30, ring_color_intensity + 50)
                        pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), 2)
        
        # Enhanced outer glow with multiple layers
        for i in range(8, 0, -1):
            alpha = int(40 - i * 4)
            radius = planet_radius + i * 5
            glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            # Animated glow intensity
            glow_intensity = max(0, min(255, alpha + int(10 * math.sin(self.frame_count * 0.05))))
            # Use RGB color and set alpha via surface
            glow_color = self.colors['planet_atmosphere'][:3]  # RGB only
            pygame.draw.circle(glow_surface, (*glow_color, glow_intensity), (radius, radius), radius)
            self.screen.blit(glow_surface, 
                           (self.center_x - radius, self.center_y - radius))
        
        # Planet shadow with blur effect
        shadow_offset = 4
        for shadow_layer in range(3):
            shadow_alpha = 80 - shadow_layer * 20
            shadow_radius = planet_radius + shadow_layer * 2
            shadow_surface = pygame.Surface((shadow_radius * 2, shadow_radius * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, shadow_alpha),
                              (0, 0, shadow_radius * 2, shadow_radius * 2))
            self.screen.blit(shadow_surface,
                           (self.center_x - shadow_radius + shadow_offset,
                            self.center_y - shadow_radius + shadow_offset))
        
        # Planet main body with enhanced gradient
        pygame.draw.circle(self.screen, self.colors['planet_dark'],
                          (self.center_x, self.center_y), planet_radius)
        
        # Middle layer
        pygame.draw.circle(self.screen, self.colors['planet'],
                          (self.center_x, self.center_y), planet_radius - 1)
        
        # Inner bright layer
        inner_radius = int(planet_radius * 0.85)
        pygame.draw.circle(self.screen, self.colors['planet_ring'],
                          (self.center_x, self.center_y), inner_radius)
        
        # Planet highlight with animation
        highlight_offset = -planet_radius // 3
        highlight_radius = planet_radius // 2.5
        # Animated highlight
        highlight_pulse = int(3 * math.sin(self.frame_count * 0.08))
        pygame.draw.circle(self.screen, self.colors['planet_highlight'],
                          (self.center_x + highlight_offset, self.center_y + highlight_offset),
                          highlight_radius + highlight_pulse)
        
        # Planet core (bright center)
        core_radius = planet_radius // 4
        pygame.draw.circle(self.screen, self.colors['planet_core'],
                          (self.center_x + highlight_offset, self.center_y + highlight_offset),
                          core_radius)
        
        # Planet surface details (craters/features) - more visible
        for i in range(5):
            angle = 2 * math.pi * i / 5 + self.frame_count * 0.01
            crater_dist = planet_radius * 0.6
            crater_x = self.center_x + math.cos(angle) * crater_dist
            crater_y = self.center_y + math.sin(angle) * crater_dist
            crater_r = np.random.randint(4, 7)
            pygame.draw.circle(self.screen, self.colors['planet_dark'],
                             (int(crater_x), int(crater_y)), crater_r)
            # Crater shadow
            pygame.draw.circle(self.screen, (0, 0, 0, 150),
                             (int(crater_x + 1), int(crater_y + 1)), crater_r - 1)
        
        # Enhanced planet ring/orbit indicator with glow
        ring_glow_radius = planet_radius + 5
        for glow_layer in range(3):
            glow_alpha = max(0, min(255, 150 - glow_layer * 40))
            ring_surface = pygame.Surface((ring_glow_radius * 2, ring_glow_radius * 2), pygame.SRCALPHA)
            ring_color = self.colors['planet_ring'][:3]  # RGB only
            pygame.draw.circle(ring_surface, (*ring_color, glow_alpha),
                             (ring_glow_radius, ring_glow_radius), ring_glow_radius, 3 - glow_layer)
            self.screen.blit(ring_surface,
                           (self.center_x - ring_glow_radius, self.center_y - ring_glow_radius))
    
    def draw_turret(self, turret_angle: float):
        """Draw enhanced turret with modern styling and effects"""
        turret_length = int(self.scale * 1.5)
        turret_width = 12  # Slightly thicker
        
        # Calculate positions
        end_x = self.center_x + math.cos(turret_angle) * turret_length
        end_y = self.center_y - math.sin(turret_angle) * turret_length
        
        # Enhanced turret base with multiple layers
        base_radius = 16
        # Base shadow with blur
        for shadow_layer in range(2):
            shadow_alpha = 120 - shadow_layer * 40
            shadow_radius = base_radius + shadow_layer
            shadow_surface = pygame.Surface((shadow_radius * 2, shadow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shadow_surface, (0, 0, 0, shadow_alpha),
                             (shadow_radius, shadow_radius), shadow_radius)
            self.screen.blit(shadow_surface,
                           (self.center_x - shadow_radius + 3,
                            self.center_y - shadow_radius + 3))
        
        # Base outer ring
        pygame.draw.circle(self.screen, self.colors['turret_base'],
                          (self.center_x, self.center_y), base_radius)
        
        # Base inner ring
        pygame.draw.circle(self.screen, self.colors['turret'],
                          (self.center_x, self.center_y), base_radius - 2)
        
        # Base core
        pygame.draw.circle(self.screen, (240, 240, 255),
                          (self.center_x, self.center_y), base_radius - 5)
        
        # Base highlight with animation
        highlight_pulse = int(2 * math.sin(self.frame_count * 0.1))
        pygame.draw.circle(self.screen, (255, 255, 255, 180),
                          (self.center_x - 4, self.center_y - 4),
                          base_radius // 2 + highlight_pulse)
        
        # Base energy ring (rotating)
        energy_angle = self.frame_count * 0.05
        for i in range(8):
            angle = energy_angle + (2 * math.pi * i / 8)
            energy_x = self.center_x + math.cos(angle) * (base_radius - 2)
            energy_y = self.center_y - math.sin(angle) * (base_radius - 2)
            pygame.draw.circle(self.screen, self.colors['turret_energy'],
                             (int(energy_x), int(energy_y)), 2)
        
        # Enhanced turret glow when firing
        if self.fire_animation_frames > 0:
            glow_intensity = min(255, self.fire_animation_frames * 30)
            # Multiple glow layers
            for glow_layer in range(3):
                layer_alpha = max(0, min(255, int(glow_intensity * (1 - glow_layer * 0.3))))
                layer_width = 12 + glow_layer * 4
                glow_surface = pygame.Surface((turret_length * 4, turret_length * 4), pygame.SRCALPHA)
                glow_color_rgb = self.colors['turret_glow'][:3]  # RGB only
                glow_color = (*glow_color_rgb, layer_alpha)
                center = turret_length * 2
                pygame.draw.line(glow_surface, glow_color,
                               (center, center),
                               (center + math.cos(turret_angle) * turret_length * 1.5,
                                center - math.sin(turret_angle) * turret_length * 1.5),
                               layer_width)
                self.screen.blit(glow_surface,
                               (self.center_x - turret_length * 2,
                                self.center_y - turret_length * 2))
            self.fire_animation_frames -= 1
        
        # Turret barrel shadow with blur
        shadow_end_x = end_x + 3
        shadow_end_y = end_y + 3
        for shadow_width in [turret_width + 2, turret_width]:
            shadow_alpha = 100 if shadow_width > turret_width else 150
            shadow_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.line(shadow_surface, (0, 0, 0, shadow_alpha),
                           (self.center_x + 3, self.center_y + 3),
                           (shadow_end_x, shadow_end_y), shadow_width)
            self.screen.blit(shadow_surface, (0, 0))
        
        # Turret barrel with gradient effect
        # Outer barrel
        pygame.draw.line(self.screen, self.colors['turret_base'],
                        (self.center_x, self.center_y),
                        (end_x, end_y), turret_width + 2)
        # Inner barrel
        pygame.draw.line(self.screen, self.colors['turret'],
                        (self.center_x, self.center_y),
                        (end_x, end_y), turret_width)
        # Core barrel
        pygame.draw.line(self.screen, (255, 255, 255),
                        (self.center_x, self.center_y),
                        (end_x, end_y), turret_width - 4)
        
        # Enhanced turret tip with multiple glow layers
        tip_radius = turret_width // 2 + 4
        # Outer glow
        for glow_layer in range(3):
            glow_alpha = max(0, min(255, 200 - glow_layer * 50))
            glow_radius = tip_radius + glow_layer * 3
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            glow_color_rgb = self.colors['turret_glow'][:3]  # RGB only
            pygame.draw.circle(glow_surface, (*glow_color_rgb, glow_alpha),
                             (glow_radius, glow_radius), glow_radius)
            self.screen.blit(glow_surface,
                           (int(end_x) - glow_radius, int(end_y) - glow_radius))
        
        # Tip core
        pygame.draw.circle(self.screen, self.colors['turret_glow'],
                          (int(end_x), int(end_y)), tip_radius)
        pygame.draw.circle(self.screen, self.colors['turret'],
                          (int(end_x), int(end_y)), tip_radius - 2)
        pygame.draw.circle(self.screen, (255, 255, 255),
                          (int(end_x), int(end_y)), tip_radius - 4)
    
    def draw_asteroid(self, angle: float, distance: float, asteroid_id: str = None,
                     size: float = 1.0, is_danger: bool = False):
        """Draw enhanced asteroid with modern styling and effects"""
        x, y = self.world_to_screen(angle, distance)
        # Make asteroids bigger and more visible
        asteroid_radius = int(self.scale * 0.6 * size)
        
        # Update trail with enhanced visibility
        if asteroid_id:
            if asteroid_id not in self.asteroid_trails:
                self.asteroid_trails[asteroid_id] = Trail(max_length=15)
            self.asteroid_trails[asteroid_id].add(x, y)
            # Enhanced trail with glow
            trail_color = self.colors['asteroid_danger'] if is_danger else self.colors['asteroid_trail']
            self.asteroid_trails[asteroid_id].draw(self.screen, trail_color, width=3)
        
        # Enhanced danger effect
        if is_danger:
            color = self.colors['asteroid_danger']
            # More intense pulsing
            pulse = int(30 * math.sin(self.frame_count * 0.5))
            danger_radius = asteroid_radius + 15 + pulse
            
            # Multiple danger rings with glow
            for ring in range(4):
                alpha = max(0, min(255, 180 - ring * 35))
                ring_radius = danger_radius - ring * 4
                # Outer glow
                glow_surface = pygame.Surface((ring_radius * 2, ring_radius * 2), pygame.SRCALPHA)
                danger_color_rgb = self.colors['asteroid_critical'][:3]  # RGB only
                pygame.draw.circle(glow_surface, (*danger_color_rgb, alpha),
                                 (ring_radius, ring_radius), ring_radius, 3)
                self.screen.blit(glow_surface, (x - ring_radius, y - ring_radius))
        else:
            color = self.colors['asteroid']
        
        # Enhanced asteroid shadow with blur
        for shadow_layer in range(2):
            shadow_alpha = 100 - shadow_layer * 30
            shadow_radius = asteroid_radius + shadow_layer
            shadow_surface = pygame.Surface((shadow_radius * 2, shadow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shadow_surface, (0, 0, 0, shadow_alpha),
                             (shadow_radius, shadow_radius), shadow_radius)
            self.screen.blit(shadow_surface,
                           (x - shadow_radius + 4, y - shadow_radius + 4))
        
        # Enhanced outline with glow
        outline_width = 4
        outline_color = self.colors['asteroid_critical'] if is_danger else (255, 255, 255)
        # Outer outline glow
        for outline_layer in range(2):
            outline_alpha = 200 - outline_layer * 50
            outline_radius = asteroid_radius + outline_width + outline_layer * 2
            outline_surface = pygame.Surface((outline_radius * 2, outline_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(outline_surface, (*outline_color, outline_alpha),
                             (outline_radius, outline_radius), outline_radius, outline_width - outline_layer)
            self.screen.blit(outline_surface, (x - outline_radius, y - outline_radius))
        
        # Asteroid body (irregular shape) - enhanced
        points = []
        num_points = 16  # More points for smoother shape
        rotation = self.frame_count * 0.015  # Slow rotation
        for i in range(num_points):
            angle_offset = (2 * math.pi * i / num_points) + rotation
            radius_variation = asteroid_radius + np.random.randint(-5, 6)
            px = x + math.cos(angle_offset) * radius_variation
            py = y + math.sin(angle_offset) * radius_variation
            points.append((px, py))
        
        # Enhanced asteroid color with gradient
        if is_danger:
            bright_color = self.colors['asteroid_danger']
        else:
            bright_color = tuple(min(255, c + 60) for c in color)
        
        # Main body
        pygame.draw.polygon(self.screen, bright_color, points)
        
        # Inner layer for depth
        inner_points = []
        for i in range(num_points):
            angle_offset = (2 * math.pi * i / num_points) + rotation
            radius_variation = int(asteroid_radius * 0.7) + np.random.randint(-3, 4)
            px = x + math.cos(angle_offset) * radius_variation
            py = y + math.sin(angle_offset) * radius_variation
            inner_points.append((px, py))
        pygame.draw.polygon(self.screen, tuple(min(255, c + 30) for c in bright_color), inner_points)
        
        # Enhanced highlight with animation
        highlight_offset = -asteroid_radius // 3
        highlight_radius = asteroid_radius // 2
        highlight_pulse = int(2 * math.sin(self.frame_count * 0.1))
        highlight_surface = pygame.Surface((highlight_radius * 2, highlight_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(highlight_surface, (255, 255, 255, 220),
                          (highlight_radius, highlight_radius),
                          highlight_radius + highlight_pulse)
        self.screen.blit(highlight_surface,
                       (x + highlight_offset - highlight_radius,
                        y + highlight_offset - highlight_radius))
        
        # Enhanced surface details
        for i in range(6):
            detail_angle = 2 * math.pi * i / 6 + rotation
            detail_dist = asteroid_radius * 0.7
            detail_x = x + math.cos(detail_angle) * detail_dist
            detail_y = y + math.sin(detail_angle) * detail_dist
            detail_color = (255, 100, 100) if is_danger else (240, 240, 255)
            detail_size = 4 if is_danger else 3
            pygame.draw.circle(self.screen, detail_color, (int(detail_x), int(detail_y)), detail_size)
            # Detail highlight
            pygame.draw.circle(self.screen, (255, 255, 255, 150),
                             (int(detail_x - 1), int(detail_y - 1)), detail_size - 1)
        
        # Enhanced distance label for dangerous asteroids
        if is_danger:
            distance_text = f"{distance:.1f}"
            # Text with glow effect
            for glow_offset in [(1, 1), (0, 0)]:
                text_color = (0, 0, 0) if glow_offset == (1, 1) else (255, 255, 255)
                text_surface = self.font_tiny.render(distance_text, True, text_color)
                text_rect = text_surface.get_rect(center=(x + glow_offset[0], y - asteroid_radius - 18 + glow_offset[1]))
                self.screen.blit(text_surface, text_rect)
            
            # Background with glow
            bg_rect = text_rect.inflate(8, 4)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            danger_color_rgb = self.colors['asteroid_danger'][:3]  # RGB only
            pygame.draw.rect(bg_surface, (*danger_color_rgb, 200),
                           (0, 0, bg_rect.width, bg_rect.height))
            pygame.draw.rect(bg_surface, (255, 255, 255, 100),
                           (0, 0, bg_rect.width, bg_rect.height), 2)
            self.screen.blit(bg_surface, bg_rect)
    
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
        projectile_glow_rgb = self.colors['projectile_glow'][:3]  # RGB only
        pygame.draw.circle(glow_surface, (*projectile_glow_rgb, 150),
                         (glow_radius, glow_radius), glow_radius)
        self.screen.blit(glow_surface, (end_x - glow_radius, end_y - glow_radius))
        
        # Projectile core
        pygame.draw.circle(self.screen, self.colors['projectile'],
                          (end_x, end_y), 5)
        pygame.draw.circle(self.screen, (255, 255, 255),
                          (end_x, end_y), 2)
    
    def draw_radar(self, env, panel_x: int, panel_y: int, size: int = 120):
        """Draw enhanced mini radar with modern styling"""
        radar_center_x = panel_x + size // 2
        radar_center_y = panel_y + size // 2
        radar_radius = size // 2 - 5
        
        # Enhanced radar background with gradient
        radar_surface = pygame.Surface((radar_radius * 2, radar_radius * 2), pygame.SRCALPHA)
        for r in range(radar_radius, 0, -1):
            alpha = int(200 - (r / radar_radius) * 100)
            color = (20, 25, 45, alpha)
            pygame.draw.circle(radar_surface, color, (radar_radius, radar_radius), r)
        self.screen.blit(radar_surface, (radar_center_x - radar_radius, radar_center_y - radar_radius))
        
        # Radar border with glow
        for glow_layer in range(2):
            glow_alpha = max(0, min(255, 150 - glow_layer * 50))
            border_radius = radar_radius + glow_layer
            border_surface = pygame.Surface((border_radius * 2, border_radius * 2), pygame.SRCALPHA)
            border_color_rgb = self.colors['ui_border'][:3]  # RGB only
            pygame.draw.circle(border_surface, (*border_color_rgb, glow_alpha),
                             (border_radius, border_radius), border_radius, 2 + glow_layer)
            self.screen.blit(border_surface,
                           (radar_center_x - border_radius, radar_center_y - border_radius))
        
        # Radar grid lines
        for angle in range(0, 360, 45):
            angle_rad = math.radians(angle)
            x1 = radar_center_x + math.cos(angle_rad) * (radar_radius - 5)
            y1 = radar_center_y - math.sin(angle_rad) * (radar_radius - 5)
            x2 = radar_center_x + math.cos(angle_rad) * radar_radius
            y2 = radar_center_y - math.sin(angle_rad) * radar_radius
            pygame.draw.line(self.screen, (50, 70, 100, 100), (x1, y1), (x2, y2), 1)
        
        # Distance rings
        for ring in [0.5, 0.75]:
            ring_radius = int(radar_radius * ring)
            ring_surface = pygame.Surface((ring_radius * 2, ring_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(ring_surface, (50, 70, 100, 80),
                             (ring_radius, ring_radius), ring_radius, 1)
            self.screen.blit(ring_surface,
                           (radar_center_x - ring_radius, radar_center_y - ring_radius))
        
        # Enhanced planet in center with glow
        planet_glow_radius = 8
        planet_glow_surface = pygame.Surface((planet_glow_radius * 2, planet_glow_radius * 2), pygame.SRCALPHA)
        planet_color_rgb = self.colors['planet'][:3]  # RGB only
        pygame.draw.circle(planet_glow_surface, (*planet_color_rgb, 150),
                         (planet_glow_radius, planet_glow_radius), planet_glow_radius)
        self.screen.blit(planet_glow_surface,
                       (radar_center_x - planet_glow_radius, radar_center_y - planet_glow_radius))
        pygame.draw.circle(self.screen, self.colors['planet'],
                         (radar_center_x, radar_center_y), 6)
        pygame.draw.circle(self.screen, self.colors['planet_core'],
                         (radar_center_x, radar_center_y), 3)
        
        # Enhanced asteroids on radar with trails
        for asteroid in env.asteroids:
            # Scale distance for radar (max distance 10.0 -> radar_radius)
            radar_distance = (asteroid["distance"] / 10.0) * (radar_radius - 8)
            radar_x = radar_center_x + math.cos(asteroid["angle"]) * radar_distance
            radar_y = radar_center_y - math.sin(asteroid["angle"]) * radar_distance
            
            # Color and size based on distance
            if asteroid["distance"] < 4.0:
                color = self.colors['asteroid_danger']
                dot_size = 5
                # Danger glow
                glow_surface = pygame.Surface((dot_size * 3, dot_size * 3), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*color, 150),
                                 (dot_size * 1.5, dot_size * 1.5), dot_size * 1.5)
                self.screen.blit(glow_surface,
                               (int(radar_x) - dot_size * 1.5, int(radar_y) - dot_size * 1.5))
            else:
                color = self.colors['asteroid']
                dot_size = 4
            
            pygame.draw.circle(self.screen, color, (int(radar_x), int(radar_y)), dot_size)
            pygame.draw.circle(self.screen, (255, 255, 255, 200),
                             (int(radar_x), int(radar_y)), dot_size - 1)
        
        # Enhanced turret direction with arrow
        turret_length = radar_radius - 8
        turret_x = radar_center_x + math.cos(env.turret_angle) * turret_length
        turret_y = radar_center_y - math.sin(env.turret_angle) * turret_length
        
        # Turret line with glow
        for glow_width in [4, 2]:
            glow_alpha = max(0, min(255, 100 if glow_width > 2 else 200))
            glow_surface = pygame.Surface((radar_radius * 2, radar_radius * 2), pygame.SRCALPHA)
            turret_glow_rgb = self.colors['turret_glow'][:3]  # RGB only
            pygame.draw.line(glow_surface, (*turret_glow_rgb, glow_alpha),
                           (radar_center_x - radar_center_x + radar_radius,
                            radar_center_y - radar_center_y + radar_radius),
                           (turret_x - radar_center_x + radar_radius,
                            turret_y - radar_center_y + radar_radius), glow_width)
            self.screen.blit(glow_surface,
                           (radar_center_x - radar_radius, radar_center_y - radar_radius))
        
        # Turret arrow tip
        arrow_size = 6
        arrow_angle1 = env.turret_angle + math.pi * 0.8
        arrow_angle2 = env.turret_angle - math.pi * 0.8
        arrow_x1 = turret_x + math.cos(arrow_angle1) * arrow_size
        arrow_y1 = turret_y - math.sin(arrow_angle1) * arrow_size
        arrow_x2 = turret_x + math.cos(arrow_angle2) * arrow_size
        arrow_y2 = turret_y - math.sin(arrow_angle2) * arrow_size
        pygame.draw.polygon(self.screen, self.colors['turret_glow'],
                          [(int(turret_x), int(turret_y)),
                           (int(arrow_x1), int(arrow_y1)),
                           (int(arrow_x2), int(arrow_y2))])
    
    def draw_targeting_line(self, env):
        """Draw line from turret to closest asteroid"""
        if not env.asteroids:
            return
        
        closest = min(env.asteroids, key=lambda a: a["distance"])
        closest_x, closest_y = self.world_to_screen(closest["angle"], closest["distance"])
        
        # Turret tip position
        turret_length = int(self.scale * 1.5)
        turret_tip_x = self.center_x + math.cos(env.turret_angle) * turret_length
        turret_tip_y = self.center_y - math.sin(env.turret_angle) * turret_length
        
        # Draw dashed targeting line
        distance = math.sqrt((closest_x - turret_tip_x)**2 + (closest_y - turret_tip_y)**2)
        num_segments = int(distance / 10)
        for i in range(num_segments):
            if i % 4 < 2:  # Dashed pattern
                t1 = i / num_segments
                t2 = (i + 1) / num_segments
                x1 = int(turret_tip_x + (closest_x - turret_tip_x) * t1)
                y1 = int(turret_tip_y + (closest_y - turret_tip_y) * t1)
                x2 = int(turret_tip_x + (closest_x - turret_tip_x) * t2)
                y2 = int(turret_tip_y + (closest_y - turret_tip_y) * t2)
                pygame.draw.line(self.screen, (0, 255, 255, 150), (x1, y1), (x2, y2), 2)
    
    def draw_ui(self, episode: int, step: int, reward: float, total_reward: float,
                asteroids_destroyed: int, agent_type: str = "", fps: float = 0, 
                remaining_asteroids: int = 0, env=None, shots_fired: int = 0, 
                shots_hit: int = 0, hit_rate: float = 0.0):
        """Draw enhanced UI panel with modern styling"""
        panel_width = 320
        panel_height = 400
        panel_x = self.width - panel_width - 20
        panel_y = 20
        
        # Enhanced UI shadow with blur
        shadow_offset = 5
        for shadow_layer in range(3):
            shadow_alpha = 100 - shadow_layer * 25
            shadow_surface = pygame.Surface((panel_width + shadow_layer * 2, 
                                           panel_height + shadow_layer * 2))
            shadow_surface.fill(self.colors['ui_shadow'])
            shadow_surface.set_alpha(shadow_alpha)
            self.screen.blit(shadow_surface, 
                           (panel_x + shadow_offset - shadow_layer,
                            panel_y + shadow_offset - shadow_layer))
        
        # Enhanced UI background with gradient and glow
        ui_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        # Gradient background
        for y in range(panel_height):
            alpha = int(240 - (y / panel_height) * 30)
            # Color gradient from top to bottom
            r = int(self.colors['ui_bg'][0] + (y / panel_height) * 5)
            g = int(self.colors['ui_bg'][1] + (y / panel_height) * 5)
            b = int(self.colors['ui_bg'][2] + (y / panel_height) * 10)
            color = (r, g, b, alpha)
            pygame.draw.line(ui_surface, color, (0, y), (panel_width, y))
        self.screen.blit(ui_surface, (panel_x, panel_y))
        
        # UI border with animated glow
        border_glow = int(20 * math.sin(self.frame_count * 0.1))
        # Outer glow
        for glow_layer in range(2):
            glow_alpha = max(0, min(255, 150 - glow_layer * 50))
            glow_surface = pygame.Surface((panel_width + 4 + glow_layer * 2,
                                         panel_height + 4 + glow_layer * 2), pygame.SRCALPHA)
            border_glow_rgb = self.colors['ui_border_glow'][:3]  # RGB only
            pygame.draw.rect(glow_surface, (*border_glow_rgb, glow_alpha),
                           (0, 0, panel_width + 4 + glow_layer * 2,
                            panel_height + 4 + glow_layer * 2), 3 + glow_layer)
            self.screen.blit(glow_surface,
                           (panel_x - 2 - glow_layer, panel_y - 2 - glow_layer))
        
        # Main border
        pygame.draw.rect(self.screen, self.colors['ui_border'],
                        (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Inner accent border
        pygame.draw.rect(self.screen, self.colors['ui_accent'],
                        (panel_x + 2, panel_y + 2, panel_width - 4, panel_height - 4), 1)
        
        # Enhanced title with glow
        title_text = "STATISTICS"
        # Title shadow
        title_shadow = self.font_medium.render(title_text, True, (0, 0, 0))
        self.screen.blit(title_shadow, (panel_x + 12, panel_y + 12))
        # Title main
        title = self.font_medium.render(title_text, True, self.colors['text_highlight'])
        self.screen.blit(title, (panel_x + 10, panel_y + 10))
        
        # Title underline with glow
        underline_y = panel_y + 45
        pygame.draw.line(self.screen, self.colors['ui_border'],
                        (panel_x + 10, underline_y),
                        (panel_x + panel_width - 10, underline_y), 2)
        pygame.draw.line(self.screen, self.colors['ui_accent'],
                        (panel_x + 10, underline_y + 1),
                        (panel_x + panel_width - 10, underline_y + 1), 1)
        
        # Enhanced content with better styling
        y_offset = panel_y + 55
        line_height = 30
        
        if agent_type:
            # Agent type with icon effect
            agent_text = f"Agent: {agent_type}"
            # Shadow
            text_shadow = self.font_small.render(agent_text, True, (0, 0, 0))
            self.screen.blit(text_shadow, (panel_x + 17, y_offset + 2))
            # Main text
            text = self.font_small.render(agent_text, True, self.colors['text_highlight'])
            self.screen.blit(text, (panel_x + 15, y_offset))
            y_offset += line_height
        
        # Episode with icon
        episode_text = f"Episode: {episode}"
        text_shadow = self.font_small.render(episode_text, True, (0, 0, 0))
        self.screen.blit(text_shadow, (panel_x + 17, y_offset + 2))
        text = self.font_small.render(episode_text, True, self.colors['text'])
        self.screen.blit(text, (panel_x + 15, y_offset))
        y_offset += line_height
        
        # Step
        step_text = f"Step: {step}"
        text_shadow = self.font_small.render(step_text, True, (0, 0, 0))
        self.screen.blit(text_shadow, (panel_x + 17, y_offset + 2))
        text = self.font_small.render(step_text, True, self.colors['text_secondary'])
        self.screen.blit(text, (panel_x + 15, y_offset))
        y_offset += line_height
        
        # Reward with enhanced color coding and glow
        reward_color = self.colors['success'] if reward > 0 else (
            self.colors['danger'] if reward < -5 else self.colors['text_secondary']
        )
        reward_text = f"Reward: {reward:.2f}"
        # Glow effect for positive rewards
        if reward > 10:
            glow_surface = pygame.Surface((200, 25), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*reward_color, 50),
                           (0, 0, 200, 25))
            self.screen.blit(glow_surface, (panel_x + 10, y_offset - 2))
        # Shadow
        text_shadow = self.font_small.render(reward_text, True, (0, 0, 0))
        self.screen.blit(text_shadow, (panel_x + 17, y_offset + 2))
        # Main text
        text = self.font_small.render(reward_text, True, reward_color)
        self.screen.blit(text, (panel_x + 15, y_offset))
        y_offset += line_height
        
        # Total reward
        total_text = f"Total: {total_reward:.2f}"
        text_shadow = self.font_small.render(total_text, True, (0, 0, 0))
        self.screen.blit(text_shadow, (panel_x + 17, y_offset + 2))
        text = self.font_small.render(total_text, True, self.colors['text'])
        self.screen.blit(text, (panel_x + 15, y_offset))
        y_offset += line_height
        
        # Destroyed with success color
        destroyed_text = f"Destroyed: {asteroids_destroyed}"
        text_shadow = self.font_small.render(destroyed_text, True, (0, 0, 0))
        self.screen.blit(text_shadow, (panel_x + 17, y_offset + 2))
        text = self.font_small.render(destroyed_text, True, self.colors['success'])
        self.screen.blit(text, (panel_x + 15, y_offset))
        y_offset += line_height
        
        # Remaining
        remaining_text = f"Remaining: {remaining_asteroids}"
        text_shadow = self.font_small.render(remaining_text, True, (0, 0, 0))
        self.screen.blit(text_shadow, (panel_x + 17, y_offset + 2))
        text = self.font_small.render(remaining_text, True, self.colors['text_secondary'])
        self.screen.blit(text, (panel_x + 15, y_offset))
        y_offset += line_height
        
        # Enhanced hit rate display
        if shots_fired > 0:
            hit_rate_color = self.colors['success'] if hit_rate >= 50 else (
                self.colors['warning'] if hit_rate >= 25 else self.colors['danger']
            )
            hit_rate_text = f"Hit Rate: {hit_rate:.1f}%"
            # Shadow
            text_shadow = self.font_small.render(hit_rate_text, True, (0, 0, 0))
            self.screen.blit(text_shadow, (panel_x + 17, y_offset + 2))
            # Main text
            text = self.font_small.render(hit_rate_text, True, hit_rate_color)
            self.screen.blit(text, (panel_x + 15, y_offset))
            y_offset += line_height
            
            shots_text = f"Shots: {shots_hit}/{shots_fired}"
            text_shadow = self.font_tiny.render(shots_text, True, (0, 0, 0))
            self.screen.blit(text_shadow, (panel_x + 17, y_offset + 2))
            text = self.font_tiny.render(shots_text, True, self.colors['text_secondary'])
            self.screen.blit(text, (panel_x + 15, y_offset))
            y_offset += line_height - 5
            
            # Enhanced hit rate progress bar with glow
            bar_width = 220
            bar_height = 10
            bar_x = panel_x + 15
            bar_y = y_offset
            
            progress = hit_rate / 100.0
            
            # Bar shadow
            pygame.draw.rect(self.screen, (0, 0, 0, 150),
                           (bar_x + 2, bar_y + 2, bar_width, bar_height))
            
            # Background with gradient
            bar_bg_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
            for x in range(bar_width):
                alpha = int(180 + (x / bar_width) * 20)
                pygame.draw.line(bar_bg_surface, (40, 40, 50, alpha),
                               (x, 0), (x, bar_height))
            self.screen.blit(bar_bg_surface, (bar_x, bar_y))
            
            # Progress with glow effect
            progress_width = int(bar_width * progress)
            if progress_width > 0:
                # Progress glow
                progress_glow = pygame.Surface((progress_width + 4, bar_height + 4), pygame.SRCALPHA)
                pygame.draw.rect(progress_glow, (*hit_rate_color, 100),
                               (0, 0, progress_width + 4, bar_height + 4))
                self.screen.blit(progress_glow, (bar_x - 2, bar_y - 2))
                
                # Progress bar with gradient
                progress_surface = pygame.Surface((progress_width, bar_height), pygame.SRCALPHA)
                for x in range(progress_width):
                    alpha = int(200 + (x / progress_width) * 55)
                    color = tuple(min(255, c + 30) for c in hit_rate_color)
                    pygame.draw.line(progress_surface, (*color, alpha),
                                   (x, 0), (x, bar_height))
                self.screen.blit(progress_surface, (bar_x, bar_y))
                
                # Progress highlight
                highlight_width = min(progress_width, 30)
                highlight_surface = pygame.Surface((highlight_width, bar_height), pygame.SRCALPHA)
                for x in range(highlight_width):
                    alpha = int(150 * (1 - x / highlight_width))
                    pygame.draw.line(highlight_surface, (255, 255, 255, alpha),
                                   (x, 0), (x, bar_height))
                self.screen.blit(highlight_surface, (bar_x, bar_y))
            
            # Border with glow
            pygame.draw.rect(self.screen, self.colors['ui_border'],
                           (bar_x, bar_y, bar_width, bar_height), 2)
            pygame.draw.rect(self.screen, self.colors['ui_accent'],
                           (bar_x + 1, bar_y + 1, bar_width - 2, bar_height - 2), 1)
            y_offset += 20
        
        # Enhanced progress bar for asteroids destroyed
        if remaining_asteroids < 5:
            bar_width = 220
            bar_height = 12
            bar_x = panel_x + 15
            bar_y = y_offset + 5
            progress = (5 - remaining_asteroids) / 5.0
            
            # Bar shadow
            pygame.draw.rect(self.screen, (0, 0, 0, 150),
                           (bar_x + 2, bar_y + 2, bar_width, bar_height))
            
            # Background with gradient
            bar_bg_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
            for x in range(bar_width):
                alpha = int(180 + (x / bar_width) * 20)
                pygame.draw.line(bar_bg_surface, (40, 40, 50, alpha),
                               (x, 0), (x, bar_height))
            self.screen.blit(bar_bg_surface, (bar_x, bar_y))
            
            # Progress with glow
            progress_width = int(bar_width * progress)
            if progress_width > 0:
                # Progress glow
                progress_glow = pygame.Surface((progress_width + 4, bar_height + 4), pygame.SRCALPHA)
                success_color_rgb = self.colors['success'][:3]  # RGB only
                pygame.draw.rect(progress_glow, (*success_color_rgb, 100),
                               (0, 0, progress_width + 4, bar_height + 4))
                self.screen.blit(progress_glow, (bar_x - 2, bar_y - 2))
                
                # Progress bar with gradient
                progress_surface = pygame.Surface((progress_width, bar_height), pygame.SRCALPHA)
                for x in range(progress_width):
                    alpha = int(200 + (x / progress_width) * 55)
                    color = tuple(min(255, c + 30) for c in self.colors['success'])
                    pygame.draw.line(progress_surface, (*color, alpha),
                                   (x, 0), (x, bar_height))
                self.screen.blit(progress_surface, (bar_x, bar_y))
                
                # Progress highlight
                highlight_width = min(progress_width, 40)
                highlight_surface = pygame.Surface((highlight_width, bar_height), pygame.SRCALPHA)
                for x in range(highlight_width):
                    alpha = int(150 * (1 - x / highlight_width))
                    pygame.draw.line(highlight_surface, (255, 255, 255, alpha),
                                   (x, 0), (x, bar_height))
                self.screen.blit(highlight_surface, (bar_x, bar_y))
            
            # Border with glow
            pygame.draw.rect(self.screen, self.colors['ui_border'],
                           (bar_x, bar_y, bar_width, bar_height), 2)
            pygame.draw.rect(self.screen, self.colors['success'],
                           (bar_x + 1, bar_y + 1, bar_width - 2, bar_height - 2), 1)
            y_offset += 25
        
        # Draw radar
        if self.show_radar and env is not None:
            self.draw_radar(env, panel_x + 10, y_offset + 10, 100)
        
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
        """Update impact visual effects with enhanced modern flashes"""
        active_effects = []
        for effect in self.impact_effects:
            effect['frame'] += 1
            if effect['frame'] < effect['max_frames']:
                active_effects.append(effect)
                # Enhanced multiple flash layers
                progress = effect['frame'] / effect['max_frames']
                ease_out = 1 - (1 - progress) ** 2  # Ease out curve
                
                # Outer flash (white) - larger and brighter
                alpha1 = int(255 * (1 - progress) ** 0.5)
                radius1 = int(60 * ease_out)
                if radius1 > 0:
                    flash_surface1 = pygame.Surface((radius1 * 2, radius1 * 2), pygame.SRCALPHA)
                    # Radial gradient effect
                    for r in range(radius1, 0, -2):
                        ring_alpha = int(alpha1 * (r / radius1))
                        pygame.draw.circle(flash_surface1, (255, 255, 255, ring_alpha),
                                         (radius1, radius1), r)
                    self.screen.blit(flash_surface1,
                                   (effect['x'] - radius1, effect['y'] - radius1))
                
                # Middle flash (yellow/orange)
                alpha2 = int(220 * (1 - progress * 0.6))
                radius2 = int(35 * ease_out)
                if radius2 > 0:
                    flash_surface2 = pygame.Surface((radius2 * 2, radius2 * 2), pygame.SRCALPHA)
                    for r in range(radius2, 0, -2):
                        ring_alpha = int(alpha2 * (r / radius2))
                        pygame.draw.circle(flash_surface2, (255, 220, 100, ring_alpha),
                                         (radius2, radius2), r)
                    self.screen.blit(flash_surface2,
                                   (effect['x'] - radius2, effect['y'] - radius2))
                
                # Inner flash (bright orange/red)
                alpha3 = int(200 * (1 - progress * 0.4))
                radius3 = int(20 * ease_out)
                if radius3 > 0:
                    flash_surface3 = pygame.Surface((radius3 * 2, radius3 * 2), pygame.SRCALPHA)
                    for r in range(radius3, 0, -1):
                        ring_alpha = int(alpha3 * (r / radius3))
                        pygame.draw.circle(flash_surface3, (255, 150, 0, ring_alpha),
                                         (radius3, radius3), r)
                    self.screen.blit(flash_surface3,
                                   (effect['x'] - radius3, effect['y'] - radius3))
                
                # Core flash (white hot)
                alpha4 = int(255 * (1 - progress * 0.3))
                radius4 = int(10 * ease_out)
                if radius4 > 0:
                    flash_surface4 = pygame.Surface((radius4 * 2, radius4 * 2), pygame.SRCALPHA)
                    pygame.draw.circle(flash_surface4, (255, 255, 255, alpha4),
                                     (radius4, radius4), radius4)
                    self.screen.blit(flash_surface4,
                                   (effect['x'] - radius4, effect['y'] - radius4))
        self.impact_effects = active_effects
    
    def render(self, env, action: Optional[int] = None, stats: Optional[dict] = None):
        """Main enhanced render function"""
        self.frame_count += 1
        
        # Clear screen with gradient background
        # Create gradient background effect
        for y in range(self.height):
            # Subtle gradient from top to bottom
            gradient_factor = y / self.height
            r = int(self.colors['background'][0] + gradient_factor * 3)
            g = int(self.colors['background'][1] + gradient_factor * 3)
            b = int(self.colors['background'][2] + gradient_factor * 5)
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (self.width, y))
        
        # Update and draw starfield
        self.update_starfield()
        
        # Draw planet
        self.draw_planet()
        
        # Draw turret
        self.draw_turret(env.turret_angle)
        
        # Draw targeting line to closest asteroid
        if self.show_targeting_line and env.asteroids:
            self.draw_targeting_line(env)
        
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
                fps=fps,
                remaining_asteroids=len(env.asteroids),
                env=env,
                shots_fired=stats.get('shots_fired', 0),
                shots_hit=stats.get('shots_hit', 0),
                hit_rate=stats.get('hit_rate', 0.0)
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
                elif event.key == pygame.K_F4:
                    # Toggle radar
                    self.show_radar = not self.show_radar
                elif event.key == pygame.K_F5:
                    # Toggle distance rings
                    self.show_distance_rings = not self.show_distance_rings
                elif event.key == pygame.K_F6:
                    # Toggle targeting line
                    self.show_targeting_line = not self.show_targeting_line
        return True
    
    def quit(self):
        """Clean up"""
        pygame.quit()
