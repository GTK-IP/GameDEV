import pygame
import random

# -----------------------------
# 1. 초기 설정
# -----------------------------
pygame.init()

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 640
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("운석 피하기 슈팅 게임")

clock = pygame.time.Clock()
FPS = 60

# 색상 정의 (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 60, 60)
DARK_RED = (60, 60, 60)
BLUE = (80, 160, 255)
YELLOW = (255, 220, 80)
GRAY = (120, 120, 120)

# 한글이 깨지지 않도록 시스템 폰트 사용 (윈도우 기준)
font = pygame.font.SysFont("malgungothic", 26)
big_font = pygame.font.SysFont("malgungothic", 48)


# -----------------------------
# 2. 플레이어(우주선) 클래스
# -----------------------------
class Player:
    WIDTH = 50
    HEIGHT = 40
    SPEED = 7

    def __init__(self):
        x = SCREEN_WIDTH // 2 - self.WIDTH // 2
        y = SCREEN_HEIGHT - self.HEIGHT - 20
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.max_health = 3   # 기획서에 명시된 최대 체력 3칸
        self.health = self.max_health

    def move(self, keys):
        # 좌우 이동 (기획서: 플레이어는 좌우 이동만 가능)
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.SPEED

    def draw(self, surface):
        # 삼각형 모양으로 우주선을 간단히 표현
        points = [
            (self.rect.centerx, self.rect.top),
            (self.rect.left, self.rect.bottom),
            (self.rect.right, self.rect.bottom),
        ]
        pygame.draw.polygon(surface, BLUE, points)


# -----------------------------
# 3. 미사일 클래스
# -----------------------------
class Missile:
    WIDTH = 4
    HEIGHT = 12
    SPEED = 10

    def __init__(self, x, y):
        self.rect = pygame.Rect(x - self.WIDTH // 2, y, self.WIDTH, self.HEIGHT)

    def update(self):
        self.rect.y -= self.SPEED  # 위로 이동

    def draw(self, surface):
        pygame.draw.rect(surface, YELLOW, self.rect)


# -----------------------------
# 4. 운석(적) 클래스
# -----------------------------
class Asteroid:
    def __init__(self, speed):
        size = random.randint(25, 45)
        # 랜덤 위치에서 생성 (기획서 반영)
        x = random.randint(0, SCREEN_WIDTH - size)
        self.rect = pygame.Rect(x, -size, size, size)
        self.speed = speed  # 등속 이동

    def update(self):
        self.rect.y += self.speed

    def draw(self, surface):
        pygame.draw.ellipse(surface, GRAY, self.rect)


# -----------------------------
# 5. 보조 함수
# -----------------------------
def draw_health(surface, health, max_health):
    """체력 3칸을 화면 좌측 상단에 표시"""
    for i in range(max_health):
        color = RED if i < health else DARK_RED
        pygame.draw.rect(surface, color, (10 + i * 30, 10, 25, 20))


def get_asteroid_speed(score):
    """점수가 높을수록 운석 속도 증가 (기획서 반영), 최대 속도 제한"""
    base_speed = 3
    bonus = score // 50  # 50점마다 속도 +1
    return min(base_speed + bonus, 12)


def get_spawn_interval(score):
    """점수가 높을수록 운석이 더 자주 생성되도록 하여 난이도 상승"""
    return max(15, 45 - score // 20)


# -----------------------------
# 6. 메인 게임 루프
# -----------------------------
def main():
    player = Player()
    missiles = []
    asteroids = []
    score = 0
    spawn_timer = 0
    game_over = False
    running = True

    while running:
        clock.tick(FPS)

        # --- 이벤트 처리 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    # 미사일 발사 (기획서: 플레이어는 미사일 발사 가능)
                    missiles.append(Missile(player.rect.centerx, player.rect.top))
                if event.key == pygame.K_r and game_over:
                    # 재시작: 모든 상태 초기화
                    player = Player()
                    missiles = []
                    asteroids = []
                    score = 0
                    spawn_timer = 0
                    game_over = False

        if not game_over:
            keys = pygame.key.get_pressed()
            player.move(keys)

            # 운석 생성
            spawn_timer += 1
            if spawn_timer >= get_spawn_interval(score):
                spawn_timer = 0
                asteroids.append(Asteroid(get_asteroid_speed(score)))

            # 미사일 이동 및 화면 밖 제거
            for m in missiles[:]:
                m.update()
                if m.rect.bottom < 0:
                    missiles.remove(m)

            # 운석 이동 및 충돌 판정
            for a in asteroids[:]:
                a.update()

                # 화면 끝까지 내려가서 '피한' 경우 → +2점
                if a.rect.top > SCREEN_HEIGHT:
                    asteroids.remove(a)
                    score += 2
                    continue

                # 플레이어와 충돌 → 체력 -1
                if a.rect.colliderect(player.rect):
                    asteroids.remove(a)
                    player.health -= 1
                    if player.health <= 0:
                        game_over = True
                    continue

                # 미사일과 충돌 → 파괴, +10점
                for m in missiles[:]:
                    if a.rect.colliderect(m.rect):
                        asteroids.remove(a)
                        missiles.remove(m)
                        score += 10
                        break

        # --- 화면 그리기 ---
        screen.fill(BLACK)
        player.draw(screen)
        for m in missiles:
            m.draw(screen)
        for a in asteroids:
            a.draw(screen)
        draw_health(screen, player.health, player.max_health)

        score_text = font.render(f"점수: {score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH - 150, 10))

        if game_over:
            over_text = big_font.render("GAME OVER", True, RED)
            restart_text = font.render("R 키를 눌러 재시작", True, WHITE)
            screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()