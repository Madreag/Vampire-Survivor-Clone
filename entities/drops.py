# entities/drops.py
"""
Collectible drops: XP gems, health pickups, and chests.
"""

import pygame
import math
import random
from settings import DROP_SETTINGS, COLORS


class Drop(pygame.sprite.Sprite):
    """Base class for all collectible drops."""
    
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.pos = pygame.math.Vector2(pos)
        self.collected = False
        self.magnet_speed = 500  # Speed when being pulled to player
        self.is_magnetized = False
    
    def magnetize(self, player_pos, pickup_radius, dt):
        """Move towards player if within pickup radius."""
        to_player = pygame.math.Vector2(player_pos) - self.pos
        distance = to_player.magnitude()
        
        if distance <= pickup_radius:
            self.is_magnetized = True
        
        if self.is_magnetized and distance > 5:
            # Move towards player
            direction = to_player.normalize()
            # Speed increases as we get closer
            speed = self.magnet_speed * (1 + (pickup_radius - distance) / pickup_radius)
            self.pos += direction * speed * dt
            self.rect.center = self.pos
            return False
        elif self.is_magnetized and distance <= 5:
            # Close enough to collect
            return True
        
        return False
    
    def update(self, dt, player_pos, pickup_radius):
        """Update the drop."""
        if self.magnetize(player_pos, pickup_radius, dt):
            self.collected = True


class ExperienceGem(Drop):
    """XP gem dropped by enemies."""
    
    def __init__(self, pos, groups, value=1):
        super().__init__(pos, groups)
        
        # Determine gem tier based on value
        if value >= 25:
            self.tier = 'large'
            self.data = DROP_SETTINGS['xp_gem_large']
        elif value >= 5:
            self.tier = 'medium'
            self.data = DROP_SETTINGS['xp_gem_medium']
        else:
            self.tier = 'small'
            self.data = DROP_SETTINGS['xp_gem_small']
        
        self.value = value
        self.color = self.data['color']
        self.size = self.data['size']
        
        # Create image
        self._create_image()
        self.rect = self.image.get_rect(center=pos)
        
        # Animation
        self.bob_offset = random.uniform(0, math.pi * 2)
        self.bob_timer = 0
    
    def _create_image(self):
        """Create gem image (diamond shape)."""
        size = self.size * 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        center = self.size
        
        # Diamond shape
        points = [
            (center, 2),
            (size - 2, center),
            (center, size - 2),
            (2, center)
        ]
        pygame.draw.polygon(self.image, self.color, points)
        pygame.draw.polygon(self.image, COLORS['white'], points, 1)
        
        # Inner shine
        inner_points = [
            (center, 4),
            (center + 3, center),
            (center, center + 3),
            (center - 3, center)
        ]
        pygame.draw.polygon(self.image, COLORS['white'], inner_points)
    
    def update(self, dt, player_pos, pickup_radius):
        """Update with bobbing animation."""
        super().update(dt, player_pos, pickup_radius)
        
        # Bobbing animation when not magnetized
        if not self.is_magnetized:
            self.bob_timer += dt * 3
            bob = math.sin(self.bob_timer + self.bob_offset) * 2
            # We don't actually move, just visual effect could be added


class HealthPickup(Drop):
    """Health pickup that restores HP."""
    
    def __init__(self, pos, groups):
        super().__init__(pos, groups)
        
        self.data = DROP_SETTINGS['health_pickup']
        self.value = self.data['value']
        self.color = self.data['color']
        self.size = self.data['size']
        
        # Create image
        self._create_image()
        self.rect = self.image.get_rect(center=pos)
        
        # Animation
        self.pulse_timer = 0
    
    def _create_image(self):
        """Create health pickup image (heart/cross shape)."""
        size = self.size * 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        center = self.size
        
        # Draw a cross/plus shape
        bar_width = self.size // 2
        
        # Vertical bar
        pygame.draw.rect(self.image, self.color,
                        (center - bar_width//2, 2, bar_width, size - 4))
        # Horizontal bar
        pygame.draw.rect(self.image, self.color,
                        (2, center - bar_width//2, size - 4, bar_width))
        
        # White border
        pygame.draw.rect(self.image, COLORS['white'],
                        (center - bar_width//2, 2, bar_width, size - 4), 1)
        pygame.draw.rect(self.image, COLORS['white'],
                        (2, center - bar_width//2, size - 4, bar_width), 1)
    
    def update(self, dt, player_pos, pickup_radius):
        """Update with pulsing animation."""
        super().update(dt, player_pos, pickup_radius)
        
        # Pulsing effect
        self.pulse_timer += dt * 4
        scale = 1 + math.sin(self.pulse_timer) * 0.1
        # Visual effect only, not actually scaling


class Chest(Drop):
    """Chest that grants random rewards when collected."""
    
    def __init__(self, pos, groups):
        super().__init__(pos, groups)
        
        self.data = DROP_SETTINGS['chest']
        self.color = self.data['color']
        self.size = self.data['size']
        
        # Chests don't magnetize, player must walk to them
        self.magnet_speed = 0
        
        # Create image
        self._create_image()
        self.rect = self.image.get_rect(center=pos)
        
        # Animation
        self.sparkle_timer = 0
    
    def _create_image(self):
        """Create chest image."""
        size = self.size * 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Chest body
        body_rect = pygame.Rect(2, self.size // 2, size - 4, self.size)
        pygame.draw.rect(self.image, self.color, body_rect)
        pygame.draw.rect(self.image, COLORS['brown'], body_rect, 2)
        
        # Chest lid
        lid_rect = pygame.Rect(2, 2, size - 4, self.size // 2 + 2)
        pygame.draw.rect(self.image, self.color, lid_rect)
        pygame.draw.rect(self.image, COLORS['brown'], lid_rect, 2)
        
        # Lock/clasp
        clasp_rect = pygame.Rect(self.size - 4, self.size // 2 - 2, 8, 8)
        pygame.draw.rect(self.image, COLORS['white'], clasp_rect)
    
    def magnetize(self, player_pos, pickup_radius, dt):
        """Chests don't magnetize, check direct collision."""
        to_player = pygame.math.Vector2(player_pos) - self.pos
        distance = to_player.magnitude()
        
        # Only collect when very close
        if distance <= self.size + 10:
            return True
        return False
    
    def update(self, dt, player_pos, pickup_radius):
        """Update with sparkle effect."""
        if self.magnetize(player_pos, pickup_radius, dt):
            self.collected = True
        
        # Sparkle animation
        self.sparkle_timer += dt


class DropManager:
    """Manages all drops in the game."""
    
    def __init__(self, drop_group, all_sprites_group):
        self.drop_group = drop_group
        self.all_sprites_group = all_sprites_group
    
    def spawn_xp_gem(self, pos, value):
        """Spawn an XP gem at position."""
        gem = ExperienceGem(pos, [self.drop_group, self.all_sprites_group], value)
        return gem
    
    def spawn_health_pickup(self, pos):
        """Spawn a health pickup at position."""
        pickup = HealthPickup(pos, [self.drop_group, self.all_sprites_group])
        return pickup
    
    def spawn_chest(self, pos):
        """Spawn a chest at position."""
        chest = Chest(pos, [self.drop_group, self.all_sprites_group])
        return chest
    
    def spawn_enemy_drops(self, enemy):
        """Spawn drops from a killed enemy."""
        drop_info = enemy.get_drop_info()
        pos = drop_info['pos']
        xp_value = drop_info['xp_value']
        
        # Always spawn XP gem
        self.spawn_xp_gem(pos, xp_value)
        
        # Chance for health pickup
        if random.random() < DROP_SETTINGS['health_pickup']['drop_chance']:
            # Offset slightly so they don't overlap
            offset_pos = pos + pygame.math.Vector2(
                random.uniform(-10, 10),
                random.uniform(-10, 10)
            )
            self.spawn_health_pickup(offset_pos)
        
        # Chance for chest
        if random.random() < DROP_SETTINGS['chest']['drop_chance']:
            offset_pos = pos + pygame.math.Vector2(
                random.uniform(-15, 15),
                random.uniform(-15, 15)
            )
            self.spawn_chest(offset_pos)
    
    def update(self, dt, player):
        """Update all drops and check for collection."""
        collected_xp = 0
        collected_health = 0
        collected_chests = []
        
        for drop in list(self.drop_group):
            drop.update(dt, player.pos, player.pickup_radius)
            
            if drop.collected:
                if isinstance(drop, ExperienceGem):
                    collected_xp += drop.value
                elif isinstance(drop, HealthPickup):
                    collected_health += drop.value
                elif isinstance(drop, Chest):
                    collected_chests.append(drop)
                
                drop.kill()
        
        return {
            'xp': collected_xp,
            'health': collected_health,
            'chests': collected_chests
        }
