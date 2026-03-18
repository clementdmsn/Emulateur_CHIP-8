import random
import time


FONT_BASE = 0x050

FONT_SPRITES = [
    0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
    0x20, 0x60, 0x20, 0x20, 0x70,  # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
    0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
    0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
    0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
    0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
    0xF0, 0x80, 0xF0, 0x80, 0x80   # F
]

class Chip8:
    def __init__(self, rom_path):
        self.START = 0x200
        self.HEIGHT = 32
        self.WIDTH = 64

        self.memory = [0] * 4096

        self.keys = [0] * 16
        self.pc = self.START 
        self.delay_timer = 0
        self. sound_timer = 0
        self.last_timer_tick = time.perf_counter()

        self.screen = [[0]*self.WIDTH for i in range(0, self.HEIGHT)]

        self.stack = []

        self.rom_path = rom_path

        self.regs = {
            "V0": 0x0,
            "V1": 0x0,
            "V2": 0x0,
            "V3": 0x0,
            "V4": 0x0,
            "V5": 0x0,
            "V6": 0x0,
            "V7": 0x0,
            "V8": 0x0,
            "V9": 0x0,
            "VA": 0x0,
            "VB": 0x0,
            "VC": 0x0,
            "VD": 0x0,
            "VE": 0x0,
            "VF": 0x0,  # carry / collision flag
            "I": 0x0,
        }

        self.load_fonts()
        self.load_rom(self.rom_path)

    def load_fonts(self):
        for i, byte in enumerate(FONT_SPRITES):
            self.memory[FONT_BASE + i] = byte

    def update_timers(self):
        now = time.perf_counter()
        if now - self.last_timer_tick >= 1 / 60:
            if self.delay_timer > 0:
                self.delay_timer -= 1
            if self.sound_timer > 0:
                self.sound_timer -= 1
            self.last_timer_tick = now

    def load_rom(self, rom_path):
        with open(rom_path, 'rb') as f:
            data = f.read()
        for i in range(0, len(data)):
            self.memory[self.START + i] = data[i]
        print([hex(x) for x in self.memory[0x200:0x230]])

    def run_instruction(self):
        opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]
        self.pc += 2
        if self.pc < 0 or self.pc + 1 >= len(self.memory):
            raise RuntimeError(f"PC out of bounds: {self.pc:#04x}")
        self.dispatch(opcode)

    def cls(self): #00E0
        print("cls")
        self.screen = [[0]*self.WIDTH for i in range(0, self.HEIGHT)]

    def ret(self): # 00EE
        print("ret")
        if not self.stack:
            raise RuntimeError("Stack underflow on RET")
        self.pc = self.stack.pop()

    def jp_addr(self, nnn): #1NNN
        print("jp_addr")
        self.pc = nnn 
        
    def call_addr(self, nnn): #2NNN
        print("call_addr")
        self.stack.append(self.pc)
        self.pc = nnn

    def se_vx_byte(self, x, kk): #3XKK
        print("se_vx_byte")
        if self.regs[f"V{x}"] == kk:
            self.pc += 2

    def sne_vx_byte(self, x, kk): #4XKK
        print("sne_vx_byte")
        if self.regs[f"V{x}"] != kk:
            self.pc += 2

    def se_vx_vy(self, x, y): #5XY0
        print("se_vx_vy")
        if self.regs[f"V{x}"] == self.regs[f"V{y}"]:
            self.pc += 2
    def ld_vx_byte(self, x, kk): #6XKK
        print("ld_vx_byte")
        self.regs[f"V{x}"] = kk
        print(self.regs[f"V{x}"])

    def add_vx_byte(self, x, kk): #7XKK
        print("add_vx_byte")
        self.regs[f"V{x}"] = (self.regs[f"V{x}"] + kk) & 0xFF

    def ld_vx_vy(self, x, y): #8XY0
        print("ld_vx_vy")
        self.regs[f"V{x}"] = self.regs[f"V{y}"] 

    def or_vx_vy(self, x, y): #8XY1
        print("or_vx_vy")
        self.regs[f"V{x}"] |=  self.regs[f"V{y}"]

    def and_vx_vy(self, x, y): #8XY2
        print("and_vx_vy")
        self.regs[f"V{x}"] &= self.regs[f"V{y}"]

    def xor_vx_vy(self, x, y): #8XY3
        print("xor_vx_vy")
        self.regs[f"V{x}"] ^= self.regs[f"V{y}"]

    def add_vx_vy(self, x, y): #8XY4
        print("add_vx_vy")
        result = self.regs[f"V{x}"] + self.regs[f"V{y}"]
        self.regs['VF'] = 1 if result > 0xFF else 0
        self.regs[f"V{x}"] = result & 0xFF

    def sub_vx_vy(self, x, y): #8XY5
        print("sub_vx_vy")
        result = self.regs[f"V{x}"] - self.regs[f"V{y}"]
        self.regs['VF'] = 1 if self.regs[f"V{x}"] >= self.regs[f"V{y}"] else 0 
        self.regs[f"V{x}"] = result & 0xFF

    def subn_vx_vy(self, x, y): #8XY7
        print("subn_vx_vy")
        result = self.regs[f"V{y}"] - self.regs[f"V{x}"]
        self.regs['VF'] = 1 if self.regs[f"V{y}"] >= self.regs[f"V{x}"] else 0 
        self.regs[f"V{x}"] = result & 0xFF

    def shr_vx(self, x, y):  # 8XY6
        print("shr_vx")
        value = self.regs[f"V{y}"]
        self.regs["VF"] = value & 0x1
        self.regs[f"V{x}"] = (value >> 1) & 0xFF

    def shl_vx(self, x, y):  # 8XYE
        print("shl_vx")
        value = self.regs[f"V{y}"]
        self.regs["VF"] = (value >> 7) & 0x1
        self.regs[f"V{x}"] = (value << 1) & 0xFF

    def sne_vx_vy(self, x, y): #9XY0
        print("sne_vx_vy")
        if self.regs[f"V{x}"] != self.regs[f"V{y}"] :
            self.pc += 2

    def ld_i_addr(self, nnn): #ANNN
        print("ld_i_addr")
        self.regs["I"] = nnn

    def jp_v0_addr(self, nnn): #BNNN
        print("jp_v0_addr")
        self.pc = nnn + self.regs[f"V0"]

    def rnd_vx_byte(self, x, kk): #CXKK
        print("rnd_vx_byte")
        self.regs[f"V{x}"] = random.randint(0, 255) & kk

    def drw_vx_vy_n(self, x, y, n): #DXYN
        vx = self.regs[f"V{x}"]
        vy = self.regs[f"V{y}"]

        self.regs['VF'] = 0

        for row in range(n):
            sprite_byte = self.memory[self.regs['I'] + row]

            for col in range(8): 
                mask = 0x80 >> col
                if sprite_byte & mask == 0:
                    continue

                px = (vx + col) % self.WIDTH
                py = (vy + row) % self.HEIGHT

                if self.screen[py][px]:
                    self.regs['VF'] = 1

                self.screen[py][px] ^= 1

    def skp_vx(self, x):  # EX9E
        print("skp_vx")
        key = self.regs[f"V{x}"] & 0xF
        if self.keys[key]:
            self.pc += 2

    def sknp_vx(self, x):  # EXA1
        print("sknp_vx")
        key = self.regs[f"V{x}"] & 0xF
        if not self.keys[key]:
            self.pc += 2

    def ld_vx_dt(self, x):  #FX07
        print("ld_vx_dt")
        self.regs[f"V{x}"] = self.delay_timer

    def ld_vx_k(self, x): # FX0A
        print("ld_vx_k")
        for i, pressed in enumerate(self.keys):
            if pressed:
                self.regs[f"V{x}"] = i
                return
        self.pc -= 2

    def ld_dt_vx(self, x): #FX15
        print("ld_dt_vx")
        self.delay_timer = self.regs[f"V{x}"]

    def ld_st_vx(self, x): #FX18
        print("ld_st_vx")
        self.sound_timer = self.regs[f"V{x}"]

    def add_i_vx(self, x): #FX1E
        print("add_i_vx")
        self.regs["I"] = (self.regs["I"] + self.regs[f"V{x}"]) & 0xFFF

    def ld_f_vx(self, x): #FX29 
        print("ld_f_vx")
        digit = self.regs[f"V{x}"] & 0xF
        self.regs['I'] = FONT_BASE + digit * 5

    def ld_b_vx(self, x): #FX33
        print("ld_b_vx")
        value = self.regs[f"V{x}"]
        self.memory[self.regs['I']] = value // 100
        self.memory[self.regs['I'] + 1]  = (value // 10) % 10
        self.memory[self.regs['I'] + 2] = value % 10

    def ld_i_vx(self, x):  # FX55
        print("ld_i_vx")
        for i in range(x + 1):
            self.memory[self.regs["I"] + i] = self.regs[f"V{i}"]
        self.regs["I"] += x + 1

    def ld_vx_i(self, x):  # FX65
        print("ld_vx_i")
        for i in range(x + 1):
            self.regs[f"V{i}"] = self.memory[self.regs["I"] + i]
        self.regs["I"] += x + 1

    def dispatch(self, opcode: int):
        nnn = opcode & 0x0FFF
        kk  = opcode & 0x00FF
        x   = (opcode >> 8) & 0x0F
        y   = (opcode >> 4) & 0x0F
        n   = opcode & 0x000F

        match opcode & 0xF000:
            case 0x0000:
                match opcode:
                    case 0x00E0:
                        self.cls()
                    case 0x00EE:
                        self.ret()
                    case _:
                        raise ValueError(f"Unknown opcode {opcode:04X}")

            case 0x1000:
                self.jp_addr(nnn)

            case 0x2000:
                self.call_addr(nnn)

            case 0x3000:
                self.se_vx_byte(x, kk)

            case 0x4000:
                self.sne_vx_byte(x, kk)

            case 0x5000:
                if n == 0:
                    self.se_vx_vy(x, y)
                else:
                    raise ValueError(f"Unknown opcode {opcode:04X}")

            case 0x6000:
                self.ld_vx_byte(x, kk)

            case 0x7000:
                self.add_vx_byte(x, kk)

            case 0x8000:
                match n:
                    case 0x0:
                        self.ld_vx_vy(x, y)
                    case 0x1:
                        self.or_vx_vy(x, y)
                    case 0x2:
                        self.and_vx_vy(x, y)
                    case 0x3:
                        self.xor_vx_vy(x, y)
                    case 0x4:
                        self.add_vx_vy(x, y)
                    case 0x5:
                        self.sub_vx_vy(x, y)
                    case 0x6:
                        self.shr_vx(x, y)
                    case 0x7:
                        self.subn_vx_vy(x, y)
                    case 0xE:
                        self.shl_vx(x, y)
                    case _:
                        raise ValueError(f"Unknown opcode {opcode:04X}")

            case 0x9000:
                if n == 0:
                    self.sne_vx_vy(x, y)
                else:
                    raise ValueError(f"Unknown opcode {opcode:04X}")

            case 0xA000:
                self.ld_i_addr(nnn)

            case 0xB000:
                self.jp_v0_addr(nnn)

            case 0xC000:
                self.rnd_vx_byte(x, kk)

            case 0xD000:
                self.drw_vx_vy_n(x, y, n)

            case 0xE000:
                match kk:
                    case 0x9E:
                        self.skp_vx(x)
                    case 0xA1:
                        self.sknp_vx(x)
                    case _:
                        raise ValueError(f"Unknown opcode {opcode:04X}")

            case 0xF000:
                match kk:
                    case 0x07:
                        self.ld_vx_dt(x)
                    case 0x0A:
                        self.ld_vx_k(x)
                    case 0x15:
                        self.ld_dt_vx(x)
                    case 0x18:
                        self.ld_st_vx(x)
                    case 0x1E:
                        self.add_i_vx(x)
                    case 0x29:
                        self.ld_f_vx(x)
                    case 0x33:
                        self.ld_b_vx(x)
                    case 0x55:
                        self.ld_i_vx(x)
                    case 0x65:
                        self.ld_vx_i(x)
                    case _:
                        raise ValueError(f"Unknown opcode {opcode:04X}")

            case _:
                raise ValueError(f"Unknown opcode {opcode:04X}")






