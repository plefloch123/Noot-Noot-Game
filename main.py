# ============================================================
# Nootnoot game — pygbag-friendly version (async loop, no threads/sleep)
# Keep your assets in:
#   graphics/...
#   music/...
# ============================================================

import random
import pygame
import sys
import asyncio
import os
from pygame import mixer
from pygame.locals import *


# ---------------------------
# Init pygame + mixer (safe)
# ---------------------------
pygame.init()
try:
    mixer.init()
except Exception:
    pass

# Window
screen = pygame.display.set_mode([608, 608])
pygame.display.set_caption("Nootnoot game")

# Colors
red = (255, 0, 0)
white = (255, 255, 255)
black = (0, 0, 0)
light_grey = (211, 211, 211)
grey = (128, 128, 128)
light_blue = (106, 148, 232)

# ---------------------------
# Global game state
# ---------------------------

# Snowball
snowball_x = 250
snowball_y = 250
random_number = [-5, -4, 4, 5]
snowball_x_direction = random.choice(random_number)
snowball_y_direction = random.choice(random_number)

pending_death_sound = False
death_sound_playing = False


# Player
player_width = 70
player_height = 70
player_x = 275
player_y = 500
player_x_direction = 0
player_y_direction = 0
player_speed = 3

# Fonts
font = pygame.font.Font("freesansbold.ttf", 20)
game_over_font = pygame.font.Font("freesansbold.ttf", 60)
my_font = pygame.font.Font("graphics/font/gumball_font.TTF", 20)
my_font_name = pygame.font.Font("graphics/font/gumball_font.TTF", 70)
my_font_the_game = pygame.font.Font("graphics/font/gumball_font.TTF", 40)
my_font_game_over = pygame.font.Font("graphics/font/gumball_font.TTF", 60)
other_font = pygame.font.Font("graphics/font/pixel_font.ttf", 30)
other_font_smaller = pygame.font.Font("graphics/font/pixel_font.ttf", 17)

# Scores
score = 0
previous_score = 0
high_score = 0

# Clock
timer = pygame.time.Clock()

# Boosts
speed_boost_available = False
speed_boost_x = -100
speed_boost_y = -100
last_speed_boost_grabbed = 0

fire_boost_available = False
fire_boost_x = -100
fire_boost_y = -100
last_fire_boost_grabbed = 0

golden_boost_available = False
golden_boost_x = -100
golden_boost_y = -100
last_golden_boost_grabbed = 0
golden_boost_activated = False

# Game state
game_Over = False
counter = 10
my_timer = 6

# Golden boost timer (pygbag-safe; no sleep/thread)
golden_boost_end_ms = 0

# ---------------------------
# Music / SFX (web-safe)
# ---------------------------
audio_unlocked = False

def debug(msg):
    # pygbag: prints to browser console (DevTools -> Console)
    print("[AUDIO]", msg)


def try_start_death_sound_from_input():
    global pending_death_sound, death_sound_playing

    if not pending_death_sound:
        return
    if death_sound_playing:
        return

    debug(f"Trying to start death sound. pending={pending_death_sound}, playing={death_sound_playing}")

    ok = unlock_audio()
    debug(f"unlock_audio() returned {ok}")

    if nootnoot_sound is None:
        debug("nootnoot_sound is None -> cannot play (wrong filename or not packaged)")
        return

    safe_sound_stop(golden_boost_music)
    safe_sound_play(nootnoot_sound, loops=-1)
    debug("Requested death sound play")

    death_sound_playing = True
    pending_death_sound = False



def load_sound(prefer_ogg_path, fallback_mp3_path=None):
    try:
        s = mixer.Sound(prefer_ogg_path)
        debug(f"Loaded OGG: {prefer_ogg_path}")
        return s
    except Exception as e:
        debug(f"FAILED OGG: {prefer_ogg_path} -> {e}")

    if fallback_mp3_path:
        try:
            s = mixer.Sound(fallback_mp3_path)
            debug(f"Loaded MP3: {fallback_mp3_path}")
            return s
        except Exception as e:
            debug(f"FAILED MP3: {fallback_mp3_path} -> {e}")

    return None


def unlock_audio():
    global audio_unlocked, golden_boost_music, nootnoot_sound

    # Keep trying until it truly works
    try:
        if not mixer.get_init():
            mixer.init()
            debug("mixer.init() OK")
        else:
            debug("mixer already initialized")
    except Exception as e:
        debug(f"mixer.init() FAILED -> {e}")
        return False

    # Check if files are actually present in the web build
    debug(f"exists music/MarioKartStar.ogg? {os.path.exists('music/MarioKartStar.ogg')}")
    debug(f"exists music/NOOT_NOOT_SOUND_EFFECT.ogg? {os.path.exists('music/NOOT_NOOT_SOUND_EFFECT.ogg')}")

    # Load/reload sounds (always attempt if None)
    if golden_boost_music is None:
        golden_boost_music = load_sound(
            "music/MarioKartStar.ogg",
            "music/Mario Kart (Star Powerup) - Gaming Music (HD) [TubeRipper.com].mp3"
        )

    if nootnoot_sound is None:
        nootnoot_sound = load_sound(
            "music/NOOT_NOOT_SOUND_EFFECT.ogg",
            "music/NOOT NOOT SOUND EFFECT.mp3"
        )

    debug(f"golden_boost_music is None? {golden_boost_music is None}")
    debug(f"nootnoot_sound is None? {nootnoot_sound is None}")

    # Only mark unlocked if at least one sound loaded
    audio_unlocked = (golden_boost_music is not None or nootnoot_sound is not None)
    debug(f"audio_unlocked set to {audio_unlocked}")
    return audio_unlocked



golden_boost_music = None
nootnoot_sound = None
# Try early load (may fail until unlock; that's fine)
golden_boost_music = load_sound(
    "music/MarioKartStar.ogg",
    "music/Mario Kart (Star Powerup) - Gaming Music (HD) [TubeRipper.com].mp3"
)
nootnoot_sound = load_sound(
    "music/NOOT_NOOT_SOUND_EFFECT.ogg",
    "music/NOOT NOOT SOUND EFFECT.mp3"
)

# Snow
snow_list = []
count = 0
WHITE = [255, 255, 255]
colourList = [WHITE]

game_level_running = "0"  # "0" menu, "1/2/3" in game

for _ in range(100):
    x = random.randrange(0, 600)
    y = random.randrange(0, 600)
    snow_list.append([x, y])


# ---------------------------
# Helpers
# ---------------------------

def safe_music_load_play(path: str, loops: int = -1):
    try:
        mixer.music.load(path)
        mixer.music.play(loops=loops)
    except Exception:
        pass

def safe_music_pause():
    try:
        mixer.music.pause()
    except Exception:
        pass

def safe_music_unpause():
    try:
        mixer.music.unpause()
    except Exception:
        pass

def safe_sound_play(snd, loops: int = 0):
    if snd is None:
        return
    try:
        snd.play(loops=loops)
    except Exception:
        pass

def safe_sound_stop(snd):
    if snd is None:
        return
    try:
        snd.stop()
    except Exception:
        pass


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


def draw_text(text, fonti, color, surface, x, y):
    textobj = fonti.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


# ---------------------------
# Golden boost timer (NO sleep/thread)
# ---------------------------

def start_golden_boost():
    global golden_boost_activated, golden_boost_end_ms, my_timer
    golden_boost_activated = True
    golden_boost_end_ms = pygame.time.get_ticks() + 6000
    my_timer = 6


def update_golden_boost_timer():
    global golden_boost_activated, my_timer
    if not golden_boost_activated:
        return

    remaining_ms = golden_boost_end_ms - pygame.time.get_ticks()
    if remaining_ms <= 0:
        golden_boost_activated = False
        my_timer = 0
        safe_sound_stop(golden_boost_music)
        safe_music_unpause()
    else:
        my_timer = max(0, int((remaining_ms + 999) // 1000))


# ---------------------------
# Boost checks
# ---------------------------

def golden_boost_check():
    global golden_boost_available, score, last_golden_boost_grabbed, golden_boost_x, golden_boost_y, game_level_running
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


def fire_boost_check():
    global fire_boost_available, score, last_fire_boost_grabbed, fire_boost_x, fire_boost_y, game_level_running
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


def speed_boost_check():
    global speed_boost_available, score, last_speed_boost_grabbed, speed_boost_x, speed_boost_y, game_level_running
    if game_level_running == "1":
        if score - last_speed_boost_grabbed > 9 and not speed_boost_available:
            speed_boost_available = True
            speed_boost_x = random.randint(10, 520)
            speed_boost_y = random.randint(10, 520)
    elif game_level_running == "2":
        if score - last_speed_boost_grabbed > 14 and not speed_boost_available:
            speed_boost_available = True
            speed_boost_x = random.randint(10, 520)
            speed_boost_y = random.randint(10, 520)
    elif game_level_running == "3":
        if score - last_speed_boost_grabbed > 19 and not speed_boost_available:
            speed_boost_available = True
            speed_boost_x = random.randint(10, 520)
            speed_boost_y = random.randint(10, 520)


# ---------------------------
# Difficulty / collision / movement
# ---------------------------

def check_not_same_starting_direction():
    global snowball_x_direction, snowball_y_direction
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


def check_difficulty():
    global score, snowball_y_direction, snowball_x_direction, counter
    if counter - score == 0:
        if snowball_x_direction > 0:
            snowball_x_direction += 1
        elif snowball_x_direction < 0:
            snowball_x_direction -= 1

        if snowball_y_direction > 0:
            snowball_y_direction += 1
        elif snowball_y_direction < 0:
            snowball_y_direction -= 1

        counter += 10


def check_collision(playerx, playery, ballx, bally):
    global player_x_direction, player_y_direction, snowball_x_direction, snowball_y_direction
    if abs(playerx - ballx) < 40 and abs(playery - bally) < 40:
        player_x_direction = 0
        player_y_direction = 0
        snowball_x_direction = 0
        snowball_y_direction = 0
        game_over()


def game_over():
    global game_Over, pending_death_sound, death_sound_playing
    draw_text('Game Over', my_font_game_over, red, screen, 80, 250)
    draw_text('Press Space to Restart ', my_font, black, screen, 130, 340)

    safe_music_pause()
    debug("GAME OVER -> queued death sound (waiting for input)")
    pending_death_sound = True
    death_sound_playing = False



def update_player_position():
    global player_x, player_y, player_x_direction, player_y_direction, player_speed

    if player_x_direction > 0:
        if player_x < 600 - player_width:
            player_x += player_x_direction * player_speed
    if player_x_direction < 0:
        if player_x > -2:
            player_x += player_x_direction * player_speed
    if player_y_direction > 0:
        if player_y < 600 - player_height:
            player_y += player_y_direction * player_speed
    if player_y_direction < 0:
        if player_y > 8:
            player_y += player_y_direction * player_speed


def update_ball_position():
    global snowball_x, snowball_y, snowball_x_direction, snowball_y_direction, score

    if snowball_x_direction > 0:
        if snowball_x < 528:
            snowball_x += snowball_x_direction
        else:
            snowball_x_direction *= -1
            score += 1
    elif snowball_x_direction < 0:
        if snowball_x > 8:
            snowball_x += snowball_x_direction
        else:
            snowball_x_direction *= -1
            score += 1

    if snowball_y_direction > 0:
        if snowball_y < 528:
            snowball_y += snowball_y_direction
        else:
            snowball_y_direction *= -1
            score += 1
    elif snowball_y_direction < 0:
        if snowball_y > 8:
            snowball_y += snowball_y_direction
        else:
            snowball_y_direction *= -1
            score += 1


# ---------------------------
# Async main menu + game levels (pygbag friendly)
# ---------------------------

async def main_menu():
    global count, snow_list, game_level_running

    background = pygame.image.load("graphics/background/background_main_menu.png")

    # Start menu music (may fail in browser until user interaction; still safe)
    safe_music_load_play("music/New Super Mario Bros. Wii OST - Track 05 - World 3.mp3", loops=-1)

    fat_noot_noot_img = pygame.image.load("graphics/player/fat pingu.png")

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

        if (button_1.collidepoint((mx, my)) or surround_button_1.collidepoint((mx, my))) and click:
            await game_level(1)
        if (button_2.collidepoint((mx, my)) or surround_button_2.collidepoint((mx, my))) and click:
            await game_level(2)
        if (button_3.collidepoint((mx, my)) or surround_button_3.collidepoint((mx, my))) and click:
            await game_level(3)

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

        # Draw snow
        for i in range(len(snow_list)):
            pygame.draw.circle(screen, snow_list[i][0], snow_list[i][1], 5)
            snow_list[i][1][0] += 1

            if snow_list[i][1][0] > 608:
                y = random.randrange(0, 2)
                snow_list[i][1][1] = y
                x = random.randrange(-300, 600)
                snow_list[i][1][0] = x

        click = False

        for event in pygame.event.get():
            if event.type in (MOUSEBUTTONDOWN, KEYDOWN):
                unlock_audio()
                try_start_death_sound_from_input()

            if event.type == QUIT:
                pygame.quit()
                return
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                return
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                click = True


        pygame.display.update()
        timer.tick(60)
        await asyncio.sleep(0)


async def game_level(level):
    global game_level_running
    global player_speed, fire_boost_available, speed_boost_available, golden_boost_activated, golden_boost_available
    global snowball_x_direction, snowball_y_direction, snowball_x, snowball_y
    global fire_boost_y, fire_boost_x, last_fire_boost_grabbed
    global speed_boost_x, speed_boost_y, last_speed_boost_grabbed
    global golden_boost_x, golden_boost_y, last_golden_boost_grabbed
    global player_x, player_y
    global score, high_score, previous_score
    global player_y_direction, player_x_direction
    global counter, game_Over

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

    # Load images
    snowball_Img = pygame.image.load(snowball_img_path)
    player_Img = pygame.image.load("graphics/player/noot-noot.png")
    player_Img_golden = pygame.image.load("graphics/player/Golden-noot-noot.png")
    background = pygame.image.load(background_path)
    speed_boost_Img = pygame.image.load("graphics/boost/red_fish.png")
    fire_boost_Img = pygame.image.load("graphics/boost/fire.png")
    golden_boost_Img = pygame.image.load("graphics/boost/golden_fish.png")

    # Start level music
    safe_music_load_play("music/Freeze-Man-Stage-Iceberg-Area-M.mp3", loops=-1)

    hud_color = white if level in (1, 3) else black

    running = True
    while running:
        update_golden_boost_timer()

        update_ball_position()
        update_player_position()
        check_difficulty()
        fire_boost_check()
        speed_boost_check()
        golden_boost_check()
        check_not_same_starting_direction()

        screen.fill((0, 0, 0))
        screen.blit(background, (0, 0))

        snowball_rect = screen.blit(snowball_Img, (snowball_x, snowball_y))

        if not golden_boost_activated:
            gamer_rect = screen.blit(player_Img, (player_x, player_y))
        else:
            gamer_rect = screen.blit(player_Img_golden, (player_x, player_y))

        if not golden_boost_activated:
            check_collision(gamer_rect.centerx, gamer_rect.centery, snowball_rect.centerx, snowball_rect.centery)

        draw_text("Score: " + str(score), other_font_smaller, hud_color, screen, 265, 17)
        draw_text("Highest Score: " + str(high_score), other_font_smaller, hud_color, screen, 18, 17)
        draw_text("Previous Score: " + str(previous_score), other_font_smaller, hud_color, screen, 400, 17)

        # Fire boost
        if fire_boost_available:
            fire_boost_rect = screen.blit(fire_boost_Img, (fire_boost_x, fire_boost_y))
            if gamer_rect.colliderect(fire_boost_rect):
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

                fire_boost_x = -100
                fire_boost_y = -100
                last_fire_boost_grabbed = score
                fire_boost_available = False

        # Speed boost
        if speed_boost_available:
            speed_boost_rect = screen.blit(speed_boost_Img, (speed_boost_x, speed_boost_y))
            if gamer_rect.colliderect(speed_boost_rect):
                player_speed += 1
                speed_boost_x = -100
                speed_boost_y = -100
                last_speed_boost_grabbed = score
                speed_boost_available = False

        # Golden boost
        if golden_boost_available:
            golden_boost_rect = screen.blit(golden_boost_Img, (golden_boost_x, golden_boost_y))
            if gamer_rect.colliderect(golden_boost_rect):
                safe_music_pause()
                safe_sound_play(golden_boost_music, loops=-1)
                start_golden_boost()

                golden_boost_x = -100
                golden_boost_y = -100
                last_golden_boost_grabbed = score
                golden_boost_available = False

        if golden_boost_activated:
            display_timer = font.render("Time left: " + str(my_timer), True, hud_color, white)
            screen.blit(display_timer, (300, 572))

        draw_text("Speed: " + str(player_speed - 2), other_font_smaller, hud_color, screen, 18, 572)

        for event in pygame.event.get():
            if event.type in (MOUSEBUTTONDOWN, KEYDOWN):
                unlock_audio()
                try_start_death_sound_from_input()

            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

                    safe_music_pause()
                    safe_sound_stop(nootnoot_sound)
                    safe_sound_stop(golden_boost_music)

                    safe_music_load_play("music/New Super Mario Bros. Wii OST - Track 05 - World 3.mp3", loops=-1)
                    game_level_running = "0"

                    snowball_x = 300
                    snowball_y = 300
                    snowball_x_direction = random.choice(random_number)
                    snowball_y_direction = random.choice(random_number)

                    player_x = 275
                    player_y = 500

                    previous_score = score
                    if score > high_score:
                        high_score = score

                    player_speed = 3

                    last_speed_boost_grabbed = 0
                    speed_boost_y = -100
                    speed_boost_x = -100
                    speed_boost_available = False

                    last_fire_boost_grabbed = 0
                    fire_boost_x = -100
                    fire_boost_y = -100
                    fire_boost_available = False

                    last_golden_boost_grabbed = 0
                    golden_boost_x = -100
                    golden_boost_y = -100
                    golden_boost_available = False
                    golden_boost_activated = False

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

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    player_x_direction = 0
                if event.key == pygame.K_RIGHT:
                    player_x_direction = 0
                if event.key == pygame.K_UP:
                    player_y_direction = 0
                if event.key == pygame.K_DOWN:
                    player_y_direction = 0

                if event.key == pygame.K_SPACE and game_Over:
                    safe_sound_stop(nootnoot_sound)
                    safe_music_unpause()

                    snowball_x = 300
                    snowball_y = 300
                    snowball_x_direction = random.choice(random_number)
                    snowball_y_direction = random.choice(random_number)

                    player_x = 275
                    player_y = 500

                    previous_score = score
                    if score > high_score:
                        high_score = score

                    player_speed = 3

                    last_speed_boost_grabbed = 0
                    speed_boost_y = -100
                    speed_boost_x = -100
                    speed_boost_available = False

                    last_fire_boost_grabbed = 0
                    fire_boost_x = -100
                    fire_boost_y = -100
                    fire_boost_available = False

                    last_golden_boost_grabbed = 0
                    golden_boost_x = -100
                    golden_boost_y = -100
                    golden_boost_available = False
                    golden_boost_activated = False

                    game_Over = False
                    score = 0
                    counter = 10

        pygame.display.update()
        timer.tick(30)
        await asyncio.sleep(0)


# ---------------------------
# Entry point for pygbag
# ---------------------------

async def main():
    await main_menu()

asyncio.run(main())
