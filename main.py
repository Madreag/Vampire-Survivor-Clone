# main.py
"""
Main entry point for the Vampire Survivors-style roguelite game.
"""

import pygame
import sys
from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE, COLORS,
    WORLD_WIDTH, WORLD_HEIGHT, CHEAT_SETTINGS, XP_SETTINGS, PASSIVE_DATA
)
from utils import SoundManager, load_high_score, save_high_score, format_time, draw_text
from systems.camera import CameraGroup
from systems.spawner import EnemySpawner
from systems.ui import HUD, LevelUpMenu, PauseMenu, DeathScreen, MainMenu, OptionsMenu, CheatsMenu
from entities.player import Player
from entities.drops import DropManager
from weapons.controller import WeaponController


class Game:
    """Main game class that manages all game systems."""
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Display
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        # Sound
        self.sound_manager = SoundManager()
        
        # Cheat settings (copy to allow modification)
        self.cheat_settings = CHEAT_SETTINGS.copy()
        
        # Menu state
        self.in_main_menu = True
        self.in_options_menu = False
        self.in_cheats_menu = False
        self.game_started = False
        
        # Game state
        self.running = True
        self.paused = False
        self.game_over = False
        self.level_up_active = False
        self.debug_mode = False
        
        # Time tracking
        self.game_time = 0
        self.dt = 0
        
        # High scores
        self.high_score, self.best_time = load_high_score()
        
        # Initialize menus first
        self._init_menus()
        
        # Start background music
        self.sound_manager.play_music()
        
        # Font for watermark
        self.watermark_font = pygame.font.Font(None, 24)
    
    def _init_menus(self):
        """Initialize menu systems."""
        self.main_menu = MainMenu()
        self.options_menu = OptionsMenu(self.sound_manager)
        self.cheats_menu = CheatsMenu(self.cheat_settings)
    
    def _init_game(self):
        """Initialize the actual game (called when starting from menu)."""
        self._init_groups()
        self._init_entities()
        self._init_systems()
        self._init_ui()
        self.game_started = True
    
    def _init_groups(self):
        """Initialize sprite groups."""
        self.all_sprites = CameraGroup()
        self.enemy_group = pygame.sprite.Group()
        self.projectile_group = pygame.sprite.Group()
        self.drop_group = pygame.sprite.Group()
    
    def _init_entities(self):
        """Initialize game entities."""
        # Player starts at center of world
        start_pos = (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
        self.player = Player(start_pos, [self.all_sprites], self.cheat_settings)
        
        # Weapon controller
        self.weapon_controller = WeaponController(
            self.player,
            self.projectile_group,
            self.enemy_group,
            self.all_sprites
        )
        
        # Give player starting weapon based on cheat settings
        starting_weapon = self.cheat_settings.get('starting_weapon', 'whip')
        self.weapon_controller.add_weapon(starting_weapon)
        
        # Apply starting weapon level from cheat settings
        starting_weapon_level = self.cheat_settings.get('starting_weapon_level', 1)
        if starting_weapon_level > 1 and starting_weapon in self.weapon_controller.weapons:
            weapon = self.weapon_controller.weapons[starting_weapon]
            # Level up the weapon to the desired level
            for _ in range(starting_weapon_level - 1):
                weapon.level_up()
        
        # Apply starting passives from cheat settings
        starting_passives = self.cheat_settings.get('starting_passives', {})
        for passive_id, level in starting_passives.items():
            if passive_id in PASSIVE_DATA:
                # Add passive at the specified level
                for _ in range(level):
                    self.weapon_controller.add_passive(passive_id)
    
    def _init_systems(self):
        """Initialize game systems."""
        # Enemy spawner
        self.spawner = EnemySpawner(self.enemy_group, self.all_sprites)
        
        # Drop manager
        self.drop_manager = DropManager(self.drop_group, self.all_sprites)
    
    def _init_ui(self):
        """Initialize UI elements."""
        self.hud = HUD()
        self.level_up_menu = LevelUpMenu()
        self.pause_menu = PauseMenu()
        self.death_screen = DeathScreen()
    
    def reset(self):
        """Reset the game to initial state."""
        # Clear all sprites
        for sprite in self.all_sprites:
            sprite.kill()
        for sprite in self.enemy_group:
            sprite.kill()
        for sprite in self.projectile_group:
            sprite.kill()
        for sprite in self.drop_group:
            sprite.kill()
        
        # Reset state
        self.paused = False
        self.game_over = False
        self.level_up_active = False
        self.game_time = 0
        
        # Reinitialize
        self._init_groups()
        self._init_entities()
        self._init_systems()
        
        # Hide menus
        self.level_up_menu.hide()
        self.pause_menu.hide()
        self.death_screen.hide()
    
    def return_to_main_menu(self):
        """Return to the main menu."""
        self.in_main_menu = True
        self.in_options_menu = False
        self.in_cheats_menu = False
        self.game_started = False
        self.game_over = False
        self.paused = False
        self.level_up_active = False
        self.main_menu.show()
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            # Handle main menu input
            if self.in_main_menu:
                result = self.main_menu.handle_input(event)
                if result == 'start':
                    self.in_main_menu = False
                    self.main_menu.hide()
                    self._init_game()
                elif result == 'options':
                    self.in_main_menu = False
                    self.main_menu.hide()
                    self.in_options_menu = True
                    self.options_menu.show()
                elif result == 'quit':
                    self.running = False
                continue
            
            # Handle options menu input
            if self.in_options_menu:
                result = self.options_menu.handle_input(event)
                if result == 'cheats':
                    self.in_options_menu = False
                    self.options_menu.hide()
                    self.in_cheats_menu = True
                    self.cheats_menu.show()
                elif result == 'back':
                    self.in_options_menu = False
                    self.options_menu.hide()
                    self.in_main_menu = True
                    self.main_menu.show()
                continue
            
            # Handle cheats menu input
            if self.in_cheats_menu:
                result = self.cheats_menu.handle_input(event)
                if result == 'back':
                    self.in_cheats_menu = False
                    self.cheats_menu.hide()
                    self.in_options_menu = True
                    self.options_menu.show()
                continue
            
            # Handle death screen input
            if self.game_over:
                result = self.death_screen.handle_input(event)
                if result == 'restart':
                    self.reset()
                elif result == 'quit':
                    self.return_to_main_menu()
                continue
            
            # Handle level up menu input
            if self.level_up_active:
                result = self.level_up_menu.handle_input(event)
                if result:
                    upgrade_type, upgrade_id, is_new, level = result
                    self.weapon_controller.apply_upgrade(upgrade_type, upgrade_id)
                    self.level_up_active = False
                    self.sound_manager.play('levelup')
                continue
            
            # Handle pause menu input
            if self.paused:
                result = self.pause_menu.handle_input(event)
                if result == 'resume':
                    self.paused = False
                    self.pause_menu.hide()
                elif result == 'restart':
                    self.reset()
                elif result == 'quit':
                    self.return_to_main_menu()
                continue
            
            # Normal gameplay input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = True
                    self.pause_menu.show()
                elif event.key == pygame.K_F1:
                    self.debug_mode = not self.debug_mode
                    self.all_sprites.toggle_debug()
    
    def update(self):
        """Update game state."""
        # Don't update if in menus or paused
        if self.in_main_menu or self.in_options_menu or self.in_cheats_menu:
            return
        
        if self.paused or self.level_up_active or self.game_over:
            return
        
        if not self.game_started:
            return
        
        # Update game time
        self.game_time += self.dt
        
        # Update player
        self.player.update(self.dt)
        
        # Check for player death
        if self.player.dead:
            self._handle_player_death()
            return
        
        # Update spawner
        self.spawner.update(self.dt, self.player.pos)
        
        # Update enemies
        for enemy in self.enemy_group:
            enemy.update(self.dt, self.player.pos)
        
        # Update weapons
        weapon_dead_enemies = self.weapon_controller.update(self.dt)
        
        # Update projectiles
        for projectile in self.projectile_group:
            projectile.update(self.dt)
        
        # Handle projectile-enemy collisions
        damage_dealt, kills, dead_enemies = self.weapon_controller.handle_projectile_collisions()
        self.player.damage_dealt += damage_dealt
        self.player.kills += kills
        
        # Combine dead enemies from weapons and projectiles
        if weapon_dead_enemies:
            dead_enemies.extend(weapon_dead_enemies)
        
        # Handle enemy deaths and drops
        for drop_info in dead_enemies:
            self.drop_manager.spawn_xp_gem(drop_info['pos'], drop_info['xp_value'])
        
        # Update drops and check collection
        collected = self.drop_manager.update(self.dt, self.player)
        
        # Apply collected items
        if collected['xp'] > 0:
            # Apply EXP multiplier from cheat settings
            exp_multiplier = self.cheat_settings.get('exp_multiplier', 1.0)
            modified_xp = int(collected['xp'] * exp_multiplier)
            if self.player.gain_xp(modified_xp):
                self._trigger_level_up()
            self.sound_manager.play('pickup')
        
        if collected['health'] > 0:
            self.player.heal(collected['health'])
            self.sound_manager.play('pickup')
        
        # Handle chest collection (grants random upgrades)
        for chest in collected['chests']:
            self._trigger_level_up()
        
        # Handle player-enemy collision
        self._handle_player_enemy_collision()
    
    def _handle_player_enemy_collision(self):
        """Handle collision between player and enemies."""
        for enemy in self.enemy_group:
            if self.player.hitbox.colliderect(enemy.hitbox):
                if enemy.can_damage() and not self.player.is_invincible:
                    if self.player.get_hit(enemy.damage):
                        # Player died
                        self._handle_player_death()
                        return
                    enemy.reset_damage_cooldown()
                    self.sound_manager.play('hit')
    
    def _trigger_level_up(self):
        """Trigger the level up menu."""
        self.level_up_active = True
        options = self.weapon_controller.get_upgrade_options(3)
        self.level_up_menu.show(options)
        self.sound_manager.play('levelup')
    
    def _handle_player_death(self):
        """Handle player death."""
        self.game_over = True
        self.sound_manager.play('death')
        
        # Calculate stats
        stats = {
            'time': self.game_time,
            'level': self.player.level,
            'kills': self.player.kills,
            'damage_dealt': self.player.damage_dealt,
        }
        
        # Save high score
        save_high_score(self.player.kills, self.game_time)
        
        # Show death screen
        self.death_screen.show(stats, self.high_score, self.best_time)
        
        # Update high scores for next game
        self.high_score, self.best_time = load_high_score()
    
    def _draw_cheats_watermark(self):
        """Draw the cheats enabled watermark."""
        if self.cheat_settings.get('cheats_enabled', False):
            watermark_text = "Cheats Enabled"
            text_surface = self.watermark_font.render(watermark_text, True, COLORS['red'])
            text_surface.set_alpha(180)
            # Position in bottom left
            x = 10
            y = WINDOW_HEIGHT - 30
            self.screen.blit(text_surface, (x, y))
    
    def draw(self):
        """Draw the game."""
        # Draw main menu
        if self.in_main_menu:
            self.main_menu.draw()
            pygame.display.flip()
            return
        
        # Draw options menu
        if self.in_options_menu:
            self.options_menu.draw()
            pygame.display.flip()
            return
        
        # Draw cheats menu
        if self.in_cheats_menu:
            self.cheats_menu.draw()
            pygame.display.flip()
            return
        
        if not self.game_started:
            pygame.display.flip()
            return
        
        # Clear screen
        self.screen.fill(COLORS['bg_color'])
        
        # Draw all sprites with camera offset
        self.all_sprites.custom_draw(self.player)
        
        # Draw projectiles (on top of enemies)
        for projectile in self.projectile_group:
            offset_pos = projectile.rect.topleft - self.all_sprites.offset
            self.screen.blit(projectile.image, offset_pos)
        
        # Draw drops
        for drop in self.drop_group:
            offset_pos = drop.rect.topleft - self.all_sprites.offset
            self.screen.blit(drop.image, offset_pos)
        
        # Draw HUD
        debug_info = None
        if self.debug_mode:
            debug_info = {
                'FPS': int(self.clock.get_fps()),
                'Enemies': len(self.enemy_group),
                'Projectiles': len(self.projectile_group),
                'Drops': len(self.drop_group),
                'Player Pos': f"({int(self.player.pos.x)}, {int(self.player.pos.y)})",
                'Spawn Rate': f"{self.spawner._get_spawn_rate():.1f}/s",
            }
        
        self.hud.draw(self.player, self.game_time, self.player.kills, debug_info)
        
        # Draw cheats watermark
        self._draw_cheats_watermark()
        
        # Draw menus
        if self.level_up_active:
            self.level_up_menu.draw()
        
        if self.paused:
            self.pause_menu.draw()
        
        if self.game_over:
            self.death_screen.draw()
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        while self.running:
            # Calculate delta time
            self.dt = self.clock.tick(FPS) / 1000.0
            
            # Cap delta time to prevent physics issues
            self.dt = min(self.dt, 0.1)
            
            # Handle events
            self.handle_events()
            
            # Update game state
            self.update()
            
            # Draw
            self.draw()
        
        # Cleanup
        pygame.quit()
        sys.exit()


def main():
    """Entry point."""
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
