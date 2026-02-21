import pygame
import math

# Point: [x, y, prev_x, prev_y, pinned]
PX, PY, PREV_X, PREV_Y, PINNED = 0, 1, 2, 3, 4
# Spring: [point_index_1, point_index_2, active]
IDX1, IDX2, ACTIVE = 0, 1, 2

GRID_COLS = 50
GRID_ROWS = 30
SPACING_X = 20
SPACING_Y = 28
DRAG_RADIUS = 30
SPRING_REST_LENGTH = 20
SPRING_BREAK_LENGTH = 100
SPRING_CUT_RADIUS = 15
RELAX_ITERATIONS = 6
VELOCITY_CLAMP = 20
GRAVITY = 0.4
DAMPING = 0.99

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_width(), screen.get_height()
clock = pygame.time.Clock()

# Build grid of points: [x, y, prev_x, prev_y, pinned (top row only)]
points = [
    [
        x * SPACING_X + WIDTH / 4,
        y * SPACING_Y + 100,
        x * SPACING_X + 100,
        y * SPACING_Y + 108,
        y == 0,
    ]
    for y in range(GRID_ROWS)
    for x in range(GRID_COLS)
]

# Horizontal springs (same row, adjacent points)
h_springs = [[i, i + 1, 1] for i in range(len(points)) if (i + 1) % GRID_COLS != 0]
# Vertical springs (row below)
v_springs = [[i, i + GRID_COLS, 1] for i in range(len(points) - GRID_COLS)]
springs = h_springs + v_springs

while True:
    for e in pygame.event.get():
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            exit()

    screen.fill((0, 5, 10))
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()

    # Update points: drag or apply velocity + gravity
    for point in points:
        if point[PINNED]:
            continue
        if mouse_buttons[0] and math.hypot(point[PX] - mouse_x, point[PY] - mouse_y) < DRAG_RADIUS:
            point[PX], point[PY] = mouse_x, mouse_y
        vx = max(-VELOCITY_CLAMP, min(VELOCITY_CLAMP, (point[PX] - point[PREV_X]) * DAMPING))
        vy = max(-VELOCITY_CLAMP, min(VELOCITY_CLAMP, (point[PY] - point[PREV_Y]) * DAMPING))
        point[PREV_X], point[PREV_Y] = point[PX], point[PY]
        point[PX] += vx
        point[PY] += vy + GRAVITY

    # Relax springs (multiple iterations)
    for _ in range(RELAX_ITERATIONS):
        for spring in springs:
            if not spring[ACTIVE]:
                continue
            p1, p2 = points[spring[IDX1]], points[spring[IDX2]]
            dx = p2[PX] - p1[PX]
            dy = p2[PY] - p1[PY]
            dist = math.hypot(dx, dy) or 0.1

            # Break spring if too long or right-click near midpoint
            mid_x = (p1[PX] + p2[PX]) / 2
            mid_y = (p1[PY] + p2[PY]) / 2
            if dist > SPRING_BREAK_LENGTH or (
                mouse_buttons[2] and math.hypot(mid_x - mouse_x, mid_y - mouse_y) < SPRING_CUT_RADIUS
            ):
                spring[ACTIVE] = 0
                continue

            force = (SPRING_REST_LENGTH - dist) / dist * 0.5
            if not p1[PINNED]:
                p1[PX] -= dx * force
                p1[PY] -= dy * force
            if not p2[PINNED]:
                p2[PX] += dx * force
                p2[PY] += dy * force

    # Draw active springs
    for idx1, idx2, active in springs:
        if not active:
            continue
        x1, y1 = points[idx1][PX], points[idx1][PY]
        x2, y2 = points[idx2][PX], points[idx2][PY]
        pygame.draw.line(screen, (0, 255, 150), (x1, y1), (x2, y2), 2)

    pygame.display.flip()
    clock.tick(60)
