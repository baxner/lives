import asyncio
import pygame
from TikTokLive import TikTokLiveClient
from TikTokLive.events import GiftEvent, ConnectEvent, DisconnectEvent, JoinEvent, LikeEvent
from game_engine import GameState
from config import GIFT_MAP

# Inicializar Juego (Global para que sea accesible)
game = GameState()
client = None # Se definirá en el main

# Debug Users para testing (rotan entre ellos)
DEBUG_USERS = ["TestUser1", "TestUser2", "TestUser3", "TestUser4", "TestUser5", "TestUser6", "TestUser7", "TestUser8", "TestUser9", "TestUser10"]
debug_user_index = 0

def get_next_debug_user():
    global debug_user_index
    user = DEBUG_USERS[debug_user_index]
    debug_user_index = (debug_user_index + 1) % len(DEBUG_USERS)
    return user

async def on_connect(event: ConnectEvent):
    print(f"✅ CONECTADO AL LIVE DE: {event.unique_id}")
    print("Esperando regalos...")

async def on_disconnect(event: DisconnectEvent):
    print("❌ DESCONECTADO")

async def on_join(event: JoinEvent):
    # Audio
    game.sound_manager.play("join")

    # Asignar alternadamente entre equipos
    # Priorizar nickname (más amigable) sobre username
    display_name = getattr(event.user, 'nick_name', None) or getattr(event.user, 'username', "Unknown")
    
    # Obtener siguiente equipo (alterna automáticamente)
    team = game.get_next_join_team()
    game.spawn_soldier(team, display_name, 1)  # Soldado básico (1 punto)
    
    # Log visual
    color = (255, 150, 150) if team == "RED" else (150, 150, 255)
    game.add_log(f"👋 {display_name} → {team}", color)
    print(f"👋 {display_name} se unió → Equipo {team}")

async def on_like(event: LikeEvent):
    # Audio (un tick por batch de likes para no saturar)
    game.sound_manager.play("tick")
    
    like_count = getattr(event, 'likes', None) or getattr(event, 'total_likes', None) or getattr(event, 'count', 1) or 1
    user_name = getattr(event.user, 'nick_name', None) or getattr(event.user, 'username', "Alguien")
    
    # Límite de seguridad para no crashear (máximo 50 por evento)
    actual_count = min(int(like_count), 50)
    
    # Log visual
    color = (255, 150, 150) if game.like_period_team == "RED" else (150, 150, 255)
    game.add_log(f"👍 {user_name} +{actual_count} likes → {game.like_period_team}", color)
    print(f"👍 {user_name} dio {like_count} like(s) → {actual_count} minis para {game.like_period_team}")
    
    for _ in range(actual_count):
        game.spawn_like_soldier()

async def on_gift(event: GiftEvent):
    """Manejador de eventos de regalos"""
    # Ignorar regalos si son parte de un combo activo (para no saturar)
    # Usamos getattr para evitar errores si la versión de la librería cambió el nombre del atributo
    streak_end = getattr(event.gift, 'streak_end', True)
    streakable = getattr(event.gift, 'streakable', False)
    
    if streakable and not streak_end:
        return

    gift_name = event.gift.name
    
    # Obtener el nickname (más amigable que username)
    display_name = getattr(event.user, 'nick_name', None) or getattr(event.user, 'username', "Unknown")
    
    print(f"🎁 Recibido: {gift_name} de {display_name}")
    
    # Buscar el regalo en nuestro mapa de config
    game_data = None
    
    # Búsqueda flexible (por si el regalo se llama "Rose" o "Sending Rose")
    for key, val in GIFT_MAP.items():
        if key.lower() in gift_name.lower():
            game_data = val
            break
            
    if game_data:
        # Audio
        game.sound_manager.play("gift")
        
        points, team = game_data
        # Log visual
        color = (255, 150, 150) if team == "RED" else (150, 150, 255)
        if team == "RESET":
            color = (255, 100, 255)  # Magenta para Galaxy
            game.add_log(f"🌌 GALAXY RESET por {display_name}!", color)
        else:
            game.add_log(f"🎁 {display_name}: {gift_name} +{points}pts → {team}", color)
        print(f"   -> Acción: {points} pts para {team}")
        game.spawn_soldier(team, display_name, points)
    else:
        print(f"   -> Regalo no configurado (Sin efecto)")

async def game_loop():
    """Mantiene vivo el juego de Pygame"""
    print("🎮 Ventana de juego abierta. Esperando conexión a TikTok...")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # client.stop() no existe en versiones recientes o es disconnect
                if client and client.connected:
                    await client.disconnect()

            # Debug Keys - Simular diferentes regalos
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_j: # J for Join Simulation
                    print("🔧 Debug: Simulando Join")
                    team = game.get_next_join_team()
                    debug_user = get_next_debug_user()
                    game.spawn_soldier(team, debug_user, 1)
                    print(f"   → {debug_user} asignado a equipo {team}")
                
                elif event.key == pygame.K_r: # R = Rose (RED, 1pt)
                    debug_user = get_next_debug_user()
                    print(f"🔧 Debug: {debug_user} → Rose (RED, 1 moneda)")
                    game.spawn_soldier("RED", debug_user, 1)
                
                elif event.key == pygame.K_g: # G = GG (BLUE, 1pt)
                    debug_user = get_next_debug_user()
                    print(f"🔧 Debug: {debug_user} → GG (BLUE, 1 moneda)")
                    game.spawn_soldier        ("BLUE", debug_user, 1)
                
                elif event.key == pygame.K_h: # H = Heart Me (RED, 1pt)
                    debug_user = get_next_debug_user()
                    print(f"🔧 Debug: {debug_user} → Heart Me (RED, 1 moneda)")
                    game.spawn_soldier("RED", debug_user, 1)
                
                elif event.key == pygame.K_i: # I = Ice Cream (BLUE, 1pt)
                    debug_user = get_next_debug_user()
                    print(f"🔧 Debug: {debug_user} → Ice Cream (BLUE, 1 moneda)")
                    game.spawn_soldier("BLUE", debug_user, 1)
                
                elif event.key == pygame.K_s: # S = I'm Ready (BLUE, 1pt)
                    debug_user = get_next_debug_user()
                    print(f"🔧 Debug: {debug_user} → I'm Ready (BLUE, 1 moneda)")
                    game.spawn_soldier("BLUE", debug_user, 1)
                
                elif event.key == pygame.K_d: # D = Dancing Hands (RED, 199)
                    debug_user = get_next_debug_user()
                    print(f"🔧 Debug: {debug_user} → Dancing Hands (RED, 199 monedas)")
                    game.spawn_soldier("RED", debug_user, 199)
                
                elif event.key == pygame.K_c: # C = Corgi (BLUE, 299)
                    debug_user = get_next_debug_user()
                    print(f"🔧 Debug: {debug_user} → Corgi (BLUE, 299 monedas)")
                    game.spawn_soldier("BLUE", debug_user, 299)
                
                elif event.key == pygame.K_m: # M = Money Gun (RED, 500)
                    debug_user = get_next_debug_user()
                    print(f"🔧 Debug: {debug_user} → Money Gun (RED, 500 monedas)")
                    game.spawn_soldier("RED", debug_user, 500)
                
                elif event.key == pygame.K_t: # T = Train (BLUE, 899)
                    debug_user = get_next_debug_user()
                    print(f"🔧 Debug: {debug_user} → Train (BLUE, 899 monedas)")
                    game.spawn_soldier("BLUE", debug_user, 899)
                
                elif event.key == pygame.K_x: # X = Galaxy (RESET)
                    print("🔧 Debug: Galaxy (RESET)")
                    game.spawn_soldier("RESET", "Galaxy", 9999)
        
        game.run_frame()
        await asyncio.sleep(0.001) # Ceder control a TikTokLive
    
    pygame.quit()

if __name__ == '__main__':
    print("--- ⚔️ GUERRA DE COLORES ⚔️ ---")
    print("--- ⚔️ GUERRA DE COLORES ⚔️ ---")
    
    # Configuración de usuario por defecto para Android/Testing
    DEFAULT_USER = "alkasstvsports" # Cambia esto si lo usas en Android
    
    try:
        user_input = input(f"Introduce el usuario de TikTok (Enter para '{DEFAULT_USER}'): ").strip()
        if not user_input:
            user_input = DEFAULT_USER
    except EOFError:
        print(f"⚠️ Entorno no interactivo detectado (Android?). Usando: {DEFAULT_USER}")
        user_input = DEFAULT_USER
    
    # Limpiar @ si el usuario lo puso
    if user_input.startswith("@"):
        user_input = user_input[1:]
        
    print(f"Conectando con: @{user_input} ...")
    
    # Crear cliente dinámicamente
    client = TikTokLiveClient(unique_id=user_input)
    
    # Registrar evento manualmente
    client.add_listener(GiftEvent, on_gift)
    client.add_listener(ConnectEvent, on_connect)
    client.add_listener(DisconnectEvent, on_disconnect)
    client.add_listener(JoinEvent, on_join)
    client.add_listener(LikeEvent, on_like)  # Likes = Mini soldados
    
    # Iniciar conexión
    loop = asyncio.get_event_loop()
    
    try:
        future = asyncio.gather(client.start(), game_loop())
        loop.run_until_complete(future)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Consejo: Verifica que el usuario esté en vivo.")