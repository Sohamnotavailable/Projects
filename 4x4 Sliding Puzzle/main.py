import turtle
import random
import time
import sys
import json
import math

## Global variables and constants
BOARD_SIZE = 4
TILE_SIZE = 80
FONT_SIZE = 24
## Screen width/height is managed by fullscreen setup

## Colour Pallete used throughout the game
BLANK_TILE_COLOR = "lightgray"
DEFAULT_TILE_COLOR = "#74C69D"
CORRECT_POSITION_COLOR = "#00B295"
TEXT_COLOR = "white"
PEN_COLOR = "darkgray"
MENU_BUTTON_COLOR = "#74C69D"
MENU_TEXT_COLOR = "white"
BACKGROUND_COLOR = "#F0F0F0"
HUD_TEXT_COLOR = "#333333"

## File Path
LEADERBOARD_FILE = "puzzle_leaderboard.json"
SAVE_GAME_FILE = "save_game.json"
MAX_LEADERBOARD_ENTRIES = 3

## This manages the state of The Game (which you just lost btw :) )
board = []
move_history = []
game_start_time = 0
move_count = 0
current_difficulty = "N/A"
game_state = "main_menu" # This includes: main_menu, in_game, game_over, leaderboard, history_view
is_timer_running = False

## The end state of the board required to win
TARGET_BOARD = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, 0]
]

leaderboard = []

## Some constants used in menu button
BUTTON_WIDTH = 240
BUTTON_HEIGHT = 50
BUTTON_Y_START = 100
BUTTON_Y_SPACING = 70

## Utility Functions
def manhattan_distance(current_board):
    #This is typically used to asses the difficulty of the game
    distance = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            tile_value = current_board[r][c]
            if tile_value == 0: continue
            target_r, target_c = divmod(tile_value - 1, BOARD_SIZE)
            distance += abs(r - target_r) + abs(c - target_c)
    return distance

def assess_difficulty(numbers_flat_with_zero_at_end):
    inversions = 0
    numbers_for_inv = [n for n in numbers_flat_with_zero_at_end if n != 0]
    for i in range(len(numbers_for_inv)):
        for j in range(i + 1, len(numbers_for_inv)):
            if numbers_for_inv[i] > numbers_for_inv[j]:
                inversions += 1
    temp_board = [numbers_flat_with_zero_at_end[i:i+BOARD_SIZE] for i in range(0, len(numbers_flat_with_zero_at_end), BOARD_SIZE)]
    manhattan_dist = manhattan_distance(temp_board)
    difficulty_score = inversions + manhattan_dist
    if difficulty_score < 40: return "Easy"
    elif difficulty_score < 70: return "Medium"
    else: return "Difficult"

## Functions used in drawing
def draw_button(y, text, pen):
    x = -BUTTON_WIDTH / 2
    pen.penup()
    pen.goto(x, y)
    pen.color(MENU_BUTTON_COLOR)
    pen.begin_fill()
    for _ in range(2):
        pen.forward(BUTTON_WIDTH)
        pen.left(90)
        pen.forward(BUTTON_HEIGHT)
        pen.left(90)
    pen.end_fill()
    pen.goto(x + BUTTON_WIDTH / 2, y + (BUTTON_HEIGHT - FONT_SIZE) / 2 - 5)
    pen.color(MENU_TEXT_COLOR)
    pen.write(text, align="center", font=("Arial", FONT_SIZE, "bold"))

def draw_tile(x, y, number, row, col, pen):
    pen.penup()
    pen.goto(x, y)
    pen.pendown()
    if number == 0:
        pen.fillcolor(BLANK_TILE_COLOR)
    elif TARGET_BOARD[row][col] == number:
        pen.fillcolor(CORRECT_POSITION_COLOR)
    else:
        pen.fillcolor(DEFAULT_TILE_COLOR)
    pen.begin_fill()
    for _ in range(4):
        pen.forward(TILE_SIZE)
        pen.right(90)
    pen.end_fill()
    if number != 0:
        pen.penup()
        pen.goto(x + TILE_SIZE / 2, y - TILE_SIZE + (TILE_SIZE - FONT_SIZE) / 2)
        pen.color(TEXT_COLOR)
        pen.write(str(number), align="center", font=("Arial", FONT_SIZE, "bold"))

def draw_game_hud():
    hud_pen.clear()
    
    elapsed_time = int(time.time() - game_start_time)
    minutes, seconds = divmod(elapsed_time, 60)
    time_str = f"Time: {minutes:02d}:{seconds:02d}"
    
    hud_pen.penup()
    hud_pen.goto(-200, screen.window_height() / 2 - 60)
    hud_pen.write(f"Moves: {move_count}", align="center", font=("Arial", 18, "bold"))
    hud_pen.goto(0, screen.window_height() / 2 - 60)
    hud_pen.write(time_str, align="center", font=("Arial", 18, "bold"))
    hud_pen.goto(200, screen.window_height() / 2 - 60)
    hud_pen.write(f"Difficulty: {current_difficulty}", align="center", font=("Arial", 18, "bold"))

def draw_board(current_board, pen):
    pen.clear()
    pen.speed(0)
    pen.hideturtle()
    
    draw_game_hud()
    
    pen.pencolor(PEN_COLOR)
    pen.pensize(2)
    board_top_left_x = - (BOARD_SIZE * TILE_SIZE) / 2
    board_top_left_y = (BOARD_SIZE * TILE_SIZE) / 2 - 50 
    
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            x = board_top_left_x + col * TILE_SIZE
            y = board_top_left_y - row * TILE_SIZE
            draw_tile(x, y, current_board[row][col], row, col, pen)
            
    pen.penup()
    board_bottom_y = board_top_left_y - (BOARD_SIZE * TILE_SIZE)
    instruction_y_pos = board_bottom_y - 40
    
    pen.goto(0, instruction_y_pos)
    pen.color(PEN_COLOR)
    pen.write("Press 'p' to Save  |  'm' for Menu  |  'h' for History", 
              align="center", 
              font=("Arial", 14, "italic"))

def draw_move_history_overlay():
    pen.clear()
    
    box_width = BOARD_SIZE * TILE_SIZE + 20
    box_height = BOARD_SIZE * TILE_SIZE + 20
    top_left_x = -box_width / 2
    top_left_y = box_height / 2 - 50

    pen.penup()
    pen.goto(top_left_x, top_left_y)
    pen.color(BACKGROUND_COLOR)
    pen.begin_fill()
    for _ in range(2):
        pen.forward(box_width)
        pen.left(90)
        pen.forward(box_height)
        pen.left(90)
    pen.end_fill()
    
    pen.goto(0, top_left_y - 40)
    pen.color(HUD_TEXT_COLOR)
    pen.write("Move History", align="center", font=("Arial", 24, "bold"))
    
    if not move_history:
        pen.goto(0, 0)
        pen.write("No moves made yet.", align="center", font=("Arial", 18, "normal"))
    else:
        y_pos = top_left_y - 90
        for i, move in enumerate(reversed(move_history[-12:])):
            _, _, tile_value = move
            move_number = move_count - i
            pen.goto(0, y_pos)
            pen.write(f"Move {move_number}: Tile {tile_value} moved", align="center", font=("Arial", 16, "normal"))
            y_pos -= 25

    pen.goto(0, top_left_y - box_height - 10)
    pen.color("blue")
    pen.write("Press 'h' to return to the game", align="center", font=("Arial", 14, "italic"))
    screen.update()

## Generating the board
def generate_solvable_board():
    numbers = list(range(1, BOARD_SIZE * BOARD_SIZE))
    random.shuffle(numbers)
   # This one makes the board solvable
    inversions = 0
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if numbers[i] > numbers[j]:
                inversions += 1
    if inversions % 2 != 0:
        numbers[0], numbers[1] = numbers[1], numbers[0]
    numbers.append(0)
    
    global current_difficulty
    current_difficulty = assess_difficulty(numbers)
    return [numbers[i:i+BOARD_SIZE] for i in range(0, len(numbers), BOARD_SIZE)]

## Game Logic
def get_blank_position(current_board):
    for r, row in enumerate(current_board):
        for c, val in enumerate(row):
            if val == 0: return r, c
    return -1, -1

def is_valid_move(row, col):
    blank_r, blank_c = get_blank_position(board)
    return (abs(row - blank_r) == 1 and col == blank_c) or \
           (abs(col - blank_c) == 1 and row == blank_r)

def make_move(tile_r, tile_c):
    global board, move_count, move_history
    if is_valid_move(tile_r, tile_c):
        blank_r, blank_c = get_blank_position(board)
        move_history.append((tile_r, tile_c, board[tile_r][tile_c]))
        board[blank_r][blank_c], board[tile_r][tile_c] = board[tile_r][tile_c], 0
        move_count += 1
        draw_board(board, pen)
        screen.update()
        if check_success():
            display_success()
        return True
    return False

def check_success():
    return board == TARGET_BOARD

##Screen and Menu drawing Functions
def display_message(title, line1, line2, line3, pen):
    pen.clear()
    hud_pen.clear()
    pen.penup()
    pen.goto(0, 150)
    pen.color("green" if "CONGRATULATIONS" in title else PEN_COLOR)
    pen.write(title, align="center", font=("Arial", 40, "bold"))
    pen.color(PEN_COLOR)
    pen.goto(0, 50)
    pen.write(line1, align="center", font=("Arial", 24, "normal"))
    pen.goto(0, 0)
    pen.write(line2, align="center", font=("Arial", 24, "normal"))
    pen.goto(0, -50)
    pen.write(line3, align="center", font=("Arial", 24, "normal"))
    pen.goto(0, -150)
    pen.write("Press 'm' for Main Menu", align="center", font=("Arial", 18, "normal"))
    screen.update()

def display_success():
    global game_state, is_timer_running
    game_state = "game_over"
    is_timer_running = False
    elapsed_time = int(time.time() - game_start_time)
    minutes, seconds = divmod(elapsed_time, 60)
    add_to_leaderboard(move_count, elapsed_time, current_difficulty)
    save_leaderboard()
    display_message("CONGRATULATIONS!", f"You solved it in {move_count} moves!", f"Time: {minutes:02d}:{seconds:02d}", f"Difficulty: {current_difficulty}", pen)
    screen.listen()

def show_leaderboard():
    global game_state
    game_state = "leaderboard"
    load_leaderboard()
    pen.clear()
    pen.penup()
    screen_height = screen.window_height()
    pen.goto(0, screen_height / 2 - 70)
    pen.color(PEN_COLOR)
    pen.write("--- LEADERBOARD ---", align="center", font=("Arial", 30, "bold"))
    if not leaderboard:
        pen.goto(0, 0)
        pen.write("No scores yet!", align="center", font=("Arial", 20, "normal"))
    else:
        y_offset = screen_height / 2 - 150
        for i, entry in enumerate(leaderboard):
            pen.goto(-250, y_offset)
            pen.color("blue" if i == 0 else "black")
            pen.write(f"{i+1}. {entry['name']}", align="left", font=("Arial", 18, "bold"))
            pen.goto(250, y_offset)
            pen.write(f"Moves: {entry['moves']}, Time: {int(entry['time_taken']/60):02d}:{int(entry['time_taken']%60):02d}", align="right", font=("Arial", 16, "normal"))
            y_offset -= 50
    draw_button(-screen_height / 2 + 50, "Back to Menu", pen)
    screen.update()

def draw_main_menu():
    global game_state, is_timer_running
    game_state = "main_menu"
    is_timer_running = False
    pen.clear()
    hud_pen.clear()
    pen.penup()
    pen.goto(0, 180)
    pen.color(PEN_COLOR)
    pen.write("15 Puzzle", align="center", font=("Arial", 40, "bold"))
    draw_button(BUTTON_Y_START, "Start New Game", pen)
    draw_button(BUTTON_Y_START - BUTTON_Y_SPACING, "Load Game", pen)
    draw_button(BUTTON_Y_START - 2 * BUTTON_Y_SPACING, "Leaderboard", pen)
    draw_button(BUTTON_Y_START - 3 * BUTTON_Y_SPACING, "Exit", pen)
    screen.update()

## Save and Load functions
def save_current_game():
    if game_state != "in_game": return
    elapsed_time = time.time() - game_start_time
    save_data = { "board": board, "move_count": move_count, "elapsed_time": elapsed_time, "move_history": move_history, "difficulty": current_difficulty }
    try:
        with open(SAVE_GAME_FILE, "w") as f:
            json.dump(save_data, f, indent=4)
        pen.penup()
        pen.goto(0, -screen.window_height()/2 + 40)
        pen.color("blue")
        pen.write("Game Saved!", align="center", font=("Arial", 16, "bold"))
        screen.update()
        time.sleep(1)
        draw_board(board, pen)
        screen.update()
    except IOError as e:
        print(f"Error saving game: {e}")

def load_previous_game():
    global board, move_count, game_start_time, move_history, current_difficulty, game_state
    try:
        with open(SAVE_GAME_FILE, "r") as f:
            save_data = json.load(f)
        board = save_data["board"]
        move_count = save_data["move_count"]
        elapsed_time = save_data["elapsed_time"]
        move_history = save_data["move_history"]
        current_difficulty = save_data["difficulty"]
        game_start_time = time.time() - elapsed_time
        start_game_timer()
        game_state = "in_game"
        draw_board(board, pen)
        screen.update()
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pen.penup()
        pen.goto(0, -220)
        pen.color("red")
        pen.write("No saved game found or data is corrupt!", align="center", font=("Arial", 14, "normal"))
        screen.update()
        time.sleep(2)
        draw_main_menu()

## Leaderboard Functions
def load_leaderboard():
    global leaderboard
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            leaderboard = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        leaderboard = []

def save_leaderboard():
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(leaderboard, f, indent=4)
    except IOError:
        print("Error saving leaderboard.")

#This one does something   Or does it? *Vsauce music intensifies*
def add_to_leaderboard(moves, time_taken, difficulty):
    global leaderboard
    player_name = screen.textinput("New High Score!", f"Enter your name (Moves: {moves}, Time: {time_taken}s)")
    if player_name:
        leaderboard.append({"name": player_name, "moves": moves, "time_taken": time_taken, "difficulty": difficulty})
        leaderboard.sort(key=lambda x: (x['moves'], x['time_taken']))
        leaderboard = leaderboard[:MAX_LEADERBOARD_ENTRIES]

##Game Setup
def start_new_game():
    global board, game_start_time, move_count, move_history, game_state
    board = generate_solvable_board()
    move_count = 0
    move_history = []
    game_start_time = time.time()
    game_state = "in_game"
    start_game_timer()
    draw_board(board, pen)
    screen.update()

## Try and Except block to prevent a crash on exit ##
def update_timer():
    if not is_timer_running:
        return # Stop the timer loop if the flag is false

    try:
        draw_game_hud()
        screen.ontimer(update_timer, 1000) # Reschedule self
    except (turtle.Terminator, turtle.TurtleGraphicsError):
        # This error can occur if the window is closed while the timer is still pending
        # With this, we can safely ignore it and let the app exit
        pass

def start_game_timer():
    global is_timer_running
    if not is_timer_running:
        is_timer_running = True
        update_timer()

##Event Handlers 
def handle_game_click(x, y):
    if game_state != "in_game": return
    screen.onclick(None)
    board_top_left_x = - (BOARD_SIZE * TILE_SIZE) / 2
    board_top_left_y = (BOARD_SIZE * TILE_SIZE) / 2 - 50
    col = int((x - board_top_left_x) // TILE_SIZE)
    row = int((board_top_left_y - y) // TILE_SIZE)
    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and board[row][col] != 0:
        make_move(row, col)
    screen.onclick(redirect_click)

def handle_menu_click(x, y):
    if -BUTTON_WIDTH/2 < x < BUTTON_WIDTH/2 and BUTTON_Y_START < y < BUTTON_Y_START + BUTTON_HEIGHT:
        start_new_game()
    elif -BUTTON_WIDTH/2 < x < BUTTON_WIDTH/2 and BUTTON_Y_START - BUTTON_Y_SPACING < y < BUTTON_Y_START - BUTTON_Y_SPACING + BUTTON_HEIGHT:
        load_previous_game()
    elif -BUTTON_WIDTH/2 < x < BUTTON_WIDTH/2 and BUTTON_Y_START - 2*BUTTON_Y_SPACING < y < BUTTON_Y_START - 2*BUTTON_Y_SPACING + BUTTON_HEIGHT:
        show_leaderboard()
    elif -BUTTON_WIDTH/2 < x < BUTTON_WIDTH/2 and BUTTON_Y_START - 3*BUTTON_Y_SPACING < y < BUTTON_Y_START - 3*BUTTON_Y_SPACING + BUTTON_HEIGHT:
        turtle.bye()

def handle_leaderboard_click(x, y):
    screen_height = screen.window_height()
    if -BUTTON_WIDTH/2 < x < BUTTON_WIDTH/2 and -screen_height/2 + 50 < y < -screen_height/2 + 50 + BUTTON_HEIGHT:
        draw_main_menu()

def redirect_click(x, y):
    if game_state == "main_menu":
        handle_menu_click(x, y)
    elif game_state == "in_game":
        handle_game_click(x, y)
    elif game_state == "leaderboard":
        handle_leaderboard_click(x, y)

def toggle_history_view():
    global game_state
    if game_state == "in_game":
        game_state = "history_view"
        draw_move_history_overlay()
    elif game_state == "history_view":
        game_state = "in_game"
        draw_board(board, pen)
        screen.update()

## Initial Setup
screen = turtle.Screen()
screen.setup(width=1.0, height=1.0)
screen.title("15 Puzzle Game")
screen.tracer(0)
screen.bgcolor(BACKGROUND_COLOR)

pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)

hud_pen = turtle.Turtle()
hud_pen.hideturtle()
hud_pen.speed(0)
hud_pen.color(HUD_TEXT_COLOR)

## Keyboard Bindings 
screen.listen()
screen.onkey(draw_main_menu, "m")
screen.onkey(save_current_game, "p")
screen.onkey(toggle_history_view, "h")
screen.onkey(lambda: turtle.bye(), "Escape")
screen.onclick(redirect_click)

## Main loop 
load_leaderboard()
draw_main_menu()

try:
    screen.mainloop()
except (turtle.Terminator, KeyboardInterrupt):
    print("Game window closed by user.")
    sys.exit()
    
    
#Yippeee  
#The code is finally perfect!
#*Cell Theme starts playing* Did I hear Perfect?
