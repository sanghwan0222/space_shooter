import pygame
from os.path import join
from random import randint, uniform

# =====================================================================
# 1. 클래스 정의 (Player, Star, Laser, Meteor, FlameMeteor)
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
        self.rect.center += self.direction * self.speed * dt 
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill() # 생명주기가 끝나면 운석 제거
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
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
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
    global running
    
    if not player.invincible:
        # 플레이어와 일반 운석 충돌 시
        collided_meteor = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
        if collided_meteor:
            handle_player_hit()
            AnimatedExplosion(explosion_frames, collided_meteor[0].rect.center, all_sprites) # 폭발 생성
            damage_sound .play() # 데미지 사운드 재생

        # 플레이어와 강화 운석 충돌 시
        collided_flame = pygame.sprite.spritecollide(player, flame_meteor_sprites, True,pygame.sprite.collide_mask)
        if collided_flame:
            handle_player_hit()
            AnimatedExplosion(explosion_frames, collided_flame[0].rect.center, all_sprites) # 폭발 생성
            damage_sound.play() # 데미지 사운드 재생

    # for문을 통해 레이저와 운석 충돌 검사
    for laser in laser_sprites:
        # 레이저에 맞은 운석들을 리스트로 받아옴
        hit_meteors = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if hit_meteors:
            laser.kill()
            for meteor in hit_meteors:
                AnimatedExplosion(explosion_frames, meteor.rect.center, all_sprites) # 폭발 생성
                explosion_sound.play() # 폭발 사운드 재생

    for laser in laser_sprites:
        collided_flames = pygame.sprite.spritecollide(laser, flame_meteor_sprites, False)
        if collided_flames:
            laser.kill()
            for meteor in collided_flames:
                meteor.health -= 1
                if meteor.health <= 0:
                    meteor.kill()
                    AnimatedExplosion(explosion_frames, meteor.rect.center, all_sprites) # 폭발 생성
                    explosion_sound.play() # 폭발 사운드 재생

def handle_player_hit():
    global running
    player.lives -= 1 # 목숨 1 감소
    player.invincible = True # 무적 상태로 변경
    player.invincible_time = pygame.time.get_ticks() # 현재 시간을 무적 시작 시간으로 기록
    if player.lives <= 0:
        running = False

score = 0
def display_score():
    global score
    score = pygame.time.get_ticks() // 100 #게임이 시작된 이후 경과 시간 //100
    text_surf = font.render(str(score), True, (240,240,240)) #RGB 색상
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2,WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,10).move(0,-8), 5, 10)

def display_lives():
    # 남은 목숨만큼 반복
    for i in range(player.lives):
        x = WINDOW_WIDTH - 50 - (i * (life_surf.get_width() + 10))
        y = 30
        display_surface.blit(life_surf, (x, y))

warning_font = None 
def display_warning():
    text_surf = warning_font.render("flame meteor is coming.", True, 'red')
    text_rect = text_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    display_surface.blit(text_surf, text_rect)

def display_game_over():
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(150)
    overlay.fill((0, 0, 0))
    display_surface.blit(overlay, (0, 0))

    score_text_surf = warning_font.render(f"Final Score: {score}", True, (255, 255, 255))
    score_text_rect = score_text_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 50))
    display_surface.blit(score_text_surf, score_text_rect)

    restart_text_surf = font.render("Press any key to quit", True, (200, 200, 200))
    restart_text_rect = restart_text_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 50))
    display_surface.blit(restart_text_surf, restart_text_rect)

# =====================================================================
# 3. 게임 초기화 및 설정
# =====================================================================

pygame.init() 
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) #튜플로 받기
running = True
clock= pygame.time.Clock() #게임 속도 조절
pygame.display.set_caption('운석 뿌셔') #게임 이름 설정

# 이미지 및 폰트 로드
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
laser_surf = pygame.image.load(join('images','laser.png')).convert_alpha()
life_surf = pygame.image.load(join('images', 'heart.png')).convert_alpha()
life_surf = pygame.transform.scale(life_surf, (40, 40))
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
warning_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 50)
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)] 

#배경음악 설정
laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav')) # 레이저 사운드
laser_sound.set_volume(0.1) # 레이저 사운드 볼륨 설정
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav')) # 레이저 사운드
explosion_sound.set_volume(0.6) # 레이저 사운드 볼륨 설정
damage_sound = pygame.mixer.Sound(join('audio', 'damage.ogg')) # 데미지 사운드
damage_sound .set_volume(0.5) # 데미지 사운드 볼륨 설정
game_music = pygame.mixer.Sound(join('audio', 'game.wav')) # 게임 사운드
game_music.set_volume(0.3) # 게임 사운드 볼륨 설정
game_music.play(-1) # 게임 사운드 무한 반복 재생




# === 운석 이미지 로드 및 크기 조절===
METEOR_SIZE = (85, 85) # 원하는 운석 크기를 여기서 한번에 조절
# 기존 운석
meteor_surf = pygame.image.load(join('images','meteor.png')).convert_alpha() #운석 이미지 불러오기
meteor_surf = pygame.transform.scale(meteor_surf, METEOR_SIZE)
# 강화 운석 (수정된 flame_meteor.png 사용)
flame_meteor_surf = pygame.image.load(join('images', 'flame_meteor.png')).convert_alpha() 
flame_meteor_surf = pygame.transform.scale(flame_meteor_surf, METEOR_SIZE)
# =================================================

# sprites 
all_sprites = pygame.sprite.Group() #스프라이트 그룹 생성
meteor_sprites = pygame.sprite.Group()      # 운석 스프라이트 그룹 생성
flame_meteor_sprites = pygame.sprite.Group() # 강화 운석 그룹
laser_sprites = pygame.sprite.Group()       # 레이저 스프라이트 그룹 생성


player = Player(all_sprites)
for i in range(20):
    Star(all_sprites, star_surf) # 별 생성 및 추가

#custom evets -> meteor event
meteor_event= pygame.event.custom_type() 
pygame.time.set_timer(meteor_event, 400)

warning_message_shown = False
show_warning_until = 0

# =====================================================================
# 4. 메인 게임 루프
# =====================================================================

while running:
    dt = clock.tick(60) / 1000 #프레임 움직임 조절(delta time)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #constant for closing game
            running = False # 이제 내 맘대로 게임 키고 끄기 가능
        if event.type == meteor_event:
            x,y = randint(0, WINDOW_WIDTH), randint(-200,-100) # 운석의 시작 위치 설정
            
            if score >= 100 and randint(1, 4) == 1:
                FlameMeteor(flame_meteor_surf, (x, y), (all_sprites, flame_meteor_sprites))
            else:
                Meteor(meteor_surf, (x,y), (all_sprites, meteor_sprites)) # 운석 생성
    
    all_sprites.update(dt) 
    collision()
    
    display_surface.fill("#14121200") #배경색 설정
    all_sprites.draw(display_surface) 
    display_score()
    display_lives()
    
    if score >= 100 and not warning_message_shown:
        show_warning_until = pygame.time.get_ticks() + 3000
        warning_message_shown = True

    if pygame.time.get_ticks() < show_warning_until:
        display_warning()
        
    pygame.display.update()

# =====================================================================
# 5. 게임 오버 루프
# =====================================================================

game_over = True
while game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = False 
        if event.type == pygame.KEYDOWN:
            game_over = False

    display_game_over()
    pygame.display.update()

pygame.quit() #중요함