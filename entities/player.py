# entities/player.py
"""
Player entity class with movement, stats, and combat handling.
"""

import pygame
import math
from settings import (
    PLAYER_SETTINGS, COLORS, WORLD_WIDTH, WORLD_HEIGHT,
    XP_SETTINGS, WINDOW_WIDTH, WINDOW_HEIGHT
)
from utils import clamp, CooldownTimer


class Player(pygame.sprite.Sprite):
    """
    The player character that the user controls.
    Handles movement, stats, leveling, and damage.
    """
    
    def __init__(self, pos, groups, cheat_settings=None):
        super().__init__(groups)
        
        # Store cheat settings
        self.cheat_settings = cheat_settings or {}
        
        # Position and movement
        self.pos = pygame.math.Vector2(pos)
        self.direction = pygame.math.Vector2()
        self.facing = pygame.math.Vector2(1, 0)  # Direction player is facing
        
        # Base stats (from settings)
        self.base_stats = PLAYER_SETTINGS.copy()
        
        # Current stats (modified by passives/upgrades)
        self.max_hp = self.base_stats['max_hp']
        self.hp = self.max_hp
        self.move_speed = self.base_stats['move_speed']
        self.pickup_radius = self.base_stats['pickup_radius']
        self.might = self.base_stats['might']
        self.cooldown_reduction = self.base_stats['cooldown_reduction']
        self.armor = self.base_stats['armor']
        self.regen = self.base_stats['regen']
        
        # Visual
        self.size = self.base_stats['size']
        self.color = self.base_stats['color']
        self._create_image()
        
        # Rect for collision
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-8, -8)
        
        # Leveling - Level 2 requires half the normal XP
        self.level = 1
        self.xp = 0
        # First level up (to level 2) requires half the base XP
        self.xp_to_next_level = XP_SETTINGS['base_xp_to_level'] // 2
        
        # Combat
        self.i_frames_duration = self.base_stats['i_frames_duration']
        self.i_frames_timer = 0
        self.is_invincible = False
        self.flash_timer = 0
        self.visible = True
        
        # Stats tracking
        self.kills = 0
        self.damage_dealt = 0
        self.damage_taken = 0
        
        # Regen timer
        self.regen_timer = 0
        
        # Death flag
        self.dead = False
    
    def _create_image(self):
        """Create the player's visual representation."""
        self.base_image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        # Draw player as a circle with a direction indicator
        center = (self.size, self.size)
        pygame.draw.circle(self.base_image, self.color, center, self.size)
        pygame.draw.circle(self.base_image, COLORS['white'], center, self.size, 2)
        
        # Direction indicator (small triangle) - pointing right (0 degrees)
        indicator_points = [
            (self.size + self.size * 0.8, self.size),
            (self.size + self.size * 0.3, self.size - self.size * 0.3),
            (self.size + self.size * 0.3, self.size + self.size * 0.3),
        ]
        pygame.draw.polygon(self.base_image, COLORS['white'], indicator_points)
        
        # Set initial image
        self.image = self.base_image.copy()
    
    def _update_image_rotation(self):
        """Rotate the player image to match the facing direction."""
        # Calculate angle from facing vector (in degrees)
        # atan2 returns angle in radians, convert to degrees
        # Pygame rotation is counter-clockwise, and atan2 gives angle from positive x-axis
        angle = math.degrees(math.atan2(-self.facing.y, self.facing.x))
        
        # Rotate the base image
        self.image = pygame.transform.rotate(self.base_image, angle)
        
        # Update rect to keep the player centered after rotation
        self.rect = self.image.get_rect(center=self.pos)
        self.hitbox.center = self.rect.center

    def _create_flash_image(self):
        """Create a flashing white image for i-frames."""
        flash_image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        center = (self.size, self.size)
        pygame.draw.circle(flash_image, COLORS['white'], center, self.size)
        return flash_image
    
    def input(self):
        """Handle player input for movement."""
        keys = pygame.key.get_pressed()
        
        # Reset direction
        self.direction.x = 0
        self.direction.y = 0
        
        # WASD / Arrow keys
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.direction.y = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.direction.y = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.direction.x = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.direction.x = 1
        
        # Normalize to prevent faster diagonal movement
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
            self.facing = self.direction.copy()
    
    def move(self, dt):
        """Move the player based on input and speed."""
        # Calculate movement
        movement = self.direction * self.move_speed * dt
        
        # Update position
        self.pos += movement
        
        # Clamp to world bounds
        self.pos.x = clamp(self.pos.x, self.size, WORLD_WIDTH - self.size)
        self.pos.y = clamp(self.pos.y, self.size, WORLD_HEIGHT - self.size)
        
        # Update rect
        self.rect.center = self.pos
        self.hitbox.center = self.rect.center
    
    def get_hit(self, damage):
        """Handle taking damage."""
        if self.is_invincible or self.dead:
            return False
        
        # Check for unlimited health cheat
        if self.cheat_settings.get('unlimited_health', False):
            # Still trigger i-frames for visual feedback but don't take damage
            self.is_invincible = True
            self.i_frames_timer = self.i_frames_duration
            return False
        
        # Apply armor reduction
        actual_damage = max(1, damage - self.armor)
        self.hp -= actual_damage
        self.damage_taken += actual_damage
        
        # Start i-frames
        self.is_invincible = True
        self.i_frames_timer = self.i_frames_duration
        
        # Check for death
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
            return True
        
        return False
    
    def heal(self, amount):
        """Heal the player."""
        self.hp = min(self.hp + amount, self.max_hp)
    
    def gain_xp(self, amount):
        """Add XP and check for level up."""
        self.xp += amount
        
        # Check for level up
        if self.xp >= self.xp_to_next_level:
            return self.level_up()
        return False
    
    def level_up(self):
        """Level up the player."""
        self.xp -= self.xp_to_next_level
        self.level += 1
        
        # Calculate XP requirement for next level
        # From level 2 onwards, XP requirement is reduced by 50%
        base_xp = (
            XP_SETTINGS['base_xp_to_level'] + 
            (self.level - 1) * XP_SETTINGS['xp_per_level_increase']
        )
        # Apply 50% reduction for level 2 and onwards
        self.xp_to_next_level = base_xp // 2
        
        # Small HP restore on level up
        self.heal(self.max_hp * 0.1)
        
        return True
    
    def apply_passive(self, passive_id, passive_data):
        """Apply a passive upgrade to player stats."""
        stat = passive_data['stat']
        value = passive_data['value']
        
        if stat == 'might':
            self.might += value
        elif stat == 'max_hp':
            self.max_hp += value
            self.hp += value  # Also heal the added HP
        elif stat == 'regen':
            self.regen += value
        elif stat == 'pickup_radius':
            self.pickup_radius *= (1 + value)
        elif stat == 'armor':
            self.armor += value
        elif stat == 'move_speed':
            self.move_speed *= (1 + value)
        elif stat == 'cooldown_reduction':
            self.cooldown_reduction += value
    
    def update_i_frames(self, dt):
        """Update invincibility frames."""
        if self.is_invincible:
            self.i_frames_timer -= dt
            
            # Flash effect
            self.flash_timer += dt
            if self.flash_timer >= 0.1:
                self.flash_timer = 0
                self.visible = not self.visible
            
            # End i-frames
            if self.i_frames_timer <= 0:
                self.is_invincible = False
                self.visible = True
                self.i_frames_timer = 0
    
    def update_regen(self, dt):
        """Update health regeneration."""
        if self.regen > 0 and self.hp < self.max_hp:
            self.regen_timer += dt
            if self.regen_timer >= 1.0:
                self.regen_timer = 0
                self.heal(self.regen)
    
    def update(self, dt):
        """Update the player."""
        if self.dead:
            return
        
        self.input()
        self.move(dt)
        self._update_image_rotation()
        self.update_i_frames(dt)
        self.update_regen(dt)
        
        # Update image alpha for flash effect
        if not self.visible:
            self.image.set_alpha(100)
        else:
            self.image.set_alpha(255)

    def get_xp_progress(self):
        """Get XP progress as a value from 0 to 1."""
        return self.xp / self.xp_to_next_level
    
    def get_hp_progress(self):
        """Get HP progress as a value from 0 to 1."""
        return self.hp / self.max_hp
    
    def get_stats_dict(self):
        """Get current stats as a dictionary."""
        return {
            'hp': self.hp,
            'max_hp': self.max_hp,
            'level': self.level,
            'xp': self.xp,
            'xp_to_next': self.xp_to_next_level,
            'might': self.might,
            'move_speed': self.move_speed,
            'pickup_radius': self.pickup_radius,
            'armor': self.armor,
            'regen': self.regen,
            'cooldown_reduction': self.cooldown_reduction,
            'kills': self.kills,
        }
