"""
Snake Eater
Made with PyGame
Last modification in January 2024 by José Carlos Pulido
Machine Learning Classes - University Carlos III of Madrid
"""

import pygame, sys, time, random, csv

# DIFFICULTY settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
DIFFICULTY = 30

# Window size
FRAME_SIZE_X = 480
FRAME_SIZE_Y = 480

# Colors (R, G, B)
BLACK = pygame.Color(51, 51, 51)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(204, 51, 0)
GREEN = pygame.Color(204, 255, 153)
BLUE = pygame.Color(0, 51, 102)


# GAME STATE CLASS
class GameState:
    def __init__(self, FRAME_SIZE):
        self.snake_pos = [100, 50]
        self.snake_body = [[100, 50], [100 - 10, 50], [100 - (2 * 10), 50]]
        ################# food in limit of frame size -> cannot go there (game_over)
        self.food_pos = [random.randrange(1, (FRAME_SIZE[0] // 10)) * 10,
                         random.randrange(1, (FRAME_SIZE[1] // 10)) * 10]
        self.food_positions = [[290, 450], [120, 110], [20, 10], [210, 110], [360, 140], [440, 410], [130, 60], [340, 380],
                    [230, 260], [180, 20], [350, 150], [380, 250], [260, 310], [280, 40]]
        self.food_pos = [220, 390]
        print('-------------------------------------------------------------------------------new food', self.food_pos  )
        self.food_spawn = True
        self.direction = 'RIGHT'
        self.prev_direction = None
        self.change_to = self.direction
        self.score = 0
        self.food_score = 0

        self.dist_x = (self.food_pos[0] - self.snake_body[0][0])/10
        self.dist_y = (self.food_pos[1] - self.snake_body[0][1])/10

        self.available_left = True
        self.available_right = True
        self.available_up = True
        self.available_down = True

# Game Over
def game_over(game):
    my_font = pygame.font.SysFont('times new roman', 90)
    game_over_surface = my_font.render('YOU DIED', True, WHITE)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (FRAME_SIZE_X / 2, FRAME_SIZE_Y / 4)
    game_window.fill(BLUE)
    game_window.blit(game_over_surface, game_over_rect)
    show_score(game, 0, WHITE, 'times', 20)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    sys.exit()


# Score
def show_score(game, choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(game.score), True, color)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (FRAME_SIZE_X / 8, 15)
    else:
        score_rect.midtop = (FRAME_SIZE_X / 2, FRAME_SIZE_Y / 1.25)
    game_window.blit(score_surface, score_rect)
    # pygame.display.flip()


# Move the snake
def move_keyboard(game, event):
    # Whenever a key is pressed down
    change_to = game.direction
    if event.type == pygame.KEYDOWN:
        # W -> Up; S -> Down; A -> Left; D -> Right
        if (event.key == pygame.K_UP or event.key == ord('w')) and game.direction != 'DOWN':
            change_to = 'UP'
        if (event.key == pygame.K_DOWN or event.key == ord('s')) and game.direction != 'UP':
            change_to = 'DOWN'
        if (event.key == pygame.K_LEFT or event.key == ord('a')) and game.direction != 'RIGHT':
            change_to = 'LEFT'
        if (event.key == pygame.K_RIGHT or event.key == ord('d')) and game.direction != 'LEFT':
            change_to = 'RIGHT'
    return change_to


# TODO: IMPLEMENT HERE THE NEW INTELLIGENT METHOD

def loop(game, axis, change_to):
    # axis == True -> it has to do a loop in the x axis
    # axis == False -> it has to do a loop in the y axis
    if axis:
        # by default it will go down, if that means getting out of bounds it will go up
        if game.snake_pos[1] == FRAME_SIZE_Y:
            change_to = 'UP'
        else:
            change_to = 'DOWN'
    else:
        # by default it will go right, if that means getting out of bounds it will go left
        if game.snake_pos[0] == FRAME_SIZE_X:
            change_to = 'LEFT'
        else:
            change_to = 'RIGHT'

    return change_to


def new_position(game, change_to):
    new_body = game.snake_body.copy()
    new_pos = game.snake_pos.copy()

    if game.direction == 'UP':
        new_pos[1] -= 10
    elif game.direction == 'DOWN':
        new_pos[1] += 10
    elif game.direction == 'LEFT':
        new_pos[0] -= 10
    elif game.direction == 'RIGHT':
        new_pos[0] += 10

    new_body.insert(0, list(new_pos))
    new_body.pop()

    body_blocked_wall = False
    body_blocked = False

    # Bump itself
    for block in new_body[1:]:
        if new_pos[0] == block[0] and new_pos[1] == block[1]:
            body_blocked = True
            print('checking bump itself')

    # Bump wall
    if (new_pos[0] < 0 or new_pos[0] > FRAME_SIZE_X
            or new_pos[1] < 0 or new_pos[1] > FRAME_SIZE_Y):
        body_blocked_wall = True
        print('checking bump wall')

    if body_blocked_wall:
        print('body blocked -> loop')
        if change_to == 'RIGHT' or change_to == 'LEFT':
            print('x loop')
            change_to = loop(game, True, change_to)
        else:
            print('y loop')
            change_to = loop(game, False, change_to)
    elif body_blocked:
        print('body blocked -> bordear')

        change_to = game.prev_direction

    return change_to


def move_tutorial_1(game):
    change_to = game.direction
    game.prev_direction = game.direction

    # if it won't bump any wall or collapse with itself, change direction
    if game.food_pos[0] == game.snake_body[0][0]:
            # food and snake are at the same x coordinate
            if game.food_pos[1] < game.snake_body[0][1] and game.direction != 'DOWN':
                change_to = 'UP'

            elif game.food_pos[1] > game.snake_body[0][1] and game.direction != 'UP':
                change_to = 'DOWN'

            else:
                change_to = loop(game, False, change_to)
                print('loop y')

    else:
            if game.food_pos[0] < game.snake_body[0][0] and game.direction != 'RIGHT':
                change_to = 'LEFT'

            elif game.food_pos[0] > game.snake_body[0][0] and game.direction != 'LEFT':
                change_to = 'RIGHT'

            else:
                change_to = loop(game, True, change_to)
                print('loop x')

    return new_position(game, change_to)


# PRINTING DATA FROM GAME STATE
def print_state(game):
    print("--------GAME STATE--------")
    #print("FrameSize:", FRAME_SIZE_X, FRAME_SIZE_Y)
    print("Direction:", game.direction)
    print("Previous Direction:", game.prev_direction)
    print("Snake X:", game.snake_pos[0], ", Snake Y:", game.snake_pos[1])
    #print("Snake Body:", game.snake_body)
    print("Snake Body Length:", len(game.snake_body))
    print("Food X:", game.food_pos[0], ", Food Y:", game.food_pos[1])
    #print("Score:", game.score)
    print("Food Score:", game.food_score)
    print("Left available direction?", game.available_left)
    print("Right available direction?", game.available_right)
    print("Up available direction?", game.available_up)
    print("Down available direction?", game.available_down)


    print("Distance to food:", game.dist_x, game.dist_y)



# TODO: IMPLEMENT HERE THE NEW INTELLIGENT METHOD
def print_line_data(game):
    line_data = [FRAME_SIZE_X, FRAME_SIZE_Y, game.direction,
                game.snake_pos[0], game.snake_pos[1], len(game.snake_body),
                game.food_pos[0], game.food_pos[1], game.score,
                game.dist_x, game.dist_y, game.food_score,
                game.available_left, game.available_right, game.available_up, game.available_down]
    with open("C:\\Users\\bucky\\Documents\\UC3M\\YEAR TWO - SPRING\\Machine Learning I\\Tutorial 1\\snakeGame.csv", "a",
              newline='') as file:
        writer = csv.writer(file)
        writer.writerow(line_data)


# Checks for errors encountered
check_errors = pygame.init()
# pygame.init() example output -> (6, 0)
# second number in tuple gives number of errors
if check_errors[1] > 0:
    print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] Game successfully initialised')

# Initialise game window
pygame.display.set_caption('Snake Eater - Machine Learning (UC3M)')
game_window = pygame.display.set_mode((FRAME_SIZE_X, FRAME_SIZE_Y))

# FPS (frames per second) controller
fps_controller = pygame.time.Clock()

# Main logic
game = GameState((FRAME_SIZE_X, FRAME_SIZE_Y))


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # Esc -> Create event to quit the game
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
        # CALLING MOVE METHOD
        # game.direction = move_tutorial_1(game)

    # UNCOMMENT WHEN METHOD IS IMPLEMENTED
    game.direction = move_tutorial_1(game)

    if game.direction == 'UP':
        game.snake_pos[1] -= 10
    elif game.direction == 'DOWN':
        game.snake_pos[1] += 10
    elif game.direction == 'LEFT':
        game.snake_pos[0] -= 10
    elif game.direction == 'RIGHT':
        game.snake_pos[0] += 10


    # Snake body growing mechanism
    game.snake_body.insert(0, list(game.snake_pos))
    if game.snake_pos[0] == game.food_pos[0] and game.snake_pos[1] == game.food_pos[1]:
        game.score += 100
        game.food_spawn = False
    else:
        game.snake_body.pop()
        game.score -= 1


    # Spawning food on the screen
    if not game.food_spawn:
        game.food_pos = [random.randrange(1, (FRAME_SIZE_X // 10)) * 10, random.randrange(1, (FRAME_SIZE_Y // 10)) * 10]
        #game.food_pos = game.food_positions.pop(0)
        print('-------------------------------------------------------------------------------new food', game.food_pos  )
        game.food_score += 1

    game.food_spawn = True

    # Calculating distance to the food
    game.dist_x = game.food_pos[0] - game.snake_body[0][0]
    game.dist_y = game.food_pos[1] - game.snake_body[0][1]

    # GFX
    game_window.fill(BLUE)
    for pos in game.snake_body:
        # Snake body
        # .draw.rect(play_surface, color, xy-coordinate)
        # xy-coordinate -> .Rect(x, y, size_x, size_y)
        pygame.draw.rect(game_window, GREEN, pygame.Rect(pos[0], pos[1], 10, 10))

    # Snake food
    pygame.draw.rect(game_window, RED, pygame.Rect(game.food_pos[0], game.food_pos[1], 10, 10))

    # Game Over conditions
    # Getting out of bounds
    if game.snake_pos[0] < 0 or game.snake_pos[0] > FRAME_SIZE_X - 10:
        print('out of bound')

        game_over(game)
    if game.snake_pos[1] < 0 or game.snake_pos[1] > FRAME_SIZE_Y - 10:
        print('out of bound')

        game_over(game)


    # Touching the snake body
    for block in game.snake_body[1:]:
        if game.snake_pos[0] == block[0] and game.snake_pos[1] == block[1]:
            print('collapsed')
            game_over(game)

    show_score(game, 1, WHITE, 'consolas', 15)
    # Refresh game screen
    pygame.display.update()
    # Refresh rate
    fps_controller.tick(DIFFICULTY)
    # PRINTING STATE AND IN CSV
    print_state(game)
    #print_line_data(game)


