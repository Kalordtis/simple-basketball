Jacksonville Hoops🏀
A fast-paced local basketball game built with Python and Pygame. Play 1-player against a bot or 2-player locally on the same keyboard.

Features
1P vs Bot mode

2P Local Multiplayer mode

First player to 11 points wins

Simple basketball physics with gravity, bouncing, air drag, and player movement

Adjustable aiming arrow that sweeps through different shot angles

Hoops placed against both sides of the court

Basket detection that only awards a point when the ball actually travels downward through the rim

Clean menu, scoreboard, win screen, and court graphics

No external physics engine required — the game uses Pygame only

Requirements
Python 3.9+ recommended

Pygame

Install Pygame with:

pip install pygame
If pip does not work, try:

python3 -m pip install pygame
How to Run
Save the program as jacksonville.py.

Open the project folder in VS Code or a terminal.

Install Pygame if you have not already.

Run:

python jacksonville.py
On some systems, use:

python3 jacksonville.py
Controls
Player 1 — Blue
Action	Key
Move left	A
Move right	D
Jump	W
Shoot	S
Player 2 — Red
Action	Key
Move left	←
Move right	→
Jump	↑
Shoot	↓
In 1P vs Bot, the red player is controlled automatically.

Menu
Press 1 — Play vs Bot

Press 2 — Two Player

Press ESC during a game — Return to menu

Win Screen
Press ENTER — Play again

Press ESC — Return to menu

How Shooting Works
When a player has the ball, a yellow aiming arrow appears above them. The arrow continuously sweeps through a range of angles.

Press the shoot key when the arrow is pointing in the direction you want.

The ball is launched using the current aiming angle and a fixed shot speed. The game then applies gravity and other physics to the ball.

Scoring
Every successful basket is worth 1 point.

A basket is counted only when:

The ball is moving downward.

The ball crosses the height of the rim.

The center of the ball is within the rim's opening.

This prevents shots that merely pass near the hoop from being counted as baskets.

Project Structure
The program is contained in a single Python file and is organized into several main sections:

Setup — Initializes Pygame and the game window.

Constants — Stores colors, court dimensions, physics values, and aiming settings.

Helpers — Utility functions such as clamping values and calculating distance.

Ball — Handles ball movement, physics, launching, trails, and drawing.

Player — Handles movement, jumping, aiming, shooting, and drawing.

Hoop — Handles hoop graphics and basket detection.

Court Drawing — Draws the basketball court and background.

Gameplay Helpers — Handles ball pickup and shooting.

Bot AI — Controls the red player in 1P mode.

Menu — Handles game-mode selection.

Win Screen — Displays the winner and restart options.

Game Loop — Processes input, physics, collisions, scoring, and rendering.

Main — Starts the menu/game cycle.

Physics
The game uses custom Pygame-based physics rather than a third-party physics library.

Important physics settings include:

Ball gravity

Player gravity

Air drag

Floor bounce

Wall bounce

Player acceleration

Maximum player speed

Jump velocity

Shot speed

These values can be changed near the top of the file to adjust the feel and difficulty of the game.

Customization
The easiest settings to modify are near the top of the file.

For example:

HOOP_Y = 330
SHOT_SPEED = 600.0
GRAVITY_BALL = 1500.0
JUMP_VELOCITY = 700.0
Changing these values lets you experiment with hoop height, shot power, ball gravity, and jump strength.

Troubleshooting
ModuleNotFoundError: No module named 'pygame'
Install Pygame:

python -m pip install pygame
The game window immediately closes
Run the program from VS Code's terminal instead of double-clicking the .py file so you can see any error message.

Controls are not working
Make sure the game window is focused and that you are pressing the correct keys listed above.

Technologies
Python

Pygame

Object-oriented programming

Real-time game loop

2D physics

Keyboard input handling

Basic bot AI

Collision and scoring logic

Goal
The objective is simple: score 11 points before your opponent does.

Have fun playing Jacksonville!
