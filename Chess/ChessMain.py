import pygame
import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def load_images():
    pieces = ['bB', 'bK', 'bN', 'bP', 'bQ', 'bR', 'wK', 'wN', 'wB', 'wR', 'wQ', 'wP']
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(
            pygame.image.load(f'images/{piece}.png'), (SQ_SIZE, SQ_SIZE)
        )


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    screen.fill(pygame.Color('white'))
    gs = ChessEngine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False
    animate = False
    load_images()
    running = True
    sq_selected = ()
    player_clicks = []
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game_over:
                    location = pygame.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sq_selected == (row, col):
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)
                    if len(player_clicks) == 2:
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        if move in valid_moves:
                            gs.make_move(move)
                            print(move.get_chess_notation())
                            move_made = True
                            animate = True
                            sq_selected = ()
                            player_clicks = []
                        else:
                            player_clicks = [sq_selected]

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    gs.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                elif event.key == pygame.K_r:
                    gs = ChessEngine.GameState()
                    valid_moves = gs.get_valid_moves()
                    move_made = False
                    sq_selected = ()
                    player_clicks = []
                    animate = False
                    game_over = False

        if move_made:
            if animate:
                animate_move(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False

        draw_game_state(screen, gs, valid_moves, sq_selected)

        if gs.checkmate:
            game_over = True
            text = 'Black wins by checkmate' if gs.white_to_move else 'White wins by checkmate'
            draw_text(screen, text)
        elif gs.stalemate:
            game_over = True
            text = 'Stalemate'
            draw_text(screen, text)

        clock.tick(MAX_FPS)
        pygame.display.flip()


def highlight_square(screen, gs, valid_moves, sq_selected):
    if gs.in_check:
        king_pos = gs.white_king_location if gs.white_to_move else gs.black_king_location
        s = pygame.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(pygame.Color('red'))
        screen.blit(s, (king_pos[1] * SQ_SIZE, king_pos[0] * SQ_SIZE))

    if sq_selected:
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'):
            s = pygame.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(pygame.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            s.fill(pygame.Color('yellow'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))


def draw_game_state(screen, gs, valid_moves, sq_selected):
    draw_board(screen)
    highlight_square(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)


def draw_board(screen):
    colors = [pygame.Color('white'), pygame.Color('gray')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            pygame.draw.rect(screen, color, (c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], (c * SQ_SIZE, r * SQ_SIZE))


def animate_move(move, screen, board, clock):
    colors = [pygame.Color('white'), pygame.Color('gray')]
    d_r = move.end_row - move.start_row
    d_c = move.end_col - move.start_col
    frames = 10
    frame_count = (abs(d_r) + abs(d_c)) * frames
    for frame in range(frame_count + 1):
        r = move.start_row + d_r * frame / frame_count
        c = move.start_col + d_c * frame / frame_count
        draw_board(screen)
        draw_pieces(screen, board)
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = pygame.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(screen, color, end_square)
        if move.piece_captured != '--':
            screen.blit(IMAGES[move.piece_captured], end_square)
        screen.blit(IMAGES[move.piece_moved], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        pygame.display.flip()
        clock.tick(60)


def draw_text(screen, text):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(150)
    overlay.fill(pygame.Color('black'))
    screen.blit(overlay, (0, 0))

    font = pygame.font.SysFont('Arial', 32, True, False)
    text_object = font.render(text, True, pygame.Color('white'))

    shadow_offset = 2
    shadow = font.render(text, True, pygame.Color('gray20'))

    text_rect = text_object.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    shadow_rect = shadow.get_rect(center=(WIDTH // 2 + shadow_offset, HEIGHT // 2 + shadow_offset))

    padding = 15
    border_rect = pygame.Rect(text_rect.left - padding, text_rect.top - padding,
                              text_rect.width + 2 * padding, text_rect.height + 2 * padding)

    border_rect.clamp_ip(pygame.Rect(10, 10, WIDTH - 20, HEIGHT - 20))

    pygame.draw.rect(screen, pygame.Color('darkblue'), border_rect)
    pygame.draw.rect(screen, pygame.Color('gold'), border_rect, 3)

    screen.blit(shadow, shadow_rect)
    screen.blit(text_object, text_rect)


if __name__ == '__main__':
    main()