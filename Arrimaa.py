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
PULL_HIGHLIGHT_COLOR = (255, 255, 0)  # Amarillo para resaltar opciones de jalar

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
pull_mode = False
pull_options = []  # Opciones para jalar
piece_to_pull = None
valid_moves = []  # Movimientos válidos para la pieza seleccionada

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

    if pull_mode:
        for px, py in pull_options:
            pygame.draw.rect(screen, PULL_HIGHLIGHT_COLOR,
                             (py * TILE_SIZE, px * TILE_SIZE, TILE_SIZE, TILE_SIZE), 5)
    # Dibujar movimientos válidos
    for vx, vy in valid_moves:
        pygame.draw.rect(screen, (255, 255, 255), (vy * TILE_SIZE, vx * TILE_SIZE, TILE_SIZE, TILE_SIZE), 3)  # Borde blanco de 3px

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

# Generar opciones de empuje (solo adyacentes en línea recta)
def generate_push_options(target_pos, pusher_pos):
    tx, ty = target_pos
    px, py = pusher_pos
    options = []
    
    # Solo se consideran los movimientos adyacentes en las direcciones rectas (arriba, abajo, izquierda, derecha)
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        new_x, new_y = tx + dx, ty + dy
        # Asegurarse de que las posiciones sean dentro de los límites del tablero y no sean la posición del empujador
        if 0 <= new_x < ROWS and 0 <= new_y < COLS and (new_x, new_y) != (px, py):
            # Verificar si la nueva casilla está vacía (sin piezas)
            if not any((nx, ny) == (new_x, new_y) for nx, ny, _ in INITIAL_POSITIONS["gold"] + INITIAL_POSITIONS["silver"]):
                options.append((new_x, new_y))
    return options

# Verificar si una pieza está adyacente a otra
def is_adjacent(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return (abs(x1 - x2) == 1 and y1 == y2) or (abs(y1 - y2) == 1 and x1 == x2)

# Generar opciones de jalar (solo si la pieza rival está adyacente)
def generate_pull_options(target_pos, puller_pos):
    tx, ty = target_pos
    px, py = puller_pos
    options = []
    
    # Verificar si la pieza rival está adyacente
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        new_x, new_y = tx + dx, ty + dy
        if 0 <= new_x < ROWS and 0 <= new_y < COLS and (new_x, new_y) != (px, py):
            # Validar que la casilla esté vacía para mover la pieza del oponente
            if not any((nx, ny) == (new_x, new_y) for nx, ny, _ in INITIAL_POSITIONS["gold"] + INITIAL_POSITIONS["silver"]):
                options.append((new_x, new_y))
    return options

# Verificar trampas para una pieza en una posición
def check_trap(x, y):
    if (x, y) in TRAP_POSITIONS:
        for color, positions in INITIAL_POSITIONS.items():
            allies_adjacent = any(
                (ax, ay) in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                for ax, ay, _ in positions
            )
            if not allies_adjacent:
                return True  # La pieza debe ser eliminada
    return False

# Eliminar una pieza
def remove_piece(x, y):
    for color, positions in INITIAL_POSITIONS.items():
        for i, (px, py, piece) in enumerate(positions):
            if (px, py) == (x, y):
                positions.pop(i)
                return

# Manejar clics
def handle_click(pos):
    global selected_square, selected_piece, remaining_moves, current_turn, push_mode, push_options, piece_to_push, valid_moves

    if current_turn == "silver":
        return

    x, y = pos[1] // TILE_SIZE, pos[0] // TILE_SIZE

    if push_mode:
        if (x, y) in push_options:
            # Mover la pieza empujada a la nueva posición
            move_piece(piece_to_push, (x, y))
            
            # La ficha que empuja ocupa la posición de la ficha empujada
            move_piece(selected_square, piece_to_push)
            
            # Verificar trampas para todas las piezas después de un empuje
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
                        valid_moves = [
                            (px + dx, py + dy)
                            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                            if 0 <= px + dx < ROWS and 0 <= py + dy < COLS and is_valid_move((px, py), (px + dx, py + dy))
                        ]
                        return
    else:
        target_color, target_piece = find_piece((x, y))

        if target_color and target_color != current_turn:
            pusher_strength = PIECE_SYMBOLS[selected_piece]
            target_strength = PIECE_SYMBOLS[target_piece]

            # Verificar si la pieza del oponente está adyacente antes de intentar empujarla
            if is_adjacent(selected_square, (x, y)) and pusher_strength > target_strength:
                push_mode = True
                push_options = generate_push_options((x, y), selected_square)
                piece_to_push = (x, y)
                return

        if is_valid_move(selected_square, (x, y)):
            move_piece(selected_square, (x, y))
            
            # Verificar trampas para todas las piezas después de un movimiento normal
            check_traps()

            remaining_moves -= 1
            end_turn_if_needed()

        selected_square = None
        valid_moves = []
        
# Terminar turno si es necesario
def end_turn_if_needed():
    global remaining_moves, current_turn
    if remaining_moves == 0:
        remaining_moves = 4
        current_turn = "silver"
        handle_opponent_turn()

# Heurística para evaluar el estado del tablero
def evaluate_board():
    score = 0
    for color, positions in INITIAL_POSITIONS.items():
        for x, y, piece in positions:
            piece_value = PIECE_SYMBOLS[piece]
            if color == "gold":
                score += piece_value
            else:
                score -= piece_value

            # Penalizar si la pieza está en una trampa sin aliados adyacentes
            if (x, y) in TRAP_POSITIONS:
                allies_adjacent = any(
                    (ax, ay) in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                    for ax, ay, _ in positions
                )
                if not allies_adjacent:
                    if color == "gold":
                        score -= piece_value
                    else:
                        score += piece_value

            # Bonificar si la pieza tiene aliados adyacentes
            allies_adjacent = sum(
                1 for ax, ay, _ in positions
                if (ax, ay) in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
            )
            score += allies_adjacent if color == "gold" else -allies_adjacent

    return score


# Algoritmo Minimax con poda alfa-beta
def minimax(depth, alpha, beta, maximizing_player):
    if depth == 0 or remaining_moves == 0:
        return evaluate_board()

    if maximizing_player:
        max_eval = float('-inf')
        for x, y, piece in INITIAL_POSITIONS["silver"]:
            possible_moves = [
                (x + dx, y + dy)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                if 0 <= x + dx < ROWS and 0 <= y + dy < COLS
            ]
            for move in possible_moves:
                if is_valid_move((x, y), move):
                    move_piece((x, y), move)
                    eval = minimax(depth - 1, alpha, beta, False)
                    move_piece(move, (x, y))  # Deshacer movimiento
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
        return max_eval
    else:
        min_eval = float('inf')
        for x, y, piece in INITIAL_POSITIONS["gold"]:
            possible_moves = [
                (x + dx, y + dy)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                if 0 <= x + dx < ROWS and 0 <= y + dy < COLS
            ]
            for move in possible_moves:
                if is_valid_move((x, y), move):
                    move_piece((x, y), move)
                    eval = minimax(depth - 1, alpha, beta, True)
                    move_piece(move, (x, y))  # Deshacer movimiento
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
        return min_eval

# Obtener el mejor movimiento para la IA usando Minimax
def get_best_move():
    best_move = None
    best_value = float('-inf')
    for x, y, piece in INITIAL_POSITIONS["silver"]:
        possible_moves = [
            (x + dx, y + dy)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
            if 0 <= x + dx < ROWS and 0 <= y + dy < COLS
        ]
        for move in possible_moves:
            if is_valid_move((x, y), move):
                move_piece((x, y), move)
                move_value = minimax(3, float('-inf'), float('inf'), False)
                move_piece(move, (x, y))  # Deshacer movimiento
                print(f"Evaluando movimiento de {x, y} a {move}: Puntaje {move_value}")  # Imprimir el puntaje del movimiento
                if move_value > best_value:
                    best_value = move_value
                    best_move = ((x, y), move)
    return best_move

# Manejar el turno del oponente
def handle_opponent_turn():
    global remaining_moves, current_turn

    while remaining_moves > 0:
        best_move = get_best_move()
        if best_move:
            start, end = best_move
            print(f"IA mueve de {start} a {end} con puntaje {evaluate_board()}")  # Imprimir la decisión de la IA con el puntaje
            move_piece(start, end)
            # Verificar si la pieza del oponente cae en una trampa
            if check_trap(end[0], end[1]):
                remove_piece(end[0], end[1])

            remaining_moves -= 1

            screen.fill((0, 0, 0))
            draw_board()
            draw_pieces()
            pygame.display.flip()
            time.sleep(0.5)

        check_traps()

    remaining_moves = 4
    current_turn = "gold"


# Verificar trampas para todas las piezas del tablero
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
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            handle_click(pos)

    screen.fill((0, 0, 0))  # Limpiar pantalla
    draw_board()
    draw_pieces()

    pygame.display.flip()

pygame.quit()