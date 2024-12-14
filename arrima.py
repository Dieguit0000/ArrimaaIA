import pygame
import copy
import math
import random

# Dimensiones del tablero
WIDTH, HEIGHT = 400, 400
ROWS, COLS = 4, 4
SQ_SIZE = WIDTH // COLS

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
TRAP_COLOR = (200, 0, 0)
HIGHLIGHT_COLOR = (50, 200, 50)

# Piezas y su valor
PIECE_VALUES = {
    "E": 50,  # Elefante
    "C": 40,  # Camello
    "H": 30,  # Caballo
    "D": 20,  # Perro
    "G": 10,  # Gato
    "R": 1,   # Conejo
}

# Casillas de trampa
TRAPS = {(2, 2), (2, 5), (5, 2), (5, 5)}

# Inicializar Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arimaa")

# Tablero inicial completo
def init_board():
    board = [["." for _ in range(COLS)] for _ in range(ROWS)]

    # Piezas iniciales jugador 1
    board[0] = ["E", "C", "H", "D", "G", "H", "C", "E"]
    board[1] = ["R", "R", "R", "R", "R", "R", "R", "R"]

    # Piezas iniciales jugador 2
    board[6] = ["r", "r", "r", "r", "r", "r", "r", "r"]
    board[7] = ["e", "c", "h", "d", "g", "h", "c", "e"]

    return board

# Dibujar el tablero
def draw_board(board):
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if (row + col) % 2 == 0 else GRAY
            pygame.draw.rect(screen, color, (col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

            # Casillas de trampa
            if (row, col) in TRAPS:
                pygame.draw.rect(screen, TRAP_COLOR, (col * SQ_SIZE + 20, row * SQ_SIZE + 20, SQ_SIZE - 40, SQ_SIZE - 40))

            # Piezas
            piece = board[row][col]
            if piece != ".":
                draw_piece(piece, row, col)

# Dibujar una pieza
def draw_piece(piece, row, col):
    font = pygame.font.SysFont("Arial", 36)
    color = BLACK if piece.isupper() else WHITE
    text = font.render(piece, True, color)
    screen.blit(text, (col * SQ_SIZE + SQ_SIZE // 4, row * SQ_SIZE + SQ_SIZE // 4))

# Movimiento válido
def valid_move(board, start, end):
    x1, y1 = start
    x2, y2 = end

    # Fuera del tablero
    if not (0 <= x2 < ROWS and 0 <= y2 < COLS):
        return False

    # La casilla de destino debe estar vacía
    if board[x2][y2] != ".":
        return False

    # Movimiento de una casilla
    return abs(x1 - x2) + abs(y1 - y2) == 1

# Realizar un movimiento
def make_move(board, start, end):
    x1, y1 = start
    x2, y2 = end

    board[x2][y2] = board[x1][y1]
    board[x1][y1] = "."

# Función de evaluación para la IA
def evaluate_board(board):
    score = 0
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece in PIECE_VALUES:
                score += PIECE_VALUES[piece] if piece.isupper() else -PIECE_VALUES[piece.upper()]
    return score

# Minimax con poda Alfa-Beta
def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0:
        return evaluate_board(board), None

    best_move = None

    if maximizing_player:
        max_eval = -math.inf
        for move in get_all_moves(board, maximizing_player):
            new_board = copy.deepcopy(board)
            make_move(new_board, move[0], move[1])
            eval, _ = minimax(new_board, depth - 1, alpha, beta, False)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move

    else:
        min_eval = math.inf
        for move in get_all_moves(board, maximizing_player):
            new_board = copy.deepcopy(board)
            make_move(new_board, move[0], move[1])
            eval, _ = minimax(new_board, depth - 1, alpha, beta, True)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

# Obtener todos los movimientos válidos
def get_all_moves(board, maximizing_player):
    moves = []
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if (piece.isupper() and maximizing_player) or (piece.islower() and not maximizing_player):
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    x2, y2 = row + dx, col + dy
                    if valid_move(board, (row, col), (x2, y2)):
                        moves.append(((row, col), (x2, y2)))
    return moves

# Bucle principal del juego
def main():
    board = init_board()
    running = True
    selected = None
    player_turn = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and player_turn:
                x, y = pygame.mouse.get_pos()
                row, col = y // SQ_SIZE, x // SQ_SIZE

                if selected:
                    if valid_move(board, selected, (row, col)):
                        make_move(board, selected, (row, col))
                        selected = None
                        player_turn = False
                    else:
                        selected = None
                else:
                    selected = (row, col)

        if not player_turn:
            _, ai_move = minimax(board, 3, -math.inf, math.inf, False)
            if ai_move:
                make_move(board, ai_move[0], ai_move[1])
            player_turn = True

        # Dibujar el tablero
        screen.fill(BLACK)
        draw_board(board)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
