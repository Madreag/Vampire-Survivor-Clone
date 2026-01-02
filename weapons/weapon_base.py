# weapons/weapon_base.py
"""
Base weapon class and weapon-related utilities.
"""

import pygame
from abc import ABC, abstractmethod
from settings import WEAPON_DATA, EVOLUTION_DATA
from utils import CooldownTimer, get_closest_enemy


class Weapon(ABC):
    """
    Abstract base class for all weapons.
    Weapons auto-fire and can be leveled up.
    """
    
    def __init__(self, weapon_id, player, projectile_group, enemy_group, all_sprites):
        self.weapon_id = weapon_id
        self.player = player
        self.projectile_group = projectile_group
        self.enemy_group = enemy_group
        self.all_sprites = all_sprites
        
        # Get base data
        self.data = WEAPON_DATA.get(weapon_id, WEAPON_DATA['whip']).copy()
        
        # Current level
        self.level = 1
        self.max_level = self.data['max_level']
        
        # Stats (will be recalculated)
        self.damage = self.data['base_damage']
        self.cooldown = self.data['base_cooldown']
        self.area = self.data['base_area']
        self.speed = self.data['base_speed']
        self.amount = self.data['base_amount']
        self.pierce = self.data.get('base_pierce', 1)
        
        # Cooldown timer
        self.cooldown_timer = CooldownTimer(self.cooldown)
        
        # Evolution status
        self.evolved = False
        self.evolution_id = self.data.get('evolution', None)
        self.evolution_passive = self.data.get('evolution_passive', None)
        
        # Calculate initial stats
        self._recalculate_stats()
    
    def _recalculate_stats(self):
        """Recalculate stats based on current level and player modifiers."""
        scaling = self.data['scaling']
        level_bonus = self.level - 1
        
        # Base stats + level scaling
        self.damage = self.data['base_damage'] + scaling['damage'] * level_bonus
        self.cooldown = max(0.1, self.data['base_cooldown'] + scaling['cooldown'] * level_bonus)
        self.area = self.data['base_area'] + scaling['area'] * level_bonus
        
        # Amount increases every 2 levels for some weapons
        if scaling['amount'] > 0:
            self.amount = self.data['base_amount'] + (level_bonus // 2) * scaling['amount']
        else:
            self.amount = self.data['base_amount']
        
        # Calculate size multiplier based on level (1.0 at level 1, 3.0 at max level)
        # Linear interpolation: size_mult = 1.0 + (level - 1) / (max_level - 1) * 2.0
        if self.max_level > 1:
            self.size_multiplier = 1.0 + (self.level - 1) / (self.max_level - 1) * 2.0
        else:
            self.size_multiplier = 1.0
        
        # Apply player modifiers
        self.damage *= self.player.might
        self.cooldown *= (1 - self.player.cooldown_reduction)
        
        # Update cooldown timer
        self.cooldown_timer = CooldownTimer(self.cooldown)
    
    def level_up(self):
        """Level up the weapon."""
        if self.level < self.max_level:
            self.level += 1
            self._recalculate_stats()
            return True
        return False
    
    def can_evolve(self, passive_inventory):
        """Check if weapon can evolve."""
        if self.evolved or not self.evolution_id:
            return False
        
        if self.level < self.max_level:
            return False
        
        # Check if player has required passive
        if self.evolution_passive and self.evolution_passive in passive_inventory:
            return True
        
        return False
    
    def evolve(self):
        """Evolve the weapon into its upgraded form."""
        if not self.evolution_id:
            return False
        
        evolution_data = EVOLUTION_DATA.get(self.evolution_id)
        if not evolution_data:
            return False
        
        self.evolved = True
        self.data['name'] = evolution_data['name']
        self.data['color'] = evolution_data['color']
        
        # Apply evolution bonuses
        self.damage *= evolution_data.get('damage_mult', 1.5)
        
        return True
    
    def get_effective_damage(self):
        """Get the current effective damage."""
        return self.damage
    
    def update(self, dt):
        """Update the weapon (check cooldown and attack)."""
        if self.cooldown_timer.use():
            self.attack()
    
    @abstractmethod
    def attack(self):
        """Perform the weapon's attack. Must be implemented by subclasses."""
        pass
    
    def get_info(self):
        """Get weapon info for UI display."""
        return {
            'id': self.weapon_id,
            'name': self.data['name'],
            'level': self.level,
            'max_level': self.max_level,
            'damage': self.damage,
            'cooldown': self.cooldown,
            'color': self.data['color'],
            'evolved': self.evolved,
        }
    
    def get_upgrade_description(self):
        """Get description of what the next level provides."""
        if self.level >= self.max_level:
            if self.can_evolve([]):
                return "Ready to evolve!"
            return "MAX LEVEL"
        
        scaling = self.data['scaling']
        desc_parts = []
        
        if scaling['damage'] > 0:
            desc_parts.append(f"+{scaling['damage']} damage")
        if scaling['cooldown'] < 0:
            desc_parts.append(f"{scaling['cooldown']:.2f}s cooldown")
        if scaling['area'] > 0:
            desc_parts.append(f"+{int(scaling['area']*100)}% area")
        if scaling['amount'] > 0 and (self.level % 2 == 0):
            desc_parts.append(f"+1 projectile")
        
        return ", ".join(desc_parts) if desc_parts else "Improved stats"


class WeaponUpgrade:
    """Represents a weapon upgrade option for the level-up screen."""
    
    def __init__(self, weapon_id, is_new=False, current_level=0):
        self.weapon_id = weapon_id
        self.is_new = is_new
        self.current_level = current_level
        self.data = WEAPON_DATA.get(weapon_id, WEAPON_DATA['whip'])
    
    def get_display_info(self):
        """Get info for displaying this upgrade option."""
        if self.is_new:
            return {
                'title': f"NEW: {self.data['name']}",
                'description': self.data['description'],
                'level_text': "Level 1",
                'color': self.data['color'],
                'is_new': True,
            }
        else:
            return {
                'title': self.data['name'],
                'description': f"Level {self.current_level} → {self.current_level + 1}",
                'level_text': f"Level {self.current_level + 1}",
                'color': self.data['color'],
                'is_new': False,
            }
