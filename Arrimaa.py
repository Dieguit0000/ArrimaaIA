import pygame
import random
import time

# Inicializar Pygame
pygame.init()

# Dimensiones del tablero
TILE_SIZE = 80  # Tamaño de cada casilla
ROWS, COLS = 8, 8  # Tablero de 8x8
WIDTH, HEIGHT = TILE_SIZE * COLS, TILE_SIZE * ROWS

# Colores
LIGHT_COLOR = (255, 206, 158)
DARK_COLOR = (209, 139, 71)
TRAP_COLOR = (255, 0, 0)  # Rojo para trampas
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

# Generar posiciones iniciales para los jugadores
def generate_random_positions():
    pieces = [
        "E", "C", "H", "H", "D", "D", "G", "G",
        "R", "R", "R", "R", "R", "R", "R", "R"
    ]
    random.shuffle(pieces)
    positions = []
    available_slots = [(row, col) for row in range(2) for col in range(COLS)]
    random.shuffle(available_slots)

    for piece in pieces:
        x, y = available_slots.pop()
        positions.append((x, y, piece))

    return positions

# Inicializar posiciones iniciales
INITIAL_POSITIONS = {
    "gold": generate_random_positions(),
    "silver": [(x + 6, y, piece) for x, y, piece in generate_random_positions()]
}

# Variables de estado
selected_square = None
selected_piece = None
current_turn = "gold"  # Turno inicial
remaining_moves = 4  # Movimientos por turno

def draw_board():
    for row in range(ROWS):
        for col in range(COLS):
            color = LIGHT_COLOR if (row + col) % 2 == 0 else DARK_COLOR
            pygame.draw.rect(screen, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    for trap in TRAP_POSITIONS:
        x, y = trap
        pygame.draw.circle(
            screen, TRAP_COLOR,
            (y * TILE_SIZE + TILE_SIZE // 2, x * TILE_SIZE + TILE_SIZE // 2),
            TILE_SIZE // 4
        )

    if selected_square:
        # Resaltar la casilla seleccionada con un borde verde
        sx, sy = selected_square
        pygame.draw.rect(screen, HIGHLIGHT_COLOR,
                         (sy * TILE_SIZE, sx * TILE_SIZE, TILE_SIZE, TILE_SIZE), 5)  # Borde de 5px

def draw_pieces():
    font = pygame.font.SysFont(None, 40)
    for color, positions in INITIAL_POSITIONS.items():
        for x, y, piece in positions:
            piece_color = PIECE_COLORS[color]
            pygame.draw.circle(
                screen, piece_color,
                (y * TILE_SIZE + TILE_SIZE // 2, x * TILE_SIZE + TILE_SIZE // 2),
                TILE_SIZE // 3
            )
            text = font.render(piece, True, (0, 0, 0))
            text_rect = text.get_rect(center=(y * TILE_SIZE + TILE_SIZE // 2, x * TILE_SIZE + TILE_SIZE // 2))
            screen.blit(text, text_rect)

            # Resaltar la pieza seleccionada con un borde si es la seleccionada
            if (x, y) == selected_square:
                pygame.draw.circle(
                    screen, HIGHLIGHT_COLOR, 
                    (y * TILE_SIZE + TILE_SIZE // 2, x * TILE_SIZE + TILE_SIZE // 2), TILE_SIZE // 4, 5
                )  # Borde de 5px

def is_valid_move(start, end):
    sx, sy = start
    ex, ey = end
    dx, dy = abs(ex - sx), abs(ey - sy)
    if dx + dy == 1:  # Movimiento a una casilla adyacente
        # Verificar que la casilla final no esté ocupada
        for positions in INITIAL_POSITIONS.values():
            for px, py, _ in positions:
                if (px, py) == end:
                    return False
        return True
    return False

def move_piece(start, end):
    global INITIAL_POSITIONS, selected_piece

    for color, positions in INITIAL_POSITIONS.items():
        for i, (x, y, piece) in enumerate(positions):
            if (x, y) == start:
                positions[i] = (end[0], end[1], piece)  # Actualizar posición
                return

def get_random_move(color):
    """Genera un movimiento aleatorio para el oponente."""
    positions = INITIAL_POSITIONS[color]
    random.shuffle(positions)

    for x, y, piece in positions:
        # Buscar movimientos válidos
        possible_moves = [
            (x + dx, y + dy)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
            if 0 <= x + dx < ROWS and 0 <= y + dy < COLS
        ]
        random.shuffle(possible_moves)

        for move in possible_moves:
            if is_valid_move((x, y), move):
                return (x, y), move
    return None, None

def handle_click(pos):
    global selected_square, selected_piece, remaining_moves, current_turn

    if current_turn == "silver":
        return  # Ignorar clics si es turno del oponente

    x, y = pos[1] // TILE_SIZE, pos[0] // TILE_SIZE

    if selected_square is None:  # Seleccionar pieza
        for color, positions in INITIAL_POSITIONS.items():
            if color == current_turn:  # Solo seleccionar piezas del jugador actual
                for px, py, piece in positions:
                    if (px, py) == (x, y):
                        selected_square = (x, y)
                        selected_piece = piece
                        return
    else:  # Mover pieza
        if is_valid_move(selected_square, (x, y)):
            move_piece(selected_square, (x, y))
            remaining_moves -= 1
            selected_square = None
            selected_piece = None

            # Cambio de turno si se acaban los movimientos
            if remaining_moves == 0:
                remaining_moves = 4
                current_turn = "silver"
                handle_opponent_turn()
        else:
            selected_square = None  # Deseleccionar si el movimiento no es válido

def handle_opponent_turn():
    global remaining_moves, current_turn

    while remaining_moves > 0:
        start, end = get_random_move("silver")
        if start and end:
            move_piece(start, end)
            remaining_moves -= 1
            
            # Dibujar cada movimiento para mostrarlo lentamente
            screen.fill((0, 0, 0))
            draw_board()
            draw_pieces()
            pygame.display.flip()
            time.sleep(0.5)  # Pausa para mostrar el movimiento

    # Cambio de turno a "gold"
    remaining_moves = 4
    current_turn = "gold"

# Bucle principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_click(pygame.mouse.get_pos())

    screen.fill((0, 0, 0))
    draw_board()
    draw_pieces()
    pygame.display.flip()

pygame.quit()