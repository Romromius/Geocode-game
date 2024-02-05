import random
from io import BytesIO
import requests
from PIL import Image
import pygame
import speaker

with open('cities', 'r', encoding='UTF-8') as f:
    cities = f.read().split('\n')


def get_fragment(toponym_to_find):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    if easy:
        print('Подсказка:', toponym_to_find)

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym_to_find,
        "format": "json"}

    try:
        response = requests.get(geocoder_api_server, params=geocoder_params)
    except requests.exceptions.ConnectionError:
        speaker.Speaker().say('bad beep', 'error', 'no net')
        quit('No net')

    if not response:
        quit(code='I have no response')

    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    delta = "0.008"

    map_params = {
        "ll": ",".join([toponym_longitude, toponym_lattitude]),
        "spn": ",".join([delta, delta]),
        "l": "map"
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=map_params)

    Image.open(BytesIO(
        response.content)).save('fragment.png')


class Button:
    def __init__(self, coords: tuple, w, h, text, event, align='center',
                 image_path="btn.png",
                 indic_path1="btn.png",
                 indic_path2="btn2.png"):
        self.font = pygame.font.SysFont('Arial', 30)
        self.x, self.y, self.w, self.h = coords[0], coords[1], w, h
        self.text = text
        t = 0
        self.phase = t
        self.sp = [indic_path1, indic_path2]
        self.align = align

        self.image = pygame.image.load(image_path)

        self.indic_image1 = pygame.image.load(indic_path1)
        self.indic_image2 = pygame.image.load(indic_path2)

        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.is_indic = False
        self.event = event

        self.rolloversound = pygame.mixer.Sound('music/buttonrollover.wav')
        self.clocksound = pygame.mixer.Sound('music/buttonclickrelease.wav')

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

        text_surface = self.font.render(self.text, True, 'black')
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def check_indic(self, pos_mouse):
        if not self.is_indic and self.rect.collidepoint(pos_mouse):
            self.rolloversound.play()
        self.is_indic = self.rect.collidepoint(pos_mouse)

    def click_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_indic:
            self.clocksound.play()
            pygame.event.post(pygame.event.Event(self.event, button=self))

    def upd(self):
        if self.is_indic:
            self.image = self.indic_image2
        else:
            self.image = self.indic_image1


SIZE = WIDTH, HEIGHT = 600, 450
FPS = 120

match input('Blitz?(y/n): '):
    case 'y'|'Y'|'':
        blitz = True
    case _:
        blitz = False
match input('Easymode?(y/n): '):
    case 'y'|'Y'|'':
        easy = True
    case _:
        easy = False


pygame.init()
window = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()

guess_event = pygame.USEREVENT + 1
fail_event = pygame.USEREVENT + 2
win_event = pygame.USEREVENT + 3


font = pygame.font.SysFont('Arial', 70)
def level(time, track):
    pygame.mixer.music.load(f'music/{track}.mp3')
    font = pygame.font.SysFont('Arial', 50)
    s = 5
    random.shuffle(cities)
    city = cities.pop()
    get_fragment(city)
    image = pygame.image.load('fragment.png')

    coords = [(0, HEIGHT - 100), (WIDTH/2, HEIGHT - 100), (WIDTH/2, HEIGHT - 50), (0, HEIGHT - 50)]
    random.shuffle(coords)

    button1 = Button(coords.pop(), 0, 0, city, guess_event)
    button2 = Button(coords.pop(), 0, 0, cities.pop(), fail_event)
    button3 = Button(coords.pop(), 0, 0, cities.pop(), fail_event)
    button4 = Button(coords.pop(), 0, 0, cities.pop(), fail_event)
    buttons = [button1, button2, button3, button4]

    t = time
    first_cycle = True
    pygame.display.flip()
    while True:
        if first_cycle:
            pygame.mixer.music.play()
            t = time + 1
            s = 5

        t -= clock.get_time() / 1000

        if t < 0:
            pygame.event.post(pygame.event.Event(fail_event))

        window.fill('black')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                return
            if event.type == fail_event:
                speaker.Speaker().say('bad beep', 'taunt')
                window.fill('red')
                pygame.mixer.music.load('music/loose.mp3')
                pygame.mixer.music.play()
                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            quit()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            quit()
                    pygame.display.flip()
                    clock.tick(FPS)
            if event.type == guess_event:
                window.fill('green')
                pygame.mixer.music.stop()
                pygame.mixer.Sound('music/0.mp3').play()
                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            quit()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            return
                    pygame.display.flip()
                    clock.tick(FPS)
                    if blitz:
                        return

            for j in buttons:
                j.click_event(event)

        s = pygame.math.lerp(s, 1, pygame.math.clamp(clock.get_time() / 2000, 0, 1))

        window.blit(pygame.transform.scale(image, (WIDTH * s, HEIGHT * s)),
                    ((WIDTH - WIDTH * s) / 2, (HEIGHT - HEIGHT * s) / 2))
        t_text = font.render(str(round(t)), True, 'black')
        if t < 5:
            t_text = font.render(str(round(t, 1)), True, 'red')
        elif t < 10:
            t_text = font.render(str(round(t, 1)), True, 'orange')
        window.blit(t_text, (0, 0))

        for i in buttons:
            i.check_indic(pygame.mouse.get_pos())
            i.upd()
            i.draw(window)

        clock.tick(FPS)

        pygame.display.flip()
        first_cycle = False


level(120, 1)
level(90, 2)
level(60, 3)
level(30, 4)
level(20, 5)
level(10, 6)
level(5, 7)
window.fill('white')
window.blit(font.render('Победа!', True, 'black'), (150, 200))
pygame.mixer.music.load('music/win.mp3')
pygame.mixer.music.play()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
    pygame.display.flip()
    clock.tick(FPS)
