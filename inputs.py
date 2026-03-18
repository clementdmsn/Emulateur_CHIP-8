import threading
import readchar
import time

class Inputs:
    def __init__(self):
        self.keys = [0] * 16
        self.running = True
        self.quit = False

        self.key_map = {
                '7': 0x1, '8': 0x2, '9': 0x3, '0': 0xC,
                'u': 0x4, 'i': 0x5, 'o': 0x6, 'p': 0xD,
                'j': 0x7, 'k': 0x8, 'l': 0x9, 'm': 0xE,
                ',': 0xA, ';': 0x0, ':': 0xB, '!': 0xF
                }

        threading.Thread(
                target = self._listen,
                daemon = True
        ).start()

    def _listen(self):
        while self.running:
            key = readchar.readkey()
            
            if key == 'q':
                self.quit = True
                self.running = False
                return

            if key in self.key_map:
                idx = self.key_map[key]
                self.keys[idx] = 1
                time.sleep(0.05)
                self.keys[idx] = 0
