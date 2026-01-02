# entities/enemy.py
"""
Enemy entities that chase and attack the player.
"""

import pygame
import math
import random
from settings import ENEMY_DATA, COLORS, WORLD_WIDTH, WORLD_HEIGHT
from utils import distance_squared, draw_polygon


class Enemy(pygame.sprite.Sprite):
    """
    Base enemy class. Enemies chase the player and deal damage on contact.
    """
    
    def __init__(self, pos, groups, enemy_type='chaser', difficulty_mult=1.0):
        super().__init__(groups)
        
        # Get enemy data
        self.enemy_type = enemy_type
        self.data = ENEMY_DATA.get(enemy_type, ENEMY_DATA['chaser']).copy()
        
        # Apply difficulty scaling
        self.difficulty_mult = difficulty_mult
        
        # Stats
        self.max_hp = int(self.data['hp'] * difficulty_mult)
        self.hp = self.max_hp
        self.damage = int(self.data['damage'] * (1 + (difficulty_mult - 1) * 0.5))
        self.speed = self.data['speed']
        self.xp_value = self.data['xp_value']
        
        # Visual
        self.size = self.data['size']
        self.color = self.data['color']
        self.shape = self.data['shape']
        
        # Position
        self.pos = pygame.math.Vector2(pos)
        self.direction = pygame.math.Vector2()
        
        # Create image
        self._create_image()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-4, -4)
        
        # State
        self.knockback = pygame.math.Vector2()
        self.knockback_timer = 0
        
        # Special behaviors
        self.special = self.data.get('special', None)
        self.special_timer = 0
        self.zigzag_direction = 1
        
        # Damage cooldown (to prevent instant multi-hits)
        self.damage_cooldown = 0
    
    def _create_image(self):
        """Create the enemy's visual representation based on shape."""
        size = self.size * 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (self.size, self.size)
        
        if self.shape == 'circle':
            pygame.draw.circle(self.image, self.color, center, self.size)
            pygame.draw.circle(self.image, COLORS['white'], center, self.size, 2)
        
        elif self.shape == 'square':
            rect = pygame.Rect(0, 0, self.size * 2 - 4, self.size * 2 - 4)
            rect.center = center
            pygame.draw.rect(self.image, self.color, rect)
            pygame.draw.rect(self.image, COLORS['white'], rect, 2)
        
        elif self.shape == 'triangle':
            points = [
                (self.size, 2),
                (2, self.size * 2 - 2),
                (self.size * 2 - 2, self.size * 2 - 2)
            ]
            pygame.draw.polygon(self.image, self.color, points)
            pygame.draw.polygon(self.image, COLORS['white'], points, 2)
    
    def take_damage(self, damage, knockback_dir=None):
        """Take damage and apply knockback."""
        self.hp -= damage
        
        # Apply knockback
        if knockback_dir and knockback_dir.magnitude() > 0:
            self.knockback = knockback_dir.normalize() * 200
            self.knockback_timer = 0.1
        
        # Flash effect (change color briefly)
        self._flash()
        
        if self.hp <= 0:
            self.kill()
            return True
        return False
    
    def _flash(self):
        """Flash white when hit."""
        size = self.size * 2
        flash_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (self.size, self.size)
        
        if self.shape == 'circle':
            pygame.draw.circle(flash_surface, COLORS['white'], center, self.size)
        elif self.shape == 'square':
            rect = pygame.Rect(0, 0, self.size * 2 - 4, self.size * 2 - 4)
            rect.center = center
            pygame.draw.rect(flash_surface, COLORS['white'], rect)
        elif self.shape == 'triangle':
            points = [
                (self.size, 2),
                (2, self.size * 2 - 2),
                (self.size * 2 - 2, self.size * 2 - 2)
            ]
            pygame.draw.polygon(flash_surface, COLORS['white'], points)
        
        # Blend with original
        self.image.blit(flash_surface, (0, 0), special_flags=pygame.BLEND_ADD)
    
    def move_towards_player(self, player_pos, dt):
        """Move towards the player position."""
        # Calculate direction to player
        to_player = pygame.math.Vector2(player_pos) - self.pos
        
        if to_player.magnitude() > 0:
            self.direction = to_player.normalize()
        
        # Apply special movement patterns
        if self.special == 'zigzag':
            self.special_timer += dt
            if self.special_timer >= 0.3:
                self.special_timer = 0
                self.zigzag_direction *= -1
            
            # Add perpendicular movement
            perp = pygame.math.Vector2(-self.direction.y, self.direction.x)
            self.direction += perp * 0.5 * self.zigzag_direction
            if self.direction.magnitude() > 0:
                self.direction = self.direction.normalize()
        
        # Apply knockback
        if self.knockback_timer > 0:
            self.knockback_timer -= dt
            movement = self.knockback * dt
        else:
            movement = self.direction * self.speed * dt
            self.knockback = pygame.math.Vector2()
        
        # Update position
        self.pos += movement
        
        # Clamp to world bounds
        self.pos.x = max(self.size, min(WORLD_WIDTH - self.size, self.pos.x))
        self.pos.y = max(self.size, min(WORLD_HEIGHT - self.size, self.pos.y))
        
        # Update rect
        self.rect.center = self.pos
        self.hitbox.center = self.rect.center
    
    def can_damage(self):
        """Check if enemy can deal damage (cooldown check)."""
        return self.damage_cooldown <= 0
    
    def reset_damage_cooldown(self):
        """Reset damage cooldown after hitting player."""
        self.damage_cooldown = 0.5  # Half second between hits
    
    def update(self, dt, player_pos):
        """Update the enemy."""
        self.move_towards_player(player_pos, dt)
        
        # Update damage cooldown
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt
        
        # Recreate image (reset flash)
        self._create_image()
    
    def get_drop_info(self):
        """Get information about what this enemy drops."""
        return {
            'xp_value': self.xp_value,
            'pos': self.pos.copy()
        }


class Chaser(Enemy):
    """Fast, weak enemy."""
    
    def __init__(self, pos, groups, difficulty_mult=1.0):
        super().__init__(pos, groups, 'chaser', difficulty_mult)


class Tank(Enemy):
    """Slow, strong enemy."""
    
    def __init__(self, pos, groups, difficulty_mult=1.0):
        super().__init__(pos, groups, 'tank', difficulty_mult)


class Swarm(Enemy):
    """Small, fast enemy that spawns in groups."""
    
    def __init__(self, pos, groups, difficulty_mult=1.0):
        super().__init__(pos, groups, 'swarm', difficulty_mult)


class Ghost(Enemy):
    """Enemy with phasing visual effect."""
    
    def __init__(self, pos, groups, difficulty_mult=1.0):
        super().__init__(pos, groups, 'ghost', difficulty_mult)
        self.alpha = 255
        self.alpha_direction = -1
    
    def update(self, dt, player_pos):
        super().update(dt, player_pos)
        
        # Phasing effect
        self.alpha += self.alpha_direction * 200 * dt
        if self.alpha <= 100:
            self.alpha = 100
            self.alpha_direction = 1
        elif self.alpha >= 255:
            self.alpha = 255
            self.alpha_direction = -1
        
        self.image.set_alpha(int(self.alpha))


class Bat(Enemy):
    """Fast enemy with zigzag movement."""
    
    def __init__(self, pos, groups, difficulty_mult=1.0):
        super().__init__(pos, groups, 'bat', difficulty_mult)


class Boss(Enemy):
    """Large, powerful enemy that spawns periodically."""
    
    def __init__(self, pos, groups, difficulty_mult=1.0):
        super().__init__(pos, groups, 'boss', difficulty_mult)
        self.is_boss = True
    
    def _create_image(self):
        """Create a more impressive boss image."""
        size = self.size * 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (self.size, self.size)
        
        # Outer glow
        pygame.draw.circle(self.image, (*self.color[:3], 100), center, self.size + 4)
        
        # Main body
        pygame.draw.rect(self.image, self.color, 
                        (4, 4, self.size * 2 - 8, self.size * 2 - 8))
        pygame.draw.rect(self.image, COLORS['gold'], 
                        (4, 4, self.size * 2 - 8, self.size * 2 - 8), 3)
        
        # Inner detail
        inner_rect = pygame.Rect(0, 0, self.size, self.size)
        inner_rect.center = center
        pygame.draw.rect(self.image, COLORS['black'], inner_rect)
        pygame.draw.rect(self.image, COLORS['red'], inner_rect, 2)


def create_enemy(enemy_type, pos, groups, difficulty_mult=1.0):
    """Factory function to create enemies by type."""
    enemy_classes = {
        'chaser': Chaser,
        'tank': Tank,
        'swarm': Swarm,
        'ghost': Ghost,
        'bat': Bat,
        'boss': Boss,
    }
    
    enemy_class = enemy_classes.get(enemy_type, Chaser)
    return enemy_class(pos, groups, difficulty_mult)
