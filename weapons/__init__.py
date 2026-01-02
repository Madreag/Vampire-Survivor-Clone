# weapons/__init__.py
"""Weapon classes for the game."""
from weapons.weapon_base import Weapon, WeaponUpgrade
from weapons.projectiles import (
    Projectile, WandProjectile, KnifeProjectile, AxeProjectile,
    WhipSlash, GarlicAura, DamageNumber
)
from weapons.controller import WeaponController
