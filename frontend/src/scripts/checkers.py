# import modules
from js import document
from pyodide.ffi import create_proxy

# global variables
selected_piece = None
current_player = "b"
is_consecutive_jump = False
event_listener_proxies = []


# function to handle cell click
def cell_click_handler(event):
    global selected_piece, current_player, is_consecutive_jump
    cell = event.currentTarget
    piece = cell.querySelector('.piece')

    # check if the cell is highlighted
    if 'highlight' in cell.classList:
        # move the piece
        move_piece(selected_piece, cell)

    # check if the cell has a piece of the current player    
    elif piece and f'piece-{current_player}' in piece.className and not is_consecutive_jump:
        # clear highlights and highlight the moves
        clear_highlights()
        selected_piece = cell
        highlight_moves(cell)


# function to move the piece
def move_piece(from_cell, to_cell):
    global current_player, is_consecutive_jump, selected_piece
    piece = from_cell.querySelector('.piece')
    to_cell.appendChild(piece.cloneNode(True))
    from_cell.innerHTML = ''
    row_diff = abs(int(to_cell.id.split('-')[1]) - int(from_cell.id.split('-')[1]))

    # check if the piece should be kinged
    to_row = int(to_cell.id.split('-')[1])
    if (current_player == 'b' and to_row == 7) or (current_player == 'r' and to_row == 0):
        to_cell.querySelector('.piece').classList.add('king')
        to_cell.querySelector('.piece').innerHTML = '<span class="king-mark">&#9813;</span>'

    # check if the piece should be removed
    if row_diff == 2:
        remove_jumped_piece(from_cell, to_cell)
        # check if the piece has additional jumps
        if has_additional_jumps(to_cell, current_player):
            is_consecutive_jump = True
            selected_piece = to_cell
            clear_highlights()
            highlight_moves(to_cell, jumps_only=True)
            return

    # end the turn
    end_turn()


# function to remove the jumped piece
def remove_jumped_piece(start_cell, end_cell):
    start_row, start_col = map(int, start_cell.id.split('-')[1:])
    end_row, end_col = map(int, end_cell.id.split('-')[1:])
    mid_row, mid_col = (start_row + end_row) // 2, (start_col + end_col) // 2
    jumped_cell = document.getElementById(f'cell-{mid_row}-{mid_col}')
    jumped_cell.innerHTML = ''

# function to check if the piece has additional jumps
def has_additional_jumps(cell, player):
    row, col = map(int, cell.id.split('-')[1:])
    piece = cell.querySelector('.piece')
    is_king = 'king' in piece.classList
    enemy = 'b' if player == 'r' else 'r'
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] if is_king else \
                 [(-1, -1), (-1, 1)] if player == 'r' else [(1, -1), (1, 1)]

    # loop through the directions to check for jumps
    for dr, dc in directions:
        adj_row, adj_col = row + dr, col + dc
        # check if the adjacent cell has an enemy piece
        if 0 <= adj_row < 8 and 0 <= adj_col < 8:
            # get the adjacent cell and the adjacent piece
            adj_cell = document.getElementById(f'cell-{adj_row}-{adj_col}')
            adj_piece = adj_cell.querySelector('.piece')
            # check if the adjacent piece is an enemy piece
            if adj_piece and f'piece-{enemy}' in adj_piece.className:
                jump_row, jump_col = adj_row + dr, adj_col + dc
                # check if the jump cell is empty
                if 0 <= jump_row < 8 and 0 <= jump_col < 8:
                    jump_cell = document.getElementById(f'cell-{jump_row}-{jump_col}')
                    if not jump_cell.querySelector('.piece'):
                        # highlight the jump cell
                        return True
                    
    # return false if no additional jumps are found
    return False
 

# function to highlight the moves
def highlight_moves(cell, jumps_only=False):
    row, col = map(int, cell.id.split('-')[1:])
    piece = cell.querySelector('.piece')
    # return if the cell is empty
    if not piece: return

    # get the piece details
    is_king = 'king' in piece.classList
    enemy = 'b' if current_player == 'r' else 'r'
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] if is_king else \
                 [(-1, -1), (-1, 1)] if current_player == 'r' else [(1, -1), (1, 1)]

    # loop through the directions to highlight the moves
    for dr, dc in directions:
        new_r, new_c = row + dr, col + dc
        # check if the new cell is within the board
        if 0 <= new_r < 8 and 0 <= new_c < 8:
            target_cell = document.getElementById(f'cell-{new_r}-{new_c}')
            # highlight the cell if it is empty
            if not target_cell.querySelector('.piece') and not jumps_only:
                target_cell.classList.add('highlight')
            # check if the cell has an enemy piece
            else:
                adj_piece = target_cell.querySelector('.piece')
                # check if the adjacent piece is an enemy piece
                if adj_piece and f'piece-{enemy}' in adj_piece.className:
                    jump_r, jump_c = new_r + dr, new_c + dc
                    # check if the jump cell is empty
                    if 0 <= jump_r < 8 and 0 <= jump_c < 8:
                        jump_cell = document.getElementById(f'cell-{jump_r}-{jump_c}')
                        if not jump_cell.querySelector('.piece'):
                            # highlight the jump cell
                            jump_cell.classList.add('highlight')


# function to update and display the current player
def update_current_player_display():
    current_player_element = document.getElementById('current-player')
    player_name = 'Black' if current_player == 'b' else 'Red'
    color = 'black' if current_player == 'b' else 'red'
    current_player_element.innerHTML = f"Current Player: <span style='color: {color};'>{player_name}</span>"


# function to check for win
def check_for_win():
    black_pieces = document.querySelectorAll('.piece-b')
    red_pieces = document.querySelectorAll('.piece-r')
    # check if one of the players has no pieces left
    if len(black_pieces) == 0:
        display_winner('Red')
    elif len(red_pieces) == 0:
        display_winner('Black')


# function to display the winner
def display_winner(winner):
    message = f"{winner} Wins!"
    # create or update a div element to show the winning message
    winner_element = document.getElementById('winner-message')
    if not winner_element:
        winner_element = document.createElement('div')
        winner_element.id = 'winner-message'
        document.body.appendChild(winner_element)
    winner_element.innerText = message
    winner_element.style.display = 'block'

    # set the color of the message based on the winner
    winner_color = 'red' if winner == 'Red' else 'black'
    winner_element.style.color = winner_color


# function to clear the highlights
def clear_highlights():
    # loop through the highlighted cells and remove the highlight
    for cell in document.querySelectorAll('.highlight'):
        cell.classList.remove('highlight')


# function to end the turn
def end_turn():
    global is_consecutive_jump, selected_piece, current_player
    # manage flags and update the current player
    is_consecutive_jump = False
    selected_piece = None
    clear_highlights()
    current_player = 'r' if current_player == 'b' else 'b'
    update_current_player_display()
    check_for_win() 


# function to create the board
def create_board():
    board_html = ''
    for row in range(8):
        for col in range(8):
            cell_class = 'white' if (row + col) % 2 == 0 else 'black'
            piece = ''
            if cell_class == 'black':
                if row < 3:
                    piece = '<div class="piece piece-b"></div>'
                elif row > 4:
                    piece = '<div class="piece piece-r"></div>'
            board_html += f'<div id="cell-{row}-{col}" class="cell {cell_class}">{piece}</div>'

    return board_html


# function to attach event listeners
def attach_event_listeners():
    global event_listener_proxies
    cells = document.querySelectorAll('.cell')
    for proxy in event_listener_proxies:
        proxy.destroy()
    event_listener_proxies.clear()
    for cell in cells:
        proxy = create_proxy(cell_click_handler)
        event_listener_proxies.append(proxy)
        cell.addEventListener('click', proxy)


# function to initialize the game
def initialize():
    board_element = document.getElementById('checkers-board')
    board_element.innerHTML = create_board()
    attach_event_listeners()
