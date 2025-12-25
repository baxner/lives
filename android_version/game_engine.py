import pygame
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from config import *

# --- SOUND MANAGER ---
class SoundManager:
    def __init__(self):
        try:
            # Android sometimes needs specific mixer settings
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            self.enabled = True
        except:
            print("Warning: Audio system could not be initialized")
            self.enabled = False
            return

        self.sounds = {}
        self.generate_sounds()

    def generate_sounds(self):
        if not self.enabled: return
        
        def make_sound(frequency, duration, wave_type="sine", volume=0.5):
            sample_rate = 44100
            n_samples = int(sample_rate * duration)
            t = np.linspace(0, duration, n_samples, False)
            
            if wave_type == "sine":
                wave = np.sin(2 * np.pi * frequency * t)
            elif wave_type == "square":
                wave = np.sign(np.sin(2 * np.pi * frequency * t))
            elif wave_type == "noise":
                wave = np.random.uniform(-1, 1, n_samples)
            else:
                wave = np.sin(2 * np.pi * frequency * t)
            
            envelope = np.linspace(1, 0, n_samples)
            wave = wave * envelope * volume
            stereo = np.column_stack((wave, wave))
            audio = (stereo * 32767).astype(np.int16)
            return pygame.sndarray.make_sound(audio)

        try:
            self.sounds["pop"] = make_sound(600, 0.05, "sine", 0.3)
            self.sounds["join"] = make_sound(880, 0.1, "sine", 0.4)
            self.sounds["gift"] = make_sound(523.25, 0.3, "sine", 0.4)
            self.sounds["win"] = make_sound(440, 0.5, "square", 0.5)
            self.sounds["tick"] = make_sound(0, 0.01, "noise", 0.1)
        except Exception as e:
            print(f"Error generating sounds: {e}")

    def play(self, name):
        if self.enabled and name in self.sounds:
            try:
                self.sounds[name].play()
            except:
                pass

# --- SOLDIER CLASS ---
class Soldier:
    def __init__(self, team, username, power_level, images):
        self.team = team
        self.username = username
        self.power_level = power_level
        self.images = images
        
        # Determinar Tier
        if self.power_level >= TIER_4_THRESHOLD:
            self.tier = 4
        elif self.power_level >= TIER_3_THRESHOLD:
            self.tier = 3
        elif self.power_level >= TIER_2_THRESHOLD:
            self.tier = 2
        else:
            self.tier = 1
            
        # Seleccionar imagen base
        base_img = self.images.get(self.tier, self.images[1])
        
        # Scaling Logic
        scale_factor = 1.0 + (self.power_level * 0.05)
        # Cap scale
        max_scale_factor = 3.0
        if self.tier == 4: max_scale_factor = 5.0
        scale_factor = min(scale_factor, max_scale_factor)
        
        self.size = int(BASE_SIZE * scale_factor)
        
        try:
            self.image = pygame.transform.scale(base_img, (self.size, self.size))
        except:
             self.image =  pygame.Surface((self.size, self.size))
             self.image.fill(RED_TEAM_COLOR if team == "RED" else BLUE_TEAM_COLOR)

        # Dirección
        if self.team == "RED":
            self.direction = 1
            self.image = pygame.transform.flip(self.image, True, False) # Voltear soldados rojos
        else:
            self.direction = -1
            
        self.rect = self.image.get_rect()
        
        # Posición Inicial
        if self.team == "RED":
            self.rect.x = random.randint(*SPAWN_X_RANGE_RED)
        else:
            self.rect.x = random.randint(*SPAWN_X_RANGE_BLUE)
            
        self.rect.y = random.randint(*SPAWN_Y_RANGE)
        
        self.health = self.size * 2
        self.floating_texts = []
        self.is_mini = False

    def grow(self, points):
        self.add_floating_text(f"+{points}", (0, 255, 0))

    def add_floating_text(self, text, color):
        if not hasattr(self, 'rect'): return
        self.floating_texts.append([text, self.rect.centerx, self.rect.top, 60, color])

    def move(self):
        self.rect.x += SPEED * self.direction

    def draw(self, screen, font, game_state=None):
        screen.blit(self.image, self.rect)
        
        if self.is_mini: return
        
        # Username
        try:
            display_name = self.username[:10] + ".." if len(self.username) > 12 else self.username
            text_surf = font.render(display_name, True, TEXT_COLOR)
            screen.blit(text_surf, (self.rect.centerx - text_surf.get_width()//2, self.rect.top - 25))
        except: pass
        
        # Floating Texts
        for ft in self.floating_texts[:]:
            txt, x, y, life, col = ft
            alpha = min(255, int((life / 60) * 255))
            if alpha <= 0:
                self.floating_texts.remove(ft)
                continue
            
            surf = font.render(str(txt), True, col)
            surf.set_alpha(alpha)
            screen.blit(surf, (x - surf.get_width()//2, y))
            ft[2] -= 1 # Subir
            ft[3] -= 1 # Decrementar vida

    def update_stats(self, new_power):
        pass # Simplificado para Android

# --- GAME STATE ---
class GameState:
    def __init__(self):
        pygame.init()
        # Fullscreen recomendado en Android
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("TikTok Battle Android")
        
        self.sound_manager = SoundManager()
        
        # Fonts
        try:
            self.font = pygame.font.SysFont("Droid Sans", 24, bold=True)
            self.ui_font = pygame.font.SysFont("Droid Sans", 40, bold=True)
        except:
            self.font = pygame.font.SysFont("Arial", 24, bold=True)
            self.ui_font = pygame.font.SysFont("Arial", 40, bold=True)
            
        self.clock = pygame.time.Clock()
        
        self.red_army = []
        self.blue_army = []
        self.soldiers_map = {}
        self.activity_log = []
        
        self.red_victories = 0
        self.blue_victories = 0
        
        # Assets Loading
        self.assets = {"RED": {}, "BLUE": {}}
        self._load_assets()
        
        self.running = True
        self.victory_timer = 0
        self.winning_team = None

    def _load_assets(self):
        # Base path relative to THIS file (game_engine.py)
        import os
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        def load(name, scale=1.0):
            try:
                # Construct full path
                full_path = os.path.join(base_path, "assets", name)
                img = pygame.image.load(full_path).convert_alpha()
                if scale != 1.0:
                    new_size = (int(img.get_width() * scale), int(img.get_height() * scale))
                    return pygame.transform.scale(img, new_size)
                return img
            except Exception as e:
                print(f"Error loading {name}: {e}")
                # Create fallback surface
                s = pygame.Surface((50, 50))
                s.fill((255, 0, 255)) # Magenta debug
                return s
        
        # Paths relatives to where main.py runs
        self.assets["RED"][4] = load("assets/red_soldier_t4.png", RED_TEAM_COLOR)
        
        self.assets["BLUE"][1] = load("assets/blue_soldier.png", BLUE_TEAM_COLOR)
        self.assets["BLUE"][2] = load("assets/blue_soldier_t2.png", BLUE_TEAM_COLOR)
        self.assets["BLUE"][3] = load("assets/blue_soldier_t3.png", BLUE_TEAM_COLOR)
        self.assets["BLUE"][4] = load("assets/blue_soldier_t4.png", BLUE_TEAM_COLOR)

    def spawn_soldier(self, team, username, points):
        if team == "RESET":
            self.red_army.clear()
            self.blue_army.clear()
            self.soldiers_map.clear()
            self.red_victories = 0
            self.blue_victories = 0
            return

        self.sound_manager.play("pop")
        
        # Simplification: Only create new soldiers, don't grow distinct instances for now to save complexity
        # Or simple logic:
        images = self.assets[team]
        s = Soldier(team, username, points, images)
        if team == "RED": self.red_army.append(s)
        else: self.blue_army.append(s)
        
    def spawn_like_soldier(self):
        # Random team for likes or alternating? Let's do random for chaos
        team = "RED" if random.random() > 0.5 else "BLUE"
        self.spawn_soldier(team, "", 1)
        self.red_army[-1].is_mini = True if team == "RED" else False
        if team == "BLUE": self.blue_army[-1].is_mini = True

    def get_next_join_team(self):
        return "RED" if len(self.red_army) <= len(self.blue_army) else "BLUE"

    def add_log(self, msg, color):
        self.activity_log.insert(0, (msg, color, 120)) # 120 frames
        if len(self.activity_log) > 5: self.activity_log.pop()

    def run_frame(self):
        self.screen.fill((30, 30, 30)) # Dark background
        
        # Draw Battlefield
        for s in self.red_army[:]:
            s.move()
            s.draw(self.screen, self.font)
            # Collision Logic (Simple)
            for enemy in self.blue_army:
                if s.rect.colliderect(enemy.rect):
                    # Battle
                    if s.size > enemy.size:
                        if enemy in self.blue_army: self.blue_army.remove(enemy)
                        # enemy.health -= s.power_level # complex logic skipped
                    elif enemy.size > s.size:
                        if s in self.red_army: self.red_army.remove(s)
                        break # soldier dead
                    else:
                        # 50/50
                        if random.random() > 0.5:
                            if enemy in self.blue_army: self.blue_army.remove(enemy)
                        else:
                            if s in self.red_army: self.red_army.remove(s)
                            break
            # Remove out of bounds
            if s.rect.x > WIDTH: 
                if s in self.red_army: 
                    self.red_victories += 1
                    self.sound_manager.play("win")
                    self.red_army.remove(s)
            
        for s in self.blue_army[:]:
            s.move()
            s.draw(self.screen, self.font)
            if s.rect.x < -s.size:
                if s in self.blue_army:
                    self.blue_victories += 1
                    self.sound_manager.play("win")
                    self.blue_army.remove(s)

        # UI Overlay
        # Scoreboard (Top Center)
        score_text = f"{self.red_victories} - {self.blue_victories}"
        surf = self.ui_font.render(score_text, True, (255, 255, 255))
        self.screen.blit(surf, (WIDTH//2 - surf.get_width()//2, 50))
        
        # Activity Log (Top Left)
        y = 100
        for msg, color, timer in self.activity_log:
            txt_surf = self.font.render(msg, True, color)
            self.screen.blit(txt_surf, (20, y))
            y += 30
            
        pygame.display.flip()
        self.clock.tick(30) # 30 FPS for mobile battery
