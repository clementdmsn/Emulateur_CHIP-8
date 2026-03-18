from chip8 import Chip8
from inputs import Inputs

import readchar
import time
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

class Front:
    def __init__(self, rom_path):
        self.emu = Chip8(rom_path)

    def make_layout(self):
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=5),
        )
        layout["body"].split_row(
            Layout(name="screen", ratio=2),
            Layout(name="regs", ratio=1),
        )
        return layout

    def render_header(self):
        return Panel("CHIP-8 Emulator", title="Status")

    def render_screen(self):
        pixel_map = {
            (0, 0): " ",
            (1, 0): "▀",
            (0, 1): "▄",
            (1, 1): "█",
        }
        lines = []
        for y in range(0, self.emu.HEIGHT, 2):
            top_row = self.emu.screen[y]
            bottom_row = self.emu.screen[y + 1] if y + 1 < self.emu.HEIGHT else [0] * self.emu.WIDTH
            line = "".join(
                pixel_map[(top_row[x], bottom_row[x])]
                for x in range(self.emu.WIDTH)
            )
            lines.append(line)
        screen_panel = Panel.fit("\n".join(lines), title="Screen")
        return Align.center(screen_panel, vertical="middle")

    def render_regs(self):
        t = Text()
        for i in range(16):
            t.append(f"V{i:X}: {hex(self.emu.regs[f'V{i:X}']).replace ('0x', '').zfill(2)} ")
            if i % 4 == 3:
                t.append("\n")
        t.append(f"\nPC: {hex(self.emu.pc).replace('0x', '').zfill(3)}   I: {hex(self.emu.regs['I']).replace('0x', '').zfill(2)}")
        return Panel(t, title="Registers")

    def render_footer(self):
        last = hex(self.emu.memory[self.emu.pc-2]).replace("0x", "").zfill(2)
        last += hex(self.emu.memory[self.emu.pc-1]).replace("0x", "").zfill(2)
        return Panel(f"Last opcode: {last}\n", title="Trace / Logs")

    def draw(self):
        console = Console()
        layout = self.make_layout()
        inputs = Inputs()

        with Live(layout, console=console, refresh_per_second=30):
            while True:
                if inputs.quit:
                    break

                self.emu.keys = inputs.keys
                self.emu.update_timers()

                for _ in range(10):   # run 10 opcodes per frame
                    self.emu.run_instruction()

                layout["header"].update(self.render_header())
                layout["screen"].update(self.render_screen())
                layout["regs"].update(self.render_regs())
                layout["footer"].update(self.render_footer())

                time.sleep(1 / 60)

        console.clear()

