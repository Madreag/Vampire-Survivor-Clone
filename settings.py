# settings.py
"""
Game settings and constants for Vampire Survivors-style roguelite.
"""

# Display settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60
TITLE = "Vampire Survivors Clone"

# World settings
WORLD_WIDTH = 2000
WORLD_HEIGHT = 2000
TILE_SIZE = 64

# Colors (RGB)
COLORS = {
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'orange': (255, 165, 0),
    'purple': (128, 0, 128),
    'cyan': (0, 255, 255),
    'pink': (255, 192, 203),
    'gray': (128, 128, 128),
    'dark_gray': (64, 64, 64),
    'light_gray': (192, 192, 192),
    'dark_green': (0, 100, 0),
    'dark_red': (139, 0, 0),
    'gold': (255, 215, 0),
    'silver': (192, 192, 192),
    'brown': (139, 69, 19),
    'bg_color': (30, 30, 40),
    'ground_color1': (40, 40, 50),
    'ground_color2': (35, 35, 45),
}

# Player settings
PLAYER_SETTINGS = {
    'max_hp': 100,
    'move_speed': 200,
    'pickup_radius': 80,
    'might': 1.0,  # Damage multiplier
    'cooldown_reduction': 0.0,  # Percentage reduction
    'armor': 0,
    'regen': 0,  # HP per second
    'size': 24,
    'color': COLORS['cyan'],
    'i_frames_duration': 0.5,  # Invincibility frames duration
}

# XP and leveling
XP_SETTINGS = {
    'base_xp_to_level': 100,
    'xp_per_level_increase': 50,
    'max_level': 100,
}

# Weapon data
WEAPON_DATA = {
    'whip': {
        'name': 'Whip',
        'description': 'Horizontal slash in facing direction',
        'color': COLORS['brown'],
        'base_damage': 20,
        'base_cooldown': 1.5,
        'base_area': 1.0,
        'base_speed': 1.0,
        'base_amount': 1,
        'base_pierce': 999,  # Hits all enemies in range
        'max_level': 8,
        'scaling': {
            'damage': 5,  # Per level
            'cooldown': -0.1,  # Per level (reduction)
            'area': 0.1,  # Per level
            'amount': 0,  # Per level
        },
        'evolution': 'bloody_whip',
        'evolution_passive': 'might_boost',
    },
    'wand': {
        'name': 'Magic Wand',
        'description': 'Fires projectile at nearest enemy',
        'color': COLORS['blue'],
        'base_damage': 10,
        'base_cooldown': 1.0,
        'base_area': 1.0,
        'base_speed': 400,
        'base_amount': 1,
        'base_pierce': 1,
        'max_level': 8,
        'scaling': {
            'damage': 3,
            'cooldown': -0.08,
            'area': 0,
            'amount': 1,  # Every 2 levels
        },
        'evolution': 'holy_wand',
        'evolution_passive': 'cooldown_boost',
    },
    'garlic': {
        'name': 'Garlic',
        'description': 'Damages nearby enemies',
        'color': COLORS['white'],
        'base_damage': 5,
        'base_cooldown': 0.5,
        'base_area': 1.0,
        'base_speed': 0,
        'base_amount': 1,
        'base_pierce': 999,
        'base_radius': 60,
        'max_level': 8,
        'scaling': {
            'damage': 2,
            'cooldown': -0.03,
            'area': 0.15,
            'amount': 0,
        },
        'evolution': 'soul_eater',
        'evolution_passive': 'regen_boost',
    },
    'axe': {
        'name': 'Axe',
        'description': 'Thrown in high arc, passes through enemies',
        'color': COLORS['gray'],
        'base_damage': 25,
        'base_cooldown': 2.0,
        'base_area': 1.0,
        'base_speed': 300,
        'base_amount': 1,
        'base_pierce': 999,
        'max_level': 8,
        'scaling': {
            'damage': 8,
            'cooldown': -0.12,
            'area': 0.1,
            'amount': 1,
        },
        'evolution': 'death_spiral',
        'evolution_passive': 'max_hp_boost',
    },
    'knife': {
        'name': 'Knife',
        'description': 'Throws knives in facing direction',
        'color': COLORS['silver'],
        'base_damage': 8,
        'base_cooldown': 0.3,
        'base_area': 1.0,
        'base_speed': 500,
        'base_amount': 1,
        'base_pierce': 1,
        'max_level': 8,
        'scaling': {
            'damage': 2,
            'cooldown': -0.02,
            'area': 0,
            'amount': 1,
        },
        'evolution': 'thousand_edge',
        'evolution_passive': 'speed_boost',
    },
}

# Evolution data
EVOLUTION_DATA = {
    'bloody_whip': {
        'name': 'Bloody Whip',
        'base_weapon': 'whip',
        'required_passive': 'might_boost',
        'color': COLORS['dark_red'],
        'damage_mult': 2.0,
        'special': 'lifesteal',  # Heals on hit
    },
    'holy_wand': {
        'name': 'Holy Wand',
        'base_weapon': 'wand',
        'required_passive': 'cooldown_boost',
        'color': COLORS['gold'],
        'damage_mult': 1.5,
        'special': 'homing',  # Projectiles home in
    },
    'soul_eater': {
        'name': 'Soul Eater',
        'base_weapon': 'garlic',
        'required_passive': 'regen_boost',
        'color': COLORS['purple'],
        'damage_mult': 1.8,
        'special': 'steal_hp',  # Steals HP from enemies
    },
}

# Enemy data
ENEMY_DATA = {
    'chaser': {
        'name': 'Chaser',
        'color': COLORS['red'],
        'shape': 'circle',
        'size': 16,
        'hp': 10,
        'damage': 10,
        'speed': 80,
        'xp_value': 1,
        'spawn_weight': 50,
    },
    'tank': {
        'name': 'Tank',
        'color': COLORS['blue'],
        'shape': 'square',
        'size': 24,
        'hp': 50,
        'damage': 20,
        'speed': 40,
        'xp_value': 5,
        'spawn_weight': 20,
    },
    'swarm': {
        'name': 'Swarm',
        'color': COLORS['green'],
        'shape': 'triangle',
        'size': 12,
        'hp': 5,
        'damage': 5,
        'speed': 100,
        'xp_value': 1,
        'spawn_weight': 30,
        'spawn_count': 5,  # Spawns in groups
    },
    'ghost': {
        'name': 'Ghost',
        'color': COLORS['light_gray'],
        'shape': 'circle',
        'size': 20,
        'hp': 15,
        'damage': 15,
        'speed': 70,
        'xp_value': 3,
        'spawn_weight': 15,
        'special': 'phase',  # Can phase through (visual effect)
    },
    'bat': {
        'name': 'Bat',
        'color': COLORS['purple'],
        'shape': 'triangle',
        'size': 14,
        'hp': 8,
        'damage': 8,
        'speed': 120,
        'xp_value': 2,
        'spawn_weight': 25,
        'special': 'zigzag',  # Moves in zigzag pattern
    },
    'boss': {
        'name': 'Boss',
        'color': COLORS['dark_red'],
        'shape': 'square',
        'size': 48,
        'hp': 500,
        'damage': 30,
        'speed': 50,
        'xp_value': 50,
        'spawn_weight': 0,  # Only spawns on timer
    },
}

# Passive data
PASSIVE_DATA = {
    'might_boost': {
        'name': 'Spinach',
        'description': '+10% Might (damage)',
        'color': COLORS['green'],
        'stat': 'might',
        'value': 0.1,
        'max_level': 5,
    },
    'max_hp_boost': {
        'name': 'Hollow Heart',
        'description': '+20 Max HP',
        'color': COLORS['red'],
        'stat': 'max_hp',
        'value': 20,
        'max_level': 5,
    },
    'regen_boost': {
        'name': 'Pummarola',
        'description': '+0.5 HP/s Regen',
        'color': COLORS['pink'],
        'stat': 'regen',
        'value': 0.5,
        'max_level': 5,
    },
    'pickup_boost': {
        'name': 'Attractorb',
        'description': '+20% Pickup Radius',
        'color': COLORS['yellow'],
        'stat': 'pickup_radius',
        'value': 0.2,  # Percentage
        'max_level': 5,
    },
    'armor_boost': {
        'name': 'Armor',
        'description': '+1 Armor (damage reduction)',
        'color': COLORS['gray'],
        'stat': 'armor',
        'value': 1,
        'max_level': 5,
    },
    'speed_boost': {
        'name': 'Wings',
        'description': '+10% Move Speed',
        'color': COLORS['cyan'],
        'stat': 'move_speed',
        'value': 0.1,  # Percentage
        'max_level': 5,
    },
    'cooldown_boost': {
        'name': 'Empty Tome',
        'description': '-8% Cooldown',
        'color': COLORS['purple'],
        'stat': 'cooldown_reduction',
        'value': 0.08,
        'max_level': 5,
    },
}

# Drop settings
DROP_SETTINGS = {
    'xp_gem_small': {
        'value': 1,
        'color': COLORS['blue'],
        'size': 6,
    },
    'xp_gem_medium': {
        'value': 5,
        'color': COLORS['green'],
        'size': 8,
    },
    'xp_gem_large': {
        'value': 25,
        'color': COLORS['yellow'],
        'size': 10,
    },
    'health_pickup': {
        'value': 20,
        'color': COLORS['red'],
        'size': 12,
        'drop_chance': 0.02,  # 2% chance
    },
    'chest': {
        'color': COLORS['gold'],
        'size': 16,
        'drop_chance': 0.005,  # 0.5% chance
    },
}

# Spawner settings
SPAWNER_SETTINGS = {
    'base_spawn_rate': 1.0,  # Enemies per second
    'spawn_rate_increase': 0.1,  # Per minute
    'max_spawn_rate': 10.0,
    'spawn_buffer': 100,  # Distance outside screen to spawn
    'boss_spawn_interval': 600,  # Seconds (10 minutes)
    'difficulty_hp_scale': 0.05,  # HP increase per minute
    'difficulty_damage_scale': 0.02,  # Damage increase per minute
}

# UI settings
UI_SETTINGS = {
    'hp_bar_width': 200,
    'hp_bar_height': 20,
    'xp_bar_width': 400,
    'xp_bar_height': 15,
    'font_size': 24,
    'small_font_size': 18,
    'large_font_size': 36,
    'card_width': 200,
    'card_height': 280,
    'card_spacing': 20,
}

# Sound settings (for generated sounds)
SOUND_SETTINGS = {
    'pickup_freq': 880,
    'pickup_duration': 50,
    'levelup_freq': 1200,
    'levelup_duration': 200,
    'hit_freq': 200,
    'hit_duration': 50,
    'death_freq': 100,
    'death_duration': 500,
}

# Inventory limits
MAX_WEAPONS = 6
MAX_PASSIVES = 6

# Cheat settings
CHEAT_SETTINGS = {
    'unlimited_health': False,
    'starting_weapon': 'whip',  # Default starting weapon
    'starting_weapon_level': 1,  # Starting weapon level (1-8)
    'starting_passives': {},  # Dict of passive_id: level for starting power-ups
    'exp_multiplier': 1.0,  # EXP gain multiplier (0.25 to 5.0)
    'cheats_enabled': False,  # Master toggle for cheats
}

# Available starting weapons for cheat menu
AVAILABLE_STARTING_WEAPONS = ['whip', 'wand', 'garlic', 'axe', 'knife']

# Available passives for cheat menu
AVAILABLE_STARTING_PASSIVES = ['might_boost', 'max_hp_boost', 'regen_boost', 'pickup_boost', 'armor_boost', 'speed_boost', 'cooldown_boost']
