import pygame
import random

# Inicializar Pygame
pygame.init()

# Dimensiones del tablero
TILE_SIZE = 80  # Tamaño de cada casilla
ROWS, COLS = 8, 8  # Tablero de 8x8
WIDTH, HEIGHT = TILE_SIZE * COLS, TILE_SIZE * ROWS

# Colores
LIGHT_COLOR = (255, 0, 0)  # Rojo
DARK_COLOR = (0, 0, 0)     # Negro
TRAP_COLOR = (255, 255, 255)  # Blanco para trampas
HIGHLIGHT_COLOR = (0, 255, 0)  # Verde para resaltar casillas

# Crear ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arimaa - Proyecto Final")

# Trampas en el tablero
TRAP_POSITIONS = [(2, 2), (2, 5), (5, 2), (5, 5)]

# Piezas iniciales
PIECE_COLORS = {
    "gold": (255, 223, 0),  # Oro
    "silver": (192, 192, 192)  # Plata
}
PIECE_SYMBOLS = {
    "E": "Elefante",
    "C": "Camello",
    "H": "Caballo",
    "D": "Perro",
    "G": "Gato",
    "R": "Conejo"
}

# Generar posiciones iniciales aleatorias para un jugador
def generate_random_positions():
    """Genera posiciones aleatorias para las piezas en las dos primeras filas."""
    pieces = [
        "E",  # 1 Elefante
        "C",  # 1 Camello
        "H", "H",  # 2 Caballos
        "D", "D",  # 2 Perros
        "G", "G",  # 2 Gatos
        "R", "R", "R", "R", "R", "R", "R", "R"  # 8 Conejos
    ]
    random.shuffle(pieces)  # Mezclar las piezas

    positions = []
    available_slots = [(row, col) for row in range(2) for col in range(COLS)]  # Filas 0 y 1
    random.shuffle(available_slots)  # Mezclar las posiciones disponibles

    for piece in pieces:
        x, y = available_slots.pop()  # Tomar una posición aleatoria
        positions.append((x, y, piece))

    return positions

# Generar posiciones iniciales aleatorias para ambos jugadores
INITIAL_POSITIONS = {
    "gold": generate_random_positions(),
    "silver": [(x + 6, y, piece) for x, y, piece in generate_random_positions()]  # Filas 6 y 7 para plata
}

# Variable para rastrear la casilla seleccionada
selected_square = None  # (fila, columna) o None si no hay selección

def draw_board():
    """Dibuja el tablero de 8x8 con colores alternos y las trampas."""
    for row in range(ROWS):
        for col in range(COLS):
            # Determinar el color de la casilla
            if (row + col) % 2 == 0:
                color = LIGHT_COLOR
            else:
                color = DARK_COLOR

            # Resaltar la casilla seleccionada
            if selected_square == (row, col):
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))

            pygame.draw.rect(screen, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE), width=0)

    # Dibujar las trampas
    for trap in TRAP_POSITIONS:
        x, y = trap
        pygame.draw.circle(
            screen, TRAP_COLOR,
            (y * TILE_SIZE + TILE_SIZE // 2, x * TILE_SIZE + TILE_SIZE // 2),
            TILE_SIZE // 4
        )

def draw_pieces():
    """Dibuja las piezas en sus posiciones iniciales."""
    font = pygame.font.SysFont(None, 40)  # Fuente para texto de piezas
    for color, positions in INITIAL_POSITIONS.items():
        for x, y, piece in positions:
            piece_color = PIECE_COLORS[color]
            pygame.draw.circle(
                screen, piece_color,
                (y * TILE_SIZE + TILE_SIZE // 2, x * TILE_SIZE + TILE_SIZE // 2),
                TILE_SIZE // 3
            )
            # Dibujar el símbolo de la pieza
            text = font.render(piece, True, (0, 0, 0))
            text_rect = text.get_rect(center=(y * TILE_SIZE + TILE_SIZE // 2, x * TILE_SIZE + TILE_SIZE // 2))
            screen.blit(text, text_rect)

def handle_click(pos):
    """Maneja el clic del mouse y selecciona una casilla."""
    global selected_square
    x, y = pos
    row, col = x // TILE_SIZE, y // TILE_SIZE

    # Alternar la selección: seleccionar o deseleccionar la casilla
    if selected_square == (row, col):
        selected_square = None  # Deseleccionar
    else:
        selected_square = (row, col)  # Seleccionar nueva casilla

# Bucle principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_click(pygame.mouse.get_pos())

    # Dibujar el tablero y las piezas
    screen.fill((0, 0, 0))  # Fondo negro
    draw_board()
    draw_pieces()

    pygame.display.flip()

pygame.quit()