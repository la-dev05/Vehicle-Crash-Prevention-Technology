import pygame
import math
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
FPS = 100
SCALE_FACTOR = 0.8
DETECTION_RADIUS = 150  # meters (will be scaled)

# Colors
ROAD_COLOR = (75, 85, 99)      # Sophisticated charcoal gray for asphalt
GRASS_COLOR = (104, 159, 56)   # Fresh, vibrant grass green
LINE_COLOR = (245, 245, 245)   # Crisp white for road markings
CAR1_COLOR = (239, 68, 68)     # Vibrant coral red
CAR2_COLOR = (59, 130, 246)    # Modern electric blue
BUTTON_COLOR = (34, 197, 94)   # Emerald green
TEXT_COLOR = (243, 244, 246)   # Soft pearl white

class Car:
    def __init__(self, x, y, direction, speed, color):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.color = color
        self.width = 40
        self.length = 60
        self.initial_speed = speed
        self.initial_x = x
        self.initial_y = y
        
    def move(self, dt):
        if self.direction == 'horizontal':
            self.x += self.speed * dt * SCALE_FACTOR
        else:
            self.y += self.speed * dt * SCALE_FACTOR

    def reset(self):
        self.x = self.initial_x
        self.y = self.initial_y
        self.speed = self.initial_speed

    def draw(self, screen):
        # Draw car body (main rectangle)
        car_rect = pygame.Rect(
            self.x - (self.length/2 if self.direction == 'horizontal' else self.width/2),
            self.y - (self.width/2 if self.direction == 'horizontal' else self.length/2),
            self.length if self.direction == 'horizontal' else self.width,
            self.width if self.direction == 'horizontal' else self.length
        )
        pygame.draw.rect(screen, self.color, car_rect, border_radius=8)

        # Add car details (windshield, etc.)
        if self.direction == 'horizontal':
            # Windshield
            windshield = pygame.Rect(
                self.x - self.length/4,
                self.y - self.width/3,
                self.length/2,
                self.width/1.5
            )
            pygame.draw.rect(screen, (150, 150, 150), windshield, border_radius=4)
        else:
            # Windshield
            windshield = pygame.Rect(
                self.x - self.width/3,
                self.y - self.length/4,
                self.width/1.5,
                self.length/2
            )
            pygame.draw.rect(screen, (150, 150, 150), windshield, border_radius=4)

        # Draw detection radius (very subtle)
        radius_surface = pygame.Surface((DETECTION_RADIUS * 2 * SCALE_FACTOR, DETECTION_RADIUS * 2 * SCALE_FACTOR), pygame.SRCALPHA)
        pygame.draw.circle(radius_surface, (*self.color, 70),
                         (DETECTION_RADIUS * SCALE_FACTOR, DETECTION_RADIUS * SCALE_FACTOR),
                         DETECTION_RADIUS * SCALE_FACTOR)
        screen.blit(radius_surface,
                   (self.x - DETECTION_RADIUS * SCALE_FACTOR,
                    self.y - DETECTION_RADIUS * SCALE_FACTOR))

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def draw_road(screen):
    # Fill background with grass
    screen.fill(GRASS_COLOR)

    # Draw roads
    road_width = 150
    pygame.draw.rect(screen, ROAD_COLOR, (0, WINDOW_HEIGHT/2 - road_width/2, WINDOW_WIDTH, road_width))
    pygame.draw.rect(screen, ROAD_COLOR, (WINDOW_WIDTH/2 - road_width/2, 0, road_width, WINDOW_HEIGHT))

    # Draw road lines
    # Center lines
    dash_length = 30
    gap_length = 30
    for i in range(0, WINDOW_WIDTH, dash_length + gap_length):
        # Horizontal road lines
        pygame.draw.rect(screen, LINE_COLOR, (i, WINDOW_HEIGHT/2 - 2, dash_length, 4))
        # Vertical road lines
        if i < WINDOW_HEIGHT:
            pygame.draw.rect(screen, LINE_COLOR, (WINDOW_WIDTH/2 - 2, i, 4, dash_length))

    # Edge lines (solid)
    # Horizontal road
    pygame.draw.line(screen, LINE_COLOR, (0, WINDOW_HEIGHT/2 - road_width/2), (WINDOW_WIDTH, WINDOW_HEIGHT/2 - road_width/2), 3)
    pygame.draw.line(screen, LINE_COLOR, (0, WINDOW_HEIGHT/2 + road_width/2), (WINDOW_WIDTH, WINDOW_HEIGHT/2 + road_width/2), 3)
    # Vertical road
    pygame.draw.line(screen, LINE_COLOR, (WINDOW_WIDTH/2 - road_width/2, 0), (WINDOW_WIDTH/2 - road_width/2, WINDOW_HEIGHT), 3)
    pygame.draw.line(screen, LINE_COLOR, (WINDOW_WIDTH/2 + road_width/2, 0), (WINDOW_WIDTH/2 + road_width/2, WINDOW_HEIGHT), 3)

def calculate_collision_time(car1, car2):
    distance = math.sqrt((car2.x - car1.x)**2 + (car2.y - car1.y)**2)
    distance_meters = distance / SCALE_FACTOR

    if car1.direction == 'horizontal':
        v1_x, v1_y = car1.speed, 0
    else:
        v1_x, v1_y = 0, car1.speed

    if car2.direction == 'horizontal':
        v2_x, v2_y = car2.speed, 0
    else:
        v2_x, v2_y = 0, car2.speed

    relative_velocity = math.sqrt((v2_x - v1_x)**2 + (v2_y - v1_y)**2)

    if relative_velocity == 0:
        return float('inf')
    return distance_meters / relative_velocity

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Intersection Collision Avoidance Simulation")
    clock = pygame.time.Clock()

    car1 = Car(0, WINDOW_HEIGHT/2, 'horizontal', 50, CAR1_COLOR)
    car2 = Car(WINDOW_WIDTH/2, 0, 'vertical', 40, CAR2_COLOR)

    restart_button = Button(WINDOW_WIDTH/2 - 60, WINDOW_HEIGHT - 80, 120, 40, "Restart", BUTTON_COLOR)

    running = True
    simulation_active = True
    last_time = time.time()

    while running:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not simulation_active and restart_button.is_clicked(event.pos):
                    car1.reset()
                    car2.reset()
                    simulation_active = True
                
        if simulation_active:
            distance = math.sqrt((car2.x - car1.x)**2 + (car2.y - car1.y)**2)

            if distance < DETECTION_RADIUS * 2 * SCALE_FACTOR:
                collision_time = calculate_collision_time(car1, car2)
                deceleration = 8 # Deceleration in units per second^2
                car1.speed = max(0, car1.speed - deceleration * dt)
                car2.speed = max(0, car2.speed - deceleration * dt)

                if car1.speed == 0 and car2.speed == 0:
                    simulation_active = False
            
            car1.move(dt)
            car2.move(dt)

        # Draw everything
        draw_road(screen)
        car1.draw(screen)
        car2.draw(screen)
        
        # Display speeds with shadow effect for better visibility
        font = pygame.font.Font(None, 36)
        def draw_text_with_shadow(text, pos):
            shadow = font.render(text, True, (0, 0, 0))
            text_surface = font.render(text, True, TEXT_COLOR)
            screen.blit(shadow, (pos[0] + 2, pos[1] + 2))
            screen.blit(text_surface, pos)
            
        draw_text_with_shadow(f"Car 1: {car1.speed:.1f} m/s", (10, 10))
        draw_text_with_shadow(f"Car 2: {car2.speed:.1f} m/s", (10, 50))
        
        if not simulation_active:
            restart_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
            
    pygame.quit()

if __name__ == "__main__":
    main()