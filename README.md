# Vampire Survivors Clone

A roguelite game inspired by Vampire Survivors, built with Python and pygame-ce.

## Requirements

- Python 3.10+
- pygame-ce (or pygame)

## Installation

pip install pygame-ce

## Running the Game

python main.py

## Controls

- WASD / Arrow Keys: Move the player
- ESC: Pause menu
- F1: Toggle debug mode (shows FPS, entity counts, hitboxes)
- 1/2/3: Quick select upgrade options during level-up
- Enter/Space: Confirm selection
- Mouse: Click to select upgrades

## Game Features

### Audio
- **Background Music**: Procedurally generated background music that plays continuously
- **Music Toggle**: Turn music ON/OFF from the Options menu
- **Volume Slider**: Adjust music volume (0-100%) using the slider or LEFT/RIGHT keys
- **Sound Effects**: Various sound effects for pickups, level-ups, hits, and death

### Player
- Auto-attacking weapons
- Stats: HP, Move Speed, Pickup Radius, Might (damage), Cooldown Reduction, Armor, Regen
- Invincibility frames after taking damage
- XP collection and leveling system

### Weapons (5 types)
1. Whip: Horizontal slash attack in facing direction
2. Magic Wand: Fires projectiles at nearest enemy
3. Garlic: Aura that damages nearby enemies
4. Axe: Thrown in arc, passes through enemies
5. Knife: Fast projectiles in facing direction

### Enemies (6 types)
1. Chaser (Red Circle): Fast, low HP
2. Tank (Blue Square): Slow, high HP
3. Swarm (Green Triangle): Spawns in groups
4. Ghost (Gray Circle): Phasing visual effect
5. Bat (Purple Triangle): Zigzag movement
6. Boss (Large Red Square): Spawns every 10 minutes

### Passives (7 types)
- Spinach: +10% Might (damage)
- Hollow Heart: +20 Max HP
- Pummarola: +0.5 HP/s Regen
- Attractorb: +20% Pickup Radius
- Armor: +1 Armor (damage reduction)
- Wings: +10% Move Speed
- Empty Tome: -8% Cooldown

### Drops
- XP Gems (Blue/Green/Yellow): Grant experience points
- Health Pickup (Red Cross): Restores HP
- Chest (Gold): Grants random upgrades

### Progression
- Enemies spawn continuously and increase over time
- Collect XP to level up
- Choose 1 of 3 upgrades on level up
- Weapons can be leveled up to level 8
- Max 6 weapons and 6 passives

## Options Menu

Access the Options menu from the Main Menu to:
- **Music: ON/OFF** - Toggle background music
- **Music Volume** - Adjust volume with slider or LEFT/RIGHT keys
- **Cheats** - Access cheat settings

## High Scores

High scores are saved to highscore.json in the game directory.

Ethan helped.
