# weapons/projectiles.py
"""
Projectile and attack effect sprites for weapons.
"""

import pygame
import math
import random
from settings import COLORS, WEAPON_DATA


class Projectile(pygame.sprite.Sprite):
    """Base projectile class for ranged attacks."""
    
    def __init__(self, pos, direction, groups, damage, speed, pierce=1, 
                 size=8, color=COLORS['white'], lifetime=5.0, size_multiplier=1.0):
        super().__init__(groups)
        
        self.pos = pygame.math.Vector2(pos)
        self.direction = pygame.math.Vector2(direction)
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        
        self.damage = damage
        self.speed = speed
        self.pierce = pierce
        self.hits_remaining = pierce
        self.size_multiplier = size_multiplier
        self.base_size = size
        self.size = int(size * size_multiplier)  # Apply size multiplier
        self.color = color
        self.lifetime = lifetime
        self.age = 0
        
        # Track hit enemies to prevent multi-hit
        self.hit_enemies = set()
        
        # Create image
        self._create_image()
        self.rect = self.image.get_rect(center=pos)
    
    def _create_image(self):
        """Create projectile image."""
        size = self.size * 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.size, self.size), self.size)
        pygame.draw.circle(self.image, COLORS['white'], (self.size, self.size), self.size, 1)
    
    def move(self, dt):
        """Move the projectile."""
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos
    
    def hit_enemy(self, enemy):
        """Called when projectile hits an enemy."""
        if id(enemy) in self.hit_enemies:
            return False
        
        self.hit_enemies.add(id(enemy))
        self.hits_remaining -= 1
        
        if self.hits_remaining <= 0:
            self.kill()
        
        return True
    
    def update(self, dt):
        """Update the projectile."""
        self.move(dt)
        self.age += dt
        
        if self.age >= self.lifetime:
            self.kill()


class WandProjectile(Projectile):
    """Magic wand projectile that flies toward target."""
    
    def __init__(self, pos, direction, groups, damage, speed, pierce=1, homing=False, size_multiplier=1.0):
        self.homing = homing
        self.target = None
        super().__init__(pos, direction, groups, damage, speed, pierce,
                        size=6, color=COLORS['blue'], lifetime=3.0, size_multiplier=size_multiplier)
    
    def _create_image(self):
        """Create a glowing orb."""
        size = self.size * 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Outer glow
        pygame.draw.circle(self.image, (*self.color, 100), (self.size, self.size), self.size)
        # Inner core
        inner_size = max(1, self.size - 2)
        pygame.draw.circle(self.image, self.color, (self.size, self.size), inner_size)
        pygame.draw.circle(self.image, COLORS['white'], (self.size, self.size), max(1, self.size // 2))
    
    def set_target(self, target):
        """Set homing target."""
        self.target = target
    
    def move(self, dt):
        """Move with optional homing."""
        if self.homing and self.target and self.target.alive():
            to_target = pygame.math.Vector2(self.target.rect.center) - self.pos
            if to_target.magnitude() > 0:
                desired = to_target.normalize()
                # Gradually turn toward target
                self.direction = self.direction.lerp(desired, 0.1)
                if self.direction.magnitude() > 0:
                    self.direction = self.direction.normalize()
        
        super().move(dt)


class KnifeProjectile(Projectile):
    """Knife projectile - fast and straight."""
    
    def __init__(self, pos, direction, groups, damage, speed, pierce=1, size_multiplier=1.0):
        # Calculate rotation before calling parent init
        self.rotation = math.degrees(math.atan2(direction[1], direction[0]))
        super().__init__(pos, direction, groups, damage, speed, pierce,
                        size=5, color=COLORS['silver'], lifetime=2.0, size_multiplier=size_multiplier)
    
    def _create_image(self):
        """Create a knife shape."""
        # Scale knife dimensions based on size_multiplier
        width = int(20 * self.size_multiplier)
        height = int(8 * self.size_multiplier)
        base_image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Knife blade - scale all points
        points = [
            (0, height // 2), 
            (int(15 * self.size_multiplier), 0), 
            (width, height // 2), 
            (int(15 * self.size_multiplier), height)
        ]
        pygame.draw.polygon(base_image, self.color, points)
        pygame.draw.polygon(base_image, COLORS['white'], points, 1)
        
        # Rotate to face direction
        self.image = pygame.transform.rotate(base_image, -self.rotation)
        self.rect = self.image.get_rect(center=self.pos)


class AxeProjectile(Projectile):
    """Axe projectile - arcs upward then falls."""
    
    def __init__(self, pos, direction, groups, damage, speed, pierce=999, size_multiplier=1.0):
        # Set arc motion properties before parent init
        self.vertical_speed = -300  # Initial upward velocity
        self.gravity = 400
        self.rotation = 0
        self.rotation_speed = 720  # Degrees per second
        super().__init__(pos, direction, groups, damage, speed, pierce,
                        size=12, color=COLORS['gray'], lifetime=3.0, size_multiplier=size_multiplier)
    
    def _create_image(self):
        """Create an axe shape."""
        size = self.size * 2
        self.base_image = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Axe head (diamond shape) - scaled based on size
        head_points = [
            (self.size, 2),
            (size - 4, self.size),
            (self.size, size - 2),
            (4, self.size)
        ]
        pygame.draw.polygon(self.base_image, self.color, head_points)
        line_width = max(1, int(2 * self.size_multiplier))
        pygame.draw.polygon(self.base_image, COLORS['brown'], head_points, line_width)
        
        # Handle
        handle_width = max(1, int(3 * self.size_multiplier))
        pygame.draw.line(self.base_image, COLORS['brown'], 
                        (self.size, self.size), (self.size, size - 2), handle_width)
        
        self.image = self.base_image.copy()
    
    def move(self, dt):
        """Move in an arc."""
        # Horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        
        # Vertical arc movement
        self.pos.y += self.vertical_speed * dt
        self.vertical_speed += self.gravity * dt
        
        # Rotation
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotate(self.base_image, self.rotation)
        
        self.rect = self.image.get_rect(center=self.pos)


class WhipSlash(pygame.sprite.Sprite):
    """Whip attack - horizontal slash."""
    
    def __init__(self, pos, direction, groups, damage, area=1.0, pierce=999, size_multiplier=1.0):
        super().__init__(groups)
        
        self.pos = pygame.math.Vector2(pos)
        self.direction = pygame.math.Vector2(direction)
        self.damage = damage
        self.pierce = pierce
        self.hits_remaining = pierce
        self.hit_enemies = set()
        self.size_multiplier = size_multiplier
        
        # Slash properties - length (width) scales with size_multiplier, height stays similar
        self.width = int(100 * area * size_multiplier)  # Length increases with level
        self.height = int(30 * area)  # Height stays relatively the same
        self.lifetime = 0.2
        self.age = 0
        
        # Position offset based on direction
        if self.direction.x >= 0:
            offset_x = 40 + self.width // 2
        else:
            offset_x = -40 - self.width // 2
        
        self.pos.x += offset_x
        
        # Create image
        self._create_image()
        self.rect = self.image.get_rect(center=self.pos)
    
    def _create_image(self):
        """Create slash effect."""
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Slash arc
        color = WEAPON_DATA['whip']['color']
        
        # Draw multiple lines for slash effect - line thickness scales slightly with size
        line_thickness = max(2, int(3 * self.size_multiplier))
        for i in range(5):
            alpha = 255 - i * 40
            y_offset = i * 3
            pygame.draw.line(self.image, (*color, alpha),
                           (0, self.height // 2 + y_offset),
                           (self.width, self.height // 2 - y_offset), line_thickness)
    
    def hit_enemy(self, enemy):
        """Called when slash hits an enemy."""
        if id(enemy) in self.hit_enemies:
            return False
        
        self.hit_enemies.add(id(enemy))
        return True
    
    def update(self, dt):
        """Update the slash."""
        self.age += dt
        
        # Fade out
        alpha = int(255 * (1 - self.age / self.lifetime))
        self.image.set_alpha(max(0, alpha))
        
        if self.age >= self.lifetime:
            self.kill()


class GarlicAura(pygame.sprite.Sprite):
    """Garlic aura - damages nearby enemies continuously."""
    
    def __init__(self, player, groups, damage, radius=60, tick_rate=0.5):
        super().__init__(groups)
        
        self.player = player
        self.damage = damage
        self.radius = radius
        self.tick_rate = tick_rate
        self.tick_timer = 0
        
        # Track recently hit enemies for damage ticks
        self.damage_timers = {}
        
        # Create image
        self._create_image()
        self.rect = self.image.get_rect(center=player.pos)
    
    def _create_image(self):
        """Create aura effect."""
        size = self.radius * 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        
        color = WEAPON_DATA['garlic']['color']
        
        # Multiple rings for effect
        for i in range(3):
            r = self.radius - i * 10
            if r > 0:
                alpha = 60 - i * 15
                pygame.draw.circle(self.image, (*color, alpha), 
                                 (self.radius, self.radius), r)
        
        # Outer ring
        pygame.draw.circle(self.image, (*color, 100), 
                         (self.radius, self.radius), self.radius, 2)
    
    def update_radius(self, new_radius):
        """Update the aura radius."""
        self.radius = new_radius
        self._create_image()
    
    def update_damage(self, new_damage):
        """Update the aura damage."""
        self.damage = new_damage
    
    def can_damage_enemy(self, enemy):
        """Check if enemy can be damaged (tick rate)."""
        enemy_id = id(enemy)
        current_time = pygame.time.get_ticks() / 1000
        
        if enemy_id not in self.damage_timers:
            self.damage_timers[enemy_id] = current_time
            return True
        
        if current_time - self.damage_timers[enemy_id] >= self.tick_rate:
            self.damage_timers[enemy_id] = current_time
            return True
        
        return False
    
    def get_enemies_in_range(self, enemy_group):
        """Get all enemies within aura range."""
        enemies = []
        for enemy in enemy_group:
            dist = (pygame.math.Vector2(enemy.rect.center) - self.player.pos).magnitude()
            if dist <= self.radius:
                enemies.append(enemy)
        return enemies
    
    def update(self, dt):
        """Update aura position to follow player."""
        self.rect.center = self.player.pos
        
        # Clean up old damage timers
        current_time = pygame.time.get_ticks() / 1000
        self.damage_timers = {
            k: v for k, v in self.damage_timers.items()
            if current_time - v < self.tick_rate * 2
        }


class DamageNumber(pygame.sprite.Sprite):
    """Floating damage number for visual feedback."""
    
    def __init__(self, pos, damage, groups, color=COLORS['white']):
        super().__init__(groups)
        
        self.pos = pygame.math.Vector2(pos)
        self.damage = damage
        self.color = color
        self.lifetime = 0.8
        self.age = 0
        self.velocity = pygame.math.Vector2(random.uniform(-20, 20), -50)
        
        # Create image
        self._create_image()
        self.rect = self.image.get_rect(center=pos)
    
    def _create_image(self):
        """Create damage number image."""
        font = pygame.font.Font(None, 24)
        text = str(int(self.damage))
        
        # Shadow
        shadow = font.render(text, True, COLORS['black'])
        text_surf = font.render(text, True, self.color)
        
        # Combine
        width = text_surf.get_width() + 2
        height = text_surf.get_height() + 2
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.blit(shadow, (2, 2))
        self.image.blit(text_surf, (0, 0))
    
    def update(self, dt):
        """Update floating number."""
        self.age += dt
        
        # Float upward
        self.pos += self.velocity * dt
        self.velocity.y += 100 * dt  # Slow down
        
        self.rect.center = self.pos
        
        # Fade out
        alpha = int(255 * (1 - self.age / self.lifetime))
        self.image.set_alpha(max(0, alpha))
        
        if self.age >= self.lifetime:
            self.kill()
