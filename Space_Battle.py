import pygame
import os
import random 
import sys

pygame.init()
pygame.mixer.init() # Sound
pygame.font.init()  # Fonts

# Global Variables
WIDTH, HEIGHT = 750, 700
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock() # Clock object
FPS = 60                    # Frames per second

# Title of Game
pygame.display.set_caption("Space Battle")

# COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Bold Fonts
seventy_B_font = pygame.font.SysFont("mono", 70, bold = True)
sixty_five_B_font = pygame.font.SysFont("mono", 65, bold = True)
fifty_five_B_font = pygame.font.SysFont("mono", 55, bold = True)
fifty_B_font = pygame.font.SysFont("mono", 50, bold = True)
forty_B_font= pygame.font.SysFont("mono", 40, bold = True)
thirty_B_font = pygame.font.SysFont("mono", 30, bold = True)

# Regular Fonts
fifty_font = pygame.font.SysFont("mono", 50)  
thirty_five_font = pygame.font.SysFont("mono", 35) 
thirty_font = pygame.font.SysFont("mono", 30)
twenty_five_font = pygame.font.SysFont("mono", 25) 
twenty_font = pygame.font.SysFont("mono", 20)   

def resource_path(relative_path):
    base_path = getattr(sys, 'MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


all_sounds = ["shoot", "hit", "enemy_past", "health", "colliding", "game_over", "Win", "level1",
              "level2", "level3", "level4", "opening_sb", "opening_in", "opening_c", "opening_o"]

for i in all_sounds:
    globals()[f"{i}"] = pygame.mixer.Sound(resource_path("sound\\" + str(i) + ".wav"))

# List of Sound names
sounds = [shoot, hit, enemy_past, health, colliding, game_over, Win, level1, level2, level3, level4]

# Default music
music = pygame.mixer.music.load(resource_path("sound\\Eye_Tiger.wav"))

all_art = ["Health_restorer", "red_enemy", "green_enemy", "blue_enemy", "light_blue_enemy",
           "light_purple_enemy", "boss",  "player", "Red_Laser", "Blue_Laser",  "Green_Laser",
           "Yellow_Laser", "LBlue_Laser", "LPurple_Laser",  "menu_arrow", "mute", "unmute",  
           "play_button", "pause_button", "return_arrow", "check_box", "checked_box"]

for i in all_art:
    globals()[f"{i}"] = pygame.image.load(resource_path("art\\" + str(i) + ".png"))
    globals()[f"{i}"].convert()    
    globals()[f"{i}"].set_colorkey(WHITE)

# Load Background image
BG = pygame.image.load(resource_path("art\\BG.png")).convert()
checked = 1



class Laser:
    def __init__(self, x, y, image):   
        self.x = x
        self.y = y
        self.image = image
        self.mask = pygame.mask.from_surface(self.image)
        
    def draw(self, window):
        window.blit(self.image, (self.x, self.y))
    
    def move(self, velocity):
        self.y += velocity

    def off_screen(self, height):
        return self.y >= height or self.y < 0
    
    def collision(self, obj):
        return collide(obj, self)
        
class Ship:
    Shoot_Cool_Down = 20
    
    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_image = None
        self.laser_image = None
        self.lasers = []
        self.restore_image = None
        self.restore = []
        self.cool_down_counter = 0
    
    def draw(self, window):
        window.blit(self.ship_image, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)
    
    def laser_movement(self, velocity, obj):
        self.Shooting_cool_down()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -=10
                self.lasers.remove(laser)             
    
    def Shooting_cool_down(self):
        if self.cool_down_counter >= self.Shoot_Cool_Down:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
    
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_image)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_image.get_width()

    def get_height(self):
        return self.ship_image.get_height()
    

class Player(Ship): #inherits from ship
    def __init__(self, x, y, health = 100):
        super().__init__(x, y, health)
        self.ship_image = player
        self.laser_image = Yellow_Laser
        self.mask = pygame.mask.from_surface(self.ship_image) #for collision
        self.max_health = health
    
    def laser_movement(self, velocity, objs):
        self.Shooting_cool_down()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
                return 0
            else:
                for obj in objs:
                    if laser.collision(obj):
                        if obj.boss:
                            obj.health -= 2
                            if obj.health <= 0:
                                objs.remove(obj)                                                            
                        else:
                            objs.remove(obj)                            
                        self.lasers.remove(laser) 
                        return 1
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y-38, self.laser_image)
            self.lasers.append(laser)
            self.cool_down_counter = 1       
                        
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
    
    def healthbar(self, window):
        pygame.draw.rect(window, RED, (self.x, self.y + self.ship_image.get_height() + 10, self.ship_image.get_width(), 10))
        pygame.draw.rect(window, GREEN, (self.x, self.y + self.ship_image.get_height() + 10, self.ship_image.get_width() * (self.health/self.max_health), 10))
        
        
class Enemy(Ship): #inherits from ship
    Color_Dict = { "red": (red_enemy, Red_Laser), 
                   "green": (green_enemy, Green_Laser),
                   "blue": (blue_enemy, Blue_Laser),
                   "Lblue": (light_blue_enemy, LBlue_Laser),
                   "Lpurple": (light_purple_enemy, LPurple_Laser),
                   "boss": (boss, LBlue_Laser)
    }
    def __init__(self, x, y, color, direction, health = 100, boss = False):
        super().__init__(x, y, health)
        self.ship_image, self.laser_image = self.Color_Dict[color]
        self.direction = direction 
        self.boss = boss
        self.mask = pygame.mask.from_surface(self.ship_image)
        self.max_health = health
        
    def move(self, velocity):
        self.y += velocity
    
    def xRight(self, velocity):
        if self.boss and self.y <= 100:
            self.y += velocity 
        elif not self.boss:
            self.y += velocity 
            
        # If off screen on Right side
        if self.x >= WIDTH - 50: 
            self.x -= velocity -1 # Move Left 
            
        # If off screen on Left side
        elif self.x <= 0:
            self.x += velocity - 1  # Move Right   
            
        # If on screen
        else:
            self.x += velocity - 1 # Move right
            
    def xLeft(self, velocity):
        if self.boss and self.y <= 100:
            self.y += velocity 
        elif not self.boss:
            self.y += velocity 
            
        # If off screen on the Right
        if self.x >= WIDTH - 50: 
            self.x -= velocity - 1  # move left
            
        # If off screen on the Left
        elif self.x <= 0:
            self.x += velocity - 1 # move right
            
        # if on screen
        else:
            self.x -= velocity - 1 # move left
    
    def shoot(self):
        if self.cool_down_counter == 0:
            if not self.boss:
                laser = Laser(self.x-19, self.y, self.laser_image)
                self.lasers.append(laser)
                self.cool_down_counter = 1 
            else:
                laser = Laser(self.x, self.y+39, self.laser_image)
                self.lasers.append(laser)
                self.cool_down_counter = 1                 

    def draw(self, window):
        super().draw(window)
        if self.boss == True:
            self.healthbar(window)
    
    def healthbar(self, window):
        pygame.draw.rect(window, RED, (self.x, self.y - 15, self.ship_image.get_width(), 10))
        pygame.draw.rect(window, GREEN, (self.x, self.y - 15, self.ship_image.get_width() * (self.health/self.max_health), 10))
            

class restore_health(Ship):
    Color_Dict = {"green": Health_restorer}
    
    def __init__(self, x, y, color, health = 100):
        super().__init__(x, y, health)
        self.ship_image = self.Color_Dict[color]
        self.mask = pygame.mask.from_surface(self.ship_image)
        
    def move(self, velocity):
        self.y += velocity  

#####################################################    
     
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None   

def volume_off():
    for i in sounds:
        i.set_volume(0) 
    pygame.mixer.music.pause()

def volume_on():
    for i in sounds:
        i.set_volume(1) 
    pygame.mixer.music.unpause()        
    
####################################################    

def main():
    run = True 
    
    Level = 0
    Lives = 3
    Score = 0
    
    restore = []
    enemies = []   
    
    # make random numbers list
    numbers = set()
    for i in range(100, 2500, 70):
        numbers.add(i)
    
    res_size = [-1500]
    res_velocity = 1
    
    wave_size = 20
    enemy_velocity = 1 # starting velocity
    switch_count = 0
    
    player_velocity = 8 
    laser_velocity = 7
    player = Player(300, 550)
        
    Game_over = False
    lose_count = 0   
    
    win = False
    win_count = 0   
        
    # pause temps
    t_enemy_velocity = enemy_velocity
    t_res_velocity = res_velocity
    t_player_velocity = player_velocity
    t_laser_velocity = laser_velocity   
            
    def redraw_window(muted = False, pause = False):
        # create labels
        lives_label = forty_B_font.render(f"Lives: {Lives}", 1, WHITE)
        level_label = forty_B_font.render(f"Level: {Level}", 1, WHITE)
        score_label = forty_B_font.render(f"Score: {Score}", 1, WHITE)
        
        # display 
        WINDOW.blit(BG, (0,0))        
        WINDOW.blit(level_label, (10, 10)) 
        WINDOW.blit(score_label, (WIDTH/2 - score_label.get_width()/2, 10))                
        WINDOW.blit(lives_label, (WIDTH-level_label.get_width() - 20, 10))
        
        # draw player
        player.draw(WINDOW)        
        
        # draw enemies      
        for enemy in enemies:
            enemy.draw(WINDOW)
        
        # draw health restorers
        for res in restore:
            res.draw(WINDOW)
        
        # RETURN ARROW
        WINDOW.blit(return_arrow, (10, 60))         
        
        # MUTE AND UNMUTE BUTTONS
        if not muted:
            WINDOW.blit(mute, (10, 110))
        elif muted:
            WINDOW.blit(unmute, (10, 110))     
        
        #  PAUSE AND PLAY BUTTONS
        if not pause:
            WINDOW.blit(pause_button, (10, 170))
        elif pause:
            pause_label = seventy_B_font.render("PAUSED", 1, (255, 255, 0))
            WINDOW.blit(pause_label, (WIDTH/2 - pause_label.get_width()/2, 350))                 
            WINDOW.blit(play_button, (10, 170))                     
        
        ############################
        # GAME OVER AND WIN LABELS #
        ############################
        
        if Game_over:
            Game_Over_label = seventy_B_font.render("GAME OVER", 1, RED)
            WINDOW.blit(Game_Over_label, (WIDTH/2 - Game_Over_label.get_width()/2, 350))
        
        if win:
            winner_label = seventy_B_font.render("YOU WIN!", 1, (255, 255, 0))
            WINDOW.blit(winner_label, (WIDTH/2 - winner_label.get_width()/2, 350))   
            
        pygame.display.update()
            
    #############
    # GAME PLAY #
    #############
    muted = False
    pause = False
    
    while run:
        # keeps FPS consistant no matter what your running game on
        clock.tick(FPS)         
        redraw_window(muted, pause) 
        
        # If player is out of lives or health -> Game over
        if Lives <= 0 or player.health <= 0:
            Game_over = True 
            lose_count += 1    
        
        # If all 4 levels are completed:
        if Level == 5:
            win = True
            win_count += 1
        
        # if Game_over:
        if Game_over:
            if lose_count == FPS:
                pygame.mixer.music.stop() # stop music
                pygame.mixer.Channel(0).play(game_over) # play game over sound
            if lose_count > FPS * 4:
                run = False # wait 4 seconds before returning to main
            else:
                continue
            
        # If win: 
        if win:
            if win_count == FPS:
                pygame.mixer.music.stop()           # stop music
                pygame.mixer.Channel(6).play(Win)   # play Win sound
            if win_count > FPS * 4:
                run = False # wait 4 seconds before returning to main
            else:
                continue
           
        
        ##############################
        # SPAWNING ENEMIES PER LEVEL #
        ##############################
        
        # if there are no enemies left go to next level 
        if len(enemies) == 0: 
            Level += 1
            
            if Level == 1 or Level == 2:
                if Level == 1:
                    pygame.mixer.Channel(7).play(level1) # Level 1 voice intro  
                    rand = random.sample(numbers, 20)    # randomized list of 20 y values                      
                    
                if Level == 2:
                    pygame.mixer.Channel(7).play(level2) # Level 2 voice intro                                       
                    rand = random.sample(numbers, 20)    # randomized list of 20 y values                    
                    enemy_velocity += 1
                    res_size.append(-2000)

                # Randomize enemies
                for i in range(wave_size): #set up enemys above canvas          
                    enemy = Enemy(random.randrange(50, WIDTH-100, 70), -(rand.pop()), random.choice(["red", "blue", "green"]), random.choice([0,1,2]))
                    enemies.append(enemy)                            
            
            if Level == 3:
                if mute == False:
                    pygame.mixer.level3.set_volume(1.3)                
                pygame.mixer.Channel(7).play(level3) # Level 3 voice intro
                res_size.append(-2500)
                
                for i in range(5): #set up enemys above canvas in zig zag
                    for p in range(150, WIDTH-150, 100):
                        enemy = Enemy(p, -p - (wave_size * (i *40) - 10), random.choice(["Lpurple", "Lblue"]), random.choice([0,1,2]))
                        enemies.append(enemy)
                        enemy = Enemy(p, p - (wave_size * (i *40) + 1150), random.choice(["Lblue", "Lpurple"]), random.choice([0,1,2]))
                        enemies.append(enemy)
                        
            if Level == 4:
                res_size.append(-3000)
                pygame.mixer.Channel(7).play(level4) # Level 4 voice intro                                                                   
                enemy_velocity += 2
                
                boss = Enemy(WIDTH-180, -100, "boss", random.choice([0,1]), boss = True)
                enemies.append(boss)
                
                # Randomize enemies
                for i in range(10): #set up enemys above canvas 
                    for p in range(150, WIDTH-150, 400):
                        enemy = Enemy(p, -((i * 2000) + 2000), random.choice(["Lblue", "Lpurple"]), 0)
                        enemies.append(enemy)                

            # Spawn randomized health restorers            
            for i in res_size:
                res = restore_health(random.randrange(50, WIDTH-100, 100), i, "green")
                restore.append(res)   
        
        ###################
        # PLAYER CONTROLS #
        ###################
        # for every event happening (mouse, keyboard)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # exiting out of game
                run = False
                pygame.QUIT
                quit()
                
            # handle MOUSEBUTTONUP
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()           
                if pos[0] >= 10 and pos[0] < 60:       # X position
                    
                    # Return to main menu click button
                    if pos[1] >= 60 and pos[1] <= 90: # Y position
                        pygame.mixer.music.stop()
                        main_menu()                    

                    # MUTE AND UNMUTE click buttons
                    elif pos[1] >= 110 and pos[1] <= 160: # Y position
                        if pause == False: # if the game is not paused:
                            if muted:
                                muted = False
                                volume_on()
                                            
                            if not muted:
                                muted = True 
                                volume_off()
                        
                    # pause and play cluck bottons
                    elif pos[1] >= 170 and pos[1] < 220:
                        if pause:
                            pause = False
                            if muted:
                                volume_on()
                            enemy_velocity = t_enemy_velocity 
                            res_velocity = t_res_velocity
                            player_velocity = t_player_velocity
                            laser_velocity = t_laser_velocity                              
                            
                        else:
                            pause = True
                            volume_off()
                            
                            enemy_velocity = 0
                            res_velocity = 0
                            player_velocity = 0
                            laser_velocity = 0                              
        
        # return dict of all keys being pressed every FPS
        keys = pygame.key.get_pressed()        
        
        if (keys[pygame.K_LEFT] or keys[pygame.K_a])  and player.x - player_velocity > 0:
            player.x -= player_velocity
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player.x + player_velocity + player.get_width() < WIDTH:
            player.x += player_velocity
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and player.y - player_velocity > 0:
            player.y -= player_velocity
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and player.y + player_velocity + player.get_height() + 50 < HEIGHT:
            player.y += player_velocity       
        
        # player shoot
        if keys[pygame.K_SPACE]:
            player.shoot()    
            pygame.mixer.Channel(0).play(shoot)
        
        # MUTE
        if keys[pygame.K_m]:
            if pause == False:
                muted = True            
                volume_off()
            
        # UNMUTE
        if keys[pygame.K_n]:
            if pause == False:
                muted = False            
                volume_on()
        
        # PAUSE
        if keys[pygame.K_p]:
            pause = True
            volume_off() # pause music
                
            enemy_velocity = 0
            res_velocity = 0
            player_velocity = 0
            laser_velocity = 0              
        
        # RESUME / PLAY
        if keys[pygame.K_u]:
            pause = False
            if not muted:
                volume_on() # pause music
            
            enemy_velocity = t_enemy_velocity 
            res_velocity = t_res_velocity
            player_velocity = t_player_velocity
            laser_velocity = t_laser_velocity              
    
        # RETURN to main menu
        if keys[pygame.K_b]:
            volume_off()           
            main_menu()
        
        # QUIT
        if keys[pygame.K_q]:
            run = False
            pygame.QUIT
            quit()      
            
        ###########################################    
        # Health Restore Movement and Interaction #
        ###########################################
        for res in restore[:]:
            
            # move restore health objs down screen
            res.move(res_velocity) 
            
            # if player collides with health plus sign...
            if collide(res, player):
                if player.health > 75: 
                    player.health = 100
                else:
                    player.health += 25
                    
                pygame.mixer.Channel(3).play(health) # Sound
                restore.remove(res)                  # remove restore obj     
                        
        ################################
        # Enemy ship movement by Level #
        ################################
        switch_count += 1
        
        for enemy in enemies:  
            
            if Level == 1 or Level == 3:
                enemy.move(enemy_velocity)
            
            if Level == 2:
                # RIGHT LEFT ZIG ZAG
                if enemy.direction == 0: 
                    if switch_count >= 0 and switch_count < FPS*2:
                        enemy.xRight(enemy_velocity)
                    elif switch_count >= FPS *2 and switch_count < FPS*4:
                        enemy.xLeft(enemy_velocity)
                    elif switch_count >= FPS *4:
                        switch_count = 0
                
                # LEFT RIGHT ZIG ZAG
                elif enemy.direction == 1: 
                    if switch_count >= 0 and switch_count < FPS*2:
                        enemy.xLeft(enemy_velocity)
                    elif switch_count >= FPS *2 and switch_count < FPS*4:
                        enemy.xRight(enemy_velocity)
                    elif switch_count >= FPS *4:
                        switch_count = 0       
                
                # STRAIGHT
                else: 
                    enemy.move(enemy_velocity)
            
            # BOSS MOVEMENTS
            if Level == 4 and enemy.boss:
                if switch_count >= 0 and switch_count <= FPS*1.3:           # LEFT                 
                    enemy.xLeft(enemy_velocity)                   
                elif switch_count >= FPS *2 and switch_count < FPS*3:       # DOWN  
                    enemy.move(enemy_velocity +1)
                elif switch_count >= FPS *3 and switch_count < FPS*4:       # UP    
                    enemy.move(- (enemy_velocity +1))
                elif switch_count >= FPS *4 and switch_count < FPS*5.3:     # LEFT  
                    enemy.xLeft(enemy_velocity)
                elif switch_count >= FPS *5.3 and switch_count < FPS*7.9:   # RIGHT 
                    enemy.xRight(enemy_velocity)                    
                elif switch_count >= FPS *7.9:                              # RESET
                    switch_count = 0
            
            if Level == 4 and not enemy.boss:                
                if enemy.y >= 60:                    
                    enemy.move(enemy_velocity -3)
                else:
                    enemy.move(enemy_velocity + 2)
                        
            # has enemy hit player with laser?
            enemy.laser_movement(laser_velocity, player)          
            
            #######################
            # ENEMY SHOOTING RATE #
            #######################
           # if the enemy is NOT the boss
            if not enemy.boss:
                if random.randrange(0, 4 * 60) == 1: # shoot 1/240 per frame
                    if enemy.y >= 0:  # start shooting when on screen 
                        enemy.shoot()    
           
           # If the enemy is the boss
            elif enemy.boss:
                if random.randrange(0, 10) == 1: # shoot 1/10 per frame
                    if enemy.y >= 0:  # start shooting when on screen 
                        enemy.shoot()                    
            
            ###################
            # ENEMY COLLISION #
            ###################
            
            # if an enemy collides with player
            if collide(enemy, player):
                
                # if the enemy is the boss:
                if enemy.boss:
                    player.y += 20
                    enemy.health -= 2
                    if enemy.health <= 0:
                        enemies.remove(enemy)  
                        
                # if the enemy is NOT the boss
                elif not enemy.boss:
                    player.health -= 10                    
                    enemies.remove(enemy) 
                    
                # play collision sound 
                pygame.mixer.Channel(4).play(colliding)
                         
            # if enemy reachs bottom subtract a life and remove enemy 
            elif enemy.y + enemy.get_height() > HEIGHT and not enemy.boss :
                Lives -= 1
                enemies.remove(enemy)
                
                # play enemy past sound
                pygame.mixer.Channel(2).play(enemy_past)                
    
        ############################
        # Player ship Interactions #
        ############################    
    
        # Has player hit enemies with laser?
        if player.laser_movement(-laser_velocity, enemies) == 1:
            
            # play crashing sound
            pygame.mixer.Channel(1).stop()
            pygame.mixer.Channel(1).play(hit)
            pygame.mixer.Channel(1).fadeout(500)
            
            # increment score
            Score += 1
        
        # Show all display elements
        pygame.display.update()


def opening():
    run = True
    clock.tick(FPS)
    counter = 0
    
    # play Space Battke voice intro
    opening_sb.play() 
    
    while run:
        # Create label
        label = sixty_five_B_font.render("SPACE BATTLE", 1, (255, 255, 255))
        
        # display labels 
        WINDOW.blit(BG, (0, 0))
        WINDOW.blit(label, (WIDTH/2 - label.get_width()/2, 250))
        
        # Quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.QUIT
                quit()                 
        
        # after FPS * 40 automatically go to main menu
        counter += 1
        if counter == FPS * 40:
            main_menu()
        
        # show all display elements
        pygame.display.update()
        
def main_menu():
    run = True
    
    clock.tick(FPS)     
    counter = 0 
    
    # menu text colors
    color0 = WHITE
    color1 = WHITE
    color2 = WHITE
    color3 = WHITE
    
    # arrow placement along menu 
    menu_options = [212, 312, 412, 512]
    y = 0
    
    while run:
        counter += 1
        
        # create menu labels
        menu_label0 = sixty_five_B_font.render("Main Menu", 1, WHITE)
        menu_label1 = fifty_font.render("Start Game", 1, color0)
        menu_label2 = fifty_font.render("Instructions", 1, color1)
        menu_label3 = fifty_font.render("Options", 1, color2)
        menu_label4 = fifty_font.render("Credits", 1, color3)
        menu_label5 = twenty_font.render("Use the mouse or arrow keys to navigate the menu options", 1, WHITE)
        menu_label6 = twenty_font.render("Left click or press the space bar to select an option", 1, WHITE)
        
        # display labels
        WINDOW.blit(BG, (0, 0))        
        WINDOW.blit(menu_arrow, (150, menu_options[y]))
        
        WINDOW.blit(menu_label0, (WIDTH/2 - menu_label0.get_width()/2, 100))
        WINDOW.blit(menu_label1, (WIDTH/2 - menu_label1.get_width()/2, 200))
        WINDOW.blit(menu_label2, (WIDTH/2 - menu_label2.get_width()/2, 300))
        WINDOW.blit(menu_label3, (WIDTH/2 - menu_label3.get_width()/2, 400))        
        WINDOW.blit(menu_label4, (WIDTH/2 - menu_label4.get_width()/2, 500))
        WINDOW.blit(menu_label5, (WIDTH/2 - menu_label5.get_width()/2, 600))
        WINDOW.blit(menu_label6, (WIDTH/2 - menu_label6.get_width()/2, 650))

        # quit 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.QUIT
                quit() 
            
            # Menu options mouse functionality
            pos = pygame.mouse.get_pos()                       
            if pos[0] >= 200 and pos[0] <= 550:      # X position
                if pos[1] >= 150 and pos[1] <= 250:  # Y position
                    y = 0
                    if event.type == pygame.MOUSEBUTTONUP:                                
                        start_menu()         
                elif pos[1] >= 250 and pos[1] <= 350:  # Y position
                    y = 1
                    if event.type == pygame.MOUSEBUTTONUP:                                
                        inst_menu()         
                elif pos[1] >= 350 and pos[1] <= 450:  # Y position
                    y = 2
                    if event.type == pygame.MOUSEBUTTONUP:                                
                        options_menu()                            
                elif pos[1] >= 450 and pos[1] <= 550:  # Y position
                    y = 3
                    if event.type == pygame.MOUSEBUTTONUP:                                
                        credit_menu()            
        
        # move up and down the menu
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and y <= 2 and counter >= FPS * 2:
            y += 1
            counter = 0            
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and y > 0 and counter >= FPS * 2:
            y -= 1
            counter = 0 
        
        # switch to other menus
        if keys[pygame.K_SPACE] and y == 0 and counter >= FPS * 2:  # START GAME
            start_menu()        
        elif (keys[pygame.K_SPACE]) and y == 1 and counter >= FPS* 2: # INSTRUCTIONS
            inst_menu()    
        elif (keys[pygame.K_SPACE]) and y == 2 and counter >= FPS* 2: # CREDITS
            options_menu()        
        elif (keys[pygame.K_SPACE]) and y == 3 and counter >= FPS* 2: # CREDITS
            credit_menu()

        # quit
        if keys[pygame.K_q]:
            run = False
            pygame.QUIT
            quit() 
            
        # change menu label colors
        if y == 0:
            color0 = BLUE
            color1 = WHITE
            color2 = WHITE
            color3 = WHITE
            
        elif y == 1:
            color1 = BLUE
            color0 = WHITE
            color2 = WHITE
            color3 = WHITE
            
        elif y ==2:
            color2 = BLUE
            color0 = WHITE
            color1 = WHITE
            color3 = WHITE
            
        else:
            color3 = BLUE
            color0 = WHITE
            color1 = WHITE
            color2 = WHITE            
        
        # display everything
        pygame.display.update()
        
def start_menu():
    clock.tick(FPS)         
    run = True
    while run:
        
        # create labels
        title_font = pygame.font.SysFont("mono", 40)        
        title_label = title_font.render("Press any key to begin", 1, WHITE)
        
        # display labels 
        WINDOW.blit(BG, (0, 0))        
        WINDOW.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        
        # RETURN ARROW
        WINDOW.blit(return_arrow, (10, 20))        
        
        # Quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.QUIT
                quit()
                
            # return arrow
            if event.type == pygame.MOUSEBUTTONUP:            
                pos = pygame.mouse.get_pos()                       
                if pos[0] >= 10 and pos[0] <= 60: # X position
                    if pos[1] >= 20 and pos[1] <= 60: # Y position
                        main_menu()   
                        
            # press any key to start
            if event.type == pygame.KEYDOWN:
                pygame.mixer.music.play(-1)
                volume_on()
                main()
                
        # return to main menu 
        keys = pygame.key.get_pressed()    
        if keys[pygame.K_b]:
            main_menu()          
                
        # quit
        if keys[pygame.K_q]:
            run = False
            pygame.QUIT
            quit()          

        pygame.display.update()
        
def inst_menu(page = 0):    
    
    def windisplay(inst1, inst2, inst3, inst4 = None, inst5 = None):
        inst_header = sixty_five_B_font.render("Instructions", 1, WHITE)        
        inst_cont = twenty_five_font.render("Press any key to continue", 1, WHITE)        

        # display labels
        WINDOW.blit(BG, (0, 0))        
        WINDOW.blit(inst_header, (WIDTH/2 - inst_header.get_width()/2, 150))
        WINDOW.blit(inst1, (WIDTH/2 - inst1.get_width()/2, 250))
        WINDOW.blit(inst2, (WIDTH/2 - inst2.get_width()/2, 300))
        WINDOW.blit(inst3, (WIDTH/2 - inst3.get_width()/2, 350))
        if inst4:
            WINDOW.blit(inst4, (WIDTH/2 - inst4.get_width()/2, 400)) 
        if inst5:
            WINDOW.blit(inst5, (WIDTH/2 - inst5.get_width()/2, 450))
        
        WINDOW.blit(inst_cont, (WIDTH/2 - inst_cont.get_width()/2, 600)) 
        
        # RETURN ARROW
        WINDOW.blit(return_arrow, (10, 20))        
        
    def page1():
        # Labels
        inst1 = thirty_five_font.render("The object of the game", 1, WHITE)
        inst2 = thirty_five_font.render("is to defeat all", 1, WHITE)
        inst3 = thirty_five_font.render("enemy ships", 1, WHITE)
        
        #display labels
        windisplay(inst1, inst2, inst3)
        
        # display enemy ships
        WINDOW.blit(red_enemy, (WIDTH/2 - red_enemy.get_width()/2 - 100, 450))
        WINDOW.blit(green_enemy, (WIDTH/2 - green_enemy.get_width()/2, 450))
        WINDOW.blit(blue_enemy, (WIDTH/2 - blue_enemy.get_width()/2 + 100, 450))        
    
        pygame.display.update()
    
    def page2():
        # Labels
        inst1 = thirty_five_font.render("Use the arrow keys", 1, WHITE)
        inst2 = thirty_five_font.render("to move your player", 1, WHITE)        
        inst3 = thirty_five_font.render("up, down, left and right", 1, WHITE)
        inst4 = thirty_five_font.render("press the space bar", 1, WHITE)
        inst5 = thirty_five_font.render("to shoot lasers", 1, WHITE)
        
        # display labels
        windisplay(inst1, inst2, inst3, inst4, inst5)
        
        pygame.display.update()
    
    def page4():
        # Labels      
        inst1 = thirty_five_font.render("You can defeat enemies", 1, WHITE)
        inst2 = thirty_five_font.render("by shooting them", 1, WHITE)        
        inst3 = thirty_five_font.render("or by crashing into them", 1, WHITE)
        inst4 = thirty_five_font.render("Note, your player will lose", 1, WHITE)
        inst5 = thirty_five_font.render("health if you crash into an enemy", 1, WHITE)
        
        # display labels
        windisplay(inst1, inst2, inst3, inst4, inst5)        
        
        pygame.display.update()        
        
    def page5():
        # Labels      
        inst1 = thirty_five_font.render("You can revive your health", 1, WHITE)
        inst2 = thirty_five_font.render("by colliding into a", 1, WHITE)        
        inst3 = thirty_five_font.render("a green plus sign", 1, WHITE)        
        
        # display labels and health restorer
        windisplay(inst1, inst2, inst3)
        WINDOW.blit(Health_restorer, (WIDTH/2 - Health_restorer.get_width()/2, 450))
        
        pygame.display.update()    
    
    def page6():
        # Labels      
        inst1 = thirty_five_font.render("If an enemy gets past your defense", 1, WHITE)
        inst2 = thirty_five_font.render("you will lose a life.", 1, WHITE)        
        inst3 = thirty_five_font.render("You only have 3 lives", 1, WHITE)        
        inst4 = thirty_five_font.render("so be careful!", 1, WHITE)        
        
        # display labels
        windisplay(inst1, inst2, inst3, inst4)        
        
        pygame.display.update()    
    
    def page7():
        # Labels     
        inst1 = thirty_five_font.render("There are 4 levels to complete", 1, WHITE)
        inst2 = thirty_five_font.render("if you beat all 4 levels", 1, WHITE)        
        inst3 = thirty_five_font.render("you win", 1, WHITE)        
        inst4 = thirty_five_font.render("Good luck!", 1, WHITE)        
        
        # display labels
        windisplay(inst1, inst2, inst3, inst4)        
                
        pygame.display.update()            

    #################
    # Run Inst Menu #
    #################
    
    clock.tick(FPS)   
    counter = 0
    run = True
    
    if page == 0: 
        opening_in.play()    

    pages = [page1, page2, page3, page4, page5, page6, page7, main_menu]    
    
    while run:
        counter += 1
        pages[page]()             
        
        # quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            
            # return arrow mouse 
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()            
                if pos[0] >= 10 and pos[0] <= 60: # X position
                    if pos[1] >= 20 and pos[1] <= 60: # Y position
                        opening_in.stop()                        
                        main_menu()            
            
            # press any key to continue
            if (event.type == pygame.KEYDOWN):
                if page == 0:
                    if counter >= FPS *20:
                        page += 1
                else:
                    page += 1
                    
        # return to main menu
        keys = pygame.key.get_pressed()    
        if keys[pygame.K_b]:
            opening_in.stop() # stop voice intro
            main_menu()  

        # quit
        if keys[pygame.K_q]:
            quit()  
                
        pygame.display.update()

def page3():
    run = True
    shoot.set_volume(1)  
    player_velocity = 8 
    laser_velocity = 7
    p = Player(WIDTH/2 - player.get_width()/2, 400)   
    enemies = []
    
    def redraw_window():
        
        # create labels
        inst_header = sixty_five_B_font.render("Instructions", 1, WHITE)
        inst_cont = twenty_five_font.render('Press "c" to key to continue', 1, WHITE)        
        inst1 = thirty_five_font.render("Try it out", 1, WHITE)
        
        # display labels
        WINDOW.blit(BG, (0, 0))        
        WINDOW.blit(inst_header, (WIDTH/2 - inst_header.get_width()/2, 150))
        WINDOW.blit(inst1, (WIDTH/2 - inst1.get_width()/2, 250))
        
        WINDOW.blit(inst_cont, (WIDTH/2 - inst_cont.get_width()/2, 600))   
        
        # RETURN ARROW
        WINDOW.blit(return_arrow, (10, 20))         
        
        # draw player
        p.draw(WINDOW)        
        
        # display everything
        pygame.display.update()
        
    while run:
        # keeps FPS consistant no matter what your running game on
        clock.tick(FPS)         
        redraw_window() 
        
        # for every event happening (mouse, keyboard)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # exiting out of game
                quit()
                
            # return arrow
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()            
                if pos[0] >= 10 and pos[0] <= 60: # X position
                    if pos[1] >= 20 and pos[1] <= 60: # Y position
                        main_menu()            
                
        # return dict of all keys being pressed every FPS
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a])  and p.x - player_velocity > 0:
            p.x -= player_velocity
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and p.x + player_velocity + p.get_width() < WIDTH:
            p.x += player_velocity
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and p.y - player_velocity > 0:
            p.y -= player_velocity
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and p.y + player_velocity + p.get_height() + 50 < HEIGHT:
            p.y += player_velocity   
        
        # player shoot
        if keys[pygame.K_SPACE]:
            p.shoot()    
            pygame.mixer.Channel(0).play(shoot)        
        
        # continue to next page
        if keys[pygame.K_c]:
            inst_menu(page = 4)
            
        # return to main menu
        if keys[pygame.K_b]:
            main_menu()   
        
        # quit
        if keys[pygame.K_q]:
            quit()          
        
        p.laser_movement(-laser_velocity, enemies)      
    
        # display everything
        pygame.display.update()   
        
def options_menu():
    clock.tick(FPS)         
    run = True
    
    global music
    global checked
   
   # make sure checked box remains checked after user selects one
    if checked == 1:
        box1 = checked_box
        box2 = check_box
        box3 = check_box   
        
    if checked == 2:
        box1 = check_box
        box2 = checked_box
        box3 = check_box        
    
    if checked == 3:
        box1 = check_box
        box2 = check_box
        box3 = checked_box             
    
    opening_o.play()
    
    while run:
        # Create Labels
        options_label = sixty_five_B_font.render("OPTIONS", 1, WHITE)
        
        label1 = thirty_B_font.render("Shortcut Options", 1, RED)
        label2 = twenty_five_font.render('Press "m" to mute', 1, WHITE)           
        label3 = twenty_five_font.render('Press "n" to unmute', 1, WHITE)   
        label4 = twenty_five_font.render('Press "b" to return to the main menu', 1, WHITE)
        label5 = twenty_five_font.render('Press "q" to quit program', 1, WHITE)                
        label6 = twenty_five_font.render('Press "p" to pause', 1, WHITE)        
        label7 = twenty_five_font.render('Press "u" to unpause', 1, WHITE)          
        
        sounds_label = thirty_B_font.render("Background Music Options", 1, BLUE)
        sounds_label1 = thirty_font.render("Eye Of The Tiger", 1, WHITE)
        sounds_label2 = thirty_font.render("He's A Pirate ", 1, WHITE)
        sounds_label3 = thirty_font.render("Star Wars Theme Song", 1, WHITE)
        
        # Display Labels
        WINDOW.blit(BG, (0, 0))           
        WINDOW.blit(options_label, (WIDTH/2 - options_label.get_width()/2, 100)) # options
        WINDOW.blit(label1, (WIDTH/2 - label1.get_width()/2, 190))      # s.o.
        WINDOW.blit(label2, (WIDTH/2 - label4.get_width()/2 - 40, 240)) # m
        WINDOW.blit(label3, (WIDTH/2 - label4.get_width()/2 - 40, 290)) # n
        WINDOW.blit(label4, (WIDTH/2 - label4.get_width()/2, 340))      # b       
        WINDOW.blit(label5, (WIDTH/2 - label5.get_width()/2, 390))      # q
        pygame.draw.line(WINDOW, WHITE, (WIDTH/2, 240), (WIDTH/2, 320)) # line
        
        WINDOW.blit(label6, (WIDTH/2 + 40, 240)) # pause
        WINDOW.blit(label7, (WIDTH/2 + 40, 290)) # unpause
        
        WINDOW.blit(sounds_label, (WIDTH/2 - sounds_label.get_width()/2, 450)) # s
        WINDOW.blit(sounds_label1, (WIDTH/2 - sounds_label2.get_width()/2, 500)) # eye_tiger
        WINDOW.blit(sounds_label2, (WIDTH/2 - sounds_label2.get_width()/2, 550)) # pirate  
        WINDOW.blit(sounds_label3, (WIDTH/2 - sounds_label2.get_width()/2, 600)) # star wars             
        
        # Display check boxs
        WINDOW.blit(box1, (185, 497))
        WINDOW.blit(box2, (185, 547))
        WINDOW.blit(box3, (185, 597))  
        
        # RETURN ARROW
        WINDOW.blit(return_arrow, (10, 20))
        
        # Quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
                
            # Check boxs 
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()           
                if pos[0] >= 185 and pos[0] <= 215:    # X position
                    if pos[1] >= 497 and pos[1] < 547: # Y position
                        music = pygame.mixer.music.load(resource_path("sound\\Eye_Tiger.wav"))                        
                        
                        box1 = checked_box
                        box2 = check_box
                        box3 = check_box  
                        
                        checked = 1
                                                
                    elif pos[1] >= 547 and pos[1] < 597:        # Y position
                        music = pygame.mixer.music.load(resource_path("sound\\Pirate.wav"))                        
                        
                        
                        box1 = check_box
                        box2 = checked_box
                        box3 = check_box 
                        
                        checked = 2
                                                
                    elif pos[1] >= 597 and pos[1] < 647:         # Y position
                        music = pygame.mixer.music.load(resource_path("sound\\Star Wars.wav"))                        
                        
                        box1 = check_box
                        box2 = check_box
                        box3 = checked_box 
                        
                        checked = 3
                        
                # return arrow
                if pos[0] >= 10 and pos[0] <= 60: # X position
                    if pos[1] >= 20 and pos[1] <= 60: # Y position
                        opening_o.stop()
                        main_menu()
                        
        # return to main menu
        keys = pygame.key.get_pressed()    
        if keys[pygame.K_b]:
            opening_o.stop()            
            main_menu()       
        
        # quit
        if keys[pygame.K_q]:
            quit()          
  
        # display everything
        pygame.display.update()        
          
def credit_menu():
    run = True
    opening_c.play() # Credits voice intro
    
    while run:

        # Create Labels
        credit_label = sixty_five_B_font.render("CREDITS", 1, WHITE)
        
        art_label = fifty_five_B_font.render("Art", 1, RED)
        art_label1 = twenty_five_font.render("Designed by: Shani Wolfson", 1, WHITE)           
        
        code_label = fifty_B_font.render("Code", 1, BLUE)
        code_label1 = twenty_five_font.render("Written by: Shani Wolfson", 1, WHITE)        

        sounds_label = fifty_B_font.render("Sounds", 1, GREEN)
        sounds_label1 = twenty_five_font.render("Gaming sounds by: https://mixkit.co/", 1, WHITE)
        sounds_label2 = twenty_five_font.render("Voice intros by: Aaron Lewis", 1, WHITE)        
        sounds_label3 = twenty_five_font.render("Eye Of The Tiger: Survivor", 1, WHITE)
        sounds_label4 = twenty_five_font.render("He's a Pirate: Klaus Badelt", 1, WHITE)
        sounds_label5 = twenty_five_font.render("Star Wars Theme Song: John Williams", 1, WHITE)

        # Display Labels
        WINDOW.blit(BG, (0, 0))           
        WINDOW.blit(credit_label, (WIDTH/2 - credit_label.get_width()/2, 125))
        WINDOW.blit(art_label, (WIDTH/2 - art_label.get_width()/2, 215))
        WINDOW.blit(art_label1, (WIDTH/2 - art_label1.get_width()/2, 265))
        WINDOW.blit(code_label, (WIDTH/2 - code_label.get_width()/2, 315))
        WINDOW.blit(code_label1, (WIDTH/2 - code_label1.get_width()/2, 365))        
        WINDOW.blit(sounds_label, (WIDTH/2 - sounds_label.get_width()/2, 415))
        WINDOW.blit(sounds_label1, (WIDTH/2 - sounds_label1.get_width()/2, 465))                        
        WINDOW.blit(sounds_label2, (WIDTH/2 - sounds_label2.get_width()/2, 505))        
        WINDOW.blit(sounds_label3, (WIDTH/2 - sounds_label3.get_width()/2, 545))        
        WINDOW.blit(sounds_label4, (WIDTH/2 - sounds_label4.get_width()/2, 585))        
        WINDOW.blit(sounds_label5, (WIDTH/2 - sounds_label5.get_width()/2, 625))        

        # RETURN ARROW
        WINDOW.blit(return_arrow, (10, 20))        
        
        # quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()    
                
            # Return to main menu mouse
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()                   
                if pos[0] >= 10 and pos[0] <= 60: # X position
                    if pos[1] >= 20 and pos[1] <= 60: # Y position
                        opening_c.stop()
                        main_menu()            

        # Return to main menu key
        keys = pygame.key.get_pressed()    
        if keys[pygame.K_b]:
            opening_c.stop()            
            main_menu()       
        
        # quit
        if keys[pygame.K_q]:
            quit()          
        
        # display everything
        pygame.display.update()
       
opening()
        
# THINGS TO DO:
# 1. Pop up messages?


#def resource_path(relative_path):
#    """ Get absolute path to resource, works for dev and for PyInstaller """
#    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
#        base_path = sys._MEIPASS
#   except Exception:
#        base_path = os.path.abspath(".")

#    return os.path.join(base_path, relative_path)

    
#def resource_path(relative):
#    return os.path.join(os.environ.get("_MEIPASS2", os.path.abspath(".")), relative)
