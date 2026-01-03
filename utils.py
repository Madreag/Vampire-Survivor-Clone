# utils.py
"""
Utility functions and helper classes for the game.
"""

import pygame
import math
import random
import json
import os
from settings import SOUND_SETTINGS, WINDOW_WIDTH, WINDOW_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT


class Timer:
    """A simple timer class for cooldowns and timed events."""
    
    def __init__(self, duration, autostart=False, func=None):
        self.duration = duration
        self.func = func
        self.start_time = 0
        self.active = False
        if autostart:
            self.activate()
    
    def activate(self):
        """Start the timer."""
        self.active = True
        self.start_time = pygame.time.get_ticks()
    
    def deactivate(self):
        """Stop the timer."""
        self.active = False
        self.start_time = 0
    
    def update(self):
        """Update the timer and call function if expired."""
        if self.active:
            current_time = pygame.time.get_ticks()
            if current_time - self.start_time >= self.duration * 1000:
                if self.func:
                    self.func()
                self.deactivate()
                return True
        return False
    
    def get_progress(self):
        """Get progress as a value from 0 to 1."""
        if not self.active:
            return 0
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - self.start_time) / 1000
        return min(elapsed / self.duration, 1.0)
    
    def get_remaining(self):
        """Get remaining time in seconds."""
        if not self.active:
            return 0
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - self.start_time) / 1000
        return max(self.duration - elapsed, 0)


class CooldownTimer:
    """Timer that automatically resets after expiring."""
    
    def __init__(self, duration):
        self.duration = duration
        self.last_time = -duration * 1000  # Allow immediate first use
    
    def ready(self):
        """Check if cooldown has expired."""
        current_time = pygame.time.get_ticks()
        return current_time - self.last_time >= self.duration * 1000
    
    def reset(self):
        """Reset the cooldown."""
        self.last_time = pygame.time.get_ticks()
    
    def use(self):
        """Use the ability if ready, returns True if successful."""
        if self.ready():
            self.reset()
            return True
        return False
    
    def get_progress(self):
        """Get cooldown progress (1.0 = ready)."""
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - self.last_time) / 1000
        return min(elapsed / self.duration, 1.0)


def clamp(value, min_val, max_val):
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))


def clamp_vector_to_world(pos):
    """Clamp a position vector to world bounds."""
    return pygame.math.Vector2(
        clamp(pos.x, 0, WORLD_WIDTH),
        clamp(pos.y, 0, WORLD_HEIGHT)
    )


def distance(pos1, pos2):
    """Calculate distance between two positions."""
    return math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)


def distance_squared(pos1, pos2):
    """Calculate squared distance (faster, no sqrt)."""
    return (pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2


def normalize_vector(vec):
    """Normalize a vector to unit length."""
    length = math.sqrt(vec[0]**2 + vec[1]**2)
    if length == 0:
        return (0, 0)
    return (vec[0] / length, vec[1] / length)


def angle_to_vector(angle_degrees):
    """Convert angle in degrees to a unit vector."""
    angle_rad = math.radians(angle_degrees)
    return pygame.math.Vector2(math.cos(angle_rad), math.sin(angle_rad))


def vector_to_angle(vec):
    """Convert a vector to angle in degrees."""
    return math.degrees(math.atan2(vec[1], vec[0]))


def get_spawn_position_on_ring(center, min_radius, max_radius=None):
    """Get a random position on a ring around center."""
    if max_radius is None:
        max_radius = min_radius
    
    angle = random.uniform(0, 2 * math.pi)
    radius = random.uniform(min_radius, max_radius)
    
    x = center[0] + math.cos(angle) * radius
    y = center[1] + math.sin(angle) * radius
    
    return pygame.math.Vector2(x, y)


def get_spawn_position_outside_camera(player_pos, buffer=100):
    """Get a spawn position just outside the camera view."""
    # Calculate spawn ring radius (half screen diagonal + buffer)
    spawn_radius = math.sqrt((WINDOW_WIDTH/2)**2 + (WINDOW_HEIGHT/2)**2) + buffer
    
    angle = random.uniform(0, 2 * math.pi)
    x = player_pos[0] + math.cos(angle) * spawn_radius
    y = player_pos[1] + math.sin(angle) * spawn_radius
    
    # Clamp to world bounds
    x = clamp(x, 50, WORLD_WIDTH - 50)
    y = clamp(y, 50, WORLD_HEIGHT - 50)
    
    return pygame.math.Vector2(x, y)


def get_closest_enemy(pos, enemy_group, max_range=None):
    """Find the closest enemy to a position."""
    closest = None
    closest_dist_sq = float('inf')
    
    if max_range:
        max_range_sq = max_range ** 2
    else:
        max_range_sq = float('inf')
    
    for enemy in enemy_group:
        dist_sq = distance_squared(pos, enemy.rect.center)
        if dist_sq < closest_dist_sq and dist_sq <= max_range_sq:
            closest_dist_sq = dist_sq
            closest = enemy
    
    return closest


def get_enemies_in_range(pos, enemy_group, range_radius):
    """Get all enemies within a certain range."""
    range_sq = range_radius ** 2
    enemies = []
    
    for enemy in enemy_group:
        if distance_squared(pos, enemy.rect.center) <= range_sq:
            enemies.append(enemy)
    
    return enemies


def lerp(a, b, t):
    """Linear interpolation between a and b."""
    return a + (b - a) * t


def ease_out_quad(t):
    """Quadratic ease out function."""
    return 1 - (1 - t) ** 2


def ease_in_out_quad(t):
    """Quadratic ease in-out function."""
    if t < 0.5:
        return 2 * t * t
    return 1 - (-2 * t + 2) ** 2 / 2


# Sound generation
def generate_beep(frequency, duration_ms, volume=0.3):
    """Generate a simple beep sound."""
    try:
        sample_rate = 22050
        n_samples = int(sample_rate * duration_ms / 1000)
        
        # Generate samples
        buf = bytes(
            int(127 + 127 * volume * math.sin(2 * math.pi * frequency * i / sample_rate))
            for i in range(n_samples)
        )
        
        sound = pygame.mixer.Sound(buffer=buf)
        sound.set_volume(volume)
        return sound
    except Exception:
        return None



def generate_background_music(duration_seconds=8, volume=0.3):
    """Generate a simple procedural background music loop."""
    try:
        sample_rate = 22050
        n_samples = int(sample_rate * duration_seconds)
        
        # Define a simple melody using frequencies (notes)
        # Using a pentatonic scale for a pleasant sound
        notes = [
            (261.63, 0.5),   # C4
            (293.66, 0.5),   # D4
            (329.63, 0.5),   # E4
            (392.00, 0.5),   # G4
            (440.00, 0.5),   # A4
            (392.00, 0.5),   # G4
            (329.63, 0.5),   # E4
            (293.66, 0.5),   # D4
            (261.63, 1.0),   # C4 (longer)
            (329.63, 0.5),   # E4
            (392.00, 0.5),   # G4
            (440.00, 1.0),   # A4 (longer)
            (392.00, 0.5),   # G4
            (329.63, 0.5),   # E4
            (293.66, 0.5),   # D4
            (261.63, 1.0),   # C4 (longer)
        ]
        
        samples = []
        current_sample = 0
        note_index = 0
        
        while current_sample < n_samples:
            freq, note_duration = notes[note_index % len(notes)]
            note_samples = int(sample_rate * note_duration)
            
            for i in range(note_samples):
                if current_sample >= n_samples:
                    break
                    
                # Create a softer sound with envelope
                t = i / note_samples
                # Attack-decay envelope
                if t < 0.1:
                    envelope = t / 0.1
                elif t > 0.7:
                    envelope = (1 - t) / 0.3
                else:
                    envelope = 1.0
                
                # Mix multiple harmonics for richer sound
                value = 0
                value += math.sin(2 * math.pi * freq * current_sample / sample_rate) * 0.5
                value += math.sin(2 * math.pi * freq * 2 * current_sample / sample_rate) * 0.25
                value += math.sin(2 * math.pi * freq * 0.5 * current_sample / sample_rate) * 0.25
                
                sample_value = int(127 + 127 * volume * envelope * value * 0.5)
                sample_value = max(0, min(255, sample_value))
                samples.append(sample_value)
                current_sample += 1
            
            note_index += 1
        
        buf = bytes(samples)
        sound = pygame.mixer.Sound(buffer=buf)
        sound.set_volume(volume)
        return sound
    except Exception as e:
        print(f"Error generating background music: {e}")
        return None


class SoundManager:
    """Manages game sounds and background music."""
    
    def __init__(self):
        self.sounds = {}
        self.enabled = True
        self.music_enabled = True
        self.music_volume = 0.03
        self.music_sound = None
        self.music_channel = None
        self._init_sounds()
        self._init_music()
    
    def _init_sounds(self):
        """Initialize all game sounds."""
        try:
            self.sounds['pickup'] = generate_beep(
                SOUND_SETTINGS['pickup_freq'],
                SOUND_SETTINGS['pickup_duration'],
                0.2
            )
            self.sounds['levelup'] = generate_beep(
                SOUND_SETTINGS['levelup_freq'],
                SOUND_SETTINGS['levelup_duration'],
                0.3
            )
            self.sounds['hit'] = generate_beep(
                SOUND_SETTINGS['hit_freq'],
                SOUND_SETTINGS['hit_duration'],
                0.2
            )
            self.sounds['death'] = generate_beep(
                SOUND_SETTINGS['death_freq'],
                SOUND_SETTINGS['death_duration'],
                0.4
            )
        except Exception:
            self.enabled = False
    
    def _init_music(self):
        """Initialize background music."""
        try:
            self.music_sound = generate_background_music(8, self.music_volume)
            # Reserve a channel for music
            if pygame.mixer.get_num_channels() < 8:
                pygame.mixer.set_num_channels(8)
            self.music_channel = pygame.mixer.Channel(7)  # Use last channel for music
        except Exception as e:
            print(f"Error initializing music: {e}")
            self.music_sound = None
    
    def play(self, sound_name):
        """Play a sound by name."""
        if self.enabled and sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except Exception:
                pass
    
    def play_music(self):
        """Start playing background music."""
        if self.music_enabled and self.music_sound and self.music_channel:
            try:
                self.music_channel.play(self.music_sound, loops=-1)
                self.music_channel.set_volume(self.music_volume)
            except Exception as e:
                print(f"Error playing music: {e}")
    
    def stop_music(self):
        """Stop background music."""
        if self.music_channel:
            try:
                self.music_channel.stop()
            except Exception:
                pass
    
    def toggle_music(self):
        """Toggle background music on/off."""
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self.play_music()
        else:
            self.stop_music()
        return self.music_enabled
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.music_channel:
            try:
                self.music_channel.set_volume(self.music_volume)
            except Exception:
                pass
    
    def get_music_volume(self):
        """Get current music volume."""
        return self.music_volume
    
    def is_music_enabled(self):
        """Check if music is enabled."""
        return self.music_enabled


# High score management
def load_high_score(filename='highscore.json'):
    """Load high score from file."""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0), data.get('best_time', 0)
    except Exception:
        pass
    return 0, 0


def save_high_score(score, time_survived, filename='highscore.json'):
    """Save high score to file."""
    try:
        current_score, current_time = load_high_score(filename)
        if score > current_score or time_survived > current_time:
            with open(filename, 'w') as f:
                json.dump({
                    'high_score': max(score, current_score),
                    'best_time': max(time_survived, current_time)
                }, f)
            return True
    except Exception:
        pass
    return False


def format_time(seconds):
    """Format seconds into MM:SS string."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def draw_text(surface, text, pos, font, color=(255, 255, 255), center=False, shadow=True):
    """Draw text with optional shadow."""
    if shadow:
        shadow_surf = font.render(text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect()
        if center:
            shadow_rect.center = (pos[0] + 2, pos[1] + 2)
        else:
            shadow_rect.topleft = (pos[0] + 2, pos[1] + 2)
        surface.blit(shadow_surf, shadow_rect)
    
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect()
    if center:
        text_rect.center = pos
    else:
        text_rect.topleft = pos
    surface.blit(text_surf, text_rect)


def draw_bar(surface, pos, size, progress, color, bg_color=(50, 50, 50), border_color=(255, 255, 255)):
    """Draw a progress bar."""
    x, y = pos
    width, height = size
    
    # Background
    pygame.draw.rect(surface, bg_color, (x, y, width, height))
    
    # Fill
    fill_width = int(width * clamp(progress, 0, 1))
    if fill_width > 0:
        pygame.draw.rect(surface, color, (x, y, fill_width, height))
    
    # Border
    pygame.draw.rect(surface, border_color, (x, y, width, height), 2)


def draw_polygon(surface, color, center, size, sides, rotation=0):
    """Draw a regular polygon."""
    points = []
    for i in range(sides):
        angle = rotation + (2 * math.pi * i / sides) - math.pi / 2
        x = center[0] + size * math.cos(angle)
        y = center[1] + size * math.sin(angle)
        points.append((x, y))
    pygame.draw.polygon(surface, color, points)


class SpatialHash:
    """Simple spatial hash for collision optimization."""
    
    def __init__(self, cell_size=100):
        self.cell_size = cell_size
        self.cells = {}
    
    def _get_cell(self, pos):
        """Get cell coordinates for a position."""
        return (int(pos[0] // self.cell_size), int(pos[1] // self.cell_size))
    
    def clear(self):
        """Clear all cells."""
        self.cells.clear()
    
    def insert(self, entity, pos):
        """Insert an entity at a position."""
        cell = self._get_cell(pos)
        if cell not in self.cells:
            self.cells[cell] = []
        self.cells[cell].append(entity)
    
    def get_nearby(self, pos, radius=1):
        """Get all entities in nearby cells."""
        center_cell = self._get_cell(pos)
        nearby = []
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                if cell in self.cells:
                    nearby.extend(self.cells[cell])
        
        return nearby
