import pygame
from os.path import join
import random as r
import pickle
import tkinter as tk # Tkinter 라이브러리 import
from tkinter import font as tkfont
from PIL import Image, ImageTk # Pillow 라이브러리 import

# =====================================================================
# 0. Tkinter 시작 화면 함수
# =====================================================================

def show_start_screen():
    # 메인 윈도우 생성
    root = tk.Tk()
    root.title("게임 시작")

    # 창 크기 및 위치 설정
    window_width = 800
    window_height = 650 # 높이 약간 늘림
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width / 2)
    center_y = int(screen_height/2 - window_height / 2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    root.configure(bg='#0E0101')
    root.overrideredirect(True)

    # 폰트 설정
    title_font = tkfont.Font(family="Helvetica", size=36, weight="bold")
    header_font = tkfont.Font(family="Helvetica", size=20, weight="bold")
    body_font = tkfont.Font(family="Helvetica", size=14)

    # 제목 레이블
    title_label = tk.Label(root, text="운석 뿌셔", font=title_font, fg="white", bg="#0E0101")
    title_label.pack(pady=(40, 20))

    # 조작 방법 섹션
    controls_frame = tk.Frame(root, bg="#0E0101")
    controls_frame.pack(pady=10, padx=40, fill="x")
    controls_header = tk.Label(controls_frame, text="[ 조작 방법 ]", font=header_font, fg="#4d94ff", bg="#0E0101")
    controls_header.pack()
    controls_text = "이동: ← ↑ → ↓\n레이저 발사: Space Bar"
    controls_label = tk.Label(controls_frame, text=controls_text, font=body_font, fg="white", bg="#0E0101", justify="left")
    controls_label.pack(pady=10)

    # 운석 정보 섹션
    meteors_frame = tk.Frame(root, bg="#0E0101")
    meteors_frame.pack(pady=10, padx=40, fill="x")
    meteors_header = tk.Label(meteors_frame, text="[ 운석 정보 ]", font=header_font, fg="#ff4d4d", bg="#0E0101")
    meteors_header.pack(pady=(0, 15))

    # 운석 이미지 및 설명 데이터
    meteor_data = {
        'meteor.png': "일반 운석입니다.",
        'flame_meteor.png': "2번 맞춰야 파괴되는 강화 운석입니다.",
        'healing_meteor.png': "파괴 시 생명력을 1 회복합니다.",
        'comet.png': "매우 빠르며, 파괴 시 높은 점수를 줍니다. 매우 낮은 확률로 등장합니다."
    }
    
    # Tkinter에서 이미지를 유지하기 위한 참조 리스트
    root.image_references = []

    for img_file, description in meteor_data.items():
        # 각 운석 정보를 담을 프레임
        item_frame = tk.Frame(meteors_frame, bg="#0E0101")
        item_frame.pack(fill='x', pady=5)

        # 이미지 로드 및 리사이즈
        img = Image.open(join('images', img_file))
        img.thumbnail((50, 50)) # 이미지 크기 조절
        photo_img = ImageTk.PhotoImage(img)
        root.image_references.append(photo_img) # 참조 유지

        # 이미지 레이블
        img_label = tk.Label(item_frame, image=photo_img, bg="#0E0101")
        img_label.pack(side="left", padx=(10, 15))

        # 설명 레이블
        desc_label = tk.Label(item_frame, text=description, font=body_font, fg="white", bg="#0E0101", justify="left")
        desc_label.pack(side="left")

    # 게임 시작 안내 메시지
    start_label = tk.Label(root, text="아무 키나 마우스를 클릭하면 게임이 시작됩니다.", font=header_font, fg="yellow", bg="#0E0101")
    start_label.pack(pady=(20, 0))

    # 키나 마우스 클릭 시 창을 닫는 함수
    def start_game(event):
        root.destroy()

    # 이벤트 바인딩
    root.bind("<KeyPress>", start_game)
    root.bind("<Button-1>", start_game)

    root.mainloop()

# =====================================================================
# 1. 클래스 정의 (Player, Star, Laser, Meteor, FlameMeteor, HealingMeteor)
# =====================================================================
class Player(pygame.sprite.Sprite):
    #sprite 클래스 상속
    def __init__(self,groups):
        super().__init__(groups) #부모 클래스 초기화
        self.image= pygame.image.load(join('images','player.png')).convert_alpha()
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.pos = pygame.Vector2(self.rect.center)
        self.direction= pygame.Vector2() # 방향 벡터 초기화
        self.speed = 300
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 500
        self.lives = 3
        self.invincible = False # 피격 후 잠시 무적
        self.invincible_time = 0
        self.invincible_duration = 1500 # 1.5초 무적
        self.mask = pygame.mask.from_surface(self.image) # 충돌 처리를 위하여 player class 안에 마스크 생성

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def check_invincibility(self): #무적 상태 처리
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.invincible_time > self.invincible_duration:
                self.invincible = False # 무적 상태 해제

    def update(self,dt):
        keys = pygame.key.get_pressed() #키보드 입력 받기
        self.direction = pygame.Vector2(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT], keys[pygame.K_DOWN] - keys[pygame.K_UP])
        if self.direction.length() != 0: # 벡터 정규화 (길이가 0이 아닐 때만)
            self.direction = self.direction.normalize()
        self.pos += self.direction * self.speed * dt # 수정: self.pos를 업데이트한 후 rect의 중앙에 적용
        self.pos.x = max(0, min(self.pos.x, WINDOW_WIDTH))
        self.pos.y = max(0, min(self.pos.y, WINDOW_HEIGHT))
        self.rect.center = (round(self.pos.x), round(self.pos.y)) # 반올림하여 정수 좌표로 변환
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf,self.rect.midtop, (all_sprites, laser_sprites)) # 레이저 생성
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play() # 레이저 사운드 재생
        self.laser_timer()
        self.check_invincibility() # 무적 상태 처리

#스타 클래스 정의
class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.scale = r.uniform(0.3, 1.2)
        self.image = pygame.transform.scale_by(surf, self.scale)
        self.rect = self.image.get_rect(center=(r.randint(0, WINDOW_WIDTH), r.randint(0, WINDOW_HEIGHT)))
        self.speed = self.scale * 100
    def update(self, dt):
        self.rect.y += self.speed * dt
        if self.rect.top > WINDOW_HEIGHT:
            self.rect.center = (r.randint(0, WINDOW_WIDTH), r.randint(-50, -10))

#레이저 클래스 정의
class Laser(pygame.sprite.Sprite):
    def __init__(self, surf,pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom=pos) # 레이저의 위치 설정
        self.speed = 1000 #레이저 속도 설정
        self.mask = pygame.mask.from_surface(self.image)
    def update(self,dt):
        self.rect.centery -= self.speed * dt # 레이저 위로 이동
        if self.rect.bottom < 0: self.kill()

#메테오 클래스 정의
class Meteor(pygame.sprite.Sprite):
    def __init__(self,surf, pos, groups):
        super().__init__(groups)
        self.origminal_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.start_time =pygame.time.get_ticks()
        self.lifetime = r.randint(2000, 5000) # 운석의 생명주기 설정 (2초에서 5초 사이)
        self.direction =pygame.Vector2(r.uniform(-0.5,0.5),1) # 아래로 떨어지는 방향 벡터
        self.speed = r.randint(200,400)
        self.rotation_speed =r.randint(40,80)
        self.rotation = 0
    def update(self,dt):
        global unavoided_meteor_count
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime: self.kill() # 생명주기가 끝나면 운석 제거
        if self.rect.top > WINDOW_HEIGHT: # 화면 밖으로 나가면 제거
            unavoided_meteor_count += 1
            self.kill()
        self.rotation+=self.rotation_speed * dt # 회전 속도 적용
        self.image = pygame.transform.rotozoom(self.origminal_surf, self.rotation, 1) # 원본 이미지를 회전
        self.rect = self.image.get_frect(center= self.rect.center) # 회전 후 rect 업데이트

#강화 메테오 클래스 정의
class FlameMeteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = r.randint(4000, 6000)
        self.direction = pygame.Vector2(r.uniform(-0.2, 0.2), 1)
        self.speed = r.randint(300,500)
        self.health = 2 # 체력: 2번 맞아야 파괴됨
    def update(self, dt):
        global unavoided_meteor_count
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime: self.kill()
        if self.rect.top > WINDOW_HEIGHT: # 화면 밖으로 나가면 제거
            unavoided_meteor_count += 1
            self.kill()

#생명 회복 메테오 클래스 정의
class HealingMeteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.origminal_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = r.randint(3000, 7000)
        self.direction = pygame.Vector2(r.uniform(-0.5, 0.5), 1)
        self.speed = r.randint(150, 300)
        self.rotation_speed = r.randint(30, 60)
        self.rotation = 0
    def update(self, dt):
        global unavoided_meteor_count
        self.rect.center += self.direction * self.speed * dt
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.origminal_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center= self.rect.center)
        if pygame.time.get_ticks() - self.start_time >= self.lifetime: self.kill()
        if self.rect.top > WINDOW_HEIGHT:
            unavoided_meteor_count += 1
            self.kill()

# 혜성 클래스 정의
class Comet(pygame.sprite.Sprite):
    def __init__(self, surf, groups):
        super().__init__(groups)
        self.image = surf
        start_x = WINDOW_WIDTH + r.randint(100, 300)
        start_y = r.randint(0, WINDOW_HEIGHT // 2)
        self.rect = self.image.get_frect(center=(start_x, start_y))
        self.mask = pygame.mask.from_surface(self.image)
        direction_x = -1
        direction_y = r.uniform(0.5, 0.8)
        self.direction = pygame.Vector2(direction_x, direction_y).normalize()
        self.speed = r.randint(800, 1000)
        self.particle_timer = pygame.time.get_ticks()
        self.particle_interval = 15

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if self.rect.right < 0 or self.rect.top > WINDOW_HEIGHT:
            self.kill()
        current_time = pygame.time.get_ticks()
        if current_time - self.particle_timer > self.particle_interval:
            self.particle_timer = current_time
            particle_pos = self.rect.center + pygame.Vector2(r.randint(-20, 20), r.randint(-20, 20))
            CometParticle(particle_pos, effects_sprites)

# 혜성 꼬리 입자 클래스
class CometParticle(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.pos = pygame.Vector2(pos)
        self.color = (r.randint(150, 255), r.randint(150, 255), 255)
        self.radius = r.randint(4, 10)
        self.lifetime = r.randint(400, 600)
        self.creation_time = pygame.time.get_ticks()

    def update(self, dt):
        elapsed_time = pygame.time.get_ticks() - self.creation_time
        if elapsed_time > self.lifetime:
            self.kill()
        else:
            self.radius = max(0, self.radius * (1 - (elapsed_time / self.lifetime)))

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), int(self.radius))

# =====================================================================
# 2. 게임 함수 정의 (collision, handle_player_hit, display 등)
# =====================================================================

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames): self.image = self.frames[int(self.frame_index)]
        else: self.kill()

class Shockwave(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.pos = pos
        self.radius, self.max_radius = 20, 100
        self.speed, self.width = 300, 5
        self.color, self.alpha = (255,255,255), 255
    def update(self, dt):
        self.radius += self.speed * dt
        self.alpha = max(0, 255 - (self.radius / self.max_radius) * 255)
        if self.radius > self.max_radius: self.kill()
    def draw(self, surface):
        temp_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surf, (*self.color, self.alpha), (self.radius, self.radius), self.radius, self.width)
        rect = temp_surf.get_rect(center=self.pos)
        surface.blit(temp_surf, rect)

def collision():
    global bonus_score
    if not player.invincible:
        # 플레이어와 운석 그룹 충돌
        if pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask) or \
           pygame.sprite.spritecollide(player, flame_meteor_sprites, True, pygame.sprite.collide_mask) or \
           pygame.sprite.spritecollide(player, comet_sprites, True, pygame.sprite.collide_mask):
            handle_player_hit(); damage_sound.play()
        # 플레이어와 힐링 운석 충돌
        if pygame.sprite.spritecollide(player, healing_meteor_sprites, True, pygame.sprite.collide_mask):
            if player.lives < 3: player.lives += 1
            explosion_sound.play()
    # 레이저와 운석 충돌
    for laser in laser_sprites:
        # 일반 운석
        collided_meteors = pygame.sprite.spritecollide(laser, meteor_sprites, False)
        if collided_meteors:
            laser.kill(); explosion_sound.play()
            for meteor in collided_meteors:
                bonus_score += 10
                Shockwave(meteor.rect.center, effects_sprites)
                meteor.kill()
        # 강화 운석
        collided_flames = pygame.sprite.spritecollide(laser, flame_meteor_sprites, False)
        if collided_flames:
            laser.kill()
            for meteor in collided_flames:
                meteor.health -= 1
                if meteor.health <= 0:
                    bonus_score += 20; explosion_sound.play()
                    Shockwave(meteor.rect.center, effects_sprites)
                    meteor.kill()
        # 힐링 운석
        if pygame.sprite.spritecollide(laser, healing_meteor_sprites, True):
            if player.lives < 3: player.lives += 1
            laser.kill(); explosion_sound.play()
        # 혜성
        if pygame.sprite.spritecollide(laser, comet_sprites, True, pygame.sprite.collide_mask):
            laser.kill()
            bonus_score += 500
            explosion_sound.play()
            AnimatedExplosion(explosion_frames, laser.rect.center, (all_sprites, effects_sprites))

def handle_player_hit():
    global running, flash_timer
    player.lives -= 1
    player.invincible, player.invincible_time = True, pygame.time.get_ticks()
    flash_timer = pygame.time.get_ticks() + 200
    if player.lives <= 0: running = False

def display_score():
    text_surf = font.render(str(score), True, (240,240,240))
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2,WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,10).move(0,-8), 5, 10)

def display_lives():
    for i in range(player.lives):
        x = WINDOW_WIDTH - 50 - (i * (life_surf.get_width() + 10))
        display_surface.blit(life_surf, (x, 30))

def display_warning(message, y_offset, color='red'):
    text_surf = warning_font.render(message, True, color)
    y_pos = WINDOW_HEIGHT / 2 + y_offset
    text_rect = text_surf.get_frect(center=(WINDOW_WIDTH / 2, y_pos))
    display_surface.blit(text_surf, text_rect)

def display_game_over(final_score, high_score):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)); overlay.set_alpha(150); overlay.fill((0, 0, 0))
    display_surface.blit(overlay, (0, 0))
    score_text = f"New High Score: {final_score}" if final_score > high_score else f"Final Score: {final_score}"
    score_text_surf = warning_font.render(score_text, True, (255, 255, 255))
    score_text_rect = score_text_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 50))
    display_surface.blit(score_text_surf, score_text_rect)
    high_score_text_surf = warning_font.render(f"Best Score: {high_score}", True, (255, 255, 255))
    high_score_text_rect = high_score_text_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    display_surface.blit(high_score_text_surf, high_score_text_rect)
    restart_text_surf = font.render("Press any key to quit", True, (200, 200, 200))
    restart_text_rect = restart_text_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 50))
    display_surface.blit(restart_text_surf, restart_text_rect)

# 최고 점수 저장 및 불러오기 함수
def save_high_score(score):
    try:
        with open("highscore.dat", "wb") as file: pickle.dump(score, file)
    except IOError: print("Error: Could not save high score.")

# 최고 점수 불러오기 함수
def load_high_score():
    try:
        with open("highscore.dat", "rb") as file: return pickle.load(file)
    except (IOError, pickle.UnpicklingError): return 0

# =====================================================================
# 3. 게임 초기화 및 설정
# =====================================================================

# Tkinter 시작 화면을 먼저 보여줌
show_start_screen()

pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
running = True
clock= pygame.time.Clock()
pygame.display.set_caption('운석 뿌셔')

# 이미지 및 폰트 로드
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
laser_surf = pygame.image.load(join('images','laser.png')).convert_alpha()
life_surf = pygame.image.load(join('images', 'heart.png')).convert_alpha()
life_surf = pygame.transform.scale(life_surf, (40, 40))
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
warning_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 50)
health_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 25)
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]
comet_surf = pygame.image.load(join('images', 'comet.png')).convert_alpha()
comet_surf = pygame.transform.scale(comet_surf, (200, 200))

# 배경음악 설정
laser_sound, explosion_sound, damage_sound, game_music = [pygame.mixer.Sound(join('audio', f)) for f in ['laser.wav', 'explosion.wav', 'damage.ogg', 'game.wav']]
laser_sound.set_volume(0.2); explosion_sound.set_volume(0.4); damage_sound.set_volume(0.5); game_music.set_volume(0.9)
game_music.play(-1)

#flame meteor의 체력
HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT = 40, 5
HEALTH_BAR_COLOR, BACKGROUND_BAR_COLOR = (0, 255, 0), (255, 0, 0) # 초록색, 빨간색

# 운석 이미지 로드 및 크기 조절
METEOR_SIZE = (85, 85)
meteor_surf = pygame.transform.scale(pygame.image.load(join('images','meteor.png')).convert_alpha(), METEOR_SIZE)
flame_meteor_surf = pygame.transform.scale(pygame.image.load(join('images', 'flame_meteor.png')).convert_alpha(), METEOR_SIZE)
healing_meteor_surf = pygame.transform.scale(pygame.image.load(join('images', 'healing_meteor.png')).convert_alpha(), METEOR_SIZE)

# 스프라이트 그룹
all_sprites, meteor_sprites, flame_meteor_sprites, healing_meteor_sprites, laser_sprites = [pygame.sprite.Group() for _ in range(5)]
effects_sprites = pygame.sprite.Group()
comet_sprites = pygame.sprite.Group()

player = Player(all_sprites)
for i in range(20): Star(all_sprites, star_surf)

# 커스텀 이벤트
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500) # 운석 생성 간격 (0.5초)

# 점수 관련 변수
score, bonus_score, high_score = 0, 0, load_high_score()

# 경고 메시지 관련 변수
warning_flags, warning_timers = {}, {}
WARNING_RULES = {100: "Flame meteor is coming!", 300: "More Flame meteors are coming!"}

# 운석 샤워 이벤트 관련 변수
unavoided_meteor_count, is_shower_active = 0, False
shower_duration, shower_cooldown, shower_end_time = 5000, 10000, 0

flash_timer = 0 # 화면 번쩍임 효과 변수

# 운석 생성 규칙을 데이터로 정의
SPAWN_RULES = [
    (300, [(FlameMeteor, flame_meteor_surf, flame_meteor_sprites, 2), (Meteor, meteor_surf, meteor_sprites, 1)]),
    (100, [(FlameMeteor, flame_meteor_surf, flame_meteor_sprites, 1), (Meteor, meteor_surf, meteor_sprites, 3)]),
    (0,   [(Meteor, meteor_surf, meteor_sprites, 1)])
]

# =====================================================================
# 4. 메인 게임 루프
# =====================================================================

while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == meteor_event:
            if r.randint(1, 100) <= 3:
                Comet(comet_surf, (all_sprites, comet_sprites))
            else:
                x, y = r.randint(0, WINDOW_WIDTH), r.randint(-200, -100)
                if r.randint(1, 100) <= 5:
                    HealingMeteor(healing_meteor_surf, (x, y), (all_sprites, healing_meteor_sprites))
                else:
                    for threshold, options in SPAWN_RULES:
                        if score >= threshold:
                            classes, surfs, groups, weights = zip(*options)
                            ChosenMeteor = r.choices(classes, weights=weights, k=1)[0]
                            idx = classes.index(ChosenMeteor)
                            ChosenMeteor(surfs[idx], (x,y), (all_sprites, groups[idx]))
                            break

    score = (pygame.time.get_ticks() // 100) + bonus_score # 점수 계산

    # 운석 샤워 이벤트 처리
    if unavoided_meteor_count >= 10 and not is_shower_active and pygame.time.get_ticks() > shower_end_time:
        is_shower_active = True; unavoided_meteor_count = 0
        pygame.time.set_timer(meteor_event, 350)
        warning_timers['shower'] = pygame.time.get_ticks() + shower_duration
        shower_end_time = pygame.time.get_ticks() + shower_duration + shower_cooldown
    if is_shower_active and pygame.time.get_ticks() > warning_timers.get('shower', 0):
        is_shower_active = False
        pygame.time.set_timer(meteor_event, 500)

    all_sprites.update(dt)
    effects_sprites.update(dt)
    collision()

    # 화면 그리기
    display_surface.fill("#0E010100")
    all_sprites.draw(display_surface)
    for effect in effects_sprites:
        if hasattr(effect, 'draw'):
             effect.draw(display_surface)

    damaged_meteors = [m for m in flame_meteor_sprites if m.health == 1]
    for meteor in damaged_meteors:
        bar_x = meteor.rect.x + (meteor.rect.width - HEALTH_BAR_WIDTH) / 2
        bar_y = meteor.rect.y - HEALTH_BAR_HEIGHT - 5
        health_ratio = meteor.health / 2.0
        current_bar_width = HEALTH_BAR_WIDTH * health_ratio
        pygame.draw.rect(display_surface, BACKGROUND_BAR_COLOR, (bar_x, bar_y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
        pygame.draw.rect(display_surface, HEALTH_BAR_COLOR, (bar_x, bar_y, current_bar_width, HEALTH_BAR_HEIGHT))
    display_score(); display_lives()

    # 경고 메시지 표시 로직
    active_warnings = []
    for score_threshold, message in WARNING_RULES.items():
        if score >= score_threshold and not warning_flags.get(score_threshold):
            warning_flags[score_threshold] = True
            warning_timers[score_threshold] = pygame.time.get_ticks() + 3000
        if warning_timers.get(score_threshold, 0) > pygame.time.get_ticks():
            active_warnings.append(message)
    if is_shower_active: active_warnings.append("METEOR SHOWER!")
    for i, message in enumerate(active_warnings):
        y_offset = i * (warning_font.get_height() + 5)
        display_warning(message, y_offset)

    if flash_timer > pygame.time.get_ticks():
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 0, 0, 100))
        display_surface.blit(overlay, (0,0))

    pygame.display.update()

# =====================================================================
# 5. 게임 오버 루프
# =====================================================================
final_score = score
if final_score > high_score:
    high_score = final_score
    save_high_score(high_score)

game_over = True
while game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            game_over = False
    display_game_over(final_score, high_score)
    pygame.display.update()

pygame.quit()
