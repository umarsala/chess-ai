import sys
import pygame
from menu import run_menu
from chess_logic import *
from ai import findBestMove
from config import settings

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

move_sound = pygame.mixer.Sound("sounds/move.wav")  #sfx
capture_sound = pygame.mixer.Sound("sounds/capture.wav") #sfx

move_sound.set_volume(0.5)
capture_sound.set_volume(0.6)

# stores piece images
PIECE_IMAGES = {}
TILE_SIZE = 100 # 8X8 BOARD

BOARD_X = 250
BOARD_Y = 50

WIDTH, HEIGHT = 1600, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CHESS - The Final Gambit")

def setup_game():
    board_state = GameState()
    return screen, board_state

def load_images():
    pieces = ['bP', 'bR', 'bN', 'bB', 'bQ', 'bK','gP', 'gR', 'gN', 'gB', 'gQ', 'gK']  #load piece images stored

    style = settings["style"] # classic/dark/wood

    for piece in pieces:
        path = f"images/{style}/{piece}.png"
        image = pygame.image.load(path).convert_alpha()
        PIECE_IMAGES[piece] = pygame.transform.smoothscale(image, (TILE_SIZE - 10, TILE_SIZE - 10))

def draw_board(screen, board_state):
    colours = [(160, 180, 210), (50, 75, 120)]  # light, dark squares

    for r in range(8):
        for c in range(8):
            colour = colours[(r + c) % 2]
            pygame.draw.rect(screen, colour, (BOARD_X + c * TILE_SIZE, BOARD_Y + r * TILE_SIZE, TILE_SIZE, TILE_SIZE))

            piece = board_state.board[r][c]
            if piece != "--":
                piece_image = PIECE_IMAGES[piece]
                offset = (TILE_SIZE - piece_image.get_width()) // 2
                screen.blit(piece_image, (BOARD_X + c * TILE_SIZE + offset, BOARD_Y + r * TILE_SIZE + offset))

def draw_timers(screen, white_time, black_time, white_to_move): #timers

    FONT = pygame.font.Font("fonts/Cinzel-Bold.ttf", 48) # gothic font

    def format_time(seconds):
        seconds = max(0, int(seconds))
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02}:{secs:02}"

    # Positions
    white_rect = pygame.Rect(1080, 80, 340, 100)
    black_rect = pygame.Rect(1080, 700, 340, 100)

    # Highlight active player
    if white_to_move:
        white_colour = (30, 45, 65)
        black_colour = (60, 90, 150)
    else:
        white_colour = (60, 90, 150)
        black_colour = (35, 45, 65)

    pygame.draw.rect(screen, white_colour, white_rect, border_radius=15)
    pygame.draw.rect(screen, black_colour, black_rect, border_radius=15)

    # Render time text
    white_text = FONT.render(format_time(white_time), True, (255,255,255))
    black_text = FONT.render(format_time(black_time), True, (255,255,255))

    screen.blit(white_text, white_text.get_rect(center=white_rect.center))
    screen.blit(black_text, black_text.get_rect(center=black_rect.center))


def draw_move_log(screen, moveLog, scroll_offset): #move history

    FONT = pygame.font.Font("fonts/Cinzel-Regular.ttf", 24)
    HEADER_FONT = pygame.font.Font("fonts/Cinzel-Bold.ttf", 26)

    panel_x = 1080
    panel_top = 250
    panel_bottom = 650
    panel_width = 380

    # Panel background
    panel_rect = pygame.Rect(panel_x - 20, panel_top - 20,
                             panel_width, panel_bottom - panel_top + 40)
    pygame.draw.rect(screen, (30, 45, 75), panel_rect, border_radius=10)

    title = HEADER_FONT.render("Move History", True, (200, 210, 230))
    screen.blit(title, (panel_x, panel_top))

    white_header = FONT.render("Grey", True, (180, 200, 255))
    black_header = FONT.render("Blue", True, (180, 200, 255))

    screen.blit(white_header, (panel_x + 60, panel_top + 35))
    screen.blit(black_header, (panel_x + 210, panel_top + 35))

    pygame.draw.line(screen, (60, 80, 120), (panel_x, panel_top + 60), (panel_x + 340, panel_top + 60), 2)

    moves_area = pygame.Rect(panel_x, panel_top + 65, 340, panel_bottom - (panel_top + 65))

    screen.set_clip(moves_area)

    line_height = 26
    y_start = panel_top + 70

    move_rows = []

    for i in range(0, len(moveLog), 2):
        move_number = i // 2 + 1
        white_move = moveLog[i].getChessNotation()

        if i + 1 < len(moveLog):
            black_move = moveLog[i + 1].getChessNotation()
        else:
            black_move = ""

        move_rows.append((move_number, white_move, black_move))

    total_rows = len(move_rows)
    max_visible = (panel_bottom - y_start) // line_height
    max_scroll = max(0, total_rows - max_visible)

    scroll_offset = max(0, min(scroll_offset, max_scroll))

    start_index = total_rows - max_visible - scroll_offset
    if start_index < 0:
        start_index = 0

    visible_rows = move_rows[start_index:start_index + max_visible]

    y = y_start

    for number, white_move, black_move in visible_rows:
        number_text = FONT.render(f"{number}.", True, (220, 220, 220))
        white_text = FONT.render(white_move, True, (255, 255, 255))
        black_text = FONT.render(black_move, True, (255, 255, 255))

        screen.blit(number_text, (panel_x, y))
        screen.blit(white_text, (panel_x + 60, y))
        screen.blit(black_text, (panel_x + 210, y))

        y += line_height

    # Reset clipping
    screen.set_clip(None)

    return scroll_offset

def highlight_squares(screen, board_state, selected_square, valid_moves):  #highlight square for pieces
    if selected_square != ():
        row, col = selected_square

        if board_state.board[row][col][0] == ('g' if board_state.whiteToMove else 'b'):

            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            s.set_alpha(100)
            s.fill((100, 200, 255))

            screen.blit(s, (BOARD_X + col * TILE_SIZE, BOARD_Y + row * TILE_SIZE))

            s.fill((200, 200, 100))
            for move in valid_moves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(s, (BOARD_X + move.endCol * TILE_SIZE,
                                    BOARD_Y + move.endRow * TILE_SIZE))
   
def highlight_check(screen, board_state): #check function red square
    king_row, king_col = board_state.findKingPosition(board_state.whiteToMove)

    if board_state.squareUnderAttack(king_row, king_col):
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        s.set_alpha(120)
        s.fill((200, 50, 50))

        screen.blit(s, (BOARD_X + king_col * TILE_SIZE,
                        BOARD_Y + king_row * TILE_SIZE))
        
def draw_game_over(screen, result_text):
    WIDTH, HEIGHT = 1600, 900

    # screen overlady
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)  # transparency
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    TITLE_FONT = pygame.font.Font("fonts/Cinzel-Bold.ttf", 70)
    BUTTON_FONT = pygame.font.Font("fonts/Cinzel-Regular.ttf", 36)
    
    text_surface = TITLE_FONT.render(result_text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
    screen.blit(text_surface, text_rect)
    
    button_width = 320
    button_height = 85
    button_rect = pygame.Rect(WIDTH // 2 - button_width // 2,HEIGHT // 2 + 30, button_width, button_height)
    mouse_pos = pygame.mouse.get_pos()
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, (85, 120, 200), button_rect, border_radius=15)
    else:
        pygame.draw.rect(screen, (65, 100, 170), button_rect, border_radius=15)

    button_text = BUTTON_FONT.render("Return to Menu", True, (255, 255, 255))
    text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, button_text.get_rect(center=button_rect.center))

    return button_rect

def draw_pause_menu(screen):  #pause menu

    WIDTH, HEIGHT = 1600, 900

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    FONT = pygame.font.Font("fonts/Cinzel-Bold.ttf", 60)
    BUTTON_FONT = pygame.font.Font("fonts/Cinzel-Regular.ttf", 36)

    title = FONT.render("Game Paused", True, (255,255,255))
    screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 120)))

    buttons = ["Resume", "Restart", "Return to Menu"]
    actions = ["resume", "restart", "menu"]

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    for i, text in enumerate(buttons):

        rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 20 + i*100, 400, 70)

        if rect.collidepoint(mouse):
            pygame.draw.rect(screen, (85,120,200), rect, border_radius=15)
            if click[0]:
                return actions[i]
        else:
            pygame.draw.rect(screen, (65,100,170), rect, border_radius=15)

        txt = BUTTON_FONT.render(text, True, (255,255,255))
        screen.blit(txt, txt.get_rect(center=rect.center))

    return None

def draw_pause_icon(screen): #pause buttn

    rect = pygame.Rect(20, 20, 60, 60)

    mouse = pygame.mouse.get_pos()

    if rect.collidepoint(mouse):
        pygame.draw.rect(screen, (90,120,200), rect, border_radius=10)
    else:
        pygame.draw.rect(screen, (60,90,160), rect, border_radius=10)

    # draw pause bars
    pygame.draw.rect(screen, (255,255,255), (35, 30, 8, 40))
    pygame.draw.rect(screen, (255,255,255), (55, 30, 8, 40))

    return rect

def show_promotion_menu(screen, colour): #prmotion menu

    WIDTH, HEIGHT = 1600, 900

    pieces = ["Q", "R", "B", "N"]
    rects = []

    while True:

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        FONT = pygame.font.Font("fonts/Cinzel-Bold.ttf", 50)

        title = FONT.render("Choose Promotion", True, (255,255,255))
        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 150)))

        mouse_pos = pygame.mouse.get_pos()
        rects.clear()

        for i, piece in enumerate(pieces):
            rect = pygame.Rect(WIDTH//2 - 200 + i*110, HEIGHT//2 - 50, 90, 90)
            rects.append(rect)

            # Hover effect
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (120,150,220), rect, border_radius=10)
            else:
                pygame.draw.rect(screen, (80,110,180), rect, border_radius=10)

            piece_code = colour + piece
            image = PIECE_IMAGES[piece_code]
            offset = (90 - image.get_width()) // 2
            screen.blit(image, (rect.x + offset, rect.y + offset))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(rects):
                    if rect.collidepoint(event.pos):
                        return pieces[i]

def game_loop(screen, board_state, mode):   #main game function
    paused = False
    ai_pending = False
    ai_move_ready = False   
    ai_think_start = 0
    running = True
    white_time = mode["time"] * 60
    black_time = mode["time"] * 60
    
    AI_THINK_TIME = 0
    if mode["mode"] == "single":
        difficulty = mode.get("difficulty", "easy")
        if difficulty == "easy":
            AI_THINK_TIME = 0.3
        elif difficulty == "medium":
            AI_THINK_TIME = 0.3
        elif difficulty == "hard":
            AI_THINK_TIME = 0.4

    clock = pygame.time.Clock()
    game_over = False
    game_result = ""

    selected_square = ()
    player_clicks = []
    valid_moves = board_state.getValidMoves()
    move_scroll_offset = 0

    while running:
        dt = clock.tick(60) / 1000
        if not game_over:
            if board_state.whiteToMove:
                black_time -= dt # checks to see if time has run out
                if black_time <= 0:
                    black_time = 0
                    game_over = True
                    game_result = "Blue wins on time!"
            else:
                white_time -= dt  # checks to see if time has run out
                if white_time <= 0:
                    white_time = 0
                    game_over = True
                    game_result = "Grey wins on time!"
        white_time = max(0, white_time)
        black_time = max(0, black_time) 

        screen.fill((0, 0, 0))
        panel_rect = pygame.Rect(1050, 50, 450, 800)
        pygame.draw.rect(screen, (25, 35, 55), panel_rect, border_radius=15)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused

            if event.type == pygame.MOUSEWHEEL:
                move_scroll_offset += event.y * 1
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pause_rect.collidepoint(event.pos):
                    paused = True

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_over:
                    if button_rect.collidepoint(event.pos):
                        return
                    continue
                
                mouse_x, mouse_y = pygame.mouse.get_pos()

                if BOARD_X <= mouse_x <= BOARD_X + 800 and BOARD_Y <= mouse_y <= BOARD_Y + 800:
                    col = (mouse_x - BOARD_X) // TILE_SIZE
                    row = (mouse_y - BOARD_Y) // TILE_SIZE

                    if selected_square == (row, col):
                        selected_square = ()
                        player_clicks = []
                    else:
                        selected_square = (row, col)
                        player_clicks.append(selected_square)

                    if len(player_clicks) == 2:
                        move = Move(player_clicks[0], player_clicks[1], board_state.board)
                    

                        for valid_move in valid_moves:
                            if move == valid_move:
                                board_state.makeMove(valid_move, realMove=True)

                                if valid_move.isPromotion:
                                    promotion_piece = show_promotion_menu(screen, valid_move.pieceMoved[0])
                                    board_state.applyPromotion(valid_move, promotion_piece)

                                if mode["mode"] == "single":
                                    ai_pending = True

                                if valid_move.pieceCaptured != "--":
                                    capture_sound.play()
                                else:
                                    move_sound.play()

                                valid_moves = board_state.getValidMoves()
                                
                    
                                # Checkmate / Stalemate
                                if len(valid_moves) == 0:
                                    if board_state.inCheck():
                                        game_over = True
                                        if board_state.whiteToMove:
                                            game_result = "Blue wins by checkmate!"
                                        else:
                                            game_result = "Grey wins by checkmate!"
                                    else:
                                        game_over = True
                                        game_result = "Draw by stalemate!" 

                                elif board_state.fiftyMoveRuleReached():
                                    game_over = True
                                    game_result = "Draw by fifty-move rule!"
                                
                                elif board_state.threefoldRepetition():
                                    game_over = True
                                    game_result = "Draw by threefold repetition!"

                                selected_square = ()
                                player_clicks = []
                                break
                        if selected_square != ():
                            player_clicks = [selected_square]
        
        if paused:
            action = draw_pause_menu(screen)
            if action == "resume":
                paused = False
            elif action == "restart":
                return "restart"
            elif action == "menu":
                return
            pygame.display.flip()
            continue

        if not game_over and mode["mode"] == "single":
            if ai_pending:
                ai_pending = False
                ai_think_start = pygame.time.get_ticks() / 1000
            elif not board_state.whiteToMove:
                current_time = pygame.time.get_ticks() / 1000
                elapsed = current_time - ai_think_start
                if elapsed >= AI_THINK_TIME and not ai_move_ready:
                    ai_move = findBestMove(board_state, mode["difficulty"])
                    ai_move_ready = True
                    
                if ai_move_ready:
                    if ai_move:
                        board_state.makeMove(ai_move)
                        if ai_move.pieceCaptured != "--":
                            capture_sound.play()
                        else:
                            move_sound.play()
                        valid_moves = board_state.getValidMoves()
            
                    selected_square = ()
                    player_clicks = []
                    ai_pending = True
                    ai_move_ready = False

        draw_board(screen, board_state)
        highlight_squares(screen, board_state, selected_square, valid_moves)#
        highlight_check(screen, board_state)
        draw_timers(screen, white_time, black_time, board_state.whiteToMove)
        move_scroll_offset = draw_move_log(screen, board_state.moveLog, move_scroll_offset)
        pause_rect = draw_pause_icon(screen)

        if game_over:
            button_rect = draw_game_over(screen, game_result)
        pygame.display.flip()
    
    pygame.quit()
    

if __name__ == "__main__":
    while True:
        mode = run_menu(screen, WIDTH, HEIGHT)

        if isinstance(mode, dict):
            if mode["mode"] == "single":
                print("Difficulty:", mode["difficulty"])
                print("Time:", mode["time"])
            
            if mode["mode"] == "two":
                print("Time:", mode["time"])
            
            while True:
                
                screen, board_state = setup_game()
                load_images()
                result = game_loop(screen, board_state, mode)
                if result == "restart":
                    continue
                break
            
        elif mode == "quit":
            pygame.quit()
            sys.exit()


        
