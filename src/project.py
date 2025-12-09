import pygame
import random

pygame.init()

WIDTH, HEIGHT = 960, 540
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Glitch Transistion")
clock = pygame.time.Clock()
scene_original = pygame.image.load("Scene.png").convert() #Replace desired image here
scene_original = pygame.transform.scale(scene_original, (WIDTH, HEIGHT))
scene = scene_original.copy()
progress = 0.0     
transition_speed = 0.4
current_state = 0       
target_state = 1        
transitioning = True    
GRID_SIZE_START = 80
GRID_SIZE_END = 10
glitch_palette = [(150, 200, 255), (255, 120, 180), (180, 255, 150)]

def safe_subsurface(image, x, y, w, h):
    img_w, img_h = image.get_size()
    x = max(0, min(x, img_w - 1))
    y = max(0, min(y, img_h - 1))
    w = max(1, min(w, img_w - x))
    h = max(1, min(h, img_h - y))
    return image.subsurface((x, y, w, h))

def diagonal_value(x, y, reversing=False):
    nx = x / WIDTH
    ny = y / HEIGHT
    if reversing:
        return nx + (1 - ny) 
    else:
        return (1 - nx) + ny  

def draw_glitch_transition(progress, reversing=False):
    if progress <= 0.0:
        screen.fill((0, 0, 0))
        return
    elif progress >= 1.0:
        screen.blit(scene, (0, 0))
        return

    fade = 1 - progress
    line_position = progress * 2.2
    line_thickness = 0.12
    block_size = int(GRID_SIZE_START * fade + GRID_SIZE_END * progress)
    line_offsets = [random.uniform(-0.25, 0.25) for _ in range(0, WIDTH, block_size)]

    for y in range(0, HEIGHT, block_size):
        for x in range(0, WIDTH, block_size):
            diag = diagonal_value(x, y, reversing)
            idx = x // block_size
            offset = line_offsets[idx]

            before_line = diag > (line_position + line_thickness + offset)
            on_glitch_line = abs(diag - (line_position + offset)) <= line_thickness
            after_line = diag < (line_position - line_thickness + offset)

            w = min(block_size, WIDTH - x)
            h = min(block_size, HEIGHT - y)

            if after_line:
                shift = int(4 * fade)
                r = safe_subsurface(scene, x + shift, y, w, h)
                g = safe_subsurface(scene, x, y, w, h)
                b = safe_subsurface(scene, x - shift, y, w, h)
                merged = pygame.Surface((w, h))
                merged.blit(r, (0, 0))
                merged.blit(g, (0, 0))
                merged.blit(b, (0, 0))
                screen.blit(merged, (x, y))

            elif on_glitch_line:
                num_squares = random.randint(2, 6)
                for _ in range(num_squares):
                    sq_w = random.randint(int(w * 0.2), w)
                    sq_h = random.randint(int(h * 0.2), h)
                    sq_x = x + random.randint(0, max(1, w - sq_w))
                    sq_y = y + random.randint(0, max(1, h - sq_h))
                    if random.random() < 0.45:
                        glitch_color = random.choice(glitch_palette)
                        pygame.draw.rect(screen, glitch_color, (sq_x, sq_y, sq_w, sq_h))
                    else:
                        jitter_x = sq_x + random.randint(-20, 20)
                        jitter_y = sq_y + random.randint(-10, 10)
                        chunk = safe_subsurface(scene, jitter_x, jitter_y, sq_w, sq_h)
                        screen.blit(chunk, (sq_x, sq_y))

            else:
                if random.random() < 0.06 * fade:
                    noise_color = (
                        random.randint(0, 40),
                        random.randint(0, 40),
                        random.randint(0, 40)
                    )
                    pygame.draw.rect(screen, noise_color, (x, y, w, h))
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (x, y, w, h))

running = True
while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not transitioning:
                target_state = 1 - current_state
                transitioning = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                tint = pygame.Surface((WIDTH, HEIGHT))
                tint.fill((random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)))
                tint.set_alpha(60)
                scene = scene_original.copy()
                scene.blit(tint, (0, 0))
            elif event.key == pygame.K_e:
                glitch_palette = [
                    (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                    for _ in range(3)
                ]
            elif event.key == pygame.K_q:
                scene = scene_original.copy()
                glitch_palette = [(150, 200, 255), (255, 120, 180), (180, 255, 150)]

    if transitioning:
        if target_state > progress:
            progress += transition_speed * dt
            progress = min(progress, target_state)
            reversing = False
        elif target_state < progress:
            progress -= transition_speed * dt
            progress = max(progress, target_state)
            reversing = True
        else:
            current_state = target_state
            transitioning = False
            reversing = False

    draw_glitch_transition(progress, reversing=reversing)
    pygame.display.flip()

pygame.quit()