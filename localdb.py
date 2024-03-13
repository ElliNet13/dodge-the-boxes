import pygame
import requests
import random
import sqlite3
from pygame.locals import QUIT, MOUSEBUTTONDOWN, KEYDOWN, K_LEFT, K_RIGHT
from io import BytesIO
import os
from time import sleep as wait
import os
import hashlib

def hash_folder(folder_path):
    sha256 = hashlib.sha256()

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)

            # Exclude files with the .py extension and the script file itself
            if not file_path.endswith(".py") and file_path != os.path.abspath(__file__):
                with open(file_path, "rb") as f:
                    # Read the file in chunks to avoid memory issues with large files
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256.update(chunk)

    return sha256.hexdigest()

def change_icon(icon):
    if os.path.exists(icon + ".ico"):
        icon = pygame.image.load(icon + ".ico")
        pygame.display.set_icon(icon)

# Set up game variables
icon_url = "https://ellinet13.github.io/favicon.ico"
alive = True
width, height = 400, 300
player_size = 50
player_x = width // 2 - player_size // 2
player_y = height - player_size - 10
falling_objects = []
speed = 20
total_dodged = 0  # Keep track of total dodged objects

# Connect to SQLite database
conn = sqlite3.connect('game_data.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS worldrecord (record INTEGER)''')

# Get current world record
cursor.execute("SELECT * FROM worldrecord")
record_row = cursor.fetchone()
if record_row:
    current_record = record_row[0]
else:
    current_record = 0

pygame.init()
print("This game was made by ElliNet13")
if not hash_folder(".") == "b0ff5077dbcba3a7ef019a9855d51249b53f0d3a514a175860a2b728ed5a67ff":
  print("But has been modified")
print("This is a game where you have to dodge falling boxes.")
print("There is no end to the game")
print("Well... the only end is game over")
print(f"The world record is currently at {current_record}")
print("Try beating it!")
DISPLAYSURF = pygame.display.set_mode((width, height))
pygame.display.set_caption('Dodge the boxes!')
response = requests.get(icon_url)
icon = pygame.image.load(BytesIO(response.content))
pygame.display.set_icon(icon)

try:
    if os.path.exists("song.mp3"):
        pygame.mixer.init()
        pygame.mixer.music.load("song.mp3")
        pygame.mixer.music.play(-1)  # -1 means play on loop
except Exception as e:
    if isinstance(e, pygame.error) and "dsp: No such audio device" in str(e):
        print("We may not be able to play our music")
        print("as you don't have an audio device")
        print("but that won't stop us from letting you play the game!")
    else:
        print("We may not be able to play our music")
        print("as there was an error")
        print("—Error details—")
        print(e)
        print("———————————————")
        print("but that won't stop us from letting you play the game!")


change_icon("icon")

# Function to generate falling objects
def generate_object():
    size = random.randint(20, 40)
    x = random.randint(0, width - size)
    y = 0
    speed = random.randint(2, 5)
    return {"rect": pygame.Rect(x, y, size, size), "speed": speed}

# Function to update player's position
def update_player_position(dx):
    global player_x
    player_x += dx
    if player_x < 0:
        player_x = 0
    elif player_x > width - player_size:
        player_x = width - player_size

# Define on-screen controls
left_button = pygame.Rect(20, height - 80, 60, 60)
right_button = pygame.Rect(width - 80, height - 80, 60, 60)

clock = pygame.time.Clock()

while alive:
    for event in pygame.event.get():
        if event.type == QUIT:
            alive = False
        elif event.type == MOUSEBUTTONDOWN:
            # Check if on-screen buttons are tapped
            if event.button == 1:
                if left_button.collidepoint(event.pos):
                    update_player_position(-speed)
                elif right_button.collidepoint(event.pos):
                    update_player_position(speed)
        elif event.type == KEYDOWN:
            if event.key == K_LEFT:
                update_player_position(-speed)
            elif event.key == K_RIGHT:
                update_player_position(speed)

    # Clear the screen
    DISPLAYSURF.fill((0, 0, 0))

    # Generate falling objects
    if random.randint(0, 100) < 5:
        falling_objects.append(generate_object())
        total_dodged += 1  # Increment total dodged count

    # Move and draw falling objects
    for obj in falling_objects:
        obj["rect"].move_ip(0, obj["speed"])
        pygame.draw.rect(DISPLAYSURF, (255, 0, 0), obj["rect"])

    # Check for collisions with player
    for obj in falling_objects:
        if obj["rect"].colliderect(pygame.Rect(player_x, player_y, player_size, player_size)):
            alive = False

    # Remove objects that are out of the screen
    falling_objects = [obj for obj in falling_objects if obj["rect"].top < height]

    # Draw player
    pygame.draw.rect(DISPLAYSURF, (0, 0, 255), (player_x, player_y, player_size, player_size))

    # Draw on-screen controls
    pygame.draw.rect(DISPLAYSURF, (0, 255, 0), left_button)
    pygame.draw.rect(DISPLAYSURF, (0, 255, 0), right_button)

    pygame.display.update()
    clock.tick(30)

# Remove on-screen controls
pygame.draw.rect(DISPLAYSURF, (0, 0, 0), left_button)
pygame.draw.rect(DISPLAYSURF, (0, 0, 0), right_button)

# Draw everything
for obj in falling_objects:
    obj["rect"].move_ip(0, obj["speed"])
    pygame.draw.rect(DISPLAYSURF, (255, 0, 0), obj["rect"])

pygame.draw.rect(DISPLAYSURF, (0, 0, 255), (player_x, player_y, player_size, player_size))

# Tell pygame to draw
pygame.display.update()

# Display game over message
change_icon("warning")
pygame.display.set_caption('Oof...')
print("Oof...")
wait(2)
pygame.quit()
print("Game over! You dodged", total_dodged, "objects.")

# Update world record if necessary
if current_record < total_dodged:
    print(f"New world record! Congratulations! The last world record was {current_record}! Your record is {total_dodged}! And that is more so you did it! You are the best!... Well... for now. Keep trying to beat the world record!")
    cursor.execute("UPDATE worldrecord SET record = ?", (total_dodged,))
else:
    print("You didn't beat the world record this time. Keep trying!")

# Commit changes and close connection
conn.commit()
conn.close()