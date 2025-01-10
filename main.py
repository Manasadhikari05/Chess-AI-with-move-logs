import pygame
import chess
import chess.engine
import os

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
BOARD_WIDTH = 600
SQUARE_SIZE = BOARD_WIDTH // 8
FPS = 60

VERTICAL_MARGIN = (SCREEN_HEIGHT - BOARD_WIDTH) // 2

# Colors
LIGHT_SQUARE = (255, 255, 255)
DARK_SQUARE = (154, 205, 50)
HIGHLIGHT_COLOR = (0, 255, 0)
POSSIBLE_MOVE_COLOR = (255, 239, 184)
TEXT_COLOR = (0, 0, 0)

# Load chess piece images
pieces = {}
assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
piece_names = ["bk", "bn", "bb", "bp", "bq", "br", "wk", "wn", "wb", "wp", "wq", "wr"]
for piece in piece_names:
    pieces[piece] = pygame.transform.scale(
        pygame.image.load(os.path.join(assets_dir, f"{piece}.png")),
        (SQUARE_SIZE, SQUARE_SIZE)
    )

# Setup the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chess AI with Move Log")

# Clock to control frame rate
clock = pygame.time.Clock()

# Initialize the chess game board
board = chess.Board()
selected_square = None
human_color = None

# Path to the Stockfish engine
STOCKFISH_PATH = "/opt/homebrew/bin/stockfish"
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

# AI decision using Stockfish
def ai_move(board):
    result = engine.play(board, chess.engine.Limit(depth=15))
    return result.move

# Draw the chessboard with grid labels
def draw_board():
    for row in range(8):
        for col in range(8):
            if human_color == chess.BLACK:
                actual_row, actual_col = 7 - row, 7 - col
            else:
                actual_row, actual_col = row, col
            color = LIGHT_SQUARE if (actual_row + actual_col) % 2 == 0 else DARK_SQUARE
            pygame.draw.rect(
                screen,
                color,
                (
                    col * SQUARE_SIZE,
                    VERTICAL_MARGIN + row * SQUARE_SIZE,
                    SQUARE_SIZE,
                    SQUARE_SIZE,
                ),
            )

# Draw the pieces on the chessboard
def draw_pieces():
    for row in range(8):
        for col in range(8):
            if human_color == chess.BLACK:
                actual_row, actual_col = 7 - row, 7 - col
            else:
                actual_row, actual_col = row, col
            square = chess.square(actual_col, 7 - actual_row)
            piece = board.piece_at(square)
            if piece:
                piece_str = f"{'w' if piece.color else 'b'}{piece.symbol().lower()}"
                screen.blit(
                    pieces[piece_str],
                    (
                        col * SQUARE_SIZE,
                        VERTICAL_MARGIN + row * SQUARE_SIZE,
                    ),
                )

# Highlight legal moves with dots
def highlight_legal_moves():
    if selected_square is not None:
        for move in board.legal_moves:
            if move.from_square == selected_square:
                to_square = move.to_square
                row, col = divmod(to_square, 8)
                if human_color == chess.BLACK:
                    row, col = 7 - row, 7 - col
                pygame.draw.circle(
                    screen,
                    POSSIBLE_MOVE_COLOR,
                    (
                        col * SQUARE_SIZE + SQUARE_SIZE // 2,
                        VERTICAL_MARGIN + (7 - row) * SQUARE_SIZE + SQUARE_SIZE // 2,
                    ),
                    SQUARE_SIZE // 6,
                )

# Constants for scrolling
SCROLL_SPEED = 30
MOVE_LOG_HEIGHT = SCREEN_HEIGHT

# Draw the move log with scrolling
def draw_move_log(move_log):
    font = pygame.font.SysFont('Comic Sans MS', 24)
    x_offset = BOARD_WIDTH + 20
    y_offset = 20
    line_spacing = 30

    screen.fill((240, 240, 240), (BOARD_WIDTH, 0, SCREEN_WIDTH - BOARD_WIDTH, SCREEN_HEIGHT))

    for index, move in enumerate(move_log):
        if "(Human)" in move:
            move_color = (139, 69, 19)  # Cream color for human moves
        else:
            move_color = (135, 206, 250)  # Sky blue color for AI moves

        move_text = font.render(move, True, move_color)
        screen.blit(move_text, (x_offset, y_offset + index * line_spacing))


# Display winner
def display_winner(winner):
    font = pygame.font.Font(None, 120)
    text = font.render(f"{winner} Wins!", True, (255, 0, 0))
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    exit()

# Main game loop
def main():
    global selected_square, human_color
    running = True
    move_log = []
    move_number = 1  # Start counting moves from 1

    # Display color choice screen
    while human_color is None:
        screen.fill((255, 255, 255))
        font = pygame.font.Font(None, 48)
        white_button = font.render("Play as White", True, (0, 0, 0))
        black_button = font.render("Play as Black", True, (0, 0, 0))
        screen.blit(white_button, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 30))
        screen.blit(black_button, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 30))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if SCREEN_WIDTH // 2 - 100 <= pos[0] <= SCREEN_WIDTH // 2 + 100:
                    if SCREEN_HEIGHT // 2 - 30 <= pos[1] <= SCREEN_HEIGHT // 2:
                        human_color = chess.WHITE
                    elif SCREEN_HEIGHT // 2 + 30 <= pos[1] <= SCREEN_HEIGHT // 2 + 60:
                        human_color = chess.BLACK

    # If human plays black, AI makes the first move
    if human_color == chess.BLACK:
        move = ai_move(board)
        board.push(move)
        move_log.append(f"{move_number}. {move} (Computer)")
        move_number += 1

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if x < BOARD_WIDTH:
                    col, row = x // SQUARE_SIZE, (y - VERTICAL_MARGIN) // SQUARE_SIZE
                    if human_color == chess.BLACK:
                        row, col = 7 - row, 7 - col
                    if 0 <= row < 8:
                        square = chess.square(col, 7 - row)
                        if selected_square is None:
                            if board.piece_at(square) and board.piece_at(square).color == human_color:
                                selected_square = square
                        else:
                            move = chess.Move(selected_square, square)
                            if move in board.legal_moves:
                                board.push(move)
                                move_log.append(f"{move_number}. {move} (Human)")
                                move_number += 1
                                selected_square = None

                                if not board.is_game_over():
                                    move = ai_move(board)
                                    board.push(move)
                                    move_log.append(f"{move_number}. {move} (Computer)")
                                    move_number += 1
                            else:
                                selected_square = None

        screen.fill((255, 255, 255))
        draw_board()
        highlight_legal_moves()
        draw_pieces()
        draw_move_log(move_log)

        if board.is_checkmate():
            winner = "Human" if board.turn != human_color else "Computer"
            display_winner(winner)
        elif board.is_stalemate():
            display_winner("No one (Stalemate)")

        pygame.display.flip()

    engine.quit()
    pygame.quit()

if __name__ == "__main__":
    main()
