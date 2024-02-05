import threading
import os
import random

import pygame


class Speaker:
    def __init__(self):
        self.sequence = []
        self.busy = False
        pygame.init()

    def speak(self):
        while self.busy:
            if not self.sequence:
                return
            pass
        self.busy = True
        word = 'ERROR'
        while self.sequence or pygame.mixer.Channel(0).get_busy():
            if not pygame.mixer.Channel(0).get_busy():
                if not self.sequence:
                    break
                try:
                    word = self.sequence.pop(0)
                    print('Saying', word)
                    sound = pygame.mixer.Sound(f'speaker/{word}/' + random.choice(os.listdir(f'speaker/{word}')))
                    pygame.mixer.Channel(0).play(sound)
                except FileNotFoundError or IndexError:
                    print('File not found!')
                    self.say('bad beep', 'speaker error', 'no file', important=True)
                    self.busy = False
                    return
        print('Done for now.')
        self.busy = False

    def say(self, *sequence, important=False):
        if important:
            self.sequence[:0] = sequence
        else:
            self.sequence.extend(sequence)
        speak_thread = threading.Thread(target=self.speak)
        speak_thread.start()


if __name__ == '__main__':
    speaker = Speaker()
    print('Hi')
    # for i in range(20):
    #     speaker.say('bad beep')
    while True:
        word = input().split(', ')
        print(word)
        speaker.say(*word)
