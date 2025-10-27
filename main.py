import random
import threading
import pygame
import sys
from pygame import mixer
from pygame.locals import *
from time import *

# Initialise the Game
pygame.init()

# Limit the screen to 600 by 600 pixel
screen = pygame.display.set_mode([608, 608])

# Set the name of the game
pygame.display.set_caption("Nootnoot game")

# Adding some color
red = (255, 0, 0)
white = (255, 255, 255)
black = (0, 0, 0)
light_grey = (211, 211, 211)
grey = (128, 128, 128)
light_blue = (106, 148, 232)

# Creating all variable for the snowball
# Starting position
snowball_x = 250
snowball_y = 250

# Taking a random number of direction at the start for x and y, can only be between -5 and -4 or 4 and 5
random_number = [-5, -4, 4, 5]
snowball_x_direction = random.choice(random_number)
snowball_y_direction = random.choice(random_number)

# Creating all the variable for the player
# creating the dimension of the player
player_width = 70
player_height = 70

# Starting position of player
player_x = 275
player_y = 500

# Player direction initialises to be 0, pressing the key will change them to -1 or 1
player_x_direction = 0
player_y_direction = 0

# Declaring that the initial speed of the player is 3
player_speed = 3

# Choosing the font
font = pygame.font.Font("freesansbold.ttf", 20)
game_over_font = pygame.font.Font("freesansbold.ttf", 60)
my_font = pygame.font.Font("graphics/font/gumball_font.ttf", 20)
my_font_name = pygame.font.Font("graphics/font/gumball_font.ttf", 70)
my_font_the_game = pygame.font.Font("graphics/font/gumball_font.ttf", 40)
my_font_game_over = pygame.font.Font("graphics/font/gumball_font.ttf", 60)
other_font = pygame.font.Font("graphics/font/pixel_font.ttf", 30)
other_font_smaller = pygame.font.Font("graphics/font/pixel_font.ttf", 17)

# Initialise score
score = 0
previous_score = 0
high_score = 0

# Creates the timer
timer = pygame.time.Clock()

# Initialise position and state of the speed boost
speed_boost_available = False
speed_boost_x = -100
speed_boost_y = -100
last_speed_boost_grabbed = 0

# Initialise position and state of the fire boost
fire_boost_available = False
fire_boost_x = -100
fire_boost_y = -100
last_fire_boost_grabbed = 0

# Initialise position and state of golden boost
golden_boost_available = False
golden_boost_x = -100
golden_boost_y = -100
last_golden_boost_grabbed = 0
golden_boost_activated = False

game_Over = False

# set counter to 10, will be used for increasing the difficulty every 10 moves
counter = 10

# Set timer to 6, will be used for golden boost
my_timer = 6

start_ticks = pygame.time.get_ticks()

golden_boost_music = mixer.Sound("music/Mario Kart (Star Powerup) - Gaming Music (HD) [TubeRipper.com].mp3")

nootnoot_sound = mixer.Sound("music/NOOT NOOT SOUND EFFECT.mp3")

snow_list = []

count = 0

WHITE = [255, 255, 255]
colourList = [WHITE]
color = random.choice(colourList)

# game_level_running = "0" is for the main menu
game_level_running = "0"

# Loop 100 times and add a snow flake in a random x,y position
for i in range(100):
    x = random.randrange(0, 600)
    y = random.randrange(0, 600)
    snow_list.append([x, y])


def recolour_snowflakes(snowflake):
    colour = random.choice(colourList)
    return colour, snowflake


def animate_snowflake(snowflake):
    x = snowflake[1][0]
    y = snowflake[1][1]
    y += random.randrange(1, 3)
    if y > 600:
        x, y = (random.randrange(-300, 600), random.randrange(0, 2))
    return snowflake[0], [x, y]


# The countdown is used for the golden boost, it is 6 seconds and display the timer on the bottom of the screen
def countdown():
    global my_timer
    global golden_boost_activated
    global golden_boost_music
    golden_boost_activated = True
    my_timer = 6
    for x in range(6):
        my_timer = my_timer - 1
        sleep(1)
    golden_boost_music.stop()
    pygame.mixer.music.unpause()
    golden_boost_activated = False


# Checks when the player took the boost and wait 30 points before creating a new golden boost
def golden_boost_check():
    global golden_boost_available
    global score
    global last_golden_boost_grabbed
    global golden_boost_x
    global golden_boost_y
    global game_level_running
    if game_level_running == "1":
        if score - last_golden_boost_grabbed > 49 and not golden_boost_available:
            golden_boost_available = True
            golden_boost_x = random.randint(10, 520)
            golden_boost_y = random.randint(10, 520)
    elif game_level_running == "2":
        if score - last_golden_boost_grabbed > 59 and not golden_boost_available:
            golden_boost_available = True
            golden_boost_x = random.randint(10, 520)
            golden_boost_y = random.randint(10, 520)
    elif game_level_running == "3":
        if score - last_golden_boost_grabbed > 89 and not golden_boost_available:
            golden_boost_available = True
            golden_boost_x = random.randint(10, 520)
            golden_boost_y = random.randint(10, 520)


# Checks when the player took the boost and wait 15 points before creating a new fire boost
def fire_boost_check():
    global fire_boost_available
    global score
    global last_fire_boost_grabbed
    global fire_boost_x
    global fire_boost_y
    global game_level_running
    if game_level_running == "1":
        if score - last_fire_boost_grabbed > 14 and not fire_boost_available:
            fire_boost_available = True
            fire_boost_x = random.randint(10, 520)
            fire_boost_y = random.randint(10, 520)
    elif game_level_running == "2":
        if score - last_fire_boost_grabbed > 19 and not fire_boost_available:
            fire_boost_available = True
            fire_boost_x = random.randint(10, 520)
            fire_boost_y = random.randint(10, 520)
    elif game_level_running == "3":
        if score - last_fire_boost_grabbed > 29 and not fire_boost_available:
            fire_boost_available = True
            fire_boost_x = random.randint(10, 520)
            fire_boost_y = random.randint(10, 520)


# Checks when the player took the boost and wait 10 points before creating a new speed boost
def speed_boost_check():
    global speed_boost_available
    global score
    global last_speed_boost_grabbed
    global speed_boost_x
    global speed_boost_y
    global game_level_running

    if game_level_running == "1":
        if score - last_speed_boost_grabbed > 9 and not speed_boost_available:
            speed_boost_available = True
            # Speed boost is 70*70, so max it can go is 530; -8 because of the wall, then it can only spawn max to 522
            speed_boost_x = random.randint(10, 520)
            speed_boost_y = random.randint(10, 520)
    elif game_level_running == "2":
        if score - last_speed_boost_grabbed > 14 and not speed_boost_available:
            speed_boost_available = True
            # Speed boost is 70*70, so max it can go is 530; -8 because of the wall, then it can only spawn max to 522
            speed_boost_x = random.randint(10, 520)
            speed_boost_y = random.randint(10, 520)
    elif game_level_running == "3":
        if score - last_speed_boost_grabbed > 19 and not speed_boost_available:
            speed_boost_available = True
            # Speed boost is 70*70, so max it can go is 530; -8 because of the wall, then it can only spawn max to 522
            speed_boost_x = random.randint(10, 520)
            speed_boost_y = random.randint(10, 520)


# Check that they do not start with the same speed
def check_not_same_starting_direction():
    global snowball_x_direction
    global snowball_y_direction
    if snowball_x_direction == snowball_y_direction or snowball_x_direction == -snowball_y_direction:
        if snowball_x_direction == random_number[1] or snowball_x_direction == random_number[2]:
            if snowball_x_direction > 0:
                snowball_x_direction += 1
            else:
                snowball_x_direction -= 1
            if snowball_y_direction > 0:
                snowball_y_direction += 1
            else:
                snowball_y_direction -= 1
            if snowball_x_direction > 0:
                snowball_x_direction -= 1
            elif snowball_x_direction < 0:
                snowball_x_direction += 1
        else:
            if snowball_x_direction > 0:
                snowball_x_direction -= 1
            if snowball_x_direction < 0:
                snowball_x_direction += 1


# Increases the speeed of the snowball every time the snowball did a number of bounce
def check_difficulty():
    global score
    global snowball_y_direction
    global snowball_x_direction
    global counter
    # It will increase randomly by 1 the direction of x and y dependant when the score is +10
    if counter - score == 0:
        if snowball_x_direction > 0:
            snowball_x_direction += 1
        # If the snowball is going towards the left
        elif snowball_x_direction < 0:
            snowball_x_direction -= 1
        # If the snowball is going down, adding 1 to the y direction every 9 or 10 point
        if snowball_y_direction > 0:
            snowball_y_direction += 1
        # If the snowball is going up
        elif snowball_y_direction < 0:
            snowball_y_direction -= 1
        counter += 10


# Detects if the player and the snowball intercepted
def check_collision(playerx, playery, ballx, bally):
    if abs(playerx-ballx) < 40 and abs(playery-bally) < 40:
        global player_x_direction
        global player_y_direction
        global snowball_x_direction
        global snowball_y_direction
        player_x_direction = 0
        player_y_direction = 0
        snowball_x_direction = 0
        snowball_y_direction = 0
        game_over()


# Creates the game Over state
def game_over():
    global game_Over
    draw_text('Game Over', my_font_game_over, red, screen, 80, 250)
    draw_text('Press Space to Restart ', my_font, black, screen, 130, 340)
    mixer.music.pause()
    nootnoot_sound.play(-1)
    game_Over = True


# Update the position of the player
def update_player_position():
    global player_x
    global player_y
    global player_x_direction
    global player_y_direction

    # Player speed is initially 3 but increases with boost
    # If we press right key (when we press right key player_x_direction = 1; so it's >0)
    if player_x_direction > 0:
        # Blocks so that the player doesn't come out of the window on the right
        if player_x < 600 - player_width:
            player_x += player_x_direction * player_speed
    # If we press left key (player_x_direction = -1)
    if player_x_direction < 0:
        # Blocks on the left side so player doesn't go off-screen
        if player_x > -2:
            player_x += player_x_direction * player_speed
    # If we press down key (player_y_direction = 1)
    if player_y_direction > 0:
        if player_y < 600 - player_height:
            player_y += player_y_direction * player_speed
    # If we press up key (player_y_direction = -1)
    if player_y_direction < 0:
        if player_y > 8:
            player_y += player_y_direction * player_speed


# Update the ball position
def update_ball_position():
    global snowball_x
    global snowball_y
    global snowball_x_direction
    global snowball_y_direction
    global score

    # When the snowball is going towards the right
    if snowball_x_direction > 0:
        # has not touches the wall yet (the snowball is 70*70 and the wall is 8 pixel long, so 600-72 = 528)
        if snowball_x < 528:
            snowball_x += snowball_x_direction
        # Touches the wall (change direction by the opposite and add +1 to the score)
        else:
            snowball_x_direction *= -1
            score += 1
    # When the snowball is going towards the left
    elif snowball_x_direction < 0:
        if snowball_x > 8:
            snowball_x += snowball_x_direction
        else:
            snowball_x_direction *= -1
            score += 1
    # When the snowball is going down
    if snowball_y_direction > 0:
        if snowball_y < 528:
            snowball_y += snowball_y_direction
        else:
            snowball_y_direction *= -1
            score += 1
    # When the snowball is going up
    elif snowball_y_direction < 0:
        if snowball_y > 8:
            snowball_y += snowball_y_direction
        else:
            snowball_y_direction *= -1
            score += 1


def draw_text(text, fonti, color, surface, x, y):
    textobj = fonti.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)



def main_menu():
    global count
    global snow_list
    global y
    global x
    background = pygame.image.load("graphics/background/background_main_menu.png")
    mixer.music.load("music/New Super Mario Bros. Wii OST - Track 05 - World 3.mp3")
    mixer.music.play()
    fat_noot_noot_img = pygame.image.load("graphics/player/fat pingu.png")

    # Ensure 'click' is defined before it's referenced in this function.
    # Without this initialization Python treats 'click' as a local variable
    # (because it's assigned later), and referencing it before assignment
    # raises UnboundLocalError on the first run. Initialize here to False.
    click = False

    while True:

        if count == 0:
            snow_list = list(map(recolour_snowflakes, snow_list))
        count += 1

        snow_list = list(map(animate_snowflake, snow_list))

        screen.fill((0, 0, 0))
        screen.blit(background, (0, 0))
        draw_text('Noot Noot', my_font_name, white, screen, 48, 50)
        draw_text('The Game', my_font_the_game, white, screen, 170, 130)

        mx, my = pygame.mouse.get_pos()

        button_1 = pygame.Rect(35, 510, 160, 50)
        surround_button_1 = pygame.Rect(30, 505, 170, 60)
        button_2 = pygame.Rect(225, 510, 160, 50)
        surround_button_2 = pygame.Rect(220, 505, 170, 60)
        button_3 = pygame.Rect(415, 510, 160, 50)
        surround_button_3 = pygame.Rect(410, 505, 170, 60)
        if button_1.collidepoint((mx, my)) or surround_button_1.collidepoint((mx, my)):
            if click:
                game_level(1)
        if button_2.collidepoint((mx, my)) or surround_button_2.collidepoint((mx, my)):
            if click:
                game_level(2)
        if button_3.collidepoint((mx, my)) or surround_button_3.collidepoint((mx, my)):
            if click:
                game_level(3)
        pygame.draw.rect(screen, grey, surround_button_1, 5, 5)
        pygame.draw.rect(screen, light_grey, button_1, 0, 5)
        pygame.draw.rect(screen, grey, surround_button_2, 5, 5)
        pygame.draw.rect(screen, light_grey, button_2)
        pygame.draw.rect(screen, grey, surround_button_3, 5, 5)
        pygame.draw.rect(screen, light_grey, button_3)
        draw_text('LEVEL 1', other_font, light_blue, screen, 47, 520)
        draw_text('LEVEL 2', other_font, light_blue, screen, 237, 520)
        draw_text('LEVEL 3', other_font, light_blue, screen, 427, 520)
        screen.blit(fat_noot_noot_img, (345, 365))
        for i in range(len(snow_list)):

            # Draw the snow flake
            pygame.draw.circle(screen, snow_list[i][0], snow_list[i][1], 5)

            # Move the snow flake down one pixel
            snow_list[i][1][0] += 1

            # If the snow flake has moved off the bottom of the screen
            if snow_list[i][1][0] > 608:
                # Reset it just above the top
                y = random.randrange(0, 2)
                snow_list[i][1][1] = y
                # Give it a new x position
                x = random.randrange(-300, 600)
                snow_list[i][1][0] = x

        # exit menu button

        click = False

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()
        timer.tick(60)

def game_level(level):

    global game_level_running
    if level == 1:
        snowball_img_path = "graphics/enemy/rock.png"
        background_path = "graphics/background/background_level1.png"
        game_level_running = "1"
    elif level == 2:
        snowball_img_path = "graphics/enemy/snowball.png"
        background_path = "graphics/background/background_icy.png"
        game_level_running = "2"
    elif level == 3:
        snowball_img_path = "graphics/enemy/fire_ball.png"
        background_path = "graphics/background/background_level3.png"
        game_level_running = "3"
    else:
        raise ValueError("Invalid game level")

    # Creating the Image for player, ball, background, and boost
    snowball_Img = pygame.image.load(snowball_img_path)
    player_Img = pygame.image.load("graphics/player/noot-noot.png")
    player_Img_golden = pygame.image.load("graphics/player/Golden-noot-noot.png")
    background = pygame.image.load(background_path)
    speed_boost_Img = pygame.image.load("graphics/boost/red_fish.png")
    fire_boost_Img = pygame.image.load("graphics/boost/fire.png")
    golden_boost_Img = pygame.image.load("graphics/boost/golden_fish.png")

    global player_speed
    global fire_boost_available
    global speed_boost_available
    global golden_boost_activated
    global golden_boost_available
    global snowball_x_direction
    global snowball_y_direction
    global snowball_x
    global snowball_y
    global fire_boost_y
    global fire_boost_x
    global last_fire_boost_grabbed
    global speed_boost_x
    global speed_boost_y
    global last_speed_boost_grabbed
    global golden_boost_x
    global golden_boost_y
    global last_golden_boost_grabbed
    global player_x
    global player_y
    global score
    global high_score
    global previous_score
    global player_y_direction
    global player_x_direction
    global score
    global counter
    global game_Over

    running = True
    mixer.music.load("music/Freeze-Man-Stage-Iceberg-Area-M.mp3")
    mixer.music.play()

    while running:
        # Playing the music of the game
        update_ball_position()
        update_player_position()
        check_difficulty()
        fire_boost_check()
        speed_boost_check()
        golden_boost_check()
        check_not_same_starting_direction()
        screen.fill((0, 0, 0))
        # Setting the background
        screen.blit(background, (0, 0))
        draw_text('Game', font, (255, 255, 255), screen, 20, 20)
        # Setting the snowball on the screen
        snowball = screen.blit(snowball_Img, (snowball_x, snowball_y))
        # Setting the player on the screen
        # If he didn't take the golden boost, he is just a normal pingu
        if golden_boost_activated is False:
            gamer = screen.blit(player_Img, (player_x, player_y))
        # Otherwise, he turns golden
        else:
            gamer = screen.blit(player_Img_golden, (player_x, player_y))
        # Checks the collision between snowball and player
        if not golden_boost_activated:
            check_collision(gamer.centerx, gamer.centery, snowball.centerx, snowball.centery)
        # Display the score
        draw_text("Score: " + str(score), other_font_smaller, black, screen, 265, 17)
        # Display the high score
        draw_text("Highest Score: " + str(high_score), other_font_smaller, black, screen, 18, 17)
        # Display previous score
        draw_text("Previous Score: " + str(previous_score), other_font_smaller, black, screen, 400, 17)

        # If the player takes the fire boost, it will take out 1 in speed in the y direction or x randomly
        if fire_boost_available:
            fire_boost = screen.blit(fire_boost_Img, (fire_boost_x, fire_boost_y))
            if gamer.colliderect(fire_boost):
                x_or_y_list = ["y_choice", "x_choice"]
                random_choice = random.choice(x_or_y_list)
                if random_choice == "x_choice":
                    if snowball_x_direction > 0:
                        snowball_x_direction -= 1
                    else:
                        snowball_x_direction += 1
                else:
                    if snowball_y_direction > 0:
                        snowball_y_direction -= 1
                    else:
                        snowball_y_direction += 1
                # Hide the boost again and turn the variables to False
                fire_boost_x = -100
                fire_boost_y = -100
                last_fire_boost_grabbed = score
                fire_boost_available = False

        # Check if speed boost is available
        if speed_boost_available:
            speed_boost = screen.blit(speed_boost_Img, (speed_boost_x, speed_boost_y))
            # When player and speed boost collide, add 1 in player speed, hide the speed boost and make it unavailable
            if gamer.colliderect(speed_boost):
                player_speed += 1
                speed_boost_x = -100
                speed_boost_y = -100
                last_speed_boost_grabbed = score
                speed_boost_available = False

        if golden_boost_available:
            golden_boost = screen.blit(golden_boost_Img, (golden_boost_x, golden_boost_y))
            # When player and speed boost collide, add 1 in player speed, hide the speed boost and make it unavailable
            if gamer.colliderect(golden_boost):
                # Pause music to start the star music
                pygame.mixer.music.pause()
                golden_boost_music.play()
                # Start the countdown in the background
                countdown_thread = threading.Thread(target=countdown)
                countdown_thread.start()
                golden_boost_x = -100
                golden_boost_y = -100
                last_golden_boost_grabbed = score
                golden_boost_available = False

        if golden_boost_activated is True:
            display_timer = font.render("Time left: " + str(my_timer), True, black, white)
            screen.blit(display_timer, (300, 572))

        # Display the speed
        draw_text("Speed: " + str(player_speed - 2), other_font_smaller, black, screen, 18, 572)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    # Stop running and stop all possible music
                    running = False
                    mixer.music.pause()
                    nootnoot_sound.stop()
                    golden_boost_music.stop()
                    mixer.music.load("music/New Super Mario Bros. Wii OST - Track 05 - World 3.mp3")
                    mixer.music.play()
                    game_level_running = "0"
                    snowball_x = 300
                    snowball_y = 300
                    snowball_x_direction = random.choice(random_number)
                    snowball_y_direction = random.choice(random_number)
                    player_x = 275
                    player_y = 500
                    # Retain the previous score
                    previous_score = score
                    # Check if High Score has been beaten
                    if score > high_score:
                        high_score = score
                    player_speed = 3
                    # hide the speed boost
                    last_speed_boost_grabbed = 0
                    speed_boost_y = -100
                    speed_boost_x = -100
                    speed_boost_available = False
                    # hide fire boost
                    last_fire_boost_grabbed = 0
                    fire_boost_x = -100
                    fire_boost_y = -100
                    fire_boost_available = False
                    # hide golden boost
                    last_golden_boost_grabbed = 0
                    golden_boost_x = -100
                    golden_boost_y = -100
                    golden_boost_available = False
                    golden_boost_activated = False
                    # reset game Over and speed boost
                    game_Over = False
                    score = 0
                    counter = 10
                if event.key == pygame.K_LEFT and not game_Over:
                    player_x_direction = -1
                if event.key == pygame.K_RIGHT and not game_Over:
                    player_x_direction = 1
                if event.key == pygame.K_UP and not game_Over:
                    player_y_direction = -1
                if event.key == pygame.K_DOWN and not game_Over:
                    player_y_direction = 1
            # If we release a key
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    player_x_direction = 0
                if event.key == pygame.K_RIGHT:
                    player_x_direction = 0
                if event.key == pygame.K_UP:
                    player_y_direction = 0
                if event.key == pygame.K_DOWN:
                    player_y_direction = 0
                # When game Over, start the game again
                if event.key == pygame.K_SPACE and game_Over:
                    nootnoot_sound.stop()
                    mixer.music.unpause()
                    snowball_x = 300
                    snowball_y = 300
                    snowball_x_direction = random.choice(random_number)
                    snowball_y_direction = random.choice(random_number)
                    player_x = 275
                    player_y = 500
                    # retain the previous score
                    previous_score = score
                    # Check if High Score has been beaten
                    if score > high_score:
                        high_score = score
                    player_speed = 3
                    # hide the speed boost
                    last_speed_boost_grabbed = 0
                    speed_boost_y = -100
                    speed_boost_x = -100
                    speed_boost_available = False
                    # hide fire boost
                    last_fire_boost_grabbed = 0
                    fire_boost_x = -100
                    fire_boost_y = -100
                    fire_boost_available = False
                    # hide golden boost
                    last_golden_boost_grabbed = 0
                    golden_boost_x = -100
                    golden_boost_y = -100
                    golden_boost_available = False
                    golden_boost_activated = False
                    # reset game Over and speed boost
                    game_Over = False
                    score = 0
                    counter = 10
        pygame.display.update()
        timer.tick(30)


main_menu()

