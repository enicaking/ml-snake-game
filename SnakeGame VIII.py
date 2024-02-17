"""
Snake Eater
Made with PyGame
Last modification in January 2024 by José Carlos Pulido
Machine Learning Classes - University Carlos III of Madrid
Assignment completed by Estefany González and Enica King
"""

import pygame, sys, time, random, csv, os

# DIFFICULTY settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
DIFFICULTY = 40

# Window size
FRAME_SIZE_X = 480
FRAME_SIZE_Y = 480
DIRECTION_INDEX = ["UP", "DOWN", "LEFT", "RIGHT"]

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
        # food in limit of frame size -> cannot go there (game_over)
        self.food_pos = [random.randrange(1, (FRAME_SIZE[0] // 10)) * 10,
                         random.randrange(1, (FRAME_SIZE[1] // 10)) * 10]
        self.food_spawn = True
        self.direction = 'RIGHT'
        self.change_to = self.direction
        self.score = 0
        self.food_score = 0

        self.dist_x = (self.food_pos[0] - self.snake_body[0][0])
        self.dist_y = (self.food_pos[1] - self.snake_body[0][1])

        self.snake_direction = [True, True, False, True]  # U D L R
        self.food_direction = [False, False, False, True]
        self.favorable_move = [False, False, False, True]

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


def new_position(new_pos, current_direction):

    if current_direction == 'UP':
        new_pos[1] -= 10
    elif current_direction == 'DOWN':
        new_pos[1] += 10
    elif current_direction == 'LEFT':
        new_pos[0] -= 10
    else:  # RIGHT
        new_pos[0] += 10

    return new_pos


def check_walls(directions, new_head):

    if new_head[0] < 0:
        print("----------------------------------------Wall")
        directions[2] = False
        directions[3] = True
        if directions[0]:
            return "UP"
        else:
            return "DOWN"
    elif new_head[0] > FRAME_SIZE_X:
        print("----------------------------------------Wall")
        directions[3] = False
        directions[2] = True
        if directions[0]:
            return "UP"
        else:
            return "DOWN"
    elif new_head[1] < 0:
        print("----------------------------------------Wall")
        directions[0] = False
        directions[1] = True
        if directions[2]:
            return "LEFT"
        else:
            return "RIGHT"
    elif new_head[1] > FRAME_SIZE_Y:
        print("----------------------------------------Wall")
        directions[1] = False
        directions[0] = True
        if directions[2]:
            return "LEFT"
        else:
            return "RIGHT"

    return directions


def move_tutorial_1(game):
    # First step is to calculate the next snake position based on current direction.
    # The MAIN goal is not to die.
    # The SECONDARY goal is to eat the food in the most direct way possible.
    # We have to calculate FIRST where the snake CAN move, and SECOND where it SHOULD move.
    new_pos = game.snake_pos.copy()
    new_head = new_position(new_pos, game.direction)
    new_body = game.snake_body.copy()
    new_body.insert(0, list(new_head))
    new_body.pop()

    change_to = game.direction  # This is what we have to figure out!

    # First, let's make sure the snake can't turn around
    game.snake_direction = [True, True, True, True]
    to_restrict = ["DOWN", "UP", "RIGHT", "LEFT"]
    game.snake_direction[to_restrict.index(game.direction)] = False

    # Now let's restrict the snake so it doesn't bump itself.
    for block in new_body[1:]:
        if new_head[0] == block[0] and new_head[1] == block[1]:
            game.snake_direction[DIRECTION_INDEX.index(game.direction)] = False
            print('--------------------------Potential collapse if we go', game.direction, '!!!', game.snake_direction)
            print("Old", game.snake_direction)
            not_get_looped(game)
            print("New", game.snake_direction)

    # We also need to restricting based on the boundaries of the game.
    # We can set this to automatically turn around since it is the last restriction.
    game.snake_direction = check_walls(game.snake_direction, new_head)

    # We know where the snake CAN move. Let's see where it SHOULD choose to go.
    # Calculate food
    game.dist_x = game.food_pos[0] - game.snake_body[0][0]
    game.dist_y = game.food_pos[1] - game.snake_body[0][1]
    game.food_direction = [False, False, False, False]
    if game.dist_x > 0:
        game.food_direction[3] = True
    elif game.dist_x < 0:
        game.food_direction[2] = True
    if game.dist_y > 0:
        game.food_direction[1] = True
    elif game.dist_y < 0:
        game.food_direction[0] = True

    # Let's see if the snake CAN move towards the food.
    game.favorable_move = [False, False, False, False]
    if game.snake_direction[0] and game.food_direction[0] and game.dist_y != 0:
        game.favorable_move[0] = True
    if game.snake_direction[1] and game.food_direction[1] and game.dist_y != 0:
        game.favorable_move[1] = True
    if game.snake_direction[2] and game.food_direction[2] and game.dist_x != 0:
        game.favorable_move[2] = True
    if game.snake_direction[3] and game.food_direction[3] and game.dist_x != 0:
        game.favorable_move[3] = True

    # We prioritise these
    if True in game.favorable_move[0:2]:
        change_to = DIRECTION_INDEX[game.favorable_move.index(True)]
    elif True in game.favorable_move[2:]:
        change_to = DIRECTION_INDEX[game.favorable_move.index(True)]
    else:  # True not in favorable_move
        print("------------------------------------------------Can't move towards the food")
        change_to = DIRECTION_INDEX[game.snake_direction.index(True)]

    return change_to


def not_get_looped(game):
    if game.snake_direction.index(True) == 0 or game.snake_direction.index(True) == 1:  # check up/down
        checker1 = [game.snake_pos[0], game.snake_pos[1] - 10]  # Going up
        if not loop_de_loop(game, checker1, "UP"):  # checker 2 is the loop, going down will kill the snake
            game.snake_direction[1] = False
        # checker2 = [game.snake_pos[0], game.snake_pos[1] + 10]  # Going down
        else:
            game.snake_direction[0] = False
    else:  # check left/right
        checker1 = [game.snake_pos[0] - 10, game.snake_pos[1]]  # Going left
        if not loop_de_loop(game, checker1, "LEFT"):
            game.snake_direction[2] = False
        else:  # checker 2 is the loop, going right will kill the snake
            game.snake_direction[3] = False


def loop_de_loop(game, checker, checker_direction):

    outside = False
    start = game.snake_pos.copy()
    snake_body = game.snake_body.copy()

    checker_pos = new_position(game.snake_pos, checker_direction)

    while not (outside or checker_pos == start):
        area = [[checker_pos[0] - 10, checker_pos[1] - 10], [checker_pos[0], checker_pos[1] - 10],
                [checker_pos[0] + 10, checker_pos[1] - 10], [checker_pos[0] + 10, checker_pos[1]],
                [checker_pos[0] + 10, checker_pos[1] + 10], [checker_pos[0], checker_pos[1] + 10],
                [checker_pos[0] - 10, checker_pos[1] + 10], [checker_pos[0] - 10, checker_pos[1]]]
        counter = 0
        for block in snake_body[1:]:
            if block in area:
                counter += 1
        if counter == 0:
            outside = True  # breaks the While loop
        else:  # there is some snake around, let's keep going

            checker_options = [True, True, True, True]  # We have to move in a direction following the snake
            to_restrict = ["DOWN", "UP", "RIGHT", "LEFT"]
            checker_options[to_restrict.index(checker_direction)] = False

            for block in snake_body[1:]:
                # Along the border
                if (checker_pos[0]-10) == block[0] and checker_pos[1] == block[1]:
                    checker_options[3] = False
                elif (checker_pos[0]+10) == block[0] and checker_pos[1] == block[1]:
                    checker_options[2] = False
                elif (checker_pos[0]) == block[0] and (checker_pos[1]-10) == block[1]:
                    checker_options[1] = False
                elif (checker_pos[0]) == block[0] and (checker_pos[1] + 10) == block[1]:
                    checker_options[0] = False
                # Make sure that it moves along the border

            new_direction = checker_options[checker_options.index(True)]

            checker_pos = new_position(checker_pos, new_direction)

    return outside


# PRINTING DATA FROM GAME STATE
def print_state(game):
    print("--------GAME STATE--------")
    print("Direction:", game.direction)
    print("Snake X:", game.snake_pos[0], ", Snake Y:", game.snake_pos[1])
    print("Snake Body:", game.snake_body)
    print("Snake Body Length:", len(game.snake_body))

    print("Where can the snake go?:", game.snake_direction)
    print("Where is the food?:", game.food_direction)
    print("Where should the snake go?:", game.favorable_move)


def print_line_data(game):
    line_data = [FRAME_SIZE_X, FRAME_SIZE_Y, game.direction, game.snake_pos[0], game.snake_pos[1],
                 len(game.snake_body), game.food_pos[0], game.food_pos[1], game.score, game.snake_direction[0],
                 game.snake_direction[1], game.snake_direction[2], game.snake_direction[3],
                 game.favorable_move[0], game.favorable_move[1], game.favorable_move[2], game.favorable_move[3]]

    return line_data


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
        # game.food_pos = game.food_positions.pop(0)
        print('-------------------------------------------------------------------------------new food', game.food_pos  )
        game.food_score += 1

    game.food_spawn = True

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
        print('Reason for death: out of bound')
        game_over(game)
    if game.snake_pos[1] < 0 or game.snake_pos[1] > FRAME_SIZE_Y - 10:
        print('Reason for death: out of bound')
        game_over(game)

    # Touching the snake body
    for block in game.snake_body[1:]:
        if game.snake_pos[0] == block[0] and game.snake_pos[1] == block[1]:
            print('Reason for death: collapsed')
            game_over(game)

    show_score(game, 1, WHITE, 'consolas', 15)
    # Refresh game screen
    pygame.display.update()
    # Refresh rate
    fps_controller.tick(DIFFICULTY)
    # PRINTING STATE AND IN CSV
    print_state(game)
    
    if not os.path.isfile('output.csv'):
        file = open('output.csv', "a", newline='')
        headerList = ['Frame Size X', 'Frame Size Y', 'Direction',
                      'Head X', 'Head Y', 'Snake Body Length', 'Food Position X', 'Food Position Y',
                      'Score', 'Possible Move UP','Possible Move DOWN', 'Possible Move LEFT', 'Possible Move RIGHT',
                      'Favorable Move UP','Favorable Move DOWN', 'Favorable Move LEFT', 'Favorable Move RIGHT' ]

        dw = csv.DictWriter(file, delimiter=',',
                            fieldnames=headerList)
        dw.writeheader()
    else:
        file = open('output.csv', "a", newline='')

    writer = csv.writer(file)
    writer.writerow(print_line_data(game))
    file.close()


