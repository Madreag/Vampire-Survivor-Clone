# systems/ui.py
"""
UI system for HUD, menus, and overlays.
"""

import pygame
from settings import (
    COLORS, UI_SETTINGS, WINDOW_WIDTH, WINDOW_HEIGHT,
    WEAPON_DATA, PASSIVE_DATA, CHEAT_SETTINGS, AVAILABLE_STARTING_WEAPONS,
    AVAILABLE_STARTING_PASSIVES
)
from utils import draw_text, draw_bar, format_time


class HUD:
    """Heads-up display showing player stats."""
    
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        
        # Fonts
        self.font = pygame.font.Font(None, UI_SETTINGS['font_size'])
        self.small_font = pygame.font.Font(None, UI_SETTINGS['small_font_size'])
        self.large_font = pygame.font.Font(None, UI_SETTINGS['large_font_size'])
        
        # Bar settings
        self.hp_bar_width = UI_SETTINGS['hp_bar_width']
        self.hp_bar_height = UI_SETTINGS['hp_bar_height']
        self.xp_bar_width = UI_SETTINGS['xp_bar_width']
        self.xp_bar_height = UI_SETTINGS['xp_bar_height']
    
    def draw(self, player, game_time, kills, debug_info=None):
        """Draw the HUD."""
        # HP Bar (top left)
        hp_pos = (20, 20)
        draw_bar(
            self.display_surface,
            hp_pos,
            (self.hp_bar_width, self.hp_bar_height),
            player.get_hp_progress(),
            COLORS['red'],
            COLORS['dark_gray']
        )
        hp_text = f"{int(player.hp)}/{int(player.max_hp)}"
        draw_text(self.display_surface, hp_text, 
                 (hp_pos[0] + self.hp_bar_width // 2, hp_pos[1] + self.hp_bar_height // 2),
                 self.small_font, COLORS['white'], center=True)
        
        # XP Bar (top center)
        xp_pos = (WINDOW_WIDTH // 2 - self.xp_bar_width // 2, 20)
        draw_bar(
            self.display_surface,
            xp_pos,
            (self.xp_bar_width, self.xp_bar_height),
            player.get_xp_progress(),
            COLORS['blue'],
            COLORS['dark_gray']
        )
        
        # Level (above XP bar)
        level_text = f"Level {player.level}"
        draw_text(self.display_surface, level_text,
                 (WINDOW_WIDTH // 2, 45),
                 self.font, COLORS['gold'], center=True)
        
        # Timer (top right)
        time_text = format_time(game_time)
        draw_text(self.display_surface, time_text,
                 (WINDOW_WIDTH - 80, 25),
                 self.large_font, COLORS['white'], center=True)
        
        # Kills (below timer)
        kills_text = f"Kills: {kills}"
        draw_text(self.display_surface, kills_text,
                 (WINDOW_WIDTH - 80, 55),
                 self.small_font, COLORS['white'], center=True)
        
        # Debug info (if enabled)
        if debug_info:
            self._draw_debug(debug_info)
    
    def _draw_debug(self, debug_info):
        """Draw debug information."""
        y = 80
        for key, value in debug_info.items():
            text = f"{key}: {value}"
            draw_text(self.display_surface, text, (20, y),
                     self.small_font, COLORS['green'])
            y += 20


class LevelUpMenu:
    """Level up upgrade selection menu."""
    
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        
        # Fonts
        self.font = pygame.font.Font(None, UI_SETTINGS['font_size'])
        self.small_font = pygame.font.Font(None, UI_SETTINGS['small_font_size'])
        self.large_font = pygame.font.Font(None, UI_SETTINGS['large_font_size'])
        
        # Card settings
        self.card_width = UI_SETTINGS['card_width']
        self.card_height = UI_SETTINGS['card_height']
        self.card_spacing = UI_SETTINGS['card_spacing']
        
        # State
        self.active = False
        self.options = []
        self.selected_index = 0
    
    def show(self, options):
        """Show the level up menu with options."""
        self.active = True
        self.options = options
        self.selected_index = 0
    
    def hide(self):
        """Hide the menu."""
        self.active = False
        self.options = []
    
    def handle_input(self, event):
        """Handle input for menu navigation."""
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._select_option()
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                index = event.key - pygame.K_1
                if index < len(self.options):
                    self.selected_index = index
                    return self._select_option()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self._handle_click(event.pos)
        
        elif event.type == pygame.MOUSEMOTION:
            self._handle_hover(event.pos)
        
        return None
    
    def _select_option(self):
        """Select the current option."""
        if self.options and 0 <= self.selected_index < len(self.options):
            option = self.options[self.selected_index]
            self.hide()
            return option
        return None
    
    def _handle_click(self, pos):
        """Handle mouse click."""
        for i, rect in enumerate(self._get_card_rects()):
            if rect.collidepoint(pos):
                self.selected_index = i
                return self._select_option()
        return None
    
    def _handle_hover(self, pos):
        """Handle mouse hover."""
        for i, rect in enumerate(self._get_card_rects()):
            if rect.collidepoint(pos):
                self.selected_index = i
                break
    
    def _get_card_rects(self):
        """Get rectangles for all cards."""
        rects = []
        total_width = len(self.options) * self.card_width + (len(self.options) - 1) * self.card_spacing
        start_x = WINDOW_WIDTH // 2 - total_width // 2
        y = WINDOW_HEIGHT // 2 - self.card_height // 2
        
        for i in range(len(self.options)):
            x = start_x + i * (self.card_width + self.card_spacing)
            rects.append(pygame.Rect(x, y, self.card_width, self.card_height))
        
        return rects
    
    def draw(self):
        """Draw the level up menu."""
        if not self.active:
            return
        
        # Darken background
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.display_surface.blit(overlay, (0, 0))
        
        # Title
        draw_text(self.display_surface, "LEVEL UP!",
                 (WINDOW_WIDTH // 2, 100),
                 self.large_font, COLORS['gold'], center=True)
        
        draw_text(self.display_surface, "Choose an upgrade:",
                 (WINDOW_WIDTH // 2, 140),
                 self.font, COLORS['white'], center=True)
        
        # Draw cards
        card_rects = self._get_card_rects()
        
        for i, (option, rect) in enumerate(zip(self.options, card_rects)):
            self._draw_card(option, rect, i == self.selected_index, i + 1)
    
    def _draw_card(self, option, rect, selected, number):
        """Draw a single upgrade card."""
        # Card background
        bg_color = COLORS['dark_gray'] if not selected else COLORS['gray']
        pygame.draw.rect(self.display_surface, bg_color, rect)
        
        # Border
        border_color = COLORS['gold'] if selected else COLORS['white']
        border_width = 3 if selected else 1
        pygame.draw.rect(self.display_surface, border_color, rect, border_width)
        
        # Get option info
        option_type, option_id, is_new, current_level = option
        
        if option_type == 'weapon':
            data = WEAPON_DATA.get(option_id, {})
            name = data.get('name', option_id)
            desc = data.get('description', '')
            color = data.get('color', COLORS['white'])
            
            if is_new:
                title = f"NEW: {name}"
                level_text = "Level 1"
            else:
                title = name
                level_text = f"Level {current_level} → {current_level + 1}"
        
        elif option_type == 'passive':
            data = PASSIVE_DATA.get(option_id, {})
            name = data.get('name', option_id)
            desc = data.get('description', '')
            color = data.get('color', COLORS['white'])
            
            if is_new:
                title = f"NEW: {name}"
                level_text = "Level 1"
            else:
                title = name
                level_text = f"Level {current_level} → {current_level + 1}"
        
        elif option_type == 'evolution':
            weapon_data = WEAPON_DATA.get(option_id, {})
            name = weapon_data.get('evolution', option_id)
            title = f"EVOLVE: {name}"
            desc = "Weapon evolution!"
            color = COLORS['gold']
            level_text = "MAX"
        
        else:
            title = str(option_id)
            desc = ""
            color = COLORS['white']
            level_text = ""
        
        # Draw icon (colored square)
        icon_rect = pygame.Rect(rect.centerx - 25, rect.y + 30, 50, 50)
        pygame.draw.rect(self.display_surface, color, icon_rect)
        pygame.draw.rect(self.display_surface, COLORS['white'], icon_rect, 2)
        
        # Draw number
        draw_text(self.display_surface, str(number),
                 (rect.x + 15, rect.y + 10),
                 self.font, COLORS['yellow'])
        
        # Draw title
        draw_text(self.display_surface, title,
                 (rect.centerx, rect.y + 100),
                 self.small_font, COLORS['white'], center=True)
        
        # Draw level
        draw_text(self.display_surface, level_text,
                 (rect.centerx, rect.y + 125),
                 self.small_font, COLORS['gold'], center=True)
        
        # Draw description (word wrap)
        self._draw_wrapped_text(desc, rect.centerx, rect.y + 160, 
                               rect.width - 20, self.small_font)
    
    def _draw_wrapped_text(self, text, x, y, max_width, font):
        """Draw text with word wrapping."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines):
            draw_text(self.display_surface, line,
                     (x, y + i * 20),
                     font, COLORS['light_gray'], center=True)


class PauseMenu:
    """Pause menu with resume/restart/quit options."""
    
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, UI_SETTINGS['font_size'])
        self.large_font = pygame.font.Font(None, UI_SETTINGS['large_font_size'])
        
        self.active = False
        self.options = ['Resume', 'Restart', 'Quit']
        self.selected_index = 0
    
    def show(self):
        """Show the pause menu."""
        self.active = True
        self.selected_index = 0
    
    def hide(self):
        """Hide the pause menu."""
        self.active = False
    
    def handle_input(self, event):
        """Handle input for menu navigation."""
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.options[self.selected_index].lower()
            elif event.key == pygame.K_ESCAPE:
                return 'resume'
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                return self._handle_click(event.pos)
        
        elif event.type == pygame.MOUSEMOTION:
            self._handle_hover(event.pos)
        
        return None
    
    def _get_option_rects(self):
        """Get rectangles for menu options."""
        rects = []
        start_y = WINDOW_HEIGHT // 2 - 50
        
        for i in range(len(self.options)):
            rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, start_y + i * 50, 200, 40)
            rects.append(rect)
        
        return rects
    
    def _handle_click(self, pos):
        """Handle mouse click."""
        for i, rect in enumerate(self._get_option_rects()):
            if rect.collidepoint(pos):
                return self.options[i].lower()
        return None
    
    def _handle_hover(self, pos):
        """Handle mouse hover."""
        for i, rect in enumerate(self._get_option_rects()):
            if rect.collidepoint(pos):
                self.selected_index = i
                break
    
    def draw(self):
        """Draw the pause menu."""
        if not self.active:
            return
        
        # Darken background
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.display_surface.blit(overlay, (0, 0))
        
        # Title
        draw_text(self.display_surface, "PAUSED",
                 (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 120),
                 self.large_font, COLORS['white'], center=True)
        
        # Options
        for i, (option, rect) in enumerate(zip(self.options, self._get_option_rects())):
            selected = i == self.selected_index
            
            bg_color = COLORS['gray'] if selected else COLORS['dark_gray']
            pygame.draw.rect(self.display_surface, bg_color, rect)
            
            border_color = COLORS['gold'] if selected else COLORS['white']
            pygame.draw.rect(self.display_surface, border_color, rect, 2)
            
            text_color = COLORS['gold'] if selected else COLORS['white']
            draw_text(self.display_surface, option,
                     rect.center, self.font, text_color, center=True)


class DeathScreen:
    """Death screen showing stats and restart option."""
    
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, UI_SETTINGS['font_size'])
        self.small_font = pygame.font.Font(None, UI_SETTINGS['small_font_size'])
        self.large_font = pygame.font.Font(None, UI_SETTINGS['large_font_size'])
        
        self.active = False
        self.stats = {}
        self.high_score = 0
        self.best_time = 0
        self.is_new_record = False
    
    def show(self, stats, high_score=0, best_time=0):
        """Show the death screen with stats."""
        self.active = True
        self.stats = stats
        self.high_score = high_score
        self.best_time = best_time
        self.is_new_record = (stats.get('kills', 0) > high_score or 
                              stats.get('time', 0) > best_time)
    
    def hide(self):
        """Hide the death screen."""
        self.active = False
    
    def handle_input(self, event):
        """Handle input."""
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
                return 'restart'
            elif event.key == pygame.K_ESCAPE:
                return 'quit'
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return 'restart'
        
        return None
    
    def draw(self):
        """Draw the death screen."""
        if not self.active:
            return
        
        # Dark background
        self.display_surface.fill(COLORS['black'])
        
        # Title
        draw_text(self.display_surface, "GAME OVER",
                 (WINDOW_WIDTH // 2, 100),
                 self.large_font, COLORS['red'], center=True)
        
        # New record indicator
        if self.is_new_record:
            draw_text(self.display_surface, "NEW RECORD!",
                     (WINDOW_WIDTH // 2, 150),
                     self.font, COLORS['gold'], center=True)
        
        # Stats
        y = 220
        stats_to_show = [
            ('Time Survived', format_time(self.stats.get('time', 0))),
            ('Level Reached', str(self.stats.get('level', 1))),
            ('Enemies Killed', str(self.stats.get('kills', 0))),
            ('Damage Dealt', str(int(self.stats.get('damage_dealt', 0)))),
        ]
        
        for label, value in stats_to_show:
            draw_text(self.display_surface, f"{label}:",
                     (WINDOW_WIDTH // 2 - 100, y),
                     self.font, COLORS['white'])
            draw_text(self.display_surface, value,
                     (WINDOW_WIDTH // 2 + 100, y),
                     self.font, COLORS['gold'])
            y += 40
        
        # High scores
        y += 30
        draw_text(self.display_surface, "--- Best Records ---",
                 (WINDOW_WIDTH // 2, y),
                 self.font, COLORS['gray'], center=True)
        y += 40
        
        draw_text(self.display_surface, f"Best Time: {format_time(self.best_time)}",
                 (WINDOW_WIDTH // 2, y),
                 self.font, COLORS['white'], center=True)
        y += 30
        
        draw_text(self.display_surface, f"Most Kills: {self.high_score}",
                 (WINDOW_WIDTH // 2, y),
                 self.font, COLORS['white'], center=True)
        
        # Restart prompt
        draw_text(self.display_surface, "Press ENTER or SPACE to restart",
                 (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100),
                 self.font, COLORS['white'], center=True)
        
        draw_text(self.display_surface, "Press ESC to quit",
                 (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60),
                 self.small_font, COLORS['gray'], center=True)


class MainMenu:
    """Main menu with Start, Options, and Quit buttons."""
    
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, UI_SETTINGS['font_size'])
        self.large_font = pygame.font.Font(None, UI_SETTINGS['large_font_size'])
        self.title_font = pygame.font.Font(None, 72)
        
        self.active = True
        self.options = ['Start', 'Options', 'Quit']
        self.selected_index = 0
    
    def show(self):
        """Show the main menu."""
        self.active = True
        self.selected_index = 0
    
    def hide(self):
        """Hide the main menu."""
        self.active = False
    
    def handle_input(self, event):
        """Handle input for menu navigation."""
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.options[self.selected_index].lower()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                return self._handle_click(event.pos)
        
        elif event.type == pygame.MOUSEMOTION:
            self._handle_hover(event.pos)
        
        return None
    
    def _get_option_rects(self):
        """Get rectangles for menu options."""
        rects = []
        start_y = WINDOW_HEIGHT // 2
        
        for i in range(len(self.options)):
            rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, start_y + i * 60, 240, 50)
            rects.append(rect)
        
        return rects
    
    def _handle_click(self, pos):
        """Handle mouse click."""
        for i, rect in enumerate(self._get_option_rects()):
            if rect.collidepoint(pos):
                return self.options[i].lower()
        return None
    
    def _handle_hover(self, pos):
        """Handle mouse hover."""
        for i, rect in enumerate(self._get_option_rects()):
            if rect.collidepoint(pos):
                self.selected_index = i
                break
    
    def draw(self):
        """Draw the main menu."""
        if not self.active:
            return
        
        # Dark background
        self.display_surface.fill(COLORS['bg_color'])
        
        # Title
        draw_text(self.display_surface, "VAMPIRE SURVIVORS",
                 (WINDOW_WIDTH // 2, 150),
                 self.title_font, COLORS['red'], center=True)
        
        draw_text(self.display_surface, "Clone",
                 (WINDOW_WIDTH // 2, 210),
                 self.large_font, COLORS['gold'], center=True)
        
        # Options
        for i, (option, rect) in enumerate(zip(self.options, self._get_option_rects())):
            selected = i == self.selected_index
            
            bg_color = COLORS['gray'] if selected else COLORS['dark_gray']
            pygame.draw.rect(self.display_surface, bg_color, rect)
            
            border_color = COLORS['gold'] if selected else COLORS['white']
            pygame.draw.rect(self.display_surface, border_color, rect, 2)
            
            text_color = COLORS['gold'] if selected else COLORS['white']
            draw_text(self.display_surface, option,
                     rect.center, self.font, text_color, center=True)
        
        # Instructions
        draw_text(self.display_surface, "Use W/S or Arrow Keys to navigate, ENTER to select",
                 (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50),
                 self.font, COLORS['gray'], center=True)


class OptionsMenu:
    """Options menu with Cheats submenu."""
    
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, UI_SETTINGS['font_size'])
        self.large_font = pygame.font.Font(None, UI_SETTINGS['large_font_size'])
        
        self.active = False
        self.options = ['Cheats', 'Back']
        self.selected_index = 0
    
    def show(self):
        """Show the options menu."""
        self.active = True
        self.selected_index = 0
    
    def hide(self):
        """Hide the options menu."""
        self.active = False
    
    def handle_input(self, event):
        """Handle input for menu navigation."""
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.options[self.selected_index].lower()
            elif event.key == pygame.K_ESCAPE:
                return 'back'
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                return self._handle_click(event.pos)
        
        elif event.type == pygame.MOUSEMOTION:
            self._handle_hover(event.pos)
        
        return None
    
    def _get_option_rects(self):
        """Get rectangles for menu options."""
        rects = []
        start_y = WINDOW_HEIGHT // 2 - 30
        
        for i in range(len(self.options)):
            rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, start_y + i * 60, 240, 50)
            rects.append(rect)
        
        return rects
    
    def _handle_click(self, pos):
        """Handle mouse click."""
        for i, rect in enumerate(self._get_option_rects()):
            if rect.collidepoint(pos):
                return self.options[i].lower()
        return None
    
    def _handle_hover(self, pos):
        """Handle mouse hover."""
        for i, rect in enumerate(self._get_option_rects()):
            if rect.collidepoint(pos):
                self.selected_index = i
                break
    
    def draw(self):
        """Draw the options menu."""
        if not self.active:
            return
        
        # Dark background
        self.display_surface.fill(COLORS['bg_color'])
        
        # Title
        draw_text(self.display_surface, "OPTIONS",
                 (WINDOW_WIDTH // 2, 150),
                 self.large_font, COLORS['gold'], center=True)
        
        # Options
        for i, (option, rect) in enumerate(zip(self.options, self._get_option_rects())):
            selected = i == self.selected_index
            
            bg_color = COLORS['gray'] if selected else COLORS['dark_gray']
            pygame.draw.rect(self.display_surface, bg_color, rect)
            
            border_color = COLORS['gold'] if selected else COLORS['white']
            pygame.draw.rect(self.display_surface, border_color, rect, 2)
            
            text_color = COLORS['gold'] if selected else COLORS['white']
            draw_text(self.display_surface, option,
                     rect.center, self.font, text_color, center=True)
        
        # Instructions
        draw_text(self.display_surface, "Press ESC to go back",
                 (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50),
                 self.font, COLORS['gray'], center=True)


class CheatsMenu:
    """Cheats submenu with toggles for unlimited health, starting weapons, weapon level, and power-ups."""
    
    def __init__(self, cheat_settings):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, UI_SETTINGS['font_size'])
        self.small_font = pygame.font.Font(None, UI_SETTINGS['small_font_size'])
        self.large_font = pygame.font.Font(None, UI_SETTINGS['large_font_size'])
        
        self.active = False
        self.cheat_settings = cheat_settings
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_visible_items = 10
        
        # Import available weapons and passives
        from settings import AVAILABLE_STARTING_WEAPONS, WEAPON_DATA, PASSIVE_DATA, AVAILABLE_STARTING_PASSIVES
        self.available_weapons = AVAILABLE_STARTING_WEAPONS
        self.weapon_data = WEAPON_DATA
        self.passive_data = PASSIVE_DATA
        self.available_passives = AVAILABLE_STARTING_PASSIVES
        
        # Initialize starting_passives if not present
        if 'starting_passives' not in self.cheat_settings:
            self.cheat_settings['starting_passives'] = {}
        if 'starting_weapon_level' not in self.cheat_settings:
            self.cheat_settings['starting_weapon_level'] = 1
    
    def show(self):
        """Show the cheats menu."""
        self.active = True
        self.selected_index = 0
        self.scroll_offset = 0
    
    def hide(self):
        """Hide the cheats menu."""
        self.active = False
    
    def _get_options(self):
        """Get current options with their states."""
        unlimited_health_state = "ON" if self.cheat_settings['unlimited_health'] else "OFF"
        current_weapon = self.weapon_data.get(self.cheat_settings['starting_weapon'], {}).get('name', 'Whip')
        weapon_level = self.cheat_settings.get('starting_weapon_level', 1)
        exp_multiplier = self.cheat_settings.get('exp_multiplier', 1.0)
        
        # Create visual slider for EXP multiplier
        exp_slider = self._get_exp_slider_display(exp_multiplier)
        
        options = [
            f"Unlimited Health: {unlimited_health_state}",
            f"Starting Weapon: {current_weapon}",
            f"Weapon Level: {weapon_level}",
            f"EXP Multiplier: {exp_slider}",
            "--- Power-ups ---",
        ]
        
        # Add power-up options with checkboxes and levels
        for passive_id in self.available_passives:
            passive_info = self.passive_data.get(passive_id, {})
            passive_name = passive_info.get('name', passive_id)
            max_level = passive_info.get('max_level', 5)
            
            if passive_id in self.cheat_settings.get('starting_passives', {}):
                level = self.cheat_settings['starting_passives'][passive_id]
                options.append(f"[X] {passive_name}: Level {level}/{max_level}")
            else:
                options.append(f"[ ] {passive_name}: OFF")
        
        options.append("Back")
        return options
    
    def _get_passive_index(self, option_index):
        """Get the passive index from the option index."""
        # Options: 0=health, 1=weapon, 2=weapon_level, 3=exp_multiplier, 4=separator, 5+=passives, last=back
        passive_start = 5
        if option_index >= passive_start and option_index < passive_start + len(self.available_passives):
            return option_index - passive_start
        return -1
    
    def handle_input(self, event):
        """Handle input for menu navigation."""
        if not self.active:
            return None
        
        options = self._get_options()
        
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(options)
                # Skip separator
                if self.selected_index == 4:
                    self.selected_index = 3
                self._update_scroll()
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(options)
                # Skip separator
                if self.selected_index == 4:
                    self.selected_index = 5
                self._update_scroll()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._select_option()
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                return self._adjust_option(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                return self._adjust_option(1)
            elif event.key == pygame.K_ESCAPE:
                return 'back'
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                return self._handle_click(event.pos)
            elif event.button == 4:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.button == 5:  # Scroll down
                max_scroll = max(0, len(options) - self.max_visible_items)
                self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
        
        elif event.type == pygame.MOUSEMOTION:
            self._handle_hover(event.pos)
        
        return None
    
    def _update_scroll(self):
        """Update scroll offset to keep selected item visible."""
        options = self._get_options()
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.max_visible_items:
            self.scroll_offset = self.selected_index - self.max_visible_items + 1
    
    def _select_option(self):
        """Select the current option."""
        options = self._get_options()
        
        if self.selected_index == 0:
            # Toggle unlimited health
            self.cheat_settings['unlimited_health'] = not self.cheat_settings['unlimited_health']
            self._update_cheats_enabled()
        elif self.selected_index == 1:
            # Cycle to next weapon
            self._cycle_weapon(1)
        elif self.selected_index == 2:
            # Cycle weapon level
            self._cycle_weapon_level(1)
        elif self.selected_index == 3:
            # Adjust EXP multiplier (increase on select)
            self._adjust_exp_multiplier(1)
        elif self.selected_index == 4:
            # Separator - do nothing
            pass
        elif self.selected_index == len(options) - 1:
            # Back
            return 'back'
        else:
            # Toggle passive
            passive_idx = self._get_passive_index(self.selected_index)
            if passive_idx >= 0:
                self._toggle_passive(passive_idx)
        
        return None
    
    def _adjust_option(self, direction):
        """Adjust the current option (for left/right keys)."""
        options = self._get_options()
        
        if self.selected_index == 0:
            # Toggle unlimited health
            self.cheat_settings['unlimited_health'] = not self.cheat_settings['unlimited_health']
            self._update_cheats_enabled()
        elif self.selected_index == 1:
            # Cycle weapon
            self._cycle_weapon(direction)
        elif self.selected_index == 2:
            # Cycle weapon level
            self._cycle_weapon_level(direction)
        elif self.selected_index == 3:
            # Adjust EXP multiplier
            self._adjust_exp_multiplier(direction)
        elif self.selected_index == 4:
            # Separator - do nothing
            pass
        elif self.selected_index == len(options) - 1:
            # Back - do nothing
            pass
        else:
            # Adjust passive level
            passive_idx = self._get_passive_index(self.selected_index)
            if passive_idx >= 0:
                self._adjust_passive_level(passive_idx, direction)
        
        return None
    
    def _cycle_weapon(self, direction):
        """Cycle through available weapons."""
        current_weapon = self.cheat_settings['starting_weapon']
        try:
            current_index = self.available_weapons.index(current_weapon)
        except ValueError:
            current_index = 0
        
        new_index = (current_index + direction) % len(self.available_weapons)
        self.cheat_settings['starting_weapon'] = self.available_weapons[new_index]
        self._update_cheats_enabled()
    
    def _cycle_weapon_level(self, direction):
        """Cycle through weapon levels (1-8)."""
        current_level = self.cheat_settings.get('starting_weapon_level', 1)
        new_level = current_level + direction
        
        # Clamp to valid range (1-8)
        if new_level < 1:
            new_level = 8
        elif new_level > 8:
            new_level = 1
        
        self.cheat_settings['starting_weapon_level'] = new_level
        self._update_cheats_enabled()
    
    def _get_exp_slider_display(self, multiplier):
        """Get a visual slider display for the EXP multiplier."""
        # Multiplier ranges from 0.25 to 5.0 in steps of 0.25
        # That's 20 steps total (0.25, 0.5, 0.75, ... 5.0)
        min_val = 0.25
        max_val = 5.0
        step = 0.25
        
        # Calculate position (0-19)
        position = int((multiplier - min_val) / step)
        total_positions = int((max_val - min_val) / step) + 1  # 20 positions
        
        # Create slider visual: [----O-----------] 1.0x
        slider_width = 19  # Number of dashes
        slider_chars = ['-'] * slider_width
        
        # Place the selector
        selector_pos = int((position / (total_positions - 1)) * (slider_width - 1))
        slider_chars[selector_pos] = 'O'
        
        slider_str = ''.join(slider_chars)
        return f"[{slider_str}] {multiplier:.2f}x"
    
    def _adjust_exp_multiplier(self, direction):
        """Adjust the EXP multiplier by 0.25 per step."""
        current = self.cheat_settings.get('exp_multiplier', 1.0)
        step = 0.25
        min_val = 0.25
        max_val = 5.0
        
        new_val = current + (direction * step)
        
        # Clamp to valid range
        new_val = max(min_val, min(max_val, new_val))
        
        # Round to avoid floating point issues
        new_val = round(new_val * 4) / 4
        
        self.cheat_settings['exp_multiplier'] = new_val
        self._update_cheats_enabled()
    
    def _toggle_passive(self, passive_idx):
        """Toggle a passive on/off."""
        if passive_idx < 0 or passive_idx >= len(self.available_passives):
            return
        
        passive_id = self.available_passives[passive_idx]
        
        if passive_id in self.cheat_settings['starting_passives']:
            # Remove passive
            del self.cheat_settings['starting_passives'][passive_id]
        else:
            # Add passive at level 1
            self.cheat_settings['starting_passives'][passive_id] = 1
        
        self._update_cheats_enabled()
    
    def _adjust_passive_level(self, passive_idx, direction):
        """Adjust the level of a passive."""
        if passive_idx < 0 or passive_idx >= len(self.available_passives):
            return
        
        passive_id = self.available_passives[passive_idx]
        passive_info = self.passive_data.get(passive_id, {})
        max_level = passive_info.get('max_level', 5)
        
        if passive_id not in self.cheat_settings['starting_passives']:
            # Enable passive at level 1 if adjusting right, do nothing if left
            if direction > 0:
                self.cheat_settings['starting_passives'][passive_id] = 1
        else:
            current_level = self.cheat_settings['starting_passives'][passive_id]
            new_level = current_level + direction
            
            if new_level < 1:
                # Remove passive if going below level 1
                del self.cheat_settings['starting_passives'][passive_id]
            elif new_level > max_level:
                # Cap at max level
                self.cheat_settings['starting_passives'][passive_id] = max_level
            else:
                self.cheat_settings['starting_passives'][passive_id] = new_level
        
        self._update_cheats_enabled()
    
    def _update_cheats_enabled(self):
        """Update the master cheats_enabled flag."""
        # Cheats are enabled if any cheat option is non-default
        has_cheats = (
            self.cheat_settings['unlimited_health'] or 
            self.cheat_settings['starting_weapon'] != 'whip' or
            self.cheat_settings.get('starting_weapon_level', 1) != 1 or
            len(self.cheat_settings.get('starting_passives', {})) > 0 or
            self.cheat_settings.get('exp_multiplier', 1.0) != 1.0
        )
        self.cheat_settings['cheats_enabled'] = has_cheats
    
    def _get_option_rects(self):
        """Get rectangles for menu options."""
        rects = []
        options = self._get_options()
        start_y = 180
        item_height = 40
        
        visible_start = self.scroll_offset
        visible_end = min(len(options), self.scroll_offset + self.max_visible_items)
        
        for i in range(visible_start, visible_end):
            y = start_y + (i - visible_start) * item_height
            rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, y, 400, item_height - 5)
            rects.append((i, rect))
        
        return rects
    
    def _handle_click(self, pos):
        """Handle mouse click."""
        for i, rect in self._get_option_rects():
            if rect.collidepoint(pos):
                self.selected_index = i
                return self._select_option()
        return None
    
    def _handle_hover(self, pos):
        """Handle mouse hover."""
        for i, rect in self._get_option_rects():
            if rect.collidepoint(pos):
                self.selected_index = i
                break
    
    def draw(self):
        """Draw the cheats menu."""
        if not self.active:
            return
        
        # Dark background
        self.display_surface.fill(COLORS['bg_color'])
        
        # Title
        draw_text(self.display_surface, "CHEATS",
                 (WINDOW_WIDTH // 2, 60),
                 self.large_font, COLORS['red'], center=True)
        
        # Warning
        draw_text(self.display_surface, "Enabling cheats will show a watermark during gameplay",
                 (WINDOW_WIDTH // 2, 100),
                 self.small_font, COLORS['yellow'], center=True)
        
        # Scroll indicator
        options = self._get_options()
        if len(options) > self.max_visible_items:
            scroll_text = f"Showing {self.scroll_offset + 1}-{min(len(options), self.scroll_offset + self.max_visible_items)} of {len(options)}"
            draw_text(self.display_surface, scroll_text,
                     (WINDOW_WIDTH // 2, 140),
                     self.small_font, COLORS['gray'], center=True)
        
        # Options
        for i, rect in self._get_option_rects():
            option = options[i]
            selected = i == self.selected_index
            
            # Different styling for separator
            if option.startswith("---"):
                draw_text(self.display_surface, option,
                         rect.center, self.small_font, COLORS['cyan'], center=True)
                continue
            
            bg_color = COLORS['gray'] if selected else COLORS['dark_gray']
            pygame.draw.rect(self.display_surface, bg_color, rect)
            
            border_color = COLORS['gold'] if selected else COLORS['white']
            pygame.draw.rect(self.display_surface, border_color, rect, 2)
            
            # Color coding for enabled options
            if option.startswith("[X]"):
                text_color = COLORS['green'] if not selected else COLORS['gold']
            elif option.startswith("[ ]"):
                text_color = COLORS['light_gray'] if not selected else COLORS['gold']
            else:
                text_color = COLORS['gold'] if selected else COLORS['white']
            
            draw_text(self.display_surface, option,
                     rect.center, self.font, text_color, center=True)
        
        # Instructions
        draw_text(self.display_surface, "UP/DOWN to navigate | LEFT/RIGHT to adjust | ENTER to toggle | ESC to go back",
                 (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60),
                 self.small_font, COLORS['gray'], center=True)
        
        draw_text(self.display_surface, "Scroll with mouse wheel if needed",
                 (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 35),
                 self.small_font, COLORS['gray'], center=True)
