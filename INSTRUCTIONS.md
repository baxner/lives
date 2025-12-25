# Proyecto: Guerra de Tacos (ROJO vs AZUL)

Este documento detalla la implementación de un juego interactivo para TikTok Live donde dos bandos luchan por el territorio.

## 📋 Requisitos del Sistema

Asegúrate de tener instalado Python.

### 1. Crear Entorno Virtual (Recomendado)
Para no ensuciar tu instalación global de Python, crea un entorno aislado:

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 2. Instalar Dependencias
Una vez activado el entorno (verás `(.venv)` en tu terminal), instala las librerías:

```bash
pip install -r requirements.txt
```

## 📂 Estructura del Proyecto

```plaintext
/GuerraTacos
│
├── main.py            # El cerebro: Conecta TikTok con el Juego
├── game_engine.py     # La lógica: Movimiento, colisiones, renderizado
├── assets/            # Imágenes de tacos, perritos, sonidos (Opcional)
├── config.py          # Configuraciones (Colores, Velocidad, Regalos)
├── requirements.txt   # Dependencias del proyecto
└── INSTRUCTIONS.md    # Este archivo
```

## 🛠️ Configuración

Puedes ajustar las reglas del juego en `config.py`:
- **Colores**: Cambia los colores de los equipos.
- **Jugabilidad**: Ajusta la velocidad, tamaño base, y crecimiento.
- **Regalos**: Configura qué regalos invocan a qué soldados y cuántos puntos valen.

## 🎮 Cómo Jugar

1.  **Ejecutar el Juego**:
    ```bash
    python main.py
    ```
2.  **Conectar a TikTok**:
    - Asegúrate de poner tu usuario de TikTok en `main.py` (variable `TIKTOK_USERNAME`).
    - El juego se conectará automáticamente al chat de tu live.
3.  **Interacción**:
    - **Rose** (Rosa): Invoca un soldado para el equipo **ROJO**.
    - **GG**: Invoca un soldado para el equipo **AZUL**.
    - **Taco**: Invoca un soldado gigante (o 10 puntos) para **ROJO**.
    - **Ice Cream**: Invoca un soldado gigante (o 10 puntos) para **AZUL**.
    - **Sombrero/Corgi**: "Héroe" que remonta la partida (50 puntos).

## 💡 Notas Adicionales

- **Assets**: Si deseas usar imágenes personalizadas, guárdalas en la carpeta `assets/` y modifica `game_engine.py` para cargarlas.
- **OBS**: Para transmitir, añade una "Captura de Ventana" en OBS y selecciona la ventana de "Guerra de Tacos".
