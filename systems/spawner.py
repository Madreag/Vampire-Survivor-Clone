# systems/spawner.py
"""
Enemy spawner system with difficulty scaling.
"""

import pygame
import random
import math
from settings import (
    ENEMY_DATA, SPAWNER_SETTINGS, WINDOW_WIDTH, WINDOW_HEIGHT,
    WORLD_WIDTH, WORLD_HEIGHT
)
from entities.enemy import create_enemy
from utils import get_spawn_position_outside_camera, clamp


class EnemySpawner:
    """
    Manages enemy spawning with time-based difficulty scaling.
    """
    
    def __init__(self, enemy_group, all_sprites_group):
        self.enemy_group = enemy_group
        self.all_sprites_group = all_sprites_group
        
        # Spawning settings
        self.base_spawn_rate = SPAWNER_SETTINGS['base_spawn_rate']
        self.spawn_rate_increase = SPAWNER_SETTINGS['spawn_rate_increase']
        self.max_spawn_rate = SPAWNER_SETTINGS['max_spawn_rate']
        self.spawn_buffer = SPAWNER_SETTINGS['spawn_buffer']
        
        # Difficulty scaling
        self.difficulty_hp_scale = SPAWNER_SETTINGS['difficulty_hp_scale']
        self.difficulty_damage_scale = SPAWNER_SETTINGS['difficulty_damage_scale']
        
        # Boss spawning
        self.boss_spawn_interval = SPAWNER_SETTINGS['boss_spawn_interval']
        self.last_boss_time = 0
        
        # Timers
        self.spawn_timer = 0
        self.game_time = 0
        
        # Enemy type weights (changes over time)
        self.enemy_weights = self._get_initial_weights()
        
        # Stats
        self.total_spawned = 0
        self.enemies_alive = 0
    
    def _get_initial_weights(self):
        """Get initial spawn weights for enemy types."""
        weights = {}
        for enemy_type, data in ENEMY_DATA.items():
            if data['spawn_weight'] > 0:
                weights[enemy_type] = data['spawn_weight']
        return weights
    
    def _get_spawn_rate(self):
        """Calculate current spawn rate based on game time."""
        minutes = self.game_time / 60
        rate = self.base_spawn_rate + self.spawn_rate_increase * minutes
        return min(rate, self.max_spawn_rate)
    
    def _get_difficulty_multiplier(self):
        """Calculate difficulty multiplier based on game time."""
        minutes = self.game_time / 60
        hp_mult = 1 + self.difficulty_hp_scale * minutes
        return hp_mult
    
    def _select_enemy_type(self):
        """Select a random enemy type based on weights."""
        # Adjust weights based on game time
        adjusted_weights = self.enemy_weights.copy()
        minutes = self.game_time / 60
        
        # Increase tank and special enemy weights over time
        if minutes > 2:
            adjusted_weights['tank'] = adjusted_weights.get('tank', 0) * (1 + minutes * 0.1)
        if minutes > 3:
            adjusted_weights['ghost'] = adjusted_weights.get('ghost', 0) * (1 + minutes * 0.1)
            adjusted_weights['bat'] = adjusted_weights.get('bat', 0) * (1 + minutes * 0.1)
        
        # Weighted random selection
        total_weight = sum(adjusted_weights.values())
        if total_weight == 0:
            return 'chaser'
        
        roll = random.uniform(0, total_weight)
        cumulative = 0
        
        for enemy_type, weight in adjusted_weights.items():
            cumulative += weight
            if roll <= cumulative:
                return enemy_type
        
        return 'chaser'
    
    def _get_spawn_position(self, player_pos):
        """Get a valid spawn position outside camera view."""
        return get_spawn_position_outside_camera(player_pos, self.spawn_buffer)
    
    def spawn_enemy(self, player_pos, enemy_type=None):
        """Spawn a single enemy."""
        if enemy_type is None:
            enemy_type = self._select_enemy_type()
        
        pos = self._get_spawn_position(player_pos)
        difficulty_mult = self._get_difficulty_multiplier()
        
        enemy = create_enemy(
            enemy_type,
            pos,
            [self.enemy_group, self.all_sprites_group],
            difficulty_mult
        )
        
        self.total_spawned += 1
        
        # Handle swarm spawning
        enemy_data = ENEMY_DATA.get(enemy_type, {})
        spawn_count = enemy_data.get('spawn_count', 1)
        
        if spawn_count > 1:
            for i in range(spawn_count - 1):
                offset = pygame.math.Vector2(
                    random.uniform(-30, 30),
                    random.uniform(-30, 30)
                )
                swarm_pos = pos + offset
                swarm_pos.x = clamp(swarm_pos.x, 50, WORLD_WIDTH - 50)
                swarm_pos.y = clamp(swarm_pos.y, 50, WORLD_HEIGHT - 50)
                
                create_enemy(
                    enemy_type,
                    swarm_pos,
                    [self.enemy_group, self.all_sprites_group],
                    difficulty_mult
                )
                self.total_spawned += 1
        
        return enemy
    
    def spawn_boss(self, player_pos):
        """Spawn a boss enemy."""
        pos = self._get_spawn_position(player_pos)
        difficulty_mult = self._get_difficulty_multiplier() * 1.5  # Extra tough
        
        boss = create_enemy(
            'boss',
            pos,
            [self.enemy_group, self.all_sprites_group],
            difficulty_mult
        )
        
        self.total_spawned += 1
        self.last_boss_time = self.game_time
        
        return boss
    
    def spawn_wave(self, player_pos, count=10, enemy_type=None):
        """Spawn a wave of enemies."""
        enemies = []
        for _ in range(count):
            enemy = self.spawn_enemy(player_pos, enemy_type)
            enemies.append(enemy)
        return enemies
    
    def update(self, dt, player_pos):
        """Update spawner and spawn enemies as needed."""
        self.game_time += dt
        self.spawn_timer += dt
        
        # Calculate spawn interval
        spawn_rate = self._get_spawn_rate()
        spawn_interval = 1.0 / spawn_rate if spawn_rate > 0 else 1.0
        
        # Spawn enemies
        while self.spawn_timer >= spawn_interval:
            self.spawn_timer -= spawn_interval
            self.spawn_enemy(player_pos)
        
        # Check for boss spawn
        if (self.game_time - self.last_boss_time >= self.boss_spawn_interval and 
            self.game_time >= self.boss_spawn_interval):
            self.spawn_boss(player_pos)
        
        # Update alive count
        self.enemies_alive = len(self.enemy_group)
    
    def get_stats(self):
        """Get spawner statistics."""
        return {
            'total_spawned': self.total_spawned,
            'enemies_alive': self.enemies_alive,
            'spawn_rate': self._get_spawn_rate(),
            'difficulty': self._get_difficulty_multiplier(),
            'game_time': self.game_time,
        }
    
    def reset(self):
        """Reset spawner state."""
        self.spawn_timer = 0
        self.game_time = 0
        self.last_boss_time = 0
        self.total_spawned = 0
        self.enemies_alive = 0


class WaveSpawner:
    """
    Alternative spawner that uses discrete waves instead of continuous spawning.
    """
    
    def __init__(self, enemy_group, all_sprites_group):
        self.enemy_group = enemy_group
        self.all_sprites_group = all_sprites_group
        
        self.wave_number = 0
        self.wave_timer = 0
        self.wave_interval = 30  # Seconds between waves
        self.enemies_per_wave = 10
        self.wave_active = False
    
    def start_wave(self, player_pos):
        """Start a new wave."""
        self.wave_number += 1
        self.wave_active = True
        
        # Calculate enemies for this wave
        enemy_count = self.enemies_per_wave + self.wave_number * 5
        
        # Spawn enemies
        for _ in range(enemy_count):
            pos = get_spawn_position_outside_camera(player_pos, 100)
            enemy_type = random.choice(['chaser', 'tank', 'swarm'])
            
            create_enemy(
                enemy_type,
                pos,
                [self.enemy_group, self.all_sprites_group],
                1 + self.wave_number * 0.1
            )
    
    def update(self, dt, player_pos):
        """Update wave spawner."""
        if not self.wave_active:
            self.wave_timer += dt
            
            if self.wave_timer >= self.wave_interval:
                self.wave_timer = 0
                self.start_wave(player_pos)
        else:
            # Check if wave is complete
            if len(self.enemy_group) == 0:
                self.wave_active = False
