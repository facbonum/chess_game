import pygame
import os
import sys
import random
import time

# Initialize Pygame
pygame.init()

# Constants
BOARD_SIZE = 8
SQUARE_SIZE = 60
WIDTH, HEIGHT = BOARD_SIZE * SQUARE_SIZE, BOARD_SIZE * SQUARE_SIZE
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Colors
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
SELECTED_SQUARE = (0, 255, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

# Set current working directory for running in VSCode
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)

# Load images for pieces and board
def load_images():
    pieces = {}
    piece_names = ["king", "queen", "rook", "bishop", "knight", "pawn"]
    colors = ["white", "black"]
    for color in colors:
        for piece in piece_names:
            image_path = f"assets/pieces/{color}_{piece}.png"
            if os.path.exists(image_path):
                image = pygame.image.load(image_path)
                pieces[f"{color}_{piece}"] = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
            else:
                print(f"Image not found: {image_path}")
    return pieces

# Initialize the chess board
def initialize_board():
    return [
        ['black_rook', 'black_knight', 'black_bishop', 'black_queen', 'black_king', 'black_bishop', 'black_knight', 'black_rook'],
        ['black_pawn'] * 8,
        [None] * 8,
        [None] * 8,
        [None] * 8,
        [None] * 8,
        ['white_pawn'] * 8,
        ['white_rook', 'white_knight', 'white_bishop', 'white_queen', 'white_king', 'white_bishop', 'white_knight', 'white_rook'],
    ]

# Helper to check if position is within board bounds
def is_in_bounds(row, col):
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

# Function to render board and pieces
def render_board(board, pieces, selected_square=None):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            # Alternate square colors
            square_color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            pygame.draw.rect(screen, square_color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            # Highlight selected square
            if selected_square == (row, col):
                pygame.draw.rect(screen, SELECTED_SQUARE, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 5)

            # Render the piece image
            piece = board[row][col]
            if piece:
                screen.blit(pieces[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

# Handle piece movement (basic validation)
def is_valid_move(piece, start, end, board, current_player):
    # Allow movement only for the correct player
    if piece and piece.startswith(current_player):
        return True
    return False

# Handle events like clicking and moving pieces
def handle_events(selected_square, board, current_player, game_mode, cpu_thinking):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if not cpu_thinking:  # Prevent player moves during CPU thinking time
                col, row = event.pos[0] // SQUARE_SIZE, event.pos[1] // SQUARE_SIZE
                if selected_square:
                    if is_valid_move(board[selected_square[0]][selected_square[1]], selected_square, (row, col), board, current_player):
                        piece = board[selected_square[0]][selected_square[1]]
                        board[row][col] = piece
                        board[selected_square[0]][selected_square[1]] = None
                        selected_square = None
                        return selected_square, True  # Move complete, return to allow turn change
                else:
                    selected_square = (row, col)
    return selected_square, False  # No move, still selecting a piece

# Function to display text
def display_text(text, position, font_size=24):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, WHITE)
    screen.blit(text_surface, position)

# Function to display a slider
def display_slider(value, min_value, max_value, position, width):
    slider_rect = pygame.Rect(position[0], position[1], width, 10)
    pygame.draw.rect(screen, WHITE, slider_rect)

    # Draw the current slider position
    slider_position = position[0] + (value - min_value) / (max_value - min_value) * width
    pygame.draw.circle(screen, WHITE, (int(slider_position), position[1] + 5), 10)

    # Display the value
    font = pygame.font.Font(None, 24)
    text_surface = font.render(str(value), True, WHITE)
    screen.blit(text_surface, (slider_position - 20, position[1] - 20))

# Show the game mode menu
def show_menu():
    screen.fill(BLACK)
    display_text("Choose Game Mode:", (WIDTH // 4, HEIGHT // 4))
    display_text("1. Player vs Player", (WIDTH // 4, HEIGHT // 4 + 50))
    display_text("2. Player vs CPU", (WIDTH // 4, HEIGHT // 4 + 100))

    # ELO Slider (adjusted range 50-2500)
    display_text("Set ELO Rating:", (WIDTH // 4, HEIGHT // 4 + 150))
    elo_value = 1200  # Starting ELO for a balanced game
    min_elo, max_elo = 50, 2500  # Elo rating range
    slider_width = 200

    running_slider = True
    while running_slider:
        screen.fill(BLACK)
        display_text("Choose Game Mode:", (WIDTH // 4, HEIGHT // 4))
        display_text("1. Player vs Player", (WIDTH // 4, HEIGHT // 4 + 50))
        display_text("2. Player vs CPU", (WIDTH // 4, HEIGHT // 4 + 100))

        display_text("Set ELO Rating:", (WIDTH // 4, HEIGHT // 4 + 150))
        display_slider(elo_value, min_elo, max_elo, (WIDTH // 4, HEIGHT // 4 + 180), slider_width)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if WIDTH // 4 <= x <= WIDTH // 4 + 200:
                    if HEIGHT // 4 + 50 <= y <= HEIGHT // 4 + 100:
                        return "pvp", elo_value  # Player vs Player
                    if HEIGHT // 4 + 100 <= y <= HEIGHT // 4 + 150:
                        return "cpu", elo_value  # Player vs CPU
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if WIDTH // 4 <= x <= WIDTH // 4 + 200 and HEIGHT // 4 + 150 <= y <= HEIGHT // 4 + 170:
                    elo_value = min_elo + (x - WIDTH // 4) / 200 * (max_elo - min_elo)

# Simple CPU move logic: randomly move a piece
def cpu_move(board, current_player):
    # Find a random piece for the CPU
    possible_moves = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece and piece.startswith(current_player):
                # Check valid moves (could be expanded)
                possible_moves.append((row, col))
    
    # Choose a random piece to move
    if possible_moves:
        start_row, start_col = random.choice(possible_moves)
        # For simplicity, we'll randomly move the piece to an empty square
        empty_squares = [(row, col) for row in range(BOARD_SIZE) for col in range(BOARD_SIZE) if not board[row][col]]
        if empty_squares:
            end_row, end_col = random.choice(empty_squares)
            board[end_row][end_col] = board[start_row][start_col]
            board[start_row][start_col] = None

# Display a countdown timer for CPU's thinking time
def display_cpu_timer(time_left):
    font = pygame.font.Font(None, 36)
    text_surface = font.render(f"CPU Thinking: {int(time_left)}s", True, WHITE)
    screen.blit(text_surface, (WIDTH // 2 - 100, HEIGHT - 50))

# Start the game loop
def start_game():
    pieces = load_images()  # Load the piece images
    board = initialize_board()  # Initialize the board
    selected_square = None
    current_player = 'white'  # White starts

    # Show the menu to choose mode before starting the game
    game_mode, elo_rating = show_menu()
    print(f"Game Mode: {game_mode}, ELO Rating: {elo_rating}")

    clock = pygame.time.Clock()
    cpu_thinking = False
    cpu_think_start_time = 0
    cpu_think_duration = 3  # 3 seconds of CPU thinking time (you can adjust)

    while True:
        screen.fill(BLACK)  # Clear screen

        # Handle events for player move
        selected_square, move_completed = handle_events(selected_square, board, current_player, game_mode, cpu_thinking)

        if move_completed:
            if current_player == 'white':  # White moves
                current_player = 'black'
                cpu_thinking = True  # CPU (black) starts thinking
                cpu_think_start_time = time.time()  # Mark time when CPU starts thinking
            else:
                # CPU's turn (black) - after some delay
                cpu_time_left = cpu_think_duration - (time.time() - cpu_think_start_time)
                if cpu_time_left <= 0:
                    cpu_move(board, current_player)  # CPU (black) makes a move
                    current_player = 'white'  # Switch back to white's turn
                    cpu_thinking = False  # CPU stops thinking
                else:
                    display_cpu_timer(cpu_time_left)  # Show CPU thinking time

        render_board(board, pieces, selected_square)  # Draw the board

        # Display the current player's turn
        display_text(f"{current_player.capitalize()}'s turn", (WIDTH // 4, HEIGHT - 30))

        pygame.display.flip()  # Update the screen
        clock.tick(FPS)  # Limit the frame rate

# Run the game
start_game()
