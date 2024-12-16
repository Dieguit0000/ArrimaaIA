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
PUSH_HIGHLIGHT_COLOR = (0, 0, 255)  # Azul para resaltar opciones de empuje

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
    "E": 6,  # Elefante
    "C": 5,  # Camello
    "H": 4,  # Caballo
    "D": 3,  # Perro
    "G": 2,  # Gato
    "R": 1   # Conejo
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
push_mode = False
push_options = []  # Opciones para empujar
piece_to_push = None

# Dibujar el tablero
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
        sx, sy = selected_square
        pygame.draw.rect(screen, HIGHLIGHT_COLOR,
                         (sy * TILE_SIZE, sx * TILE_SIZE, TILE_SIZE, TILE_SIZE), 5)  # Borde de 5px

    if push_mode:
        for px, py in push_options:
            pygame.draw.rect(screen, PUSH_HIGHLIGHT_COLOR,
                             (py * TILE_SIZE, px * TILE_SIZE, TILE_SIZE, TILE_SIZE), 5)

# Dibujar piezas
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

# Encontrar pieza en una posición
def find_piece(position):
    for color, positions in INITIAL_POSITIONS.items():
        for x, y, piece in positions:
            if (x, y) == position:
                return color, piece
    return None, None

# Mover pieza
def move_piece(start, end):
    for color, positions in INITIAL_POSITIONS.items():
        for i, (x, y, piece) in enumerate(positions):
            if (x, y) == start:
                positions[i] = (end[0], end[1], piece)
                return

# Validar movimiento
def is_valid_move(start, end):
    sx, sy = start
    ex, ey = end
    dx, dy = abs(ex - sx), abs(ey - sy)

    if dx + dy != 1:
        return False

    for positions in INITIAL_POSITIONS.values():
        for px, py, _ in positions:
            if (px, py) == end:
                return False

    return True

# Generar opciones de empuje
def generate_push_options(target_pos, pusher_pos):
    tx, ty = target_pos
    px, py = pusher_pos
    options = []
    
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        new_x, new_y = tx + dx, ty + dy
        if 0 <= new_x < ROWS and 0 <= new_y < COLS and (new_x, new_y) != (px, py):
            if not any((nx, ny) == (new_x, new_y) for nx, ny, _ in INITIAL_POSITIONS["gold"] + INITIAL_POSITIONS["silver"]):
                options.append((new_x, new_y))
    return options

# Verificar si una pieza cae en una trampa
def is_in_trap(position):
    return position in TRAP_POSITIONS

# Eliminar pieza que cae en la trampa
def remove_piece_from_board(position, color):
    for i, (x, y, piece) in enumerate(INITIAL_POSITIONS[color]):
        if (x, y) == position:
            del INITIAL_POSITIONS[color][i]
            break

# Manejar clics
def handle_click(pos):
    global selected_square, selected_piece, remaining_moves, current_turn, push_mode, push_options, piece_to_push

    if current_turn == "silver":
        return

    x, y = pos[1] // TILE_SIZE, pos[0] // TILE_SIZE

    if push_mode:
        if (x, y) in push_options:
            # Realizar el empuje: mover la pieza empujadora y la pieza empujada
            move_piece(piece_to_push, (x, y))  # Mover la pieza empujadora a la posición de la ficha empujada
            move_piece(selected_square, piece_to_push)  # Mover la ficha empujada a la nueva posición seleccionada

            # Verificar si la pieza empujada cae en una trampa
            if is_in_trap((x, y)):
                print(f"La ficha empujada cae en una trampa en la posición ({x}, {y})")
                # Eliminar la pieza empujada si no tiene aliados adyacentes
                piece_color, _ = find_piece((x, y))
                if piece_color:
                    # Comprobar si no tiene aliados adyacentes
                    allies_adjacent = any(
                        (ax, ay) in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                        for ax, ay, _ in INITIAL_POSITIONS[piece_color]
                    )
                    if not allies_adjacent:
                        remove_piece_from_board((x, y), piece_color)
                        print(f"Se ha eliminado la pieza en la trampa: ({x}, {y})")
            
            # Verificar todas las fichas después del empuje
            check_traps()
            
            push_mode = False
            remaining_moves -= 1
            end_turn_if_needed()
        else:
            push_mode = False
        return

    if selected_square is None:
        for color, positions in INITIAL_POSITIONS.items():
            if color == current_turn:
                for px, py, piece in positions:
                    if (px, py) == (x, y):
                        selected_square = (x, y)
                        selected_piece = piece
                        return
    else:
        target_color, target_piece = find_piece((x, y))

        if target_color and target_color != current_turn:
            pusher_strength = PIECE_SYMBOLS[selected_piece]
            target_strength = PIECE_SYMBOLS[target_piece]

            if pusher_strength > target_strength:
                push_mode = True
                push_options = generate_push_options((x, y), selected_square)
                piece_to_push = (x, y)
                return

        if is_valid_move(selected_square, (x, y)):
            move_piece(selected_square, (x, y))
            remaining_moves -= 1
            end_turn_if_needed()

        selected_square = None

# Terminar turno si es necesario
def end_turn_if_needed():
    global remaining_moves, current_turn
    if remaining_moves == 0:
        remaining_moves = 4
        current_turn = "silver"
        handle_opponent_turn()

# Movimiento aleatorio del oponente
def get_random_move(color):
    positions = INITIAL_POSITIONS[color]
    random.shuffle(positions)

    for x, y, piece in positions:
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

# Manejar el turno del oponente
def handle_opponent_turn():
    global remaining_moves, current_turn

    while remaining_moves > 0:
        start, end = get_random_move("silver")
        if start and end:
            move_piece(start, end)
            remaining_moves -= 1

            screen.fill((0, 0, 0))
            draw_board()
            draw_pieces()
            pygame.display.flip()
            time.sleep(0.5)

        check_traps()

    remaining_moves = 4
    current_turn = "gold"

# Verificar trampas
def check_traps():
    global INITIAL_POSITIONS
    for color, positions in INITIAL_POSITIONS.items():
        to_remove = []
        for x, y, piece in positions:
            if (x, y) in TRAP_POSITIONS:
                allies_adjacent = any(
                    (ax, ay) in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                    for ax, ay, _ in positions
                )
                if not allies_adjacent:
                    to_remove.append((x, y, piece))

        for item in to_remove:
            positions.remove(item)

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