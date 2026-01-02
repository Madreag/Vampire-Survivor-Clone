# systems/camera.py
"""
Camera system for following the player and rendering the world.
"""

import pygame
from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT,
    TILE_SIZE, COLORS
)


class CameraGroup(pygame.sprite.Group):
    """
    A sprite group that handles camera offset for all sprites.
    The player stays centered on screen while the world moves around them.
    """
    
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        self.half_width = WINDOW_WIDTH // 2
        self.half_height = WINDOW_HEIGHT // 2
        
        # Ground surface for tiled background
        self.ground_surface = self._create_ground_surface()
        self.ground_rect = self.ground_surface.get_rect(topleft=(0, 0))
        
        # Debug mode
        self.debug_mode = False
    
    def _create_ground_surface(self):
        """Create a tiled ground surface."""
        ground = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))
        ground.fill(COLORS['bg_color'])
        
        # Draw checkerboard pattern
        for x in range(0, WORLD_WIDTH, TILE_SIZE):
            for y in range(0, WORLD_HEIGHT, TILE_SIZE):
                if (x // TILE_SIZE + y // TILE_SIZE) % 2 == 0:
                    color = COLORS['ground_color1']
                else:
                    color = COLORS['ground_color2']
                pygame.draw.rect(ground, color, (x, y, TILE_SIZE, TILE_SIZE))
        
        # Draw world boundary
        pygame.draw.rect(ground, COLORS['dark_red'], (0, 0, WORLD_WIDTH, WORLD_HEIGHT), 4)
        
        return ground
    
    def center_target_camera(self, target):
        """Center the camera on a target (usually the player)."""
        self.offset.x = target.rect.centerx - self.half_width
        self.offset.y = target.rect.centery - self.half_height
    
    def custom_draw(self, player):
        """Draw all sprites with camera offset."""
        # Center camera on player
        self.center_target_camera(player)
        
        # Draw ground
        ground_offset = self.ground_rect.topleft - self.offset
        self.display_surface.blit(self.ground_surface, ground_offset)
        
        # Sort sprites by y position for depth effect (optional)
        # For now, just draw all sprites
        for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)
            
            # Debug: draw hitboxes
            if self.debug_mode:
                debug_rect = sprite.rect.copy()
                debug_rect.topleft = offset_pos
                pygame.draw.rect(self.display_surface, COLORS['green'], debug_rect, 1)
    
    def toggle_debug(self):
        """Toggle debug mode."""
        self.debug_mode = not self.debug_mode
        return self.debug_mode


class SimpleCamera:
    """
    A simpler camera class that just provides offset calculations.
    Use this if you want more control over drawing order.
    """
    
    def __init__(self):
        self.offset = pygame.math.Vector2()
        self.half_width = WINDOW_WIDTH // 2
        self.half_height = WINDOW_HEIGHT // 2
    
    def update(self, target):
        """Update camera position to follow target."""
        self.offset.x = target.rect.centerx - self.half_width
        self.offset.y = target.rect.centery - self.half_height
    
    def apply(self, entity):
        """Apply camera offset to an entity's rect."""
        return entity.rect.move(-self.offset.x, -self.offset.y)
    
    def apply_pos(self, pos):
        """Apply camera offset to a position."""
        return (pos[0] - self.offset.x, pos[1] - self.offset.y)
    
    def reverse_apply(self, screen_pos):
        """Convert screen position to world position."""
        return (screen_pos[0] + self.offset.x, screen_pos[1] + self.offset.y)


class ParallaxLayer:
    """A parallax background layer for visual depth."""
    
    def __init__(self, image, parallax_factor=0.5):
        self.image = image
        self.parallax_factor = parallax_factor
        self.rect = self.image.get_rect()
    
    def draw(self, surface, camera_offset):
        """Draw the layer with parallax effect."""
        offset_x = -camera_offset.x * self.parallax_factor
        offset_y = -camera_offset.y * self.parallax_factor
        
        # Tile the image if needed
        surface.blit(self.image, (offset_x % self.rect.width - self.rect.width,
                                   offset_y % self.rect.height - self.rect.height))
