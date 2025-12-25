import asyncio
import os
import sys

# 1. Configurar SSL para Android (CRITICO para TikTokLive)
try:
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['SSL_CERT_DIR'] = os.path.dirname(certifi.where())
except:
    pass

# Variables Globales (se llenarán dentro del try)
game = None
client = None
TIKTOK_USER = "alkasstvsports"

if __name__ == '__main__':
    # 2. Crash Handler desde el principio
    try:
        import pygame
        
        # 3. Importaciones diferidas para atrapar errores de dependencias
        print(f"📱 Iniciando versión Android para: {TIKTOK_USER}")
        from TikTokLive import TikTokLiveClient
        from TikTokLive.events import GiftEvent, ConnectEvent, DisconnectEvent, JoinEvent, LikeEvent
        from game_engine import GameState
        from config import GIFT_MAP

        # 4. Inicializar Juego
        game = GameState()
        
        # Definir handlers dentro del scope donde 'game' existe
        async def on_connect(event: ConnectEvent):
            print(f"✅ CONECTADO AL LIVE DE: {event.unique_id}")
            game.add_log(f"✅ CONECTADO: {event.unique_id}", (0, 255, 0))

        async def on_disconnect(event: DisconnectEvent):
            print("❌ DESCONECTADO")
            game.add_log("❌ DESCONECTADO", (255, 0, 0))

        async def on_join(event: JoinEvent):
            game.sound_manager.play("join")
            display_name = getattr(event.user, 'nick_name', None) or getattr(event.user, 'username', "Unknown")
            team = game.get_next_join_team()
            game.spawn_soldier(team, display_name, 1)
            
            color = (255, 150, 150) if team == "RED" else (150, 150, 255)
            game.add_log(f"👋 {display_name} -> {team}", color)

        async def on_like(event: LikeEvent):
            game.sound_manager.play("tick")
            like_count = getattr(event, 'likes', None) or getattr(event, 'total_likes', None) or getattr(event, 'count', 1) or 1
            actual_count = min(int(like_count), 20) 
            
            for _ in range(actual_count):
                game.spawn_like_soldier()

        async def on_gift(event: GiftEvent):
            streak_end = getattr(event.gift, 'streak_end', True)
            streakable = getattr(event.gift, 'streakable', False)
            if streakable and not streak_end: return

            gift_name = event.gift.name
            display_name = getattr(event.user, 'nick_name', None) or getattr(event.user, 'username', "Unknown")
            
            game_data = None
            for key, val in GIFT_MAP.items():
                if key.lower() in gift_name.lower():
                    game_data = val
                    break
                    
            if game_data:
                game.sound_manager.play("gift")
                points, team = game_data
                
                color = (255, 150, 150) if team == "RED" else (150, 150, 255)
                if team == "RESET":
                    game.add_log(f"🌌 GALAXY RESET!", (255, 0, 255))
                else:
                    game.add_log(f"🎁 {display_name}: {gift_name}", color)
                    
                game.spawn_soldier(team, display_name, points)

        async def game_loop():
            print("🎮 Iniciando motor gráfico...")
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        if client and client.connected:
                            await client.disconnect()
                        pygame.quit()
                        return
                
                game.run_frame()
                await asyncio.sleep(0.001)

        # 5. Configurar Cliente
        client = TikTokLiveClient(unique_id=TIKTOK_USER)
        client.add_listener(GiftEvent, on_gift)
        client.add_listener(ConnectEvent, on_connect)
        client.add_listener(DisconnectEvent, on_disconnect)
        client.add_listener(JoinEvent, on_join)
        client.add_listener(LikeEvent, on_like)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        future = asyncio.gather(client.start(), game_loop())
        loop.run_until_complete(future)
        
    except Exception as e:
        # 6. CRASH HANDLER ROBUSTO
        import traceback
        error_msg = traceback.format_exc()
        print("❌ CRASH FATAL:")
        print(error_msg)
        
        try:
            import pygame
            pygame.init()
            screen = pygame.display.set_mode((1080, 1920))
            try:
                font = pygame.font.SysFont("monospace", 30)
            except:
                font = pygame.font.SysFont(None, 30)
            
            while True:
                screen.fill((50, 0, 0)) # Fondo Rojo Sangre
                
                y = 50
                # Renderizar mensaje de error multilinea
                final_text = "ERROR FATAL:\n" + error_msg[-600:] # Mostrar ultimos 600 caracteres para que quepa
                for line in final_text.split('\n'):
                    # Wrap manual básico
                    while len(line) > 50:
                        chunk = line[:50]
                        line = line[50:]
                        txt = font.render(chunk, True, (255, 200, 200))
                        screen.blit(txt, (20, y))
                        y += 35
                    
                    txt = font.render(line, True, (255, 200, 200))
                    screen.blit(txt, (20, y))
                    y += 35
                    
                    if y > 1800: break # Evitar salir de pantalla
                    
                pygame.display.flip()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
        except Exception as display_error:
            # Si falla hasta el crash handler, escribir archivo
            print(f"Crash handler failed: {display_error}")
            with open("/sdcard/tiktok_crash.txt", "w") as f:
                f.write(error_msg)
