import pygame
from os.path import join
from random import randint, uniform
import pickle # 최고 점수 저장을 위해 pickle 모듈 추가

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

        #cooldown time
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 500

        #목숨 개수
        self.lives = 3
        self.invincible = False # 피격 후 잠시 무적
        self.invincible_time = 0
        self.invincible_duration = 1500 # 1.5초 무적

        #mask
        self.mask = pygame.mask.from_surface(self.image) # 충돌 처리를 위하여 player class 안에 마스크 생성
    
    def laser_timer(self): 
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    #무적 상태 처리 
    def check_invincibility(self):
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.invincible_time > self.invincible_duration:
                self.invincible = False # 무적 상태 해제
    
    def update(self,dt):
        keys = pygame.key.get_pressed() #키보드 입력 받기
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT]) #왼쪽 오른쪽 키 입력
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])   #위 아래 키 입력
        
        # 벡터 정규화 (길이가 0이 아닐 때만)
        if self.direction.length() != 0:
            self.direction = self.direction.normalize()

        # 수정: self.pos를 업데이트한 후 rect의 중앙에 적용
        self.pos += self.direction * self.speed * dt
        
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
    

class Star(pygame.sprite.Sprite):
    def __init__(self, groups,surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=(randint(0,WINDOW_WIDTH),randint(0,WINDOW_HEIGHT)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf,pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom=pos) # 레이저의 위치 설정
        self.speed = 1000 #레이저 속도 설정
        self.mask = pygame.mask.from_surface(self.image)

    def update(self,dt):
        self.rect.centery -= self.speed * dt # 레이저 위로 이동
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self,surf, pos, groups):
        super().__init__(groups)
        self.origminal_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.start_time =pygame.time.get_ticks()
        self.lifetime = randint(2000, 5000) # 운석의 생명주기 설정 (2초에서 5초 사이)
        self.direction =pygame.Vector2(uniform(-0.5,0.5),1) # 아래로 떨어지는 방향 벡터
        self.speed = randint(200,400)
        self.rotation_speed =randint(40,80)
        self.rotation = 0
    
    def update(self,dt):
        global unavoided_meteor_count
        self.rect.center += self.direction * self.speed * dt 
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill() # 생명주기가 끝나면 운석 제거
        if self.rect.top > WINDOW_HEIGHT: # 화면 밖으로 나가면 제거
            unavoided_meteor_count += 1
            self.kill()
        self.rotation+=self.rotation_speed * dt # 회전 속도 적용
        self.image = pygame.transform.rotozoom(self.origminal_surf, self.rotation, 1) # 원본 이미지를 회전
        self.rect = self.image.get_frect(center= self.rect.center) # 회전 후 rect 업데이트

class FlameMeteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = randint(4000, 6000)
        self.direction = pygame.Vector2(uniform(-0.2, 0.2), 1)
        self.speed = randint(300,500)
        self.health = 2 # 체력: 2번 맞아야 파괴됨

    def update(self, dt):
        global unavoided_meteor_count
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        if self.rect.top > WINDOW_HEIGHT: # 화면 밖으로 나가면 제거
            unavoided_meteor_count += 1
            self.kill()

# 추가: HealingMeteor 클래스
class HealingMeteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.origminal_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = randint(3000, 7000)
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(150, 300)
        self.rotation_speed = randint(30, 60)
        self.rotation = 0

    def update(self, dt):
        global unavoided_meteor_count
        self.rect.center += self.direction * self.speed * dt
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.origminal_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center= self.rect.center)
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        if self.rect.top > WINDOW_HEIGHT:
            unavoided_meteor_count += 1
            self.kill()


# =====================================================================
# 2. 게임 함수 정의 (collision, handle_player_hit, display 등)
# =====================================================================

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
        
    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

def collision():
    global bonus_score
    
    if not player.invincible:
        # 플레이어와 운석 그룹 충돌
        if pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask) or \
           pygame.sprite.spritecollide(player, flame_meteor_sprites, True, pygame.sprite.collide_mask):
            handle_player_hit()
            damage_sound.play()

        # 플레이어와 힐링 운석 충돌
        if pygame.sprite.spritecollide(player, healing_meteor_sprites, True, pygame.sprite.collide_mask):
            if player.lives < 3:
                player.lives += 1
            explosion_sound.play() 

    # 레이저와 운석 충돌
    for laser in laser_sprites:
        # 일반 운석
        if pygame.sprite.spritecollide(laser, meteor_sprites, True):
            laser.kill()
            bonus_score += 10
            explosion_sound.play()
        
        # 강화 운석
        collided_flames = pygame.sprite.spritecollide(laser, flame_meteor_sprites, False)
        if collided_flames:
            laser.kill()
            for meteor in collided_flames:
                meteor.health -= 1
                if meteor.health <= 0:
                    meteor.kill()
                    bonus_score += 20
                    explosion_sound.play()

        # 힐링 운석
        if pygame.sprite.spritecollide(laser, healing_meteor_sprites, True):
            if player.lives < 3:
                player.lives += 1
            laser.kill()
            explosion_sound.play() # 힐링 운석 파괴 시 사운드 추가

def handle_player_hit():
    global running
    player.lives -= 1
    player.invincible = True
    player.invincible_time = pygame.time.get_ticks()
    if player.lives <= 0:
        running = False

def display_score():
    text_surf = font.render(str(score), True, (240,240,240))
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2,WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,10).move(0,-8), 5, 10)

def display_lives():
    for i in range(player.lives):
        x = WINDOW_WIDTH - 50 - (i * (life_surf.get_width() + 10))
        y = 30
        display_surface.blit(life_surf, (x, y))

def display_warning(message, color='red'):
    text_surf = warning_font.render(message, True, color)
    text_rect = text_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    display_surface.blit(text_surf, text_rect)

def display_game_over(final_score, high_score):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(150)
    overlay.fill((0, 0, 0))
    display_surface.blit(overlay, (0, 0))

    score_text = f"Final Score: {final_score}"
    if final_score > high_score:
        score_text = f"New High Score: {final_score}"

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
        with open("highscore.dat", "wb") as file:
            pickle.dump(score, file)
    except IOError:
        print("Error: Could not save high score.")

def load_high_score():
    try:
        with open("highscore.dat", "rb") as file:
            return pickle.load(file)
    except (IOError, pickle.UnpicklingError):
        return 0

# =====================================================================
# 3. 게임 초기화 및 설정
# =====================================================================

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

# 배경음악 설정
laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.1)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
explosion_sound.set_volume(0.6)
damage_sound = pygame.mixer.Sound(join('audio', 'damage.ogg'))
damage_sound.set_volume(0.5)
game_music = pygame.mixer.Sound(join('audio', 'game.wav'))
game_music.set_volume(0.3)
game_music.play(-1)

#flame meteor의 체력
HEALTH_BAR_WIDTH = 40
HEALTH_BAR_HEIGHT = 5
HEALTH_BAR_COLOR = (0, 255, 0)  # 초록색
BACKGROUND_BAR_COLOR = (255, 0, 0) # 빨간색

# 운석 이미지 로드 및 크기 조절
METEOR_SIZE = (85, 85)
meteor_surf = pygame.transform.scale(pygame.image.load(join('images','meteor.png')).convert_alpha(), METEOR_SIZE)
flame_meteor_surf = pygame.transform.scale(pygame.image.load(join('images', 'flame_meteor.png')).convert_alpha(), METEOR_SIZE)
healing_meteor_surf = pygame.transform.scale(pygame.image.load(join('images', 'healing_meteor.png')).convert_alpha(), METEOR_SIZE)

# 스프라이트 그룹
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
flame_meteor_sprites = pygame.sprite.Group()
healing_meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

player = Player(all_sprites)
for i in range(20):
    Star(all_sprites, star_surf)

# 커스텀 이벤트
meteor_event = pygame.event.custom_type() 
pygame.time.set_timer(meteor_event, 500) # 운석 생성 간격 (0.5초)

# 점수 관련 변수
score = 0
bonus_score = 0
high_score = load_high_score()

# 경고 메시지 관련 변수
warning_flags = {'100': False, '300': False, 'shower': False}
warning_timers = {'100': 0, '300': 0, 'shower': 0}

# 운석 샤워 이벤트 관련 변수
unavoided_meteor_count = 0
is_shower_active = False
shower_duration = 5000 # 5초
shower_cooldown = 10000 # 10초
shower_end_time = 0

# =====================================================================
# 4. 메인 게임 루프
# =====================================================================

while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            
            # 5% 확률로 힐링 운석 생성
            if randint(1, 100) <= 5:
                HealingMeteor(healing_meteor_surf, (x, y), (all_sprites, healing_meteor_sprites))
            # 점수에 따른 운석 생성 로직
            elif score >= 300:
                if randint(1, 3) == 1: # 1/3 확률로 일반 운석
                    Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))
                else: # 2/3 확률로 강화 운석
                    FlameMeteor(flame_meteor_surf, (x, y), (all_sprites, flame_meteor_sprites))
            elif score >= 100:
                if randint(1, 4) == 1: # 1/4 확률로 강화 운석
                    FlameMeteor(flame_meteor_surf, (x, y), (all_sprites, flame_meteor_sprites))
                else:
                    Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))
            else:
                Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))

    # 점수 계산
    score = (pygame.time.get_ticks() // 100) + bonus_score

    # 운석 샤워 이벤트 처리
    if unavoided_meteor_count >= 10 and not is_shower_active and pygame.time.get_ticks() > shower_end_time:
        is_shower_active = True
        unavoided_meteor_count = 0
        pygame.time.set_timer(meteor_event, 250) # 운석 생성 속도 2배
        warning_timers['shower'] = pygame.time.get_ticks() + shower_duration
        shower_end_time = pygame.time.get_ticks() + shower_duration + shower_cooldown

    if is_shower_active and pygame.time.get_ticks() > warning_timers['shower']:
        is_shower_active = False
        pygame.time.set_timer(meteor_event, 500) # 운석 생성 속도 원상 복구

    # 업데이트 및 충돌 감지
    all_sprites.update(dt) 
    collision()
    
    # 화면 그리기
    display_surface.fill("#0E010100")
    all_sprites.draw(display_surface) 
    for meteor in flame_meteor_sprites:
        # 체력이 1일 때만(피해를 입었을 때만) 체력 바를 표시합니다.
        if meteor.health == 1:
            # 체력 바 위치 계산 (운석 이미지 바로 위)
            bar_x = meteor.rect.x + (meteor.rect.width - HEALTH_BAR_WIDTH) / 2
            bar_y = meteor.rect.y - HEALTH_BAR_HEIGHT - 5

            # 체력 비율 계산 (최대 체력 2 기준)
            health_ratio = meteor.health / 2.0
            current_bar_width = HEALTH_BAR_WIDTH * health_ratio

            # 체력 바 그리기
            pygame.draw.rect(display_surface, BACKGROUND_BAR_COLOR, (bar_x, bar_y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
            pygame.draw.rect(display_surface, HEALTH_BAR_COLOR, (bar_x, bar_y, current_bar_width, HEALTH_BAR_HEIGHT))
    display_score()
    display_lives()
  
    
    # 경고 메시지 표시
    if score >= 100 and not warning_flags['100']:
        warning_flags['100'] = True
        warning_timers['100'] = pygame.time.get_ticks() + 3000
    if score >= 300 and not warning_flags['300']:
        warning_flags['300'] = True
        warning_timers['300'] = pygame.time.get_ticks() + 3000

    if pygame.time.get_ticks() < warning_timers['100']:
        display_warning("Flame meteor is coming!")
    if pygame.time.get_ticks() < warning_timers['300']:
        display_warning("More Flame meteors are coming!")
    if is_shower_active:
        display_warning("METEOR SHOWER!")
        
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