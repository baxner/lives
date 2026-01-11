# --- CONFIGURACIÓN ANDROID (VERTICAL) ---

# Pantalla (Vertical 9:16)
WIDTH = 1080
HEIGHT = 1920

# Colores de Equipos
# Rojo intenso vs Azul eléctrico
RED_TEAM_COLOR = (255, 50, 50)
BLUE_TEAM_COLOR = (50, 50, 255)
TEXT_COLOR = (255, 255, 255)
GOLD_COLOR = (255, 215, 0)

# Configuración de Soldados
BASE_SIZE = 60 # Un poco más grandes para verlos bien en el móvil
SPEED = 3
SPAWN_X_RANGE_RED = (-100, -20)
SPAWN_X_RANGE_BLUE = (WIDTH + 20, WIDTH + 100)
# Spawn en la mitad inferior de la pantalla mayormente
SPAWN_Y_RANGE = (300, HEIGHT - 300) 

# Evolución
TIER_2_THRESHOLD = 50
TIER_3_THRESHOLD = 200
TIER_4_THRESHOLD = 1000  # DIOS

# Mapa de Regalos (Nombre del Regalo -> Puntos, Equipo)
# Ajusta los nombres según lo que veas en los logs de regalos
GIFT_MAP = {
    "Rose": (1, "RED"), 
    "Rosa": (1, "RED"),
    "TikTok": (1, "RED"),
    "Heart Me": (1, "RED"),
    "Finger Heart": (1, "RED"),
    
    "GG": (1, "BLUE"),
    "Good Game": (1, "BLUE"),
    "Ice Cream": (1, "BLUE"),
    "Helado": (1, "BLUE"),
    "I'm Ready": (1, "BLUE"),
    
    # Regalos Medios
    "Hand Heart": (10, "RED"),
    "Confetti": (10, "BLUE"),
    "Heart": (10, "RED"),
    
    # Regalos Grandes
    "Dancing Hands": (199, "RED"),
    "Corgi": (299, "BLUE"),
    "Money Gun": (500, "RED"),
    "Train": (899, "BLUE"),
    
    # Regalos Especiales
    "Galaxy": (9999, "RESET"),
    "Leon": (5000, "RED"),
    "Fenix": (5000, "BLUE"),
    "Gem Gun": (500, "BLUE"),
    "Love U": (500, "RED")
}
