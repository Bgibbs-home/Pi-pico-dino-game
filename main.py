from machine import Pin, I2C
from time import sleep
import random
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

# LCD configuration
I2C_ADDR = 0x27  # Replace with your LCD I2C address
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)  # 16x2 LCD

# Button configuration
jump_button = Pin(2, Pin.IN, Pin.PULL_DOWN)
duck_button = Pin(3, Pin.IN, Pin.PULL_DOWN)

# Game variables
dino_pos = 1  # Dino's position (1: ground, 0: jump, 2: duck)
obstacle_pos = 15
bird_pos = -1  # Bird position (-1 means no bird)
score = 0
game_over = False

# Display Dino and obstacles
def display_game():
    lcd.clear()

    # Top row: Bird or empty space
    if bird_pos >= 0:
        top_row = " " * bird_pos + "🐦" + " " * (15 - bird_pos)
    else:
        top_row = " " * 16
    lcd.putstr(top_row[:16])

    # Bottom row: Dino and cactus
    if obstacle_pos >= 0:
        obstacle = "🌵"
        bottom_row = " " * (obstacle_pos - 1) + obstacle if obstacle_pos > 0 else obstacle
    else:
        bottom_row = " " * 16

    if dino_pos == 1:  # Dino on the ground
        bottom_row = "🦖" + bottom_row[1:]
    elif dino_pos == 2:  # Dino ducking
        bottom_row = "_" + bottom_row[1:]  # Show ducking
    lcd.move_to(0, 1)
    lcd.putstr(bottom_row[:16])

# Check collision
def check_collision():
    global game_over
    if obstacle_pos == 1 and dino_pos == 1:  # Dino on ground and hits cactus
        game_over = True
    if bird_pos == 0 and dino_pos == 0:  # Dino jumping and hits bird
        game_over = True

# Wait for both buttons to be pressed
def wait_for_both_buttons(message):
    lcd.clear()
    lcd.putstr(message)
    while True:
        if jump_button.value() and duck_button.value():
            break
        sleep(0.1)

# Main game loop
def game_loop():
    global dino_pos, obstacle_pos, bird_pos, score, game_over

    # Start message
    wait_for_both_buttons("Press both to start")

    lcd.clear()
    lcd.putstr("Dino Game Start!")
    sleep(2)

    while not game_over:
        # Handle Dino's actions
        if jump_button.value():
            dino_pos = 0  # Jump
        elif duck_button.value():
            dino_pos = 2  # Duck
        else:
            dino_pos = 1  # Ground

        # Move obstacle
        obstacle_pos -= 1
        if obstacle_pos < 0:
            obstacle_pos = random.randint(10, 15)  # Respawn obstacle
            score += 1  # Increment score

        # Spawn or move bird occasionally
        if random.random() < 0.1 and bird_pos == -1:
            bird_pos = random.randint(10, 15)  # Spawn bird
        if bird_pos >= 0:
            bird_pos -= 1
            if bird_pos < 0:  # Bird has moved out of view
                bird_pos = -1

        # Update game display
        display_game()
        check_collision()

        # Delay for game speed
        sleep(0.3)

    # Game Over
    lcd.clear()
    lcd.putstr("Game Over!")
    lcd.move_to(0, 1)
    lcd.putstr(f"Score: {score}")
    wait_for_both_buttons("Press both to reset")
    restart_game()

# Restart the game
def restart_game():
    global dino_pos, obstacle_pos, bird_pos, score, game_over
    dino_pos = 1
    obstacle_pos = 15
    bird_pos = -1
    score = 0
    game_over = False
    game_loop()

# Start the game
game_loop()
