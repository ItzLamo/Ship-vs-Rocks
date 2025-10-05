import pygame
import random
import sys
import os

pygame.init()

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ship vs Rocks Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

player_image = pygame.image.load("ship.png")  
obstacle_image = pygame.image.load("rock1.png") 
background_image = pygame.image.load("background.png")
powerup_image = pygame.image.load("powerup.png") 
coin_image = pygame.image.load("coin.png") 
explosion_image = pygame.image.load("explosion.png")  

try:
    game_over_image = pygame.image.load("D:\Hack Club\First Week Siege Project - Ship vs Rocks\game_over.png")  
    game_over_image = pygame.transform.scale(game_over_image, (int(SCREEN_WIDTH * 0.45), int(SCREEN_HEIGHT * 0.5)))  # Resize image
except Exception as e:
    print(f"Error loading game over image: {e}")
    game_over_image = None


player_image = pygame.transform.scale(player_image, (50, 50))
obstacle_image = pygame.transform.scale(obstacle_image, (50, 50))
powerup_image = pygame.transform.scale(powerup_image, (30, 30))
coin_image = pygame.transform.scale(coin_image, (25, 25))
explosion_image = pygame.transform.scale(explosion_image, (50, 50))
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

font_path = os.path.join("D:\Hack Club\First Week Siege Project - Ship vs Rocks\font.otf")
font = pygame.font.Font(font_path, 36)
small_font = pygame.font.Font(font_path, 24)

player_x = 100
player_y = SCREEN_HEIGHT // 2
player_speed = 5
player_health = 3

obstacles = []
for _ in range(3):
    obstacles.append({
        "x": SCREEN_WIDTH,
        "y": random.randint(0, SCREEN_HEIGHT - 50),
        "speed": 5
    })

powerup = {
    "x": SCREEN_WIDTH,
    "y": random.randint(0, SCREEN_HEIGHT - 30),
    "speed": 5,
    "active": False
}

# Coin settings
coins = []
for _ in range(5):  # 5 coins for week theme ;)
    coins.append({
        "x": random.randint(SCREEN_WIDTH, SCREEN_WIDTH * 2),
        "y": random.randint(0, SCREEN_HEIGHT - 20),
        "speed": 5,
        "active": True
    })

explosions = []

score = 0
high_score = 0

pygame.mixer.init()
collision_sound = pygame.mixer.Sound("collision.mp3")
powerup_sound = pygame.mixer.Sound("powerup.mp3") 
coin_sound = pygame.mixer.Sound("coin.mp3") 

START = 0
PLAYING = 1
GAME_OVER = 2
PAUSED = 3
game_state = START

bg_x = 0

base_obstacle_speed = 4
base_coin_speed = 5
difficulty_interval = 40 

particles = []

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if game_state == START:
        screen.fill(BLACK)
        start_text = font.render("Press SPACE to Start", True, WHITE)
        screen.blit(start_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            game_state = PLAYING
    elif game_state == PLAYING:

        if score > 0 and score % difficulty_interval == 0:
            base_obstacle_speed += 1 
            base_coin_speed += 1 
            if len(obstacles) < 10:  
                obstacles.append({
                    "x": SCREEN_WIDTH,
                    "y": random.randint(0, SCREEN_HEIGHT - 50),
                    "speed": base_obstacle_speed
                })

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and player_y > 0:
            player_y -= player_speed
        if keys[pygame.K_DOWN] and player_y < SCREEN_HEIGHT - 50:
            player_y += player_speed
        if keys[pygame.K_p]: 
            game_state = PAUSED

        for obstacle in obstacles:
            obstacle["x"] -= obstacle["speed"]
            if obstacle["x"] < 0:
                obstacle["x"] = SCREEN_WIDTH
                obstacle["y"] = random.randint(0, SCREEN_HEIGHT - 50)

        if not powerup["active"]:
            powerup["x"] -= powerup["speed"]
            if powerup["x"] < 0:
                powerup["x"] = SCREEN_WIDTH
                powerup["y"] = random.randint(0, SCREEN_HEIGHT - 30)
                powerup["active"] = True

        for coin in coins:
            coin["x"] -= coin["speed"]
            if coin["x"] < 0:
                coin["x"] = random.randint(SCREEN_WIDTH, SCREEN_WIDTH * 2)
                coin["y"] = random.randint(0, SCREEN_HEIGHT - 20)
                coin["active"] = True

        player_rect = pygame.Rect(player_x, player_y, 50, 50)
        for obstacle in obstacles:
            obstacle_rect = pygame.Rect(obstacle["x"], obstacle["y"], 50, 50)
            if player_rect.colliderect(obstacle_rect):
                collision_sound.play()
                player_health -= 1
                explosions.append({"x": player_x, "y": player_y, "frame": 0})
                if player_health <= 0:
                    game_state = GAME_OVER
                obstacle["x"] = SCREEN_WIDTH

        powerup_rect = pygame.Rect(powerup["x"], powerup["y"], 30, 30)
        if player_rect.colliderect(powerup_rect) and powerup["active"]:
            powerup_sound.play()
            powerup["active"] = False
            player_speed += 2 

        for coin in coins:
            coin_rect = pygame.Rect(coin["x"], coin["y"], 20, 20)
            if player_rect.colliderect(coin_rect) and coin["active"]:
                coin_sound.play()
                coin["active"] = False
                score += 10
                for _ in range(10):
                    particles.append({
                        "x": coin["x"],
                        "y": coin["y"],
                        "vx": random.uniform(-2, 2),
                        "vy": random.uniform(-2, 2),
                        "life": 30
                    })

        bg_x -= 1
        if bg_x <= -SCREEN_WIDTH:
            bg_x = 0
        screen.blit(background_image, (bg_x, 0))
        screen.blit(background_image, (bg_x + SCREEN_WIDTH, 0))

        screen.blit(player_image, (player_x, player_y))
        for obstacle in obstacles:
            screen.blit(obstacle_image, (obstacle["x"], obstacle["y"]))
        if powerup["active"]:
            screen.blit(powerup_image, (powerup["x"], powerup["y"]))
        for coin in coins:
            if coin["active"]:
                screen.blit(coin_image, (coin["x"], coin["y"]))

        for explosion in explosions:
            screen.blit(explosion_image, (explosion["x"], explosion["y"]))
            explosion["frame"] += 1
            if explosion["frame"] > 10: 
                explosions.remove(explosion)

        for particle in particles:
            pygame.draw.circle(screen, WHITE, (int(particle["x"]), int(particle["y"])), 2)
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["life"] -= 1
            if particle["life"] <= 0:
                particles.remove(particle)

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        health_text = font.render(f"Health: {player_health}", True, RED)
        screen.blit(health_text, (10, 50))
    elif game_state == GAME_OVER:
        screen.fill(BLACK) 

        if game_over_image:
            game_over_rect = game_over_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(game_over_image, game_over_rect)

        game_over_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 170))
        restart_text = small_font.render("Press R to Restart", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 150))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            player_x = 100
            player_y = SCREEN_HEIGHT // 2
            player_speed = 5
            player_health = 3
            obstacles = []
            for _ in range(3):
                obstacles.append({
                    "x": SCREEN_WIDTH,
                    "y": random.randint(0, SCREEN_HEIGHT - 50),
                    "speed": base_obstacle_speed
                })
            powerup["x"] = SCREEN_WIDTH
            powerup["y"] = random.randint(0, SCREEN_HEIGHT - 30)
            powerup["active"] = False
            coins = []
            for _ in range(5):
                coins.append({
                    "x": random.randint(SCREEN_WIDTH, SCREEN_WIDTH * 2),
                    "y": random.randint(0, SCREEN_HEIGHT - 20),
                    "speed": base_coin_speed,
                    "active": True
                })
            score = 0
            base_obstacle_speed = 5
            base_coin_speed = 5 
            explosions.clear() 
            particles.clear() 
            game_state = PLAYING
    elif game_state == PAUSED:
        screen.fill(BLACK)
        pause_text = font.render("Paused - Press P to Resume", True, WHITE)
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            game_state = PLAYINGpygame.quit()


    pygame.display.flip()

    clock.tick(60)


pygame.quit()
sys.exit()