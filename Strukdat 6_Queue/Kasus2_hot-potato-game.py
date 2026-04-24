
import pygame
import math
import time
import sys
import random
from collections import deque

# ── Warna ──────────────────────────────────────────────────────────────────
BG          = (15,  17,  26)
BG2         = (22,  26,  40)
CARD        = (30,  35,  55)
CARD2       = (40,  46,  70)
WHITE       = (240, 242, 248)
GRAY        = (120, 128, 155)
DIM         = (60,  66,  90)
CYAN        = (56,  189, 248)
CYAN_DIM    = (20,  80, 110)
GREEN       = (52,  211, 153)
GREEN_DIM   = (15,  70,  50)
RED         = (248,  80,  80)
RED_DIM     = (90,  25,  25)
YELLOW      = (250, 204,  21)
YELLOW_DIM  = (90,  74,  10)
ORANGE      = (251, 146,  60)
PURPLE      = (167, 139, 250)
PINK        = (244, 114, 182)

PLAYER_COLORS = [
    (56, 189, 248),   # cyan
    (52, 211, 153),   # green
    (250, 204, 21),   # yellow
    (251, 146, 60),   # orange
    (167, 139, 250),  # purple
    (244, 114, 182),  # pink
    (94, 234, 212),   # teal
    (248, 113, 113),  # red
]

# ── Queue ───────────────────────────────────────────────────────────────────
class Queue:
    def __init__(self):
        self._q = deque()

    def enqueue(self, item):
        self._q.append(item)

    def dequeue(self):
        return self._q.popleft()

    def peek(self):
        return self._q[0] if self._q else None

    def __len__(self):
        return len(self._q)

    def to_list(self):
        return list(self._q)


def hot_potato(names, num):
    """Algoritma Hot Potato — kembalikan urutan eliminasi & pemenang."""
    q = Queue()
    for name in names:
        q.enqueue(name)

    eliminated = []
    while len(q) > 1:
        for _ in range(num):
            q.enqueue(q.dequeue())   # oper melingkar
        eliminated.append(q.dequeue())   # tersingkir!

    winner = q.dequeue()
    return eliminated, winner


# ── Pygame helpers ───────────────────────────────────────────────────────────
def draw_rounded_rect(surf, color, rect, radius=14, alpha=255):
    s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), (0, 0, rect[2], rect[3]), border_radius=radius)
    surf.blit(s, (rect[0], rect[1]))


def draw_circle_outline(surf, color, center, radius, width=2):
    pygame.draw.circle(surf, color, center, radius, width)


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def draw_text(surf, text, font, color, cx, cy, anchor="center"):
    rendered = font.render(text, True, color)
    r = rendered.get_rect()
    if anchor == "center":
        r.center = (cx, cy)
    elif anchor == "topleft":
        r.topleft = (cx, cy)
    elif anchor == "midleft":
        r.midleft = (cx, cy)
    surf.blit(rendered, r)


def glow_circle(surf, color, center, radius, glow_r=18):
    """Draw a soft glow behind a circle."""
    glow = pygame.Surface((glow_r*2, glow_r*2), pygame.SRCALPHA)
    for i in range(glow_r, 0, -1):
        alpha = int(80 * (i / glow_r) ** 2)
        pygame.draw.circle(glow, (*color, alpha), (glow_r, glow_r), i)
    surf.blit(glow, (center[0]-glow_r, center[1]-glow_r))


# ── State mesin animasi ──────────────────────────────────────────────────────
class HotPotatoViz:
    def __init__(self):
        pygame.init()
        self.W, self.H = 1000, 680
        self.screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("🥔 Hot Potato — Circular Queue")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_lg  = pygame.font.SysFont("segoeui", 26, bold=True)
        self.font_md  = pygame.font.SysFont("segoeui", 18, bold=False)
        self.font_sm  = pygame.font.SysFont("segoeui", 14)
        self.font_xs  = pygame.font.SysFont("segoeui", 12)
        self.font_xl  = pygame.font.SysFont("segoeui", 36, bold=True)
        self.font_code= pygame.font.SysFont("consolas", 13)

        # Game data
        self.NAMES = ["Alice", "Bob", "Charlie", "Diana",
                      "Evan", "Fiona", "Grace"]
        self.NUM_PASS = 4   # jumlah operan sebelum tersingkir

        self.reset()

    # ── reset / init state ────────────────────────────────────────────────
    def reset(self):
        n = len(self.NAMES)
        self.players = [
            {"name": self.NAMES[i],
             "color": PLAYER_COLORS[i % len(PLAYER_COLORS)],
             "alive": True,
             "scale": 1.0,
             "alpha": 255,
             "shake": 0}
            for i in range(n)
        ]
        self.queue = list(range(n))   # indeks pemain dalam antrian

        self.potato_holder = 0        # indeks dalam self.queue
        self.pass_count    = 0        # sudah berapa kali dioper putaran ini
        self.round_num     = 1
        self.eliminated    = []       # nama yang sudah tersingkir
        self.winner        = None
        self.game_over     = False

        # Animasi
        self.anim_phase    = "idle"   # idle | passing | eliminating | winner
        self.anim_t        = 0.0
        self.anim_speed    = 1.5
        self.potato_pos    = (0, 0)
        self.potato_target = (0, 0)
        self.potato_src    = (0, 0)
        self.auto_play     = False
        self.auto_timer    = 0.0
        self.auto_delay    = 0.55     # detik antar operan otomatis

        self.log           = []
        self._add_log(f"Game dimulai! {len(self.NAMES)} pemain, operan per ronde: {self.NUM_PASS}", CYAN)
        self._add_log("Tekan SPACE untuk oper  |  A untuk auto-play  |  R untuk reset", GRAY)

        # Hitung posisi melingkar
        self._calc_positions()
        self.potato_pos = self.get_player_pos(self.queue[self.potato_holder])

    def _calc_positions(self):
        cx, cy = 340, 330
        r = min(195, 50 + len(self.players) * 22)
        self.circle_cx, self.circle_cy, self.circle_r = cx, cy, r
        n = len(self.players)
        self.player_positions = []
        for i in range(n):
            angle = math.radians(-90 + 360 * i / n)
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            self.player_positions.append((int(x), int(y)))

    def get_player_pos(self, player_idx):
        return self.player_positions[player_idx]

    def _add_log(self, msg, color=WHITE):
        self.log.append((msg, color))
        if len(self.log) > 12:
            self.log.pop(0)

    # ── satu langkah operan ───────────────────────────────────────────────
    def step_pass(self):
        if self.game_over or self.anim_phase != "idle":
            return

        current_holder_idx = self.queue[self.potato_holder]
        next_holder_pos    = (self.potato_holder + 1) % len(self.queue)
        next_holder_idx    = self.queue[next_holder_pos]

        self.potato_src    = self.get_player_pos(current_holder_idx)
        self.potato_target = self.get_player_pos(next_holder_idx)
        self.anim_phase    = "passing"
        self.anim_t        = 0.0
        self.pass_count   += 1

        # Rotate queue: enqueue(dequeue())
        front = self.queue.pop(0)
        self.queue.append(front)

        name_from = self.players[current_holder_idx]["name"]
        name_to   = self.players[next_holder_idx]["name"]
        self._add_log(f"  🥔 {name_from} → {name_to}  (oper #{self.pass_count})", YELLOW)

    def _finish_elimination(self):
        """Tersingkirkan pemain saat potato_holder (setelah animasi)."""
        elim_idx  = self.queue[0]
        elim_name = self.players[elim_idx]["name"]
        self.eliminated.append(elim_name)
        self.players[elim_idx]["alive"]  = False
        self.players[elim_idx]["shake"]  = 20
        self.queue.pop(0)
        self._add_log(f"❌ {elim_name} TERSINGKIR! (ronde {self.round_num})", RED)
        self.round_num  += 1
        self.pass_count  = 0

        if len(self.queue) == 1:
            winner_idx     = self.queue[0]
            self.winner    = self.players[winner_idx]["name"]
            self.game_over = True
            self.anim_phase = "winner"
            self.anim_t     = 0.0
            self._add_log(f"🏆 {self.winner} MENANG!", GREEN)
        else:
            self.anim_phase = "idle"
            # Potato ada di pemain [0] baru
            self.potato_holder = 0
            self.potato_pos = self.get_player_pos(self.queue[0])

    # ── update ────────────────────────────────────────────────────────────
    def update(self, dt):
        # Auto-play
        if self.auto_play and not self.game_over:
            self.auto_timer += dt
            if self.auto_timer >= self.auto_delay and self.anim_phase == "idle":
                self.auto_timer = 0.0
                if self.pass_count < self.NUM_PASS:
                    self.step_pass()
                else:
                    self._trigger_elimination()

        # Shake
        for p in self.players:
            if p["shake"] > 0:
                p["shake"] = max(0, p["shake"] - 1)

        # Anim: passing
        if self.anim_phase == "passing":
            self.anim_t += dt * 3.5
            if self.anim_t >= 1.0:
                self.anim_t      = 1.0
                self.potato_pos  = self.potato_target
                self.anim_phase  = "idle"
                if self.pass_count >= self.NUM_PASS:
                    # Langsung trigger eliminasi
                    self._trigger_elimination()
            else:
                t = self.anim_t
                # Arc parabolic
                sx, sy = self.potato_src
                tx, ty = self.potato_target
                x = lerp(sx, tx, t)
                y = lerp(sy, ty, t) - 60 * math.sin(math.pi * t)
                self.potato_pos = (int(x), int(y))

        # Anim: eliminating
        if self.anim_phase == "eliminating":
            self.anim_t += dt * 2.5
            if self.anim_t >= 1.0:
                self._finish_elimination()

        # Anim: winner pulse
        if self.anim_phase == "winner":
            self.anim_t += dt

    def _trigger_elimination(self):
        self.anim_phase = "eliminating"
        self.anim_t     = 0.0
        elim_idx  = self.queue[0]
        elim_name = self.players[elim_idx]["name"]
        self._add_log(f"⚠️  {elim_name} pegang saat waktu habis!", ORANGE)

    # ── draw ──────────────────────────────────────────────────────────────
    def draw(self):
        self.screen.fill(BG)

        self._draw_title()
        self._draw_arena()
        self._draw_potato()
        self._draw_queue_panel()
        self._draw_code_panel()
        self._draw_log_panel()
        self._draw_controls()

        if self.game_over:
            self._draw_winner_overlay()

        pygame.display.flip()

    def _draw_title(self):
        draw_text(self.screen, "🥔 Hot Potato — Circular Queue Simulation",
                  self.font_lg, WHITE, self.W//2, 26, "center")
        info = f"Pemain: {len(self.NAMES)}   |   Operan per ronde: {self.NUM_PASS}   |   Ronde: {self.round_num}"
        draw_text(self.screen, info, self.font_sm, GRAY, self.W//2, 50, "center")

    def _draw_arena(self):
        cx, cy, r = self.circle_cx, self.circle_cy, self.circle_r

        # Background lingkaran arena
        draw_rounded_rect(self.screen, BG2, (30, 65, 625, 560), radius=20)

        # Garis lingkaran panduan
        pygame.draw.circle(self.screen, DIM, (cx, cy), r, 1)

        # Garis koneksi antar pemain hidup
        alive_queue = [i for i in self.queue]
        for k in range(len(alive_queue)):
            a = self.get_player_pos(alive_queue[k])
            b = self.get_player_pos(alive_queue[(k+1) % len(alive_queue)])
            pygame.draw.line(self.screen, CARD2, a, b, 1)

        # Gambar pemain
        for i, p in enumerate(self.players):
            pos = self.player_positions[i]
            shake_x = random.randint(-2, 2) if p["shake"] > 0 else 0
            px = pos[0] + shake_x
            py = pos[1]

            if not p["alive"]:
                # Pemain tersingkir — tampilkan samar
                draw_circle_outline(self.screen, DIM, (px, py), 28, 1)
                draw_text(self.screen, p["name"], self.font_sm, DIM, px, py - 42, "center")
                draw_text(self.screen, "❌", self.font_md, RED_DIM, px, py, "center")
                continue

            # Cek apakah pemain ini pemegang potato
            holder_idx = self.queue[0] if self.queue else -1
            is_holder  = (i == holder_idx)

            # Glow jika pegang potato
            if is_holder and self.anim_phase in ("idle", "eliminating"):
                glow_circle(self.screen, p["color"], (px, py), 34, glow_r=42)

            # Lingkaran pemain
            bg_col = lerp_color(CARD, p["color"], 0.25) if is_holder else CARD
            pygame.draw.circle(self.screen, bg_col, (px, py), 28)
            border_w = 3 if is_holder else 1
            pygame.draw.circle(self.screen, p["color"], (px, py), 28, border_w)

            # Nama
            col = p["color"] if is_holder else WHITE
            draw_text(self.screen, p["name"], self.font_sm, col, px, py - 42, "center")

            # Posisi queue
            if i in self.queue:
                qi = self.queue.index(i)
                draw_text(self.screen, f"#{qi+1}", self.font_xs, GRAY, px + 30, py - 28, "center")

            # Indikator eliminating
            if is_holder and self.anim_phase == "eliminating":
                t = self.anim_t
                pulse = abs(math.sin(t * math.pi * 4))
                r_out = int(28 + 14 * pulse)
                s = pygame.Surface((r_out*2+4, r_out*2+4), pygame.SRCALPHA)
                pygame.draw.circle(s, (*RED, int(180*pulse)), (r_out+2, r_out+2), r_out, 3)
                self.screen.blit(s, (px - r_out - 2, py - r_out - 2))

        # Label tengah
        alive = len(self.queue)
        draw_text(self.screen, f"{alive} pemain", self.font_sm, GRAY, cx, cy - 10, "center")
        draw_text(self.screen, "tersisa", self.font_xs, DIM, cx, cy + 10, "center")

    def _draw_potato(self):
        if self.game_over and self.anim_phase == "winner":
            return
        px, py = self.potato_pos

        # Shadow
        s = pygame.Surface((30, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (0, 0, 0, 80), (0, 0, 30, 10))
        self.screen.blit(s, (px - 15, py + 20))

        # Glow
        glow = pygame.Surface((60, 60), pygame.SRCALPHA)
        for ri in range(28, 0, -1):
            alpha = int(100 * (ri/28)**2)
            pygame.draw.circle(glow, (*YELLOW, alpha), (30, 30), ri)
        self.screen.blit(glow, (px - 30, py - 30))

        # Emoji potato via text
        draw_text(self.screen, "🥔", self.font_xl, YELLOW, px, py, "center")

    def _draw_queue_panel(self):
        x, y, w, h = 665, 65, 325, 220
        draw_rounded_rect(self.screen, CARD, (x, y, w, h), radius=14)
        draw_text(self.screen, "📋 Circular Queue", self.font_md, CYAN, x+14, y+16, "topleft")

        # Header
        pygame.draw.line(self.screen, DIM, (x+10, y+36), (x+w-10, y+36), 1)
        draw_text(self.screen, "Pos", self.font_xs, GRAY, x+20, y+46, "topleft")
        draw_text(self.screen, "Nama", self.font_xs, GRAY, x+70, y+46, "topleft")
        draw_text(self.screen, "Status", self.font_xs, GRAY, x+200, y+46, "topleft")

        row_y = y + 60
        for qi, pi in enumerate(self.queue[:9]):
            p = self.players[pi]
            is_front = (qi == 0)
            row_col = CARD2 if is_front else None
            if row_col:
                draw_rounded_rect(self.screen, row_col, (x+8, row_y-3, w-16, 20), radius=6)

            # Pos badge
            bc = p["color"] if is_front else DIM
            draw_text(self.screen, f"#{qi+1}", self.font_xs, bc, x+20, row_y+6, "topleft")

            # Color dot
            pygame.draw.circle(self.screen, p["color"], (x+58, row_y+8), 5)
            # Nama
            name_col = p["color"] if is_front else WHITE
            draw_text(self.screen, p["name"], self.font_sm, name_col, x+70, row_y+6, "topleft")

            # Status
            if is_front:
                draw_text(self.screen, "🥔 pegang", self.font_xs, YELLOW, x+200, row_y+6, "topleft")
            elif qi == len(self.queue)-1:
                draw_text(self.screen, "← belakang", self.font_xs, GRAY, x+200, row_y+6, "topleft")

            row_y += 20

        if len(self.queue) > 9:
            draw_text(self.screen, f"... +{len(self.queue)-9} lagi", self.font_xs, GRAY, x+20, row_y+4, "topleft")

        # Pass counter
        pygame.draw.line(self.screen, DIM, (x+10, y+h-46), (x+w-10, y+h-46), 1)
        draw_text(self.screen, f"Operan ronde ini: {self.pass_count} / {self.NUM_PASS}",
                  self.font_sm, ORANGE, x+14, y+h-32, "topleft")

        # Progress bar operan
        bar_w = w - 28
        pct   = min(1.0, self.pass_count / self.NUM_PASS)
        draw_rounded_rect(self.screen, DIM, (x+14, y+h-16, bar_w, 8), radius=4)
        if pct > 0:
            col = lerp_color(GREEN, RED, pct)
            draw_rounded_rect(self.screen, col, (x+14, y+h-16, int(bar_w*pct), 8), radius=4)

    def _draw_code_panel(self):
        x, y, w, h = 665, 300, 325, 220
        draw_rounded_rect(self.screen, CARD, (x, y, w, h), radius=14)
        draw_text(self.screen, "💻 Kode Berjalan", self.font_md, PURPLE, x+14, y+16, "topleft")
        pygame.draw.line(self.screen, DIM, (x+10, y+36), (x+w-10, y+36), 1)

        lines = [
            ("def hot_potato(names, num):", WHITE, False),
            ("  q = Queue()", GRAY, False),
            ("  for name in names:", GRAY, False),
            ("    q.enqueue(name)", GRAY, False),
            ("  while len(q) > 1:", CYAN, True),
            ("    for _ in range(num):", YELLOW, self.anim_phase == "passing"),
            ("      q.enqueue(q.dequeue())", YELLOW, self.anim_phase == "passing"),
            ("    q.dequeue()  # tersingkir!", RED, self.anim_phase == "eliminating"),
            ("  return q.dequeue()  # pemenang!", GREEN, self.anim_phase == "winner"),
        ]
        ly = y + 46
        for line_txt, col, highlight in lines:
            if highlight:
                draw_rounded_rect(self.screen, lerp_color(BG, col, 0.15),
                                  (x+8, ly-1, w-16, 17), radius=4)
                draw_rounded_rect(self.screen, col, (x+8, ly-1, 3, 17), radius=2)
            draw_text(self.screen, line_txt, self.font_code, col if highlight else DIM,
                      x+16, ly+7, "topleft")
            ly += 18

    def _draw_log_panel(self):
        x, y, w, h = 665, 532, 325, 120
        draw_rounded_rect(self.screen, CARD, (x, y, w, h), radius=14)
        draw_text(self.screen, "📜 Log", self.font_md, GRAY, x+14, y+12, "topleft")
        pygame.draw.line(self.screen, DIM, (x+10, y+32), (x+w-10, y+32), 1)

        ly = y + 40
        for msg, col in self.log[-5:]:
            # Truncate jika terlalu panjang
            if len(msg) > 42:
                msg = msg[:41] + "…"
            draw_text(self.screen, msg, self.font_xs, col, x+12, ly, "topleft")
            ly += 17

    def _draw_controls(self):
        y = self.H - 34
        controls = [
            ("SPACE", "Oper 1x"),
            ("A",     "Auto-play"),
            ("R",     "Reset"),
            ("ESC",   "Keluar"),
        ]
        x = 40
        for key, desc in controls:
            draw_rounded_rect(self.screen, CARD2, (x, y, 38, 22), radius=6)
            draw_text(self.screen, key, self.font_xs, CYAN, x+19, y+11, "center")
            x += 44
            draw_text(self.screen, desc, self.font_xs, GRAY, x, y+11, "midleft")
            x += len(desc)*7 + 20

        # Auto-play indicator
        if self.auto_play:
            draw_rounded_rect(self.screen, GREEN_DIM, (self.W-150, y, 120, 22), radius=6)
            draw_text(self.screen, "● AUTO-PLAY ON", self.font_xs, GREEN, self.W-90, y+11, "center")

    def _draw_winner_overlay(self):
        t = self.anim_t
        pulse = 0.5 + 0.5 * math.sin(t * 3)

        # Semi-transparent overlay
        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        # Winner card
        cw, ch = 420, 300
        cx, cy = self.W//2 - cw//2, self.H//2 - ch//2
        draw_rounded_rect(self.screen, CARD, (cx, cy, cw, ch), radius=24)

        border_col = lerp_color(GREEN, YELLOW, pulse)
        pygame.draw.rect(self.screen, border_col, (cx, cy, cw, ch), 2, border_radius=24)

        # Trophy
        draw_text(self.screen, "🏆", pygame.font.SysFont("segoeui", 72),
                  YELLOW, self.W//2, cy+70, "center")
        draw_text(self.screen, "PEMENANG!", self.font_xl, YELLOW, self.W//2, cy+130, "center")

        winner_idx = self.queue[0] if self.queue else 0
        w_color = self.players[winner_idx]["color"]
        draw_text(self.screen, self.winner, self.font_lg, w_color, self.W//2, cy+168, "center")

        # Eliminated order
        draw_text(self.screen, "Urutan tersingkir:", self.font_sm, GRAY, self.W//2, cy+198, "center")
        elim_str = "  →  ".join(self.eliminated)
        if len(elim_str) > 50:
            elim_str = elim_str[:50] + "…"
        draw_text(self.screen, elim_str, self.font_xs, DIM, self.W//2, cy+216, "center")

        draw_text(self.screen, "Tekan R untuk main lagi", self.font_sm, GRAY,
                  self.W//2, cy+260, "center")

        # Confetti
        random.seed(int(t * 20))
        for _ in range(30):
            cx2 = random.randint(0, self.W)
            cy2 = random.randint(0, self.H)
            col = random.choice([YELLOW, GREEN, CYAN, PINK, ORANGE])
            size = random.randint(3, 7)
            pygame.draw.rect(self.screen, col, (cx2, cy2, size, size), border_radius=2)

    # ── main loop ─────────────────────────────────────────────────────────
    def run(self):
        prev_time = time.time()
        while True:
            now = time.time()
            dt  = now - prev_time
            prev_time = now

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_SPACE:
                        if not self.game_over and self.anim_phase == "idle":
                            if self.pass_count < self.NUM_PASS:
                                self.step_pass()
                            else:
                                self._trigger_elimination()
                    elif event.key == pygame.K_a:
                        self.auto_play = not self.auto_play
                        self.auto_timer = 0.0

            self.update(dt)
            self.draw()
            self.clock.tick(60)


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    viz = HotPotatoViz()
    viz.run()