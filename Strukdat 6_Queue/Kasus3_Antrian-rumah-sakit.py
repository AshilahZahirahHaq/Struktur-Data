"""
🏥 Antrian Rumah Sakit — Bounded Priority Queue
Visualisasi GUI Animasi menggunakan Pygame
Prioritas: 0=Kritis, 1=Darurat, 2=Menengah, 3=Ringan
"""

import pygame, sys, time, math, random
from collections import deque

# ═══════════════════════════════════════════════════════════════════
# WARNA
# ═══════════════════════════════════════════════════════════════════
BG        = (12,  15,  23)
BG2       = (18,  22,  36)
CARD      = (25,  30,  48)
CARD2     = (35,  41,  62)
CARD3     = (45,  52,  78)
WHITE     = (235, 238, 248)
GRAY      = (110, 118, 148)
DIM       = (55,  62,  88)
LINE      = (40,  46,  68)

# Priority colors
P_COLORS = {
    0: (239,  68,  68),   # Kritis  — merah
    1: (249, 115,  22),   # Darurat — oranye
    2: (234, 179,   8),   # Menengah— kuning
    3: (34,  197,  94),   # Ringan  — hijau
}
P_DIM = {
    0: (80,  20,  20),
    1: (80,  38,  10),
    2: (80,  60,   5),
    3: (12,  65,  32),
}
P_LABELS = {0: "KRITIS", 1: "DARURAT", 2: "MENENGAH", 3: "RINGAN"}
P_ICONS  = {0: "🔴", 1: "🟠", 2: "🟡", 3: "🟢"}

CYAN    = (56,  189, 248)
GREEN   = (52,  211, 153)
YELLOW  = (250, 204,  21)
ORANGE  = (251, 146,  60)
PURPLE  = (167, 139, 250)
PINK    = (244, 114, 182)
TEAL    = (45,  212, 191)

# ═══════════════════════════════════════════════════════════════════
# BOUNDED PRIORITY QUEUE
# ═══════════════════════════════════════════════════════════════════
class BPriorityQueue:
    """
    Priority Queue dengan 'num_levels' level prioritas.
    Tiap level adalah FIFO queue biasa.
    enqueue(item, priority) → masukkan ke slot prioritas
    dequeue()               → ambil dari prioritas tertinggi (0) dulu
    """
    def __init__(self, num_levels: int):
        self.num_levels = num_levels
        self._queues: list[deque] = [deque() for _ in range(num_levels)]

    def enqueue(self, item, priority: int):
        assert 0 <= priority < self.num_levels
        self._queues[priority].append(item)

    def dequeue(self):
        for q in self._queues:
            if q:
                return q.popleft()
        raise IndexError("Priority queue kosong!")

    def peek(self):
        for q in self._queues:
            if q:
                return q[0]
        return None

    def isEmpty(self) -> bool:
        return all(len(q) == 0 for q in self._queues)

    def total(self) -> int:
        return sum(len(q) for q in self._queues)

    def snapshot(self) -> list[list]:
        """Kembalikan snapshot semua level sebagai list of list."""
        return [list(q) for q in self._queues]


# ═══════════════════════════════════════════════════════════════════
# DATA PASIEN DEMO
# ═══════════════════════════════════════════════════════════════════
DEMO_PATIENTS = [
    ("Budi",   3, "Sakit kepala ringan"),
    ("Ani",    0, "Serangan jantung"),
    ("Citra",  2, "Demam tinggi"),
    ("Dedi",   0, "Kecelakaan berat"),
    ("Eka",    1, "Patah tulang"),
    ("Fajar",  2, "Infeksi paru"),
    ("Gita",   1, "Pendarahan sedang"),
    ("Hendra", 3, "Flu biasa"),
    ("Indah",  0, "Gagal napas"),
    ("Joko",   2, "Nyeri hebat"),
]

# ═══════════════════════════════════════════════════════════════════
# HELPER DRAW
# ═══════════════════════════════════════════════════════════════════
def rr(surf, color, rect, r=12, alpha=255, border=0, border_color=None):
    """Rounded rect, opsional border."""
    if alpha < 255:
        s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, alpha), (0, 0, rect[2], rect[3]), border_radius=r)
        surf.blit(s, (rect[0], rect[1]))
    else:
        pygame.draw.rect(surf, color, rect, border_radius=r)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=r)

def txt(surf, text, font, color, x, y, anchor="topleft"):
    rendered = font.render(str(text), True, color)
    rc = rendered.get_rect()
    setattr(rc, anchor, (x, y))
    surf.blit(rendered, rc)

def lerp(a, b, t): return a + (b - a) * t
def lerpc(c1, c2, t): return tuple(int(lerp(c1[i], c2[i], max(0,min(1,t)))) for i in range(3))
def ease_out(t): return 1 - (1 - t) ** 3
def ease_in_out(t): return t * t * (3 - 2 * t)

def glow(surf, color, cx, cy, radius, strength=90):
    s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    for ri in range(radius, 0, -4):
        a = int(strength * (ri/radius)**2.5)
        pygame.draw.circle(s, (*color, min(255, a)), (radius, radius), ri)
    surf.blit(s, (cx - radius, cy - radius))


# ═══════════════════════════════════════════════════════════════════
# PARTICLE SYSTEM
# ═══════════════════════════════════════════════════════════════════
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vx = random.uniform(-120, 120)
        self.vy = random.uniform(-200, -60)
        self.color = color
        self.life = 1.0
        self.size = random.randint(3, 7)

    def update(self, dt):
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        self.vy += 280 * dt  # gravity
        self.life -= dt * 1.8

    def draw(self, surf):
        if self.life <= 0: return
        a = int(255 * self.life)
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, a), (self.size, self.size), self.size)
        surf.blit(s, (int(self.x)-self.size, int(self.y)-self.size))


# ═══════════════════════════════════════════════════════════════════
# CARD animasi pasien
# ═══════════════════════════════════════════════════════════════════
class PatientCard:
    def __init__(self, name, priority, diagnosis, card_id):
        self.name = name
        self.priority = priority
        self.diagnosis = diagnosis
        self.id = card_id

        self.x = self.y = 0.0
        self.target_x = self.target_y = 0.0
        self.alpha = 0.0
        self.scale = 0.7
        self.phase = "spawning"   # spawning | idle | moving | serving | done
        self.t = 0.0
        self.particles: list[Particle] = []

    @property
    def color(self): return P_COLORS[self.priority]
    @property
    def dim(self): return P_DIM[self.priority]
    @property
    def label(self): return P_LABELS[self.priority]


# ═══════════════════════════════════════════════════════════════════
# MAIN VISUALIZER
# ═══════════════════════════════════════════════════════════════════
class HospitalPQViz:
    W, H = 1060, 700

    # Layout
    QUEUE_X   = 30     # panel antrian kiri
    QUEUE_W   = 480
    CODE_X    = 530    # panel kode tengah-kanan
    CODE_W    = 240
    INFO_X    = 785    # panel info kanan
    INFO_W    = 260
    PANEL_Y   = 72
    PANEL_H   = 580

    CARD_W    = 440
    CARD_H    = 52
    CARD_GAP  = 8
    LEVEL_H   = 128    # tinggi per level di panel antrian

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("🏥 Antrian Rumah Sakit — Priority Queue")
        self.clock = pygame.time.Clock()

        self.fxl  = pygame.font.SysFont("segoeui", 28, bold=True)
        self.flg  = pygame.font.SysFont("segoeui", 20, bold=True)
        self.fmd  = pygame.font.SysFont("segoeui", 15)
        self.fsm  = pygame.font.SysFont("segoeui", 13)
        self.fxs  = pygame.font.SysFont("segoeui", 11)
        self.fco  = pygame.font.SysFont("consolas", 12)
        self.fco2 = pygame.font.SysFont("consolas", 11)

        self.reset()

    # ── init ────────────────────────────────────────────────────────
    def reset(self):
        self.pq         = BPriorityQueue(4)
        self.cards: list[PatientCard] = []
        self.served: list[PatientCard] = []
        self.card_id    = 0

        self.demo_idx   = 0          # indeks pasien demo berikutnya
        self.auto_play  = False
        self.auto_timer = 0.0
        self.auto_delay = 1.2

        self.anim_phase = "idle"     # idle | enqueue_anim | serve_anim
        self.serve_card: PatientCard | None = None
        self.serve_t    = 0.0

        self.log: list[tuple[str, tuple]] = []
        self.global_t   = 0.0
        self.particles: list[Particle] = []

        self._log("Sistem siap. Tambah pasien atau tekan A untuk auto.", GRAY)

    def _log(self, msg, color=WHITE):
        self.log.append((msg, color))
        if len(self.log) > 10: self.log.pop(0)

    # ── enqueue pasien ──────────────────────────────────────────────
    def add_patient(self, name=None, priority=None, diagnosis=None):
        if self.anim_phase != "idle": return
        if name is None:
            if self.demo_idx >= len(DEMO_PATIENTS):
                self._log("Semua pasien demo sudah ditambahkan.", GRAY)
                return
            name, priority, diagnosis = DEMO_PATIENTS[self.demo_idx]
            self.demo_idx += 1

        card = PatientCard(name, priority, diagnosis or "-", self.card_id)
        self.card_id += 1

        # Spawn dari kanan atas, akan bergerak ke posisi di queue
        card.x = self.W + 50
        card.y = self.PANEL_Y + 20
        card.alpha = 0
        card.scale = 0.85
        card.phase = "spawning"

        self.pq.enqueue(card, priority)
        self.cards.append(card)
        self._update_card_targets()
        self._log(f"+ {name} ({P_LABELS[priority]}) masuk antrian", P_COLORS[priority])

    def _update_card_targets(self):
        """Hitung posisi target semua card berdasarkan snapshot queue."""
        snap = self.pq.snapshot()
        for lvl, items in enumerate(snap):
            level_y = self.PANEL_Y + 10 + lvl * self.LEVEL_H + 42
            for pos, card in enumerate(items):
                card.target_x = float(self.QUEUE_X + 14)
                card.target_y = float(level_y + pos * (self.CARD_H + self.CARD_GAP))

    # ── dequeue (layani) pasien ─────────────────────────────────────
    def serve_next(self):
        if self.anim_phase != "idle": return
        if self.pq.isEmpty():
            self._log("Antrian kosong!", GRAY)
            return

        card = self.pq.dequeue()
        card.phase = "serving"
        self.serve_card = card
        self.serve_t    = 0.0
        self.anim_phase = "serve_anim"
        self._update_card_targets()
        self._log(f"✓ Melayani: {card.name} ({P_LABELS[card.priority]})", card.color)

        # Spawn particles
        for _ in range(30):
            self.particles.append(Particle(card.x + self.CARD_W//2,
                                           card.y + self.CARD_H//2, card.color))

    # ── update ──────────────────────────────────────────────────────
    def update(self, dt):
        self.global_t += dt

        # Auto-play
        if self.auto_play and self.anim_phase == "idle":
            self.auto_timer += dt
            if self.auto_timer >= self.auto_delay:
                self.auto_timer = 0.0
                if self.demo_idx < len(DEMO_PATIENTS) and len(self.pq.total and [] or self.cards) < 10:
                    # Tambah dulu beberapa, lalu serve bergantian
                    if self.demo_idx < len(DEMO_PATIENTS) and (self.pq.isEmpty() or self.demo_idx % 3 != 0):
                        self.add_patient()
                    else:
                        self.serve_next()
                else:
                    self.serve_next()

        # Update serve animation
        if self.anim_phase == "serve_anim":
            self.serve_t += dt * 2.2
            if self.serve_t >= 1.0:
                if self.serve_card:
                    self.serve_card.phase = "done"
                    self.served.append(self.serve_card)
                    self.serve_card = None
                self.anim_phase = "idle"

        # Update cards
        for card in self.cards:
            if card.phase == "done": continue

            if card.phase == "serving":
                # Animasi card bergerak ke area pelayanan (kanan)
                t = ease_out(min(1.0, self.serve_t))
                target_x = self.INFO_X + 10.0
                target_y = self.PANEL_Y + 60.0
                card.x = lerp(card.x, target_x, t * 0.15 + 0.05)
                card.y = lerp(card.y, target_y, t * 0.15 + 0.05)
                card.alpha = lerp(card.alpha, 0, t * 0.08)
                card.scale = lerp(card.scale, 1.2, t * 0.05)
                continue

            # Spawning → idle
            if card.phase == "spawning":
                card.t += dt * 3.0
                if card.t >= 1.0:
                    card.phase = "idle"
                    card.t = 0.0
                t = ease_out(min(1.0, card.t))
                card.alpha = lerp(0, 255, t)
                card.scale = lerp(0.75, 1.0, t)
            else:
                card.scale = lerp(card.scale, 1.0, 0.12)
                card.alpha = lerp(card.alpha, 255, 0.12)

            # Smooth move ke target
            card.x = lerp(card.x, card.target_x, 0.12)
            card.y = lerp(card.y, card.target_y, 0.12)

        # Particles
        for p in self.particles[:]:
            p.update(dt)
            if p.life <= 0:
                self.particles.remove(p)

    # ── draw ────────────────────────────────────────────────────────
    def draw(self):
        self.screen.fill(BG)
        self._draw_header()
        self._draw_queue_panel()
        self._draw_code_panel()
        self._draw_info_panel()
        self._draw_cards()
        self._draw_particles()
        self._draw_log()
        self._draw_controls()
        pygame.display.flip()

    def _draw_header(self):
        txt(self.screen, "🏥  Antrian Rumah Sakit — Bounded Priority Queue",
            self.flg, WHITE, self.W//2, 14, "midtop")
        sub = f"4 Level Prioritas  |  Pasien: {self.pq.total()}  |  Sudah dilayani: {len(self.served)}"
        txt(self.screen, sub, self.fsm, GRAY, self.W//2, 44, "midtop")

    # ── panel antrian ────────────────────────────────────────────────
    def _draw_queue_panel(self):
        rr(self.screen, BG2, (self.QUEUE_X, self.PANEL_Y, self.QUEUE_W, self.PANEL_H), r=18)
        txt(self.screen, "📋  Antrian Prioritas", self.fmd, CYAN,
            self.QUEUE_X+16, self.PANEL_Y+12)

        level_labels = [
            ("0  KRITIS",   P_COLORS[0]),
            ("1  DARURAT",  P_COLORS[1]),
            ("2  MENENGAH", P_COLORS[2]),
            ("3  RINGAN",   P_COLORS[3]),
        ]
        for lvl, (label, col) in enumerate(level_labels):
            ly = self.PANEL_Y + 10 + lvl * self.LEVEL_H + 36
            # Level strip
            rr(self.screen, P_DIM[lvl], (self.QUEUE_X+10, ly, self.QUEUE_W-20, self.LEVEL_H-14), r=10)
            pygame.draw.rect(self.screen, col,
                             (self.QUEUE_X+10, ly, 4, self.LEVEL_H-14), border_radius=2)

            # Icon + label
            txt(self.screen, P_ICONS[lvl], self.fmd, col,
                self.QUEUE_X+20, ly+6)
            txt(self.screen, label, self.fsm, col,
                self.QUEUE_X+44, ly+8)

            # Count badge
            count = len(self.pq.snapshot()[lvl])
            bc    = col if count else DIM
            rr(self.screen, lerpc(BG2, col, 0.2),
               (self.QUEUE_X + self.QUEUE_W - 60, ly+4, 44, 22), r=11)
            txt(self.screen, f"{count} pasien", self.fxs, bc,
                self.QUEUE_X + self.QUEUE_W - 38, ly+13, "center")

            # Empty hint
            if count == 0:
                txt(self.screen, "— kosong —", self.fxs, DIM,
                    self.QUEUE_X+22, ly+38, "topleft")

    # ── panel kode ───────────────────────────────────────────────────
    def _draw_code_panel(self):
        rr(self.screen, BG2, (self.CODE_X, self.PANEL_Y, self.CODE_W, self.PANEL_H), r=18)
        txt(self.screen, "💻  Kode", self.fmd, PURPLE, self.CODE_X+14, self.PANEL_Y+12)

        is_enqueue = self.anim_phase == "idle" and self.demo_idx > 0
        is_serve   = self.anim_phase == "serve_anim"
        is_done    = self.pq.isEmpty() and len(self.served) > 0

        def code_line(text, color, highlight=False, indent=0):
            return (text, color, highlight, indent)

        lines = [
            code_line("class BPriorityQueue:", PURPLE),
            code_line("  def __init__(self, n):", GRAY),
            code_line("    self._q = [", GRAY),
            code_line("      deque() for _", DIM),
            code_line("      in range(n)]", DIM),
            code_line("", WHITE),
            code_line("  def enqueue(self,", GRAY),
            code_line("      item, pri):", GRAY),
            code_line("    self._q[pri]", CYAN, is_enqueue),
            code_line("      .append(item)", CYAN, is_enqueue),
            code_line("", WHITE),
            code_line("  def dequeue(self):", GRAY),
            code_line("    for q in self._q:", GREEN, is_serve),
            code_line("      if q:", GREEN, is_serve),
            code_line("        return", GREEN, is_serve),
            code_line("          q.popleft()", GREEN, is_serve),
            code_line("", WHITE),
            code_line("# Main:", GRAY),
            code_line("pq = BPriorityQueue(4)", WHITE),
            code_line("", WHITE),
            code_line("pq.enqueue(name, pri)", CYAN, is_enqueue),
            code_line("", WHITE),
            code_line("while not pq.isEmpty():", WHITE, is_done),
            code_line("  pq.dequeue()", GREEN, is_serve),
        ]

        ly = self.PANEL_Y + 38
        for (text, color, highlight, *_) in lines:
            if not text:
                ly += 8; continue
            if highlight:
                rr(self.screen, lerpc(BG2, color, 0.15),
                   (self.CODE_X+6, ly-2, self.CODE_W-12, 17), r=4)
                rr(self.screen, color, (self.CODE_X+6, ly-2, 3, 17), r=2)
            txt(self.screen, text, self.fco, color if highlight else (color if color != GRAY else DIM),
                self.CODE_X+14, ly)
            ly += 18

    # ── panel info ───────────────────────────────────────────────────
    def _draw_info_panel(self):
        rr(self.screen, BG2, (self.INFO_X, self.PANEL_Y, self.INFO_W, self.PANEL_H), r=18)
        txt(self.screen, "📊  Statistik", self.fmd, TEAL, self.INFO_X+14, self.PANEL_Y+12)

        # Stat cards
        stats = [
            ("Total masuk", str(self.card_id), CYAN),
            ("Dilayani",    str(len(self.served)), GREEN),
            ("Menunggu",    str(self.pq.total()), YELLOW if self.pq.total() else GRAY),
        ]
        sy = self.PANEL_Y + 42
        sw = (self.INFO_W - 32) // 3
        for i, (label, val, col) in enumerate(stats):
            sx = self.INFO_X + 10 + i * (sw + 6)
            rr(self.screen, CARD, (sx, sy, sw, 56), r=10)
            txt(self.screen, val,   self.flg, col,  sx + sw//2, sy+16, "midtop")
            txt(self.screen, label, self.fxs, GRAY, sx + sw//2, sy+40, "midtop")
        sy += 64

        # Priority breakdown bar
        txt(self.screen, "Distribusi prioritas:", self.fxs, GRAY, self.INFO_X+12, sy+4)
        sy += 22
        snap  = self.pq.snapshot()
        total = max(1, self.pq.total())
        bar_w = self.INFO_W - 24
        bx    = self.INFO_X + 12
        segments = []
        for lvl in range(4):
            c = len(snap[lvl])
            if c: segments.append((c, P_COLORS[lvl], P_LABELS[lvl]))
        if segments:
            cx2 = bx
            for count, col, label in segments:
                w2 = int(bar_w * count / total)
                rr(self.screen, col, (cx2, sy, max(4, w2), 18), r=4)
                cx2 += w2 + 2
        else:
            rr(self.screen, DIM, (bx, sy, bar_w, 18), r=4)
        sy += 26

        # Legend
        for lvl in range(4):
            c = len(snap[lvl])
            pygame.draw.circle(self.screen, P_COLORS[lvl], (self.INFO_X+18, sy+6), 5)
            txt(self.screen, f"{P_LABELS[lvl]}: {c}", self.fxs,
                P_COLORS[lvl] if c else DIM, self.INFO_X+28, sy+1)
            sy += 17
        sy += 10

        # Separator
        pygame.draw.line(self.screen, LINE,
                         (self.INFO_X+10, sy), (self.INFO_X+self.INFO_W-10, sy), 1)
        sy += 10

        # Sedang dilayani
        txt(self.screen, "🩺  Sedang dilayani:", self.fxs, GRAY, self.INFO_X+12, sy)
        sy += 20
        if self.serve_card:
            sc = self.serve_card
            rr(self.screen, P_DIM[sc.priority],
               (self.INFO_X+10, sy, self.INFO_W-20, 58), r=10,
               border=2, border_color=sc.color)
            txt(self.screen, sc.name, self.fmd, sc.color, self.INFO_X+18, sy+8)
            txt(self.screen, sc.label, self.fxs, sc.color, self.INFO_X+18, sy+28)
            txt(self.screen, sc.diagnosis[:26], self.fxs, GRAY, self.INFO_X+18, sy+42)
            sy += 66
        else:
            rr(self.screen, CARD, (self.INFO_X+10, sy, self.INFO_W-20, 38), r=8)
            txt(self.screen, "— menunggu —", self.fxs, DIM,
                self.INFO_X + self.INFO_W//2, sy+19, "center")
            sy += 46

        sy += 6
        # Riwayat layanan
        txt(self.screen, "✅  Riwayat dilayani:", self.fxs, GRAY, self.INFO_X+12, sy)
        sy += 18
        for sc in reversed(self.served[-8:]):
            rr(self.screen, P_DIM[sc.priority],
               (self.INFO_X+10, sy, self.INFO_W-20, 22), r=6)
            pygame.draw.circle(self.screen, sc.color, (self.INFO_X+20, sy+11), 4)
            txt(self.screen, sc.name, self.fxs, sc.color, self.INFO_X+30, sy+6)
            txt(self.screen, P_LABELS[sc.priority], self.fxs, GRAY,
                self.INFO_X + self.INFO_W - 14, sy+6, "topright")
            sy += 26

    # ── gambar kartu pasien ──────────────────────────────────────────
    def _draw_cards(self):
        # Gambar semua card kecuali yang done
        t = self.global_t
        for card in self.cards:
            if card.phase == "done": continue
            self._draw_one_card(card, t)

    def _draw_one_card(self, card, t):
        x, y = int(card.x), int(card.y)
        w, h = self.CARD_W, self.CARD_H
        col  = card.color
        alpha= int(min(255, card.alpha))
        s    = card.scale

        # Scale transform
        sw = int(w * s)
        sh = int(h * s)
        ox = x + (w - sw)//2
        oy = y + (h - sh)//2

        # Card surface
        surf = pygame.Surface((sw, sh), pygame.SRCALPHA)

        # Background
        pygame.draw.rect(surf, (*P_DIM[card.priority], alpha),
                         (0, 0, sw, sh), border_radius=10)
        pygame.draw.rect(surf, (*col, min(255, int(alpha*0.9))),
                         (0, 0, sw, sh), 1, border_radius=10)

        # Left accent bar
        pygame.draw.rect(surf, (*col, alpha), (0, 0, 5, sh), border_radius=2)

        # Priority badge
        badge_col = lerpc(P_DIM[card.priority], col, 0.4)
        pygame.draw.rect(surf, (*badge_col, alpha),
                         (sw-90, 6, 82, 20), border_radius=10)
        label_surf = self.fxs.render(card.label, True, col)
        surf.blit(label_surf, (sw-88, 9))

        # Name
        nf = self.fmd.render(card.name, True, WHITE)
        surf.blit(nf, (14, 8))

        # Diagnosis
        diag = card.diagnosis[:32]
        df = self.fxs.render(diag, True, (*GRAY, alpha))
        surf.blit(df, (14, 30))

        # Arrival order indicator
        idf = self.fxs.render(f"#{card.id+1}", True, (*GRAY, alpha))
        surf.blit(idf, (sw-94, 30))

        self.screen.blit(surf, (ox, oy))

        # Glow pada card paling depan
        snap = self.pq.snapshot()
        front = snap[card.priority][0] if snap[card.priority] else None
        if front is card and card.phase == "idle":
            pulse = 0.5 + 0.5 * math.sin(t * 4)
            glow(self.screen, col, x + w//2, y + h//2, 32, int(40 * pulse))

    def _draw_particles(self):
        for p in self.particles:
            p.draw(self.screen)

    def _draw_log(self):
        lx, ly = self.QUEUE_X, self.PANEL_Y + self.PANEL_H + 10
        for msg, col in self.log[-3:]:
            if len(msg) > 70: msg = msg[:69] + "…"
            txt(self.screen, msg, self.fxs, col, lx, ly)
            ly += 16

    def _draw_controls(self):
        cy2 = self.H - 22
        controls = [
            ("SPACE", "Tambah pasien demo"),
            ("S",     "Layani pasien"),
            ("A",     "Auto-play"),
            ("1/2/3/4", "Tambah prioritas tertentu"),
            ("R",     "Reset"),
            ("ESC",   "Keluar"),
        ]
        cx2 = self.W - 20
        for key, desc in reversed(controls):
            full = f"[{key}] {desc}"
            surf = self.fxs.render(full, True, GRAY)
            self.screen.blit(surf, (cx2 - surf.get_width(), cy2))
            cx2 -= surf.get_width() + 24

        # Auto indicator
        if self.auto_play:
            rr(self.screen, (15, 60, 35),
               (self.W - 130, cy2 - 4, 115, 20), r=10)
            txt(self.screen, "● AUTO-PLAY ON", self.fxs, GREEN,
                self.W - 72, cy2 + 2, "center")

    # ── main loop ────────────────────────────────────────────────────
    def run(self):
        prev = time.time()
        # Pre-load beberapa pasien
        for i in range(5):
            self.add_patient()

        while True:
            now = time.time()
            dt  = min(now - prev, 0.05)
            prev = now

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    k = event.key
                    if k == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                    elif k == pygame.K_r:
                        self.reset()
                    elif k == pygame.K_SPACE:
                        self.add_patient()
                    elif k == pygame.K_s:
                        self.serve_next()
                    elif k == pygame.K_a:
                        self.auto_play = not self.auto_play
                        self.auto_timer = 0.0
                    elif k == pygame.K_1:
                        names = ["Pasien-Kritis", "Darurat-A", "Darurat-B"]
                        n = random.choice(names) + str(random.randint(1,99))
                        self.add_patient(n, 0, "Kondisi kritis")
                    elif k == pygame.K_2:
                        self.add_patient("Pasien-Darurat"+str(random.randint(1,99)),
                                         1, "Darurat segera")
                    elif k == pygame.K_3:
                        self.add_patient("Pasien-Sedang"+str(random.randint(1,99)),
                                         2, "Perlu perhatian")
                    elif k == pygame.K_4:
                        self.add_patient("Pasien-Ringan"+str(random.randint(1,99)),
                                         3, "Kondisi ringan")

            self.update(dt)
            self.draw()
            self.clock.tick(60)


# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    viz = HospitalPQViz()
    viz.run()