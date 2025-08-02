import pygame
from os.path import join
from random import randint, uniform

class Player(pygame.sprite.Sprite):
     #sprite 클래스 상속
    def __init__(self,groups):
        super().__init__(groups) #부모 클래스 초기화
        self.image= pygame.image.load(join('images','player.png')).convert_alpha()
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction= pygame.Vector2()  # 방향 벡터 초기화

        self.pos = pygame.Vector2(self.rect.center)
        self.direction= pygame.Vector2()
        self.speed =300

        #cooldown time
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration =2000

        #목숨 개수
        self.lives = 3
        self.invincible = False # 피격 후 잠시 무적
        self.invincible_time = 0
        self.invincible_duration = 150 # 1.5초 무적
    
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
        self.rect.center = (round(self.pos.x), round(self.pos.y)) # 반올림하여 정수 좌표로 변환
        
        recent_keys = pygame.key.get_just_pressed() 
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf,self.rect.midtop, (all_sprites, laser_sprites))  # 레이저 생성
            print('fire laser')
            self.can_shoot =True
            self.laser_shoot_time = pygame.time.get_ticks()
        
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
        self.rect = self.image.get_frect(midbottom=pos)  # 레이저의 위치 설정
        self.speed =1000

    def update(self,dt):
        self.rect.centery -= self.speed * dt  # 레이저 위로 이동  
        if self.rect.bottom <50:
            self.kill()
  
class Meteteor(pygame.sprite.Sprite):
    def __init__(self,surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.start_time =pygame.time.get_ticks()
        self.lifetime = randint(2000, 5000)  # 운석의 생명주기 설정 (2초에서 5초 사이)
        self.direction =pygame.Vector2(uniform(-0.5,0.5),1) # 아래로 떨어지는 방향 벡터
        self.speed = randint(200,400)
    
    def update(self,dt):
        self.rect.center += self.direction * self.speed * dt 
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()  # 생명주기가 끝나면 운석 제거
        
def collision():
    global running
     # 1. 플레이어가 무적이 아닐 때만 충돌을 검사
    if not player.invincible:
        collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True)
        if collision_sprites:
            print("운석에 맞았습니다!")
            player.lives -= 1               # 목숨 1 감소
            player.invincible = True        # 무적 상태로 변경
            player.invincible_time = pygame.time.get_ticks() # 현재 시간을 무적 시작 시간으로 기록
            
            # 목숨이 0 이하면 게임 종료
            if player.lives <= 0:
                running = False

    for laser in laser_sprites: #for문을 통해 레이저와 운석 충돌 검사
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill() 

def display_score():
    current_time = pygame.time.get_ticks() // 100 #게임이 시작된 이후 경과 시간 //100
    text_surf = font.render(str(current_time), True, (240,240,240)) #RGB 색상
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2,WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,10).move(0,-8), 5, 10)

def display_lives():
    # 남은 목숨만큼 반복
    for i in range(player.lives):
        # 아이콘 위치 계산 (화면 우측 상단부터 왼쪽으로)
        x = WINDOW_WIDTH - 50 - (i * (life_surf.get_width() + 10))
        y = 30
        display_surface.blit(life_surf, (x, y))

#general setup
pygame.init() 
WINDOW_WIDTH, WINDOW_HEIGHT =1200,720
display_surface =pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) #튜플로 받기
running = True
clock= pygame.time.Clock() #게임 속도 조절
pygame.display.set_caption('운석 뿌셔') #게임 이름 설정

#plain surface
surf = pygame.Surface((100,200)) #튜플로 묶기
surf.fill('darkorange') # target 색깔 설정
x=100

star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()

all_sprites = pygame.sprite.Group() #스프라이트 그룹 생성
for i in range(20):
    Star(all_sprites, star_surf)  # 별 생성 및 추가



for i in range(20):
    Star(all_sprites,star_surf)  # 별 생성 및 추가
player = Player(all_sprites)

#import
meteor_surf = pygame.image.load(join('images','meteor.png')).convert_alpha() #운석 이미지 불러오기 
laser_surf = pygame.image.load(join('images','laser.png')).convert_alpha() #레이저 이미지 불러오기
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)

life_surf = pygame.image.load(join('images', 'heart.png')).convert_alpha()
life_surf = pygame.transform.scale(life_surf, (40, 40))
# sprites 
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()  # 운석 스프라이트 그룹 생성
laser_sprites = pygame.sprite.Group()  # 레이저 스프라이트 그룹 생성
for i in range(20):
    Star(all_sprites, star_surf)
player = Player(all_sprites)

#custom evets -> meteor event
meteor_event= pygame.event.custom_type() 
pygame.time.set_timer(meteor_event,500)


while running:
    dt=clock.tick() /1000   #프레임 움직임 조절(delta time)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #constant for closing game
            running = False # 이제 내 맘대로 게임 키고 끄기 가능
        if event.type == meteor_event:
            x,y =randint(0, WINDOW_WIDTH), randint(-200,-200) # 운석의 시작 위치 설정
            Meteteor(meteor_surf, (x,y), (all_sprites, meteor_sprites))  # 운석 생성
        
    #스프라이트 그룹 업데이트
    all_sprites.update(dt) 
    collision()
    
    
 

    # 레이저와 운석 충돌 검사
    for laser in laser_sprites: 
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True) 
        if collided_sprites:
            laser.kill()

    #draw the game  
    display_surface.fill("#350f3a") #배경색 설정
    all_sprites.draw(display_surface) 
    display_score()
    display_lives()
    pygame.display.update()
   

pygame.quit() #증요함 
