from types import DynamicClassAttribute
import pygame as pg
import pygame as pg
from pygame import mouse
from pygame.constants import K_BACKSPACE, K_LCTRL, K_v
from game import Game
from settings import *
from sprites import *
import json
import dexcom_integration as dex_int
import clipboard
from datetime import datetime
from time import sleep
from advice import *
import random

class App():

    def __init__(self):
        pg.init()
        self.running = True
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption('Insulate Development Build')
        self.clock = pg.time.Clock()
        self.state = 'menu-main'
        self.manual_bs_input = ''
        self.manual_bs_data = []
        self.auth_code = ''
        self.bearer_token = ''
        self.app_settings = self.load_settings()
        self.current_date = self.get_date_time()
        self.average = 0
        self.plays_remaining = 0
        game = Game()
        self.game_stats = game.load_stats()
        self.todays_advice = []
        
    def run(self):
        self.events()
        self.update()
        self.draw()

    def new(self):
        self.all_sprites = pg.sprite.Group()
        if self.state == 'menu-main':
            self.logo = Image('./assets/img/logo.png', 0, 35)
            self.check = Image('./assets/img/menu-main/check.png', WIDTH / 2 - 93.5, 240)
            self.track = Image('./assets/img/menu-main/track.png', WIDTH / 2 - 98, 300)
            self.settings = Image('./assets/img/menu-main/settings.png', WIDTH / 2 - 133.5, 360)
            self.quit = Image('./assets/img/menu-main/quit.png', WIDTH / 2 - 69, 420)
            self.help = Image('./assets/img/menu-main/help.png', WIDTH - 56, HEIGHT - 56)
            self.all_sprites.add(self.logo, self.check, self.track, self.settings, self.quit, self.help)
        if self.state == 'menu-track':
            self.header = Image('./assets/img/menu-track/header.png', 0, 0)
            self.manual = Image('./assets/img/menu-track/manual.png', WIDTH / 2 - 90.5 , 220)
            self.dexcom = Image('assets/img/menu-track/dexcom.png', WIDTH / 2 - 160.5, 340)
            self.all_sprites.add(self.header, self.manual, self.dexcom)
        if self.state == 'track-manual':
            self.header = Image('./assets/img/manual-input/header-' + str(self.app_settings['collection_range']) + '.png', 0, 0)
            self.input_box = Surface(WIDTH / 2 - 135, HEIGHT / 2 - 50 , 270, 120, CHARLESTON_GREEN)
            self.enter = Image('./assets/img/manual-input/enter.png', HEIGHT / 2 - 73.5, HEIGHT / 2 + 110)
            self.all_sprites.add(self.header, self.enter, self.input_box)
        if self.state == 'track-dexcom':
            self.header = Image('./assets/img/dexcom-integration/header.png', 0, 25)
            self.sign_in = Image('./assets/img/dexcom-integration/open.png', WIDTH / 2 - 144, 150)
            self.get_data = Image('./assets/img/dexcom-integration/get.png', WIDTH /2 - 108, 375)
            self.input_box = Surface(10, 230, WIDTH - 20, 120, CHARLESTON_GREEN)
            self.paste = Image('./assets/img/dexcom-integration/paste.png', WIDTH - 120, HEIGHT - 37)
            self.all_sprites.add(self.header, self.sign_in, self.get_data, self.input_box, self.paste)
        if self.state == 'menu-check':
            self.header = Image('./assets/img/menu-check/header.png', 0, 20)
            self.start_check = Image('./assets/img/menu-check/check_and_play.png', WIDTH / 2 - 162.5, 200)
            self.stats = Image('./assets/img/menu-check/stats.png', WIDTH / 2 - 173, 280)
            self.how_to = Image('./assets/img/menu-check/how_to_play.png', WIDTH / 2 - 135, 360)
            if self.current_date[0:10] == self.app_settings['last_check']:
                self.check_status = Image('./assets/img/menu-check/yes.png', WIDTH - 277, HEIGHT - 30)
            else:
                self.check_status = Image('./assets/img/menu-check/no.png', WIDTH - 328, HEIGHT - 30)
            self.error = Image('./assets/img/menu-check/error.png', 500, 0)
            self.all_sprites.add(self.header, self.start_check, self.stats, self.how_to, self.check_status, self.error)
        if self.state == 'check':
            self.header = Image('./assets/img/check/header.png', 0, 0)
            self.play = Image('./assets/img/check/play.png', WIDTH / 2 - 55, 240)
            self.advice = Image('./assets/img/check/advice.png', WIDTH / 2 - 77.5, 290)
            self.remaining = Image('./assets/img/check/remaining.png', WIDTH - 304, HEIGHT - 35)
            self.all_sprites.add(self.header, self.play, self.advice, self.remaining)
        if self.state == 'stats':
            self.header = Image('./assets/img/stats/header.png', 0, 0)
            self.back = Image('./assets/img/back.png', WIDTH / 2 - 28, HEIGHT - 56)
            self.all_sprites.add(self.header, self.back)
        if self.state == 'how_to_play':
            self.image = Image('./assets/img/how_to_play.png', 0, 0)
            self.back = Image('./assets/img/back.png', WIDTH / 2 - 28, HEIGHT - 56)
            self.all_sprites.add(self.image, self.back)
        if self.state == 'advice':
            self.header = Image('./assets/img/advice/header.png', 0, 0)
            self.text_box = Surface(20, 100, WIDTH - 40, 330, CHARLESTON_GREEN)
            self.back = Image('./assets/img/back.png', WIDTH / 2 - 28, HEIGHT - 56)
            self.all_sprites.add(self.header, self.text_box, self.back)
        if self.state == 'settings':
            self.header = Image('./assets/img/settings/header.png', 0, 50)
            self.high = Image('./assets/img/settings/high.png', 45, 150)
            self.low = Image('./assets/img/settings/low.png', 45, 200)
            self.collect = Image('./assets/img/settings/collection.png', 45, 250)
            self.left_arrow_h = Image('./assets/img/settings/left-arrow.png', 325, 150)
            self.option_box_h = Surface(355, 150, 65, 40, CHARLESTON_GREEN)
            self.right_arrow_h = Image('./assets/img/settings/right-arrow.png', 430, 150)
            self.left_arrow_l = Image('./assets/img/settings/left-arrow.png', 325, 200)
            self.option_box_l = Surface(355, 200, 65, 40, CHARLESTON_GREEN)
            self.right_arrow_l = Image('./assets/img/settings/right-arrow.png', 430, 200)
            self.left_arrow_c = Image('./assets/img/settings/left-arrow.png', 325, 250)
            self.option_box_c = Surface(355, 250, 65, 40, CHARLESTON_GREEN)
            self.right_arrow_c = Image('./assets/img/settings/right-arrow.png', 430, 250)
            self.save = Image('./assets/img/settings/save.png', WIDTH / 2 - 93.5, 350)
            self.all_sprites.add(self.header, self.high, self.low, self.collect, self.left_arrow_h, self.option_box_h, self.right_arrow_h, self.left_arrow_l, self.option_box_l, self.right_arrow_l, self.left_arrow_c, self.option_box_c, self.right_arrow_c, self.save)
        if self.state != 'menu-main' and self.state != 'advice' and self.state != 'how_to_play' and self.state != 'stats':
            self.back = Image('./assets/img/back.png', 0, HEIGHT - 56)
            self.all_sprites.add(self.back)
        self.run()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
            if self.state == 'track-manual' and event.type == pg.KEYDOWN and event.unicode in DIGITS and len(self.manual_bs_input) <= 2:
                self.manual_bs_input += event.unicode
            if self.state == 'track-dexcom' and event.type == pg.KEYDOWN and len(self.auth_code) < 32:
                self.auth_code += event.unicode
            if self.state == 'track-dexcom' and event.type == pg.KEYDOWN and event.key == K_BACKSPACE:
                self.auth_code = ''
            if self.state == 'track-manual' and event.type == pg.KEYDOWN and event.key == K_BACKSPACE:
                self.manual_bs_input = ''
            if self.state == 'check':
                mouse_pos = pg.mouse.get_pos()
                if event.type == pg.MOUSEBUTTONUP and self.play.rect.collidepoint(mouse_pos[0], mouse_pos[1]) and self.plays_remaining > 0:
                    game = Game()
                    while game.running:
                        game.new()
                    self.game_stats = game.load_stats()
                    self.plays_remaining -= 1
            if event.type == pg.MOUSEBUTTONUP and self.state == 'settings': 
                mouse_pos = pg.mouse.get_pos()
                if self.left_arrow_h.rect.collidepoint(mouse_pos[0], mouse_pos[1]) and self.app_settings['high_setting'] > 120:
                    self.app_settings['high_setting'] -= 5
                elif self.right_arrow_h.rect.collidepoint(mouse_pos[0], mouse_pos[1]) and self.app_settings['high_setting'] < 400:
                    self.app_settings['high_setting'] += 5
                
                if self.left_arrow_l.rect.collidepoint(mouse_pos[0], mouse_pos[1]) and self.app_settings['low_setting'] > 60:
                    self.app_settings['low_setting'] -= 5
                elif self.right_arrow_l.rect.collidepoint(mouse_pos[0], mouse_pos[1]) and self.app_settings['low_setting'] < 100:
                    self.app_settings['low_setting'] += 5

                if self.left_arrow_c.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                    if self.app_settings['collection_range'] == 24: self.app_settings['collection_range'] = 12
                    elif self.app_settings['collection_range'] == 48: self.app_settings['collection_range'] = 24
                elif self.right_arrow_c.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                    if self.app_settings['collection_range'] == 12: self.app_settings['collection_range'] = 24
                    elif self.app_settings['collection_range'] == 24: self.app_settings['collection_range'] = 48

    def update(self):
        self.all_sprites.update()
        mouse_pos = pg.mouse.get_pos()
        if self.state == 'menu-main':
            if pg.mouse.get_pressed()[0] and self.quit.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.running = False
            
            if pg.mouse.get_pressed()[0] and self.check.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.state_change('menu-check')

            if pg.mouse.get_pressed()[0] and self.track.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.state_change('menu-track')

            if pg.mouse.get_pressed()[0] and self.settings.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.state_change('settings')

        if self.state == 'menu-track':
            if pg.mouse.get_pressed()[0] and self.back.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.state_change('menu-main')
            
            if pg.mouse.get_pressed()[0] and self.manual.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.state_change('track-manual')

            if pg.mouse.get_pressed()[0] and self.dexcom.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.state_change('track-dexcom')
        
        if self.state == 'track-dexcom':
            if pg.mouse.get_pressed()[0] and self.back.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.state_change('menu-track')

            if pg.mouse.get_pressed()[0] and self.sign_in.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                dex_int.prompt_login()
            
            if pg.mouse.get_pressed()[0] and self.get_data.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                try:
                    bearer = dex_int.get_bearer(self.auth_code)
                    end_date = self.get_date_time()
                    start_date = self.calc_start_date_time(end_date)
                    data = dex_int.get_egvs(bearer['access_token'], start_date, end_date)
                    with open('data/full_cgm_data.json', 'w') as f:
                        json.dump(data, f, indent=4)
                        f.close()
                    self.analyze_cgm_data()
                    self.auth_code = 'DATA WAS SUCCESSFULLY OBTAINED!'
                except:
                    self.auth_code = 'AN ERROR HAS OCCURRED!'

            if pg.mouse.get_pressed()[0] and self.paste.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.auth_code = clipboard.paste()

        if self.state == 'track-manual':
            if pg.mouse.get_pressed()[0] and self.back.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.state_change('menu-main')
                if self.manual_bs_data:
                    i = 0
                    while i < len(self.manual_bs_data):
                        self.manual_bs_data[i] = int(self.manual_bs_data[i])
                        i += 1
                with open('data/gv_data.json', 'w') as f:
                    json.dump(self.manual_bs_data, f)
                    f.close()

            if pg.mouse.get_pressed()[0] and self.enter.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.manual_bs_data.append(self.manual_bs_input)
                self.manual_bs_input = ''
                while '' in self.manual_bs_data:
                    self.manual_bs_data.remove('')
        
        if self.state == 'menu-check':
            
            if pg.mouse.get_pressed()[0] and self.back.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.state_change('menu-main')

            if pg.mouse.get_pressed()[0] and self.start_check.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                if self.app_settings['last_check'] != self.current_date[0:10]:
                    self.state_change('check')
                    data = self.load_bs_data()
                    if not data:
                        self.average = "NONE"
                        self.no_data = True
                    else:
                        self.average = self.average_data(data)
                        if self.average >= self.app_settings['high_setting'] or self.average <= self.app_settings['low_setting']:
                            self.plays_remaining = 1
                        else: 
                            self.plays_remaining = 3
                        self.get_advice()
                        self.no_data = False
                            
                # WHEN DONE WITH APP TRY TO GET ERROR MESSAGE WORKING
            if pg.mouse.get_pressed()[0] and self.stats.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.state_change('stats')
                
            if pg.mouse.get_pressed()[0] and self.how_to.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.state_change('how_to_play')
                
        if self.state == 'check':
            
            if pg.mouse.get_pressed()[0] and self.back.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.state_change('menu-check')
                if not self.no_data:
                    self.app_settings['last_check'] = self.current_date[0:10]
                    self.save_settings()
                
            if pg.mouse.get_pressed()[0] and self.advice.rect.collidepoint(mouse_pos[0], mouse_pos[1]) and self.no_data == False:
                self.state_change('advice')
                
        if self.state == 'stats':
            
            if pg.mouse.get_pressed()[0] and self.back.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.state_change('menu-check')
                
        if self.state == 'how_to_play':
            
            if pg.mouse.get_pressed()[0] and self.back.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.state_change('menu-check')

        if self.state == 'advice':
            if pg.mouse.get_pressed()[0] and self.back.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.state_change('check')
                                                          
        if self.state == 'settings':

            if pg.mouse.get_pressed()[0] and self.back.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.state_change('menu-main')
                
            if pg.mouse.get_pressed()[0] and self.save.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.save_settings()

    def draw(self):
        self.screen.fill(ASH_GRAY)
        self.all_sprites.draw(self.screen)
        if self.state == 'check' and self.average != 'NONE':
            self.draw_text(str(round(self.average, 2)), 64, CHARLESTON_GREEN, 370, 80)
            self.draw_text(str(self.plays_remaining), 39, CHARLESTON_GREEN, WIDTH - 28, HEIGHT - 32)
        elif self.state == 'check':
            self.draw_text("NONE", 64, CHARLESTON_GREEN, 370, 68)
            self.draw_text('0', 39, CHARLESTON_GREEN, WIDTH - 28, HEIGHT - 36)
        if self.state == 'track-manual':
            self.draw_text(self.manual_bs_input, 110, BEIGE, WIDTH / 2, HEIGHT / 2 - 25)
        if self.state == 'track-dexcom':
            self.draw_text(self.auth_code, 32, BEIGE, WIDTH / 2, 272)
        if self.state == 'stats':
            self.draw_text("High Score: " + str(self.game_stats['high_score']), 55, CHARLESTON_GREEN, WIDTH / 2, 120)
            self.draw_text("Total Score: " + str(self.game_stats['total_score']), 55, CHARLESTON_GREEN, WIDTH / 2, 170)
            self.draw_text("Coins Collected: " + str(self.game_stats['total_coins_collected']), 50, CHARLESTON_GREEN, WIDTH / 2, 220)
            self.draw_text("Enemies Defeated: " + str(self.game_stats['total_enemies_defeated']), 50, CHARLESTON_GREEN, WIDTH / 2, 270)
            self.draw_text("Games Played: " + str(self.game_stats['games_played']), 55, CHARLESTON_GREEN, WIDTH / 2, 320)
        if self.state == 'settings':
            self.draw_text(str(self.app_settings['high_setting']), 32, ASH_GRAY, 387, 152)
            self.draw_text(str(self.app_settings['low_setting']), 32, ASH_GRAY, 387, 202)
            self.draw_text(str(self.app_settings['collection_range']), 32, ASH_GRAY, 387, 252)
        if self.state == 'advice':
            self.draw_text(self.todays_advice[0], 32, BEIGE, WIDTH / 2, 110)
            self.draw_text(self.todays_advice[1], 32, BEIGE, WIDTH / 2, 140)
            self.draw_text(self.todays_advice[2], 32, BEIGE, WIDTH / 2, 170)
            self.draw_text(self.todays_advice[3], 32, BEIGE, WIDTH / 2, 200)
            self.draw_text(self.todays_advice[4], 32, BEIGE, WIDTH / 2, 230)
            self.draw_text(self.todays_advice[5], 32, BEIGE, WIDTH / 2, 260)
            self.draw_text(self.todays_advice[6], 32, BEIGE, WIDTH / 2, 290)
            self.draw_text(self.todays_advice[7], 32, BEIGE, WIDTH / 2, 320)
            self.draw_text(self.todays_advice[8], 32, BEIGE, WIDTH / 2, 350)
            self.draw_text(self.todays_advice[9], 32, BEIGE, WIDTH / 2, 380)
        pg.display.flip()

    def draw_text(self, text, size, color, x, y):
        
        "Draws the text to the screen." 
       
        font = pg.font.Font('./assets/font/font.otf', size) # Checks to see if the font is part of Pygame's font library. 
        text_surface = font.render(text, True, color) 
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def state_change(self, new_state: str):

        "Changes the state that the app is on."

        self.state = new_state
        self.new()

    def average_data(self, data: list):

        "Calculates the average of a list of integers or floats."

        return sum(data) / len(data)

    def get_date_time(self):

        "Gets the current date and time of the system."

        now = datetime.now()
        current_time = now.strftime("%Y-%m-%dT%H:%M:%S")
        return current_time

    def calc_start_date_time(self, date: str):

        "Calculate a date and time based on the apps collection range settings."
        
        hours = int(date[11] + date[12])
        day = int(date[8] + date[9])
        month = int(date[5] + date[6])
        year = int(date[0] + date[1] + date[2] + date[3])
        minutes = date[14] + date [15]
        seconds = date [17] + date[18]
        hours = hours - self.app_settings['collection_range']
        
        if hours < 0:
            if self.app_settings['collection_range'] == 48:
                day -= 2

            else:
                day -= 1
                if int(day) < 10:
                    day = '0' + str(day)

            if self.app_settings['collection_range'] == 12:
                hours += 24

        if int(day) <= 0:
            month -= 1
            if month == 2:
                if year % 400 == 0:
                    if self.app_settings['collection_range'] == 48:
                        month = '0' + str(month)
                        day = 28
                    else:
                        month = '0' + str(month)
                        day = 29
                else:
                    if self.app_settings['collection_range'] == 48:
                        month = '0' + str(month)
                        day = 27
                    else:
                        month = '0' + str(month) 
                        day = 28
            elif month == 0:
                year -= 1
                month = 12
                if self.app_settings['collection_range'] == 48:
                    day = 30
                else:
                    day = 31

            else:
                day = DAYS_IN_MONTHS[month-1]
                if self.app_settings['collection_range'] == 48:
                    day = int(day) - 1
                if month < 10:
                    month = '0' + str(month)
        else:
            month = date[5] + date[6]

        if self.app_settings['collection_range'] == 24 or self.app_settings['collection_range'] == 48:
            hours = date[11] + date[12]
        elif self.app_settings['collection_range'] == 12:
            if hours < 10:
                hours = '0' + str(hours)
            if day < 10:
                day = '0' + str(day)
            
        if self.app_settings['collection_range'] == 48:
            day = '0' + str(day)

        start_date = "{}-{}-{}T{}:{}:{}".format(year, month, day, hours, minutes, seconds)
        return start_date
 
    def analyze_cgm_data(self):
        filtered_data = []
        with open('data/full_cgm_data.json', 'r') as f:
            cgm_data = json.load(f)

        for egv in cgm_data['egvs']:
            filtered_data.append(egv['value'])

        f.close()
        
        with open('data/gv_data.json', 'w') as f:
            json.dump(filtered_data, f)

        f.close()

    def load_bs_data(self):
        
        "Load blood sugars from 'gv_data.json.'"
        
        with open('./data/gv_data.json', 'r') as f:
            data = json.load(f)
            
        return data

    def load_settings(self):

        "Loads settings from './data/settings.json.'"

        with open('./data/settings.json', 'r') as f:
            settings = json.load(f)

        f.close()
        return settings

    def save_settings(self):

        "Save settings when altered."

        with open('./data/settings.json', 'w') as f:
            json.dump(self.app_settings, f, indent=4)
            f.close()
            
    def get_advice(self):
        
        "Gets random advice depending on blood sugars average."
        
        option = random.randint(0, 2)
        if self.average >= self.app_settings['high_setting']:
            result = HIGH
        elif self.average <= self.app_settings['low_setting']:
            result = LOW
        else:
            result = IN_RANGE
        
        for x in result[random.randint(0, len(result) - 1)]:
            self.todays_advice.append(x)
            
        
        
        
        

