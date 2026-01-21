import random
import time

import pygame as py

py.init()


WHITE = (255, 255, 255)
GREY = (20, 20, 20)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

size = (1001, 701)
screen = py.display.set_mode(size)
py.display.set_caption("Maze Game with AIRSTRIKE")
clock = py.time.Clock()

width = 25
cols = int(size[0] / width)
rows = int(size[1] / width)

# Load the images in and size them

player_image = py.image.load("catphoto.png")
player_image = py.transform.scale(player_image, (width - 4, width - 4))

goal_image = py.image.load("fish.png")
goal_image = py.transform.scale(goal_image, (width - 4, width - 4))

explosion_image = py.image.load("explosion.png")
explosion_image = py.transform.scale(explosion_image, (width * 5, width * 5))

# Maze generation initialization


class Cell:
    def __init__(self, x, y):
        global width
        self.x = x * width
        self.y = y * width

        self.visited = False
        self.walls = [True, True, True, True]
        self.neighbors = []

        # No neighbor at first
        self.top = 0
        self.right = 0
        self.bottom = 0
        self.left = 0

    # Drawing out the walls for the maze

    def draw(self):
        py.draw.rect(screen, WHITE, (self.x, self.y, width, width))

        # Top wall

        if self.walls[0]:
            py.draw.line(screen, BLACK, (self.x, self.y), ((self.x + width), self.y), 1)

        # Right wall

        if self.walls[1]:
            py.draw.line(
                screen,
                BLACK,
                ((self.x + width), self.y),
                ((self.x + width), (self.y + width)),
                1,
            )

        # Bottom wall

        if self.walls[2]:
            py.draw.line(
                screen,
                BLACK,
                ((self.x + width), (self.y + width)),
                (self.x, (self.y + width)),
                1,
            )

        # Left wall

        if self.walls[3]:
            py.draw.line(screen, BLACK, (self.x, (self.y + width)), (self.x, self.y), 1)

    # Check the neighbors

    def checkNeighbors(self):
        # Check and save the grids, make sure not on edge of screen

        if int(self.y / width) - 1 >= 0:
            self.top = grid[int(self.y / width) - 1][int(self.x / width)]
        if int(self.x / width) + 1 <= cols - 1:
            self.right = grid[int(self.y / width)][int(self.x / width) + 1]
        if int(self.y / width) + 1 <= rows - 1:
            self.bottom = grid[int(self.y / width) + 1][int(self.x / width)]
        if int(self.x / width) - 1 >= 0:
            self.left = grid[int(self.y / width)][int(self.x / width) - 1]

        # Add unvisited neighbor to the list

        if self.top != 0:
            if self.top.visited == False:
                self.neighbors.append(self.top)
        if self.right != 0:
            if self.right.visited == False:
                self.neighbors.append(self.right)
        if self.bottom != 0:
            if self.bottom.visited == False:
                self.neighbors.append(self.bottom)
        if self.left != 0:
            if self.left.visited == False:
                self.neighbors.append(self.left)

        # Return if any unvisited neighbor exist or just end the check

        if len(self.neighbors) > 0:
            return self.neighbors[random.randrange(0, len(self.neighbors))]
        else:
            return False


# Removes the walls between the two cells
# Randomly goes a direction for the path carver and goes to unvisited neighbor until all paths has been completed


def removeWalls(current_cell, next_cell):
    x = int(current_cell.x / width) - int(next_cell.x / width)
    y = int(current_cell.y / width) - int(next_cell.y / width)
    if x == -1:
        current_cell.walls[1] = False
        next_cell.walls[3] = False
    elif x == 1:
        current_cell.walls[3] = False
        next_cell.walls[1] = False
    elif y == -1:
        current_cell.walls[2] = False
        next_cell.walls[0] = False
    elif y == 1:
        current_cell.walls[0] = False
        next_cell.walls[2] = False


# Grid creation to fill it with cells

grid = []
for y in range(rows):
    grid.append([])
    for x in range(cols):
        grid[y].append(Cell(x, y))

# Generate the maze completely before showing it
stack = []
current_cell = grid[0][0]
current_cell.visited = True

# Player starting position (top left)
player_x = 0
player_y = 0

# Ending position (bottom right)
end_x = cols - 1
end_y = rows - 1

# Timer set to 120 countdown
start_time = py.time.get_ticks()
countdown_duration = 120
time_remaining = countdown_duration
game_won = False
game_lost = False
loss_reason = ""  # Empty string for now, add reason later

# Explosion variables
explosion_active = False
explosion_x = 0
explosion_y = 0
explosion_start_time = 0
explosion_duration = 2000
last_explosion_spawn = py.time.get_ticks()
explosion_interval = 2000

# Change movement speed so its not too fast
last_move_time = 0
move_delay = 150

while True:
    next_cell = current_cell.checkNeighbors()

    if next_cell != False:
        current_cell.neighbors = []
        stack.append(current_cell)
        removeWalls(current_cell, next_cell)
        current_cell = next_cell
        current_cell.visited = True

    elif len(stack) > 0:
        current_cell = stack.pop()

    else:
        break  # Maze generation complete

# Main display loop, keep the game running until pressed quit
endgame = False
while not endgame:
    for event in py.event.get():
        if event.type == py.QUIT:
            endgame = True

        # Check for restart key only when game has ended

        if event.type == py.KEYDOWN:
            if event.key == py.K_r and (game_won or game_lost):
                # Reset game state
                player_x = 0
                player_y = 0
                start_time = py.time.get_ticks()
                time_remaining = countdown_duration
                game_won = False
                game_lost = False
                loss_reason = ""

                # Reset explosion state
                explosion_active = False
                last_explosion_spawn = py.time.get_ticks()

                # Regenerate maze if restarted
                grid = []
                for y in range(rows):
                    grid.append([])
                    for x in range(cols):
                        grid[y].append(Cell(x, y))

                stack = []
                current_cell = grid[0][0]
                current_cell.visited = True

                while True:
                    next_cell = current_cell.checkNeighbors()

                    if next_cell != False:
                        current_cell.neighbors = []
                        stack.append(current_cell)
                        removeWalls(current_cell, next_cell)
                        current_cell = next_cell
                        current_cell.visited = True

                    elif len(stack) > 0:
                        current_cell = stack.pop()

                    else:
                        break

    if not game_won and not game_lost:
        # Calculate time remaining
        elapsed_time = (py.time.get_ticks() - start_time) / 1000
        time_remaining = countdown_duration - elapsed_time

        # Check if time ran out
        if time_remaining <= 0:
            game_lost = True
            time_remaining = 0
            loss_reason = "TIMER RUN OUT"

        current_time = py.time.get_ticks()

        # Spawn new explosion every 2 seconds
        if current_time - last_explosion_spawn >= explosion_interval:
            explosion_active = True
            explosion_x = random.randint(0, cols - 5)
            explosion_y = random.randint(0, rows - 5)
            explosion_start_time = current_time
            last_explosion_spawn = current_time

        # Check if explosion should disappear
        if (
            explosion_active
            and current_time - explosion_start_time >= explosion_duration
        ):
            explosion_active = False

        # Check if player is hit by explosion
        if explosion_active:
            if (
                player_x >= explosion_x
                and player_x < explosion_x + 5
                and player_y >= explosion_y
                and player_y < explosion_y + 5
            ):
                time.sleep(1)
                game_lost = True
                loss_reason = "YOU GOT HIT BY AN AIR STRIKE"

        if current_time - last_move_time > move_delay:
            keys = py.key.get_pressed()
            moved = False

            # Press wasd to move in either direction
            # Check if the direction the sprite is moving does not have a wall or side of screen

            if keys[py.K_w] and not moved:
                if player_y > 0 and not grid[player_y][player_x].walls[0]:
                    player_y -= 1
                    moved = True
            if keys[py.K_s] and not moved:
                if player_y < rows - 1 and not grid[player_y][player_x].walls[2]:
                    player_y += 1
                    moved = True
            if keys[py.K_a] and not moved:
                if player_x > 0 and not grid[player_y][player_x].walls[3]:
                    player_x -= 1
                    moved = True
            if keys[py.K_d] and not moved:
                if player_x < cols - 1 and not grid[player_y][player_x].walls[1]:
                    player_x += 1
                    moved = True

            if moved:
                last_move_time = current_time

    screen.fill(GREY)

    # Draw the completed maze
    for y in range(rows):
        for x in range(cols):
            grid[y][x].draw()

    # Draw the ending point (using fish image)
    screen.blit(goal_image, (end_x * width + 2, end_y * width + 2))

    # Draw explosion
    if explosion_active and not game_won:
        screen.blit(explosion_image, (explosion_x * width, explosion_y * width))

    # Draw the player (image)
    screen.blit(player_image, (player_x * width + 2, player_y * width + 2))

    # Check if player reached the end
    if player_x == end_x and player_y == end_y and not game_won and not game_lost:
        game_won = True

    # The timer on screen
    if not game_won and not game_lost:
        font_timer = py.font.Font(None, 48)
        timer_text = font_timer.render(f"Time: {int(time_remaining)}s", True, BLACK)
        screen.blit(timer_text, (10, 10))

    # Winning screen
    if game_won:
        font_b = py.font.Font(None, 74)
        text = font_b.render("You Win :)", True, GREEN)
        screen.blit(text, (size[0] // 2 - 120, size[1] // 2 - 100))

        font_s = py.font.Font(None, 36)
        time_text = font_s.render(f"Time Left: {time_remaining} seconds", True, BLACK)
        screen.blit(time_text, (size[0] // 2 - 150, size[1] // 2 - 20))

        restart_text = font_s.render("Press R to Restart", True, BLACK)
        screen.blit(restart_text, (size[0] // 2 - 120, size[1] // 2 + 40))

    # Losing screen for different reasons
    if game_lost:
        font_b = py.font.Font(None, 74)
        text = font_b.render("YOU LOSE", True, RED)
        screen.blit(text, (size[0] // 2 - 150, size[1] // 2 - 100))

        font_s = py.font.Font(None, 36)
        time_text = font_s.render(loss_reason, True, RED)
        screen.blit(time_text, (size[0] // 2 - 180, size[1] // 2 - 20))

        restart_text = font_s.render("Press R to Restart", True, RED)
        screen.blit(restart_text, (size[0] // 2 - 120, size[1] // 2 + 40))

    py.display.flip()
    clock.tick(60)

py.quit()
