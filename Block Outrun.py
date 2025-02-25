import pygame
import random
import sys

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 500, 600
PLAYER_WIDTH, PLAYER_HEIGHT = 50, 50
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 50, 50
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
SPEED = 5
INITIAL_OBSTACLE_SPEED = 3
STAGE_INCREMENT = 20
MAX_PERCENTAGE = 100
WIN_SCORE = 115
VOLUME = 0.5
BOOST_POWER = -15  # Negative because moving up reduces y-coordinate
BOOST_COOLDOWN = 60  # Frames (1 second at 60 FPS)
BOOST_COLOR = (0, 255, 255)  # Cyan color for boost indicator

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge the Falling Obstacles!")

# Font setup
font = pygame.font.Font(None, 36)

# Clock setup
clock = pygame.time.Clock()

# Global variables
score = 0
running = True

# Load sounds with error handling
try:
    collision_sound = pygame.mixer.Sound("collision.wav")
    score_sound = pygame.mixer.Sound("score.wav")
    background_music = pygame.mixer.Sound("background.wav")
    # Set initial volume for all sounds
    collision_sound.set_volume(VOLUME)
    score_sound.set_volume(VOLUME)
    background_music.set_volume(VOLUME)
    background_music.play(-1)
except (pygame.error, FileNotFoundError) as e:
    print(f"Warning: Sound files not found. Playing without sound. Error: {e}")
    class DummySound:
        def play(self, *args): pass
        def set_volume(self, volume): pass
    collision_sound = score_sound = background_music = DummySound()

def draw_text(text, x, y, color=(0, 0, 0)):
    text_surface = font.render(str(text), True, color)
    screen.blit(text_surface, (x, y))

def draw_speed_bar(score):
    percentage = min((score / WIN_SCORE) * 100, 100)
    bar_width = 400 * (percentage / 100)
    pygame.draw.rect(screen, (200, 200, 200), (50, 20, 400, 20))
    pygame.draw.rect(screen, (0, 255, 0), (50, 20, bar_width, 20))
    pygame.draw.rect(screen, (0, 0, 0), (50, 20, 400, 20), 2)
    draw_text(f"Progress: {int(percentage)}%", WIDTH//2 - 70, 50)

def draw_volume_slider(volume):
    slider_x = WIDTH//2 - 100
    slider_y = HEIGHT//2 + 50
    slider_width = 200
    slider_height = 20
    
    pygame.draw.rect(screen, (200, 200, 200), (slider_x, slider_y, slider_width, slider_height))
    pygame.draw.rect(screen, (0, 255, 0), (slider_x, slider_y, slider_width * volume, slider_height))
    pygame.draw.rect(screen, (0, 0, 0), (slider_x, slider_y, slider_width, slider_height), 2)
    draw_text(f"Volume: {int(volume * 100)}%", slider_x, slider_y - 30)

def draw_fps():
    fps = int(clock.get_fps())
    draw_text(f"FPS: {fps}", WIDTH - 100, 10)

def draw_boost_meter(boost_cooldown):
    meter_width = 100
    meter_height = 10
    x = WIDTH - meter_width - 10
    y = 40
    
    pygame.draw.rect(screen, (200, 200, 200), (x, y, meter_width, meter_height))
    available_boost = (BOOST_COOLDOWN - boost_cooldown) / BOOST_COOLDOWN
    pygame.draw.rect(screen, BOOST_COLOR, (x, y, meter_width * available_boost, meter_height))
    pygame.draw.rect(screen, (0, 0, 0), (x, y, meter_width, meter_height), 1)
    draw_text("Boost", x - 50, y)

def quit_game():
    pygame.mixer.quit()
    pygame.quit()
    sys.exit()

def how_to_play_menu():
    waiting = True
    while waiting:
        screen.fill(WHITE)
        
        instructions = [
            "How to Play",
            "",
            "Controls:",
            "← → Arrow Keys: Move left/right",
            "↑ Arrow Key: Activate boost",
            "ESC: Pause game",
            "P: Resume game",
            "",
            "Objectives:",
            "- Dodge the falling obstacles",
            "- Reach score 115 to win",
            "- Use boost wisely to escape",
            "",
            "Tips:",
            "- Watch your boost meter",
            "- Speed increases with score",
            "",
            "Press ESC or H to return"
        ]
        
        y_pos = 50
        for line in instructions:
            if line == "How to Play":
                draw_text(line, WIDTH//2 - 100, y_pos, RED)
            else:
                draw_text(line, 50, y_pos)
            y_pos += 30
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_h):
                    waiting = False
        
        pygame.display.flip()
        clock.tick(60)

def pause_menu():
    global VOLUME
    paused = True
    while paused:
        screen.fill((200, 200, 200))
        draw_text("PAUSED", WIDTH//2 - 50, HEIGHT//2 - 100)
        draw_text("Press ESC to Resume", WIDTH//2 - 100, HEIGHT//2 - 50)
        draw_text("Press R to Restart", WIDTH//2 - 90, HEIGHT//2)
        draw_text("Press Q to Quit", WIDTH//2 - 80, HEIGHT//2 + 150)
        draw_text("Press H for How to Play", WIDTH//2 - 100, HEIGHT//2 + 50)
        
        draw_volume_slider(VOLUME)
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        slider_x = WIDTH//2 - 100
        slider_y = HEIGHT//2 + 50
        slider_width = 200
        slider_height = 20
        
        if mouse_clicked and slider_y <= mouse_y <= slider_y + slider_height:
            if slider_x <= mouse_x <= slider_x + slider_width:
                VOLUME = (mouse_x - slider_x) / slider_width
                VOLUME = max(0, min(1, VOLUME))
                collision_sound.set_volume(VOLUME)
                score_sound.set_volume(VOLUME)
                background_music.set_volume(VOLUME)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False
                if event.key == pygame.K_r:
                    return "restart"
                if event.key == pygame.K_q:
                    quit_game()
                if event.key == pygame.K_h:
                    how_to_play_menu()
        
        pygame.display.flip()
        clock.tick(30)
    return "resume"

def title_screen(win=False):
    screen.fill(YELLOW if win else WHITE)
    if win:
        draw_text("You Win!", WIDTH//2 - 70, HEIGHT//2 - 100, RED)
        draw_text(f"Final Score: {score}", WIDTH//2 - 70, HEIGHT//2 - 50)
    else:
        draw_text("Dodge the Falling Obstacles!", WIDTH//2 - 150, HEIGHT//2 - 100, RED)
        draw_text("By Sathvik Harish", WIDTH//2 - 100, HEIGHT//2 - 50, BLUE)
    draw_text("Press ENTER to Start", WIDTH//2 - 100, HEIGHT//2)
    draw_text("Press ESC to Pause", WIDTH//2 - 90, HEIGHT - 100)
    draw_text("Press H for How to Play", WIDTH//2 - 100, HEIGHT - 50)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                if event.key == pygame.K_h:
                    how_to_play_menu()

def end_screen():
    screen.fill(WHITE)
    draw_text("Game Over!", WIDTH//2 - 100, HEIGHT//2 - 50, RED)
    draw_text(f"Final Score: {score}", WIDTH//2 - 100, HEIGHT//2)
    draw_text("Press R to Restart or Q to Quit", WIDTH//2 - 150, HEIGHT//2 + 50)
    draw_text("Press H for How to Play", WIDTH//2 - 100, HEIGHT//2 + 100)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q:
                    quit_game()
                if event.key == pygame.K_h:
                    how_to_play_menu()

def main():
    global score, running
    
    player = pygame.Rect(WIDTH//2 - PLAYER_WIDTH//2, HEIGHT - 100, PLAYER_WIDTH, PLAYER_HEIGHT)
    obstacles = []
    score = 0
    obstacle_speed = INITIAL_OBSTACLE_SPEED
    running = True
    boost_cooldown = 0
    
    while running:
        screen.fill(WHITE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    result = pause_menu()
                    if result == "restart":
                        return True
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x > 0:
            player.x -= SPEED
        if keys[pygame.K_RIGHT] and player.x < WIDTH - PLAYER_WIDTH:
            player.x += SPEED
        
        # Boost mechanic
        if keys[pygame.K_UP] and boost_cooldown == 0:
            player.y += BOOST_POWER
            boost_cooldown = BOOST_COOLDOWN
        
        # Update boost cooldown
        if boost_cooldown > 0:
            boost_cooldown -= 1
        
        # Keep player in bounds
        player.y = min(max(player.y, 0), HEIGHT - PLAYER_HEIGHT)
        
        # Natural falling
        if player.y < HEIGHT - 100:
            player.y += 5
        
        # Generate obstacles
        if random.randint(1, 30) == 1:
            obstacles.append(pygame.Rect(
                random.randint(0, WIDTH - OBSTACLE_WIDTH),
                0,
                OBSTACLE_WIDTH,
                OBSTACLE_HEIGHT
            ))
        
        # Move and check obstacles
        for obstacle in obstacles[:]:
            obstacle.y += obstacle_speed
            if obstacle.y > HEIGHT:
                obstacles.remove(obstacle)
                score += 1
                score_sound.play()
                if score % 15 == 0:
                    obstacle_speed += 0.5
        
        if score >= WIN_SCORE:
            title_screen(win=True)
            return True
        
        for obstacle in obstacles:
            if player.colliderect(obstacle):
                collision_sound.play()
                running = False
                break
        
        # Draw boost meter
        draw_boost_meter(boost_cooldown)
        
        # Draw player with boost effect
        if boost_cooldown > BOOST_COOLDOWN - 10:
            pygame.draw.rect(screen, BOOST_COLOR, player)
        else:
            pygame.draw.rect(screen, BLUE, player)
        
        for obstacle in obstacles:
            pygame.draw.rect(screen, RED, obstacle)
        
        draw_speed_bar(score)
        draw_text(f"Score: {score}", 10, 10)
        draw_fps()
        
        pygame.display.flip()
        clock.tick(60)
    
    return end_screen()

def run_game():
    while True:
        title_screen()
        if not main():
            break

if __name__ == "__main__":
    try:
        run_game()
    except KeyboardInterrupt:
        quit_game()
    except Exception as e:
        print(f"Error: {e}")
        quit_game()
