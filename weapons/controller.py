# weapons/controller.py
"""
Weapon controller that manages the player's weapon inventory.
"""

import pygame
import random
from settings import WEAPON_DATA, PASSIVE_DATA, MAX_WEAPONS, MAX_PASSIVES, COLORS
from weapons.weapon_base import Weapon, WeaponUpgrade
from weapons.projectiles import (
    WandProjectile, KnifeProjectile, AxeProjectile,
    WhipSlash, GarlicAura, DamageNumber
)
from utils import get_closest_enemy, get_enemies_in_range


class WhipWeapon(Weapon):
    """Whip weapon - horizontal slash attack."""
    
    def __init__(self, player, projectile_group, enemy_group, all_sprites):
        super().__init__('whip', player, projectile_group, enemy_group, all_sprites)
    
    def attack(self):
        """Perform whip slash attack."""
        for i in range(self.amount):
            # Alternate directions if multiple slashes
            if i % 2 == 0:
                direction = self.player.facing.copy()
            else:
                direction = -self.player.facing.copy()
            
            slash = WhipSlash(
                self.player.pos.copy(),
                direction,
                [self.projectile_group, self.all_sprites],
                self.damage,
                self.area,
                self.pierce,
                self.size_multiplier  # Pass size multiplier for length scaling
            )


class WandWeapon(Weapon):
    """Magic wand - fires projectiles at nearest enemy."""
    
    def __init__(self, player, projectile_group, enemy_group, all_sprites):
        super().__init__('wand', player, projectile_group, enemy_group, all_sprites)
        self.homing = False
    
    def attack(self):
        """Fire projectile at nearest enemy."""
        for i in range(self.amount):
            target = get_closest_enemy(self.player.pos, self.enemy_group)
            
            if target:
                direction = pygame.math.Vector2(target.rect.center) - self.player.pos
            else:
                # Fire in facing direction if no enemies
                direction = self.player.facing.copy()
            
            if direction.magnitude() > 0:
                direction = direction.normalize()
            
            # Slight spread for multiple projectiles
            if self.amount > 1:
                angle_offset = (i - self.amount // 2) * 15
                direction = direction.rotate(angle_offset)
            
            projectile = WandProjectile(
                self.player.pos.copy(),
                direction,
                [self.projectile_group, self.all_sprites],
                self.damage,
                self.speed,
                self.pierce,
                self.homing,
                self.size_multiplier  # Pass size multiplier for projectile scaling
            )
            
            if self.homing and target:
                projectile.set_target(target)
    
    def evolve(self):
        """Evolve to Holy Wand with homing."""
        if super().evolve():
            self.homing = True
            return True
        return False


class GarlicWeapon(Weapon):
    """Garlic - aura that damages nearby enemies."""
    
    def __init__(self, player, projectile_group, enemy_group, all_sprites):
        super().__init__('garlic', player, projectile_group, enemy_group, all_sprites)
        
        # Create persistent aura
        base_radius = self.data.get('base_radius', 60)
        self.aura = GarlicAura(
            player,
            [self.projectile_group, self.all_sprites],
            self.damage,
            int(base_radius * self.area * self.size_multiplier),  # Apply size multiplier
            self.cooldown
        )
    
    def _recalculate_stats(self):
        """Recalculate and update aura."""
        super()._recalculate_stats()
        
        if hasattr(self, 'aura'):
            base_radius = self.data.get('base_radius', 60)
            # Apply size_multiplier to radius for increased collision area
            self.aura.update_radius(int(base_radius * self.area * self.size_multiplier))
            self.aura.update_damage(self.damage)
            self.aura.tick_rate = self.cooldown
    
    def attack(self):
        """Garlic attacks through its aura - handled in update."""
        pass
    
    def update(self, dt):
        """Update garlic aura and deal damage."""
        self.aura.update(dt)
        
        # Check for enemies in range
        enemies_in_range = self.aura.get_enemies_in_range(self.enemy_group)
        
        dead_enemies = []
        for enemy in enemies_in_range:
            if self.aura.can_damage_enemy(enemy):
                knockback_dir = pygame.math.Vector2(enemy.rect.center) - self.player.pos
                # Get drop info BEFORE the enemy is killed
                drop_info = enemy.get_drop_info()
                if enemy.take_damage(self.damage, knockback_dir):
                    dead_enemies.append(drop_info)
        
        return dead_enemies


class AxeWeapon(Weapon):
    """Axe - thrown in arc, passes through enemies."""
    
    def __init__(self, player, projectile_group, enemy_group, all_sprites):
        super().__init__('axe', player, projectile_group, enemy_group, all_sprites)
    
    def attack(self):
        """Throw axes in arc."""
        for i in range(self.amount):
            # Random direction with upward bias
            angle = random.uniform(-60, 60)
            direction = self.player.facing.rotate(angle)
            
            # Alternate left/right for multiple axes
            if self.amount > 1:
                if i % 2 == 0:
                    direction.x = abs(direction.x)
                else:
                    direction.x = -abs(direction.x)
            
            AxeProjectile(
                self.player.pos.copy(),
                direction,
                [self.projectile_group, self.all_sprites],
                self.damage,
                self.speed,
                self.pierce,
                self.size_multiplier  # Pass size multiplier for projectile scaling
            )


class KnifeWeapon(Weapon):
    """Knife - fast projectiles in facing direction."""
    
    def __init__(self, player, projectile_group, enemy_group, all_sprites):
        super().__init__('knife', player, projectile_group, enemy_group, all_sprites)
    
    def attack(self):
        """Throw knives."""
        for i in range(self.amount):
            direction = self.player.facing.copy()
            
            # Spread for multiple knives
            if self.amount > 1:
                spread = 10 * (self.amount - 1)
                angle_offset = -spread/2 + (spread / (self.amount - 1)) * i if self.amount > 1 else 0
                direction = direction.rotate(angle_offset)
            
            KnifeProjectile(
                self.player.pos.copy(),
                direction,
                [self.projectile_group, self.all_sprites],
                self.damage,
                self.speed,
                self.pierce,
                self.size_multiplier  # Pass size multiplier for projectile scaling
            )


# Weapon factory
WEAPON_CLASSES = {
    'whip': WhipWeapon,
    'wand': WandWeapon,
    'garlic': GarlicWeapon,
    'axe': AxeWeapon,
    'knife': KnifeWeapon,
}


class WeaponController:
    """
    Manages the player's weapon and passive inventory.
    Handles weapon attacks, upgrades, and evolutions.
    """
    
    def __init__(self, player, projectile_group, enemy_group, all_sprites):
        self.player = player
        self.projectile_group = projectile_group
        self.enemy_group = enemy_group
        self.all_sprites = all_sprites
        
        # Inventories
        self.weapons = {}  # weapon_id: Weapon instance
        self.passives = {}  # passive_id: level
        
        # Limits
        self.max_weapons = MAX_WEAPONS
        self.max_passives = MAX_PASSIVES
    
    def add_weapon(self, weapon_id):
        """Add a new weapon or level up existing one."""
        if weapon_id in self.weapons:
            # Level up existing weapon
            return self.weapons[weapon_id].level_up()
        
        if len(self.weapons) >= self.max_weapons:
            return False
        
        # Create new weapon
        weapon_class = WEAPON_CLASSES.get(weapon_id)
        if weapon_class:
            self.weapons[weapon_id] = weapon_class(
                self.player,
                self.projectile_group,
                self.enemy_group,
                self.all_sprites
            )
            return True
        
        return False
    
    def add_passive(self, passive_id):
        """Add a new passive or level up existing one."""
        passive_data = PASSIVE_DATA.get(passive_id)
        if not passive_data:
            return False
        
        if passive_id in self.passives:
            # Level up existing passive
            if self.passives[passive_id] < passive_data['max_level']:
                self.passives[passive_id] += 1
                self.player.apply_passive(passive_id, passive_data)
                self._update_weapon_stats()
                return True
            return False
        
        if len(self.passives) >= self.max_passives:
            return False
        
        # Add new passive
        self.passives[passive_id] = 1
        self.player.apply_passive(passive_id, passive_data)
        self._update_weapon_stats()
        return True
    
    def _update_weapon_stats(self):
        """Update all weapon stats after passive changes."""
        for weapon in self.weapons.values():
            weapon._recalculate_stats()
    
    def check_evolutions(self):
        """Check if any weapons can evolve."""
        evolutions = []
        for weapon_id, weapon in self.weapons.items():
            if weapon.can_evolve(self.passives):
                evolutions.append(weapon_id)
        return evolutions
    
    def evolve_weapon(self, weapon_id):
        """Evolve a weapon."""
        if weapon_id in self.weapons:
            return self.weapons[weapon_id].evolve()
        return False
    
    def get_upgrade_options(self, count=3):
        """Get random upgrade options for level-up screen."""
        options = []
        
        # Collect all possible upgrades
        possible = []
        
        # Weapons that can be leveled up
        for weapon_id, weapon in self.weapons.items():
            if weapon.level < weapon.max_level:
                possible.append(('weapon', weapon_id, False, weapon.level))
        
        # New weapons (if slots available)
        if len(self.weapons) < self.max_weapons:
            for weapon_id in WEAPON_DATA:
                if weapon_id not in self.weapons:
                    possible.append(('weapon', weapon_id, True, 0))
        
        # Passives that can be leveled up
        for passive_id, level in self.passives.items():
            passive_data = PASSIVE_DATA.get(passive_id)
            if passive_data and level < passive_data['max_level']:
                possible.append(('passive', passive_id, False, level))
        
        # New passives (if slots available)
        if len(self.passives) < self.max_passives:
            for passive_id in PASSIVE_DATA:
                if passive_id not in self.passives:
                    possible.append(('passive', passive_id, True, 0))
        
        # Check for evolutions
        for weapon_id in self.check_evolutions():
            possible.append(('evolution', weapon_id, False, 0))
        
        # Randomly select options
        random.shuffle(possible)
        options = possible[:count]
        
        # If not enough options, add some duplicates or filler
        while len(options) < count and possible:
            options.append(random.choice(possible))
        
        return options
    
    def apply_upgrade(self, upgrade_type, upgrade_id):
        """Apply a selected upgrade."""
        if upgrade_type == 'weapon':
            return self.add_weapon(upgrade_id)
        elif upgrade_type == 'passive':
            return self.add_passive(upgrade_id)
        elif upgrade_type == 'evolution':
            return self.evolve_weapon(upgrade_id)
        return False
    
    def update(self, dt):
        """Update all weapons."""
        dead_enemies = []
        for weapon in self.weapons.values():
            result = weapon.update(dt)
            # Some weapons (like garlic) return dead enemies
            if result and isinstance(result, list):
                dead_enemies.extend(result)
        return dead_enemies
    
    def handle_projectile_collisions(self):
        """Handle collisions between projectiles and enemies."""
        damage_dealt = 0
        kills = 0
        dead_enemies = []  # Collect drop info before enemies are removed
        
        for projectile in self.projectile_group:
            # Skip auras (handled separately)
            if isinstance(projectile, GarlicAura):
                continue
            
            # Check collision with enemies
            for enemy in list(self.enemy_group):
                if projectile.rect.colliderect(enemy.rect):
                    if hasattr(projectile, 'hit_enemy'):
                        if projectile.hit_enemy(enemy):
                            knockback_dir = pygame.math.Vector2(enemy.rect.center) - pygame.math.Vector2(projectile.rect.center)
                            # Get drop info BEFORE the enemy is killed
                            drop_info = enemy.get_drop_info()
                            if enemy.take_damage(projectile.damage, knockback_dir):
                                kills += 1
                                dead_enemies.append(drop_info)
                            damage_dealt += projectile.damage
        
        return damage_dealt, kills, dead_enemies
    
    def get_inventory_info(self):
        """Get inventory info for UI display."""
        weapon_info = []
        for weapon_id, weapon in self.weapons.items():
            weapon_info.append(weapon.get_info())
        
        passive_info = []
        for passive_id, level in self.passives.items():
            passive_data = PASSIVE_DATA.get(passive_id, {})
            passive_info.append({
                'id': passive_id,
                'name': passive_data.get('name', passive_id),
                'level': level,
                'max_level': passive_data.get('max_level', 5),
                'color': passive_data.get('color', COLORS['white']),
            })
        
        return {
            'weapons': weapon_info,
            'passives': passive_info,
        }
