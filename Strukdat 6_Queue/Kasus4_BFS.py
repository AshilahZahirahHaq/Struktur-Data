"""
🔍 BFS (Breadth-First Search) — Visualisasi Animasi Pygame
Pencarian jalur level-demi-level menggunakan Queue (FIFO)
"""

import pygame, sys, time, math, random
from collections import deque

# ═══════════════════════════════════════════════════════════════════
# WARNA
# ═══════════════════════════════════════════════════════════════════
BG        = (10,  13,  22)
BG2       = (16,  20,  34)
CARD      = (22,  28,  46)
CARD2     = (30,  38,  60)
LINE_COL  = (38,  46,  72)
WHITE     = (232, 236, 248)
GRAY      = (100, 110, 140)
DIM       = (50,  58,  85)

CYAN      = (56,  189, 248)
GREEN     = (52,  211, 153)
YELLOW    = (250, 204,  21)
ORANGE    = (251, 146,  60)
PURPLE    = (167, 139, 250)
RED       = (248,  80,  80)
PINK      = (244, 114, 182)
TEAL      = (45,  212, 191)

# Warna state node
COL_UNVISITED = (38,  46,  72)
COL_IN_QUEUE  = (167, 139, 250)   # ungu — di dalam queue
COL_CURRENT   = (250, 204,  21)   # kuning — sedang diproses
COL_VISITED   = (52,  211, 153)   # hijau  — sudah dikunjungi
COL_PATH      = (56,  189, 248)   # cyan   — jalur terpendek
COL_TARGET    = (248,  80,  80)   # merah  — node target

# Warna per level BFS
LEVEL_COLORS = [
    (56,  189, 248),   # L0 — start (cyan)
    (52,  211, 153),   # L1 (hijau)
    (250, 204,  21),   # L2 (kuning)
    (251, 146,  60),   # L3 (oranye)
    (244, 114, 182),   # L4 (pink)
    (167, 139, 250),   # L5 (ungu)
    (45,  212, 191),   # L6 (teal)
]

# ═══════════════════════════════════════════════════════════════════
# QUEUE
# ═══════════════════════════════════════════════════════════════════
class Queue:
    def __init__(self):
        self._q = deque()

    def enqueue(self, item):
        self._q.append(item)

    def dequeue(self):
        return self._q.popleft()

    def isEmpty(self):
        return len(self._q) == 0

    def to_list(self):
        return list(self._q)

    def __len__(self):
        return len(self._q)


# ═══════════════════════════════════════════════════════════════════
# GRAF
# ═══════════════════════════════════════════════════════════════════
GRAPHS = {
    "Kota": {
        "nodes": {
            "A": (320, 100),
            "B": (180, 220),
            "C": (460, 220),
            "D": (100, 350),
            "E": (280, 350),
            "F": (400, 350),
            "G": (540, 350),
            "H": (160, 480),
            "I": (360, 480),
            "J": (500, 480),
        },
        "edges": [
            ("A","B"),("A","C"),
            ("B","D"),("B","E"),
            ("C","F"),("C","G"),
            ("D","H"),
            ("E","H"),("E","I"),
            ("F","I"),("F","J"),
            ("G","J"),
        ],
        "start": "A",
        "target": "J",
    },
    "Jaringan": {
        "nodes": {
            "S": (280,  90),
            "1": (140, 210),
            "2": (280, 210),
            "3": (420, 210),
            "4": (80,  340),
            "5": (210, 340),
            "6": (350, 340),
            "7": (480, 340),
            "T": (280, 460),
        },
        "edges": [
            ("S","1"),("S","2"),("S","3"),
            ("1","4"),("1","5"),
            ("2","5"),("2","6"),
            ("3","6"),("3","7"),
            ("4","T"),("5","T"),("6","T"),("7","T"),
        ],
        "start": "S",
        "target": "T",
    },
    "Sosial": {
        "nodes": {
            "Aku":   (290,  95),
            "Ali":   (140, 205),
            "Budi":  (440, 205),
            "Cici":  ( 70, 330),
            "Dani":  (220, 330),
            "Eva":   (360, 330),
            "Fani":  (500, 330),
            "Gina":  (145, 455),
            "Hadi":  (310, 455),
            "Ilham": (460, 455),
        },
        "edges": [
            ("Aku","Ali"),("Aku","Budi"),
            ("Ali","Cici"),("Ali","Dani"),
            ("Budi","Eva"),("Budi","Fani"),
            ("Cici","Gina"),
            ("Dani","Gina"),("Dani","Hadi"),
            ("Eva","Hadi"),("Eva","Ilham"),
            ("Fani","Ilham"),
        ],
        "start": "Aku",
        "target": "Ilham",
    },
}

# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════
def lerp(a, b, t):     return a + (b - a) * t
def ease_out(t):       return 1 - (1-t)**3
def ease_in_out(t):    return t*t*(3-2*t)
def lerpc(c1,c2,t):
    t = max(0, min(1, t))
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))

def rr(surf, color, rect, r=10, alpha=255, border=0, bc=None):
    if alpha < 255:
        s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, alpha), (0,0,rect[2],rect[3]), border_radius=r)
        surf.blit(s, (rect[0], rect[1]))
    else:
        pygame.draw.rect(surf, color, rect, border_radius=r)
    if border and bc:
        pygame.draw.rect(surf, bc, rect, border, border_radius=r)

def txt(surf, text, font, color, x, y, anchor="topleft"):
    r = font.render(str(text), True, color)
    rc = r.get_rect()
    setattr(rc, anchor, (x, y))
    surf.blit(r, rc)

def glow_circle(surf, color, cx, cy, radius, strength=80):
    s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    for ri in range(radius, 0, -3):
        a = int(strength * (ri/radius)**2.2)
        pygame.draw.circle(s, (*color, min(255,a)), (radius,radius), ri)
    surf.blit(s, (cx-radius, cy-radius))

def draw_arrow_line(surf, color, p1, p2, width=2):
    """Garis dengan panah di tengah."""
    pygame.draw.line(surf, color, p1, p2, width)
    mx = (p1[0]+p2[0])//2
    my = (p1[1]+p2[1])//2
    ang = math.atan2(p2[1]-p1[1], p2[0]-p1[0])
    size = 7
    pts = [
        (mx + size*math.cos(ang),   my + size*math.sin(ang)),
        (mx + size*math.cos(ang+2.4), my + size*math.sin(ang+2.4)),
        (mx + size*math.cos(ang-2.4), my + size*math.sin(ang-2.4)),
    ]
    pygame.draw.polygon(surf, color, [(int(p[0]),int(p[1])) for p in pts])


# ═══════════════════════════════════════════════════════════════════
# PARTIKEL
# ═══════════════════════════════════════════════════════════════════
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = float(x), float(y)
        ang = random.uniform(0, math.pi*2)
        spd = random.uniform(60, 180)
        self.vx = math.cos(ang)*spd
        self.vy = math.sin(ang)*spd
        self.color = color
        self.life = 1.0
        self.size = random.randint(2, 5)

    def update(self, dt):
        self.x += self.vx*dt; self.vy += 150*dt
        self.y += self.vy*dt; self.life -= dt*2

    def draw(self, surf):
        if self.life <= 0: return
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, int(255*self.life)),
                           (self.size,self.size), self.size)
        surf.blit(s, (int(self.x)-self.size, int(self.y)-self.size))


# ═══════════════════════════════════════════════════════════════════
# ANIMASI EDGE (sorot edge saat BFS traverse)
# ═══════════════════════════════════════════════════════════════════
class EdgeAnim:
    def __init__(self, p1, p2, color):
        self.p1, self.p2 = p1, p2
        self.color = color
        self.t = 0.0
        self.done = False

    def update(self, dt):
        self.t = min(1.0, self.t + dt * 3.5)
        if self.t >= 1.0: self.done = True

    def draw(self, surf):
        t = ease_out(self.t)
        ex = lerp(self.p1[0], self.p2[0], t)
        ey = lerp(self.p1[1], self.p2[1], t)
        pygame.draw.line(surf, self.color, self.p1, (int(ex),int(ey)), 3)


# ═══════════════════════════════════════════════════════════════════
# BFS STEP-BY-STEP ENGINE
# ═══════════════════════════════════════════════════════════════════
class BFSEngine:
    def __init__(self, graph_data):
        self.graph_data = graph_data
        self.reset()

    def reset(self):
        gd = self.graph_data
        # Build adjacency
        self.adj = {n: [] for n in gd["nodes"]}
        for u, v in gd["edges"]:
            self.adj[u].append(v)
            self.adj[v].append(u)

        self.start   = gd["start"]
        self.target  = gd["target"]

        self.queue   = Queue()
        self.visited = set()
        self.parent  = {}
        self.level   = {}
        self.state   = {}   # node -> "unvisited"|"in_queue"|"current"|"visited"
        self.current_node   = None
        self.path    = []
        self.found   = False
        self.done    = False
        self.steps   = []   # log langkah
        self.step_count = 0

        for n in self.adj:
            self.state[n] = "unvisited"

        # Init BFS
        self.queue.enqueue(self.start)
        self.visited.add(self.start)
        self.level[self.start] = 0
        self.state[self.start] = "in_queue"
        self.parent[self.start] = None
        self._log(f"Mulai dari '{self.start}' — masuk queue", CYAN)

    def _log(self, msg, color=WHITE):
        self.steps.append((msg, color))
        if len(self.steps) > 12: self.steps.pop(0)

    def step(self):
        """Lakukan satu langkah BFS. Kembalikan (node, neighbors_added, edge_anims)."""
        if self.done or self.queue.isEmpty():
            self.done = True
            return None, [], []

        node = self.queue.dequeue()
        self.current_node = node
        self.state[node] = "current"
        self.step_count += 1
        lvl = self.level.get(node, 0)
        self._log(f"dequeue '{node}' (level {lvl})", LEVEL_COLORS[lvl % len(LEVEL_COLORS)])

        new_neighbors = []
        edge_anims    = []
        gd = self.graph_data

        for nb in self.adj[node]:
            if nb not in self.visited:
                self.visited.add(nb)
                self.queue.enqueue(nb)
                self.parent[nb] = node
                self.level[nb]  = lvl + 1
                self.state[nb]  = "in_queue"
                new_neighbors.append(nb)

                p1 = gd["nodes"][node]
                p2 = gd["nodes"][nb]
                col = LEVEL_COLORS[(lvl+1) % len(LEVEL_COLORS)]
                edge_anims.append(EdgeAnim(p1, p2, col))
                self._log(f"  enqueue '{nb}' (level {lvl+1})", col)

        if node == self.target:
            self.found = True
            self.done  = True
            # Reconstruct path
            p = node
            while p is not None:
                self.path.append(p)
                p = self.parent.get(p)
            self.path.reverse()
            self._log(f"🎯 Target '{self.target}' ditemukan! Jarak: {lvl}", GREEN)
            self._log(f"   Jalur: {' → '.join(self.path)}", CYAN)
        else:
            self.state[node] = "visited"

        if self.queue.isEmpty() and not self.found:
            self.done = True
            self._log("Queue kosong — semua node terjelajahi", GRAY)

        return node, new_neighbors, edge_anims


# ═══════════════════════════════════════════════════════════════════
# MAIN VISUALIZER
# ═══════════════════════════════════════════════════════════════════
class BFSViz:
    W, H    = 1100, 700
    GRAPH_X = 30
    GRAPH_W = 580
    GRAPH_H = 580
    GRAPH_Y = 70
    # Panel kanan
    PANEL_X = 628
    PANEL_W = 455

    NODE_R  = 26

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("🔍 BFS — Breadth-First Search Visualizer")
        self.clock = pygame.time.Clock()

        self.fxl  = pygame.font.SysFont("segoeui", 26, bold=True)
        self.flg  = pygame.font.SysFont("segoeui", 19, bold=True)
        self.fmd  = pygame.font.SysFont("segoeui", 15)
        self.fsm  = pygame.font.SysFont("segoeui", 13)
        self.fxs  = pygame.font.SysFont("segoeui", 11)
        self.fco  = pygame.font.SysFont("consolas", 12)

        self.graph_names = list(GRAPHS.keys())
        self.graph_idx   = 0
        self.reset()

    def reset(self):
        gname = self.graph_names[self.graph_idx]
        self.gd     = GRAPHS[gname]
        self.engine = BFSEngine(self.gd)

        self.node_anim  = {}   # node -> animasi t [0..1]
        self.edge_anims: list[EdgeAnim] = []
        self.visited_edges = set()   # edge yang sudah diwarnai permanen
        self.particles: list[Particle] = []

        self.auto_play  = False
        self.auto_timer = 0.0
        self.auto_delay = 0.85
        self.global_t   = 0.0

        # Node scale pulse
        self.node_scale = {n: 1.0 for n in self.gd["nodes"]}
        self.node_t     = {n: 0.0  for n in self.gd["nodes"]}

        # Path flash timer
        self.path_t = 0.0

    # ── step BFS ────────────────────────────────────────────────────
    def do_step(self):
        if self.engine.done: return
        node, neighbors, edge_anims = self.engine.step()
        if node is None: return

        # Pulse animasi node saat ini
        self.node_t[node] = 0.0

        # Partikel pada node
        pos = self.gd["nodes"][node]
        col = COL_CURRENT
        for _ in range(18):
            self.particles.append(Particle(pos[0]+self.GRAPH_X,
                                           pos[1]+self.GRAPH_Y, col))

        # Edge anims baru
        for ea in edge_anims:
            p1 = (ea.p1[0]+self.GRAPH_X, ea.p1[1]+self.GRAPH_Y)
            p2 = (ea.p2[0]+self.GRAPH_X, ea.p2[1]+self.GRAPH_Y)
            self.edge_anims.append(EdgeAnim(p1, p2, ea.color))

        # Partikel hijau jika target ditemukan
        if self.engine.found:
            tpos = self.gd["nodes"][self.engine.target]
            for _ in range(40):
                self.particles.append(Particle(
                    tpos[0]+self.GRAPH_X, tpos[1]+self.GRAPH_Y, GREEN))

    # ── update ──────────────────────────────────────────────────────
    def update(self, dt):
        self.global_t += dt
        if self.engine.found:
            self.path_t += dt

        # Auto-play
        if self.auto_play and not self.engine.done:
            self.auto_timer += dt
            if self.auto_timer >= self.auto_delay:
                self.auto_timer = 0.0
                self.do_step()

        # Node pulse
        for n in self.node_t:
            if self.node_t[n] < 1.0:
                self.node_t[n] = min(1.0, self.node_t[n] + dt * 4)

        # Edge anims
        for ea in self.edge_anims[:]:
            ea.update(dt)
            if ea.done:
                self.edge_anims.remove(ea)

        # Particles
        for p in self.particles[:]:
            p.update(dt)
            if p.life <= 0:
                self.particles.remove(p)

    # ── draw ────────────────────────────────────────────────────────
    def draw(self):
        self.screen.fill(BG)
        self._draw_header()
        self._draw_graph_panel()
        self._draw_right_panels()
        self._draw_particles()
        pygame.display.flip()

    def _draw_header(self):
        gname = self.graph_names[self.graph_idx]
        txt(self.screen, f"🔍  BFS — Breadth-First Search    Graf: {gname}",
            self.flg, WHITE, self.W//2, 12, "midtop")
        info = (f"Node: {len(self.gd['nodes'])}   Edge: {len(self.gd['edges'])}   "
                f"Langkah: {self.engine.step_count}   "
                f"Start: '{self.engine.start}'   Target: '{self.engine.target}'")
        txt(self.screen, info, self.fxs, GRAY, self.W//2, 40, "midtop")

    # ── panel graf ───────────────────────────────────────────────────
    def _draw_graph_panel(self):
        rr(self.screen, BG2,
           (self.GRAPH_X-5, self.GRAPH_Y-5, self.GRAPH_W+10, self.GRAPH_H+10), r=20)

        nodes = self.gd["nodes"]
        edges = self.gd["edges"]
        eng   = self.engine

        # ── Gambar semua edge (abu-abu tipis)
        for u, v in edges:
            p1 = (nodes[u][0]+self.GRAPH_X, nodes[u][1]+self.GRAPH_Y)
            p2 = (nodes[v][0]+self.GRAPH_X, nodes[v][1]+self.GRAPH_Y)
            pygame.draw.line(self.screen, LINE_COL, p1, p2, 2)

        # ── Sorot edge jalur terpendek
        if eng.found and eng.path:
            for i in range(len(eng.path)-1):
                u, v = eng.path[i], eng.path[i+1]
                p1 = (nodes[u][0]+self.GRAPH_X, nodes[u][1]+self.GRAPH_Y)
                p2 = (nodes[v][0]+self.GRAPH_X, nodes[v][1]+self.GRAPH_Y)
                pulse = 0.55 + 0.45*math.sin(self.path_t*4 + i)
                col   = lerpc(CYAN, WHITE, pulse*0.4)
                pygame.draw.line(self.screen, col, p1, p2, 4)
                # Arrow
                ang  = math.atan2(p2[1]-p1[1], p2[0]-p1[0])
                mx   = (p1[0]+p2[0])//2; my = (p1[1]+p2[1])//2
                sz   = 8
                pts  = [
                    (mx+sz*math.cos(ang),    my+sz*math.sin(ang)),
                    (mx+sz*math.cos(ang+2.5), my+sz*math.sin(ang+2.5)),
                    (mx+sz*math.cos(ang-2.5), my+sz*math.sin(ang-2.5)),
                ]
                pygame.draw.polygon(self.screen, col,
                                    [(int(x),int(y)) for x,y in pts])

        # ── Edge animasi BFS
        for ea in self.edge_anims:
            ea.draw(self.screen)

        # ── Sorot edge visited (permanen)
        for u, v in edges:
            if u in eng.visited and v in eng.visited:
                p1 = (nodes[u][0]+self.GRAPH_X, nodes[u][1]+self.GRAPH_Y)
                p2 = (nodes[v][0]+self.GRAPH_X, nodes[v][1]+self.GRAPH_Y)
                lvl = min(eng.level.get(u,0), eng.level.get(v,0))
                col = lerpc(LEVEL_COLORS[lvl % len(LEVEL_COLORS)], DIM, 0.6)
                pygame.draw.line(self.screen, col, p1, p2, 2)

        # ── Gambar node
        for node, pos in nodes.items():
            cx = pos[0]+self.GRAPH_X
            cy = pos[1]+self.GRAPH_Y
            state = eng.state.get(node, "unvisited")
            lvl   = eng.level.get(node, -1)

            # Warna berdasarkan state
            if eng.found and node in eng.path:
                base_col = COL_PATH
            elif state == "current":
                base_col = COL_CURRENT
            elif state == "in_queue":
                base_col = COL_IN_QUEUE
            elif state == "visited":
                base_col = LEVEL_COLORS[lvl % len(LEVEL_COLORS)] if lvl >= 0 else COL_VISITED
            else:
                base_col = COL_UNVISITED

            if node == eng.target and not eng.found:
                base_col = lerpc(base_col, COL_TARGET, 0.5)

            # Pulse scale
            pt = ease_in_out(self.node_t[node])
            scale = 1.0 + 0.25*(1-pt) if self.node_t[node] < 1.0 else 1.0

            # Global pulse untuk current node
            if state == "current":
                scale = 1.0 + 0.12*math.sin(self.global_t*8)
            if eng.found and node in eng.path:
                scale = 1.0 + 0.08*math.sin(self.path_t*4)

            r = int(self.NODE_R * scale)

            # Glow
            if state in ("current", "in_queue") or (eng.found and node in eng.path):
                glow_circle(self.screen, base_col, cx, cy, r+20, 60)

            # Lingkaran node
            pygame.draw.circle(self.screen, lerpc(BG2, base_col, 0.3), (cx,cy), r)
            pygame.draw.circle(self.screen, base_col, (cx,cy), r, 3)

            # Ikon target
            if node == eng.target:
                pygame.draw.circle(self.screen, lerpc(COL_TARGET, WHITE, 0.3),
                                   (cx,cy), r-8, 2)

            # Label node
            ncol = WHITE if state != "unvisited" else GRAY
            txt(self.screen, node, self.fmd, ncol, cx, cy, "center")

            # Level badge
            if lvl >= 0 and state != "unvisited":
                bx, by = cx+r-4, cy-r+4
                pygame.draw.circle(self.screen, BG2, (bx,by), 10)
                pygame.draw.circle(self.screen, base_col, (bx,by), 10, 2)
                txt(self.screen, str(lvl), self.fxs, base_col, bx, by, "center")

        # Legend state
        self._draw_graph_legend()

    def _draw_graph_legend(self):
        lx = self.GRAPH_X + 8
        ly = self.GRAPH_Y + self.GRAPH_H - 28
        items = [
            (COL_UNVISITED, "Belum"),
            (COL_IN_QUEUE,  "Di queue"),
            (COL_CURRENT,   "Proses"),
            (COL_VISITED,   "Selesai"),
            (COL_PATH,      "Jalur ✓"),
        ]
        for col, label in items:
            pygame.draw.circle(self.screen, col, (lx+6, ly+7), 6)
            pygame.draw.circle(self.screen, col, (lx+6, ly+7), 6, 2)
            txt(self.screen, label, self.fxs, GRAY, lx+16, ly+1)
            lx += len(label)*6 + 28

    # ── panel kanan ──────────────────────────────────────────────────
    def _draw_right_panels(self):
        px = self.PANEL_X
        pw = self.PANEL_W
        py = self.GRAPH_Y - 5

        # ── Queue panel
        qh = 170
        rr(self.screen, BG2, (px, py, pw, qh), r=16)
        txt(self.screen, "📋  Queue (FIFO)", self.fmd, CYAN, px+14, py+12)
        pygame.draw.line(self.screen, LINE_COL, (px+10,py+34), (px+pw-10,py+34), 1)

        q_list = self.engine.queue.to_list()
        if not q_list:
            txt(self.screen, "— kosong —", self.fxs, DIM, px+pw//2, py+75, "center")
        else:
            # Gambar node dalam queue horizontal
            item_w = min(64, (pw-28) // max(1, len(q_list)))
            qx = px + 14
            for i, node in enumerate(q_list):
                lvl = self.engine.level.get(node, 0)
                col = LEVEL_COLORS[lvl % len(LEVEL_COLORS)]
                rr(self.screen, lerpc(BG2, col, 0.2),
                   (qx, py+42, item_w-4, 44), r=8, border=2, bc=col)
                txt(self.screen, node, self.fsm, col, qx+item_w//2-2, py+54, "center")
                txt(self.screen, f"L{lvl}", self.fxs, lerpc(col, WHITE, 0.4),
                    qx+item_w//2-2, py+72, "center")
                # Panah ke item berikutnya
                if i < len(q_list)-1:
                    ax = qx + item_w - 4
                    ay = py + 64
                    pygame.draw.polygon(self.screen, DIM,
                                        [(ax,ay-4),(ax+8,ay),(ax,ay+4)])
                qx += item_w

        # Keterangan front/back
        if q_list:
            txt(self.screen, "← front (dequeue)", self.fxs, GRAY, px+14, py+qh-22)
            txt(self.screen, "back (enqueue) →", self.fxs, GRAY,
                px+pw-14, py+qh-22, "topright")

        # ── Level panel
        py2 = py + qh + 10
        lh  = 185
        rr(self.screen, BG2, (px, py2, pw, lh), r=16)
        txt(self.screen, "🌊  Eksplorasi Level demi Level", self.fmd, PURPLE, px+14, py2+12)
        pygame.draw.line(self.screen, LINE_COL, (px+10,py2+34), (px+pw-10,py2+34), 1)

        # Grup node per level
        level_groups: dict[int, list] = {}
        for node, lvl in self.engine.level.items():
            if self.engine.state.get(node,"unvisited") != "unvisited":
                level_groups.setdefault(lvl, []).append(node)

        ly2 = py2 + 44
        for lvl in sorted(level_groups.keys()):
            nodes_in_lvl = level_groups[lvl]
            col = LEVEL_COLORS[lvl % len(LEVEL_COLORS)]
            # Bar
            bar_full = pw - 28
            bar_fill = min(bar_full, len(nodes_in_lvl)*28)
            rr(self.screen, lerpc(BG2, col, 0.12),
               (px+14, ly2, bar_full, 26), r=6)
            rr(self.screen, lerpc(BG2, col, 0.35),
               (px+14, ly2, bar_fill, 26), r=6)
            pygame.draw.rect(self.screen, col,
                             (px+14, ly2, 4, 26), border_radius=2)
            txt(self.screen, f"L{lvl}", self.fxs, col, px+22, ly2+7)
            nodes_str = "  ".join(nodes_in_lvl)
            txt(self.screen, nodes_str, self.fsm, WHITE, px+46, ly2+7)
            txt(self.screen, f"({len(nodes_in_lvl)})", self.fxs, GRAY,
                px+pw-16, ly2+7, "topright")
            ly2 += 32

        if not level_groups:
            txt(self.screen, "Mulai BFS untuk melihat level...", self.fxs, DIM,
                px+pw//2, py2+90, "center")

        # ── Kode panel
        py3 = py2 + lh + 10
        ch  = 188
        rr(self.screen, BG2, (px, py3, pw, ch), r=16)
        txt(self.screen, "💻  Kode BFS", self.fmd, YELLOW, px+14, py3+12)
        pygame.draw.line(self.screen, LINE_COL, (px+10,py3+34), (px+pw-10,py3+34), 1)

        eng = self.engine
        is_dequeue = eng.step_count > 0
        is_enqueue = eng.step_count > 0
        is_done    = eng.done

        code_lines = [
            ("def bfs(graph, start, target):", WHITE,       False),
            ("  visited = set()", GRAY,                     False),
            ("  queue = Queue()", GRAY,                     False),
            ("  queue.enqueue(start)", CYAN,                eng.step_count==0),
            ("  visited.add(start)", CYAN,                  eng.step_count==0),
            ("  while not queue.isEmpty():", WHITE,         not is_done),
            ("    node = queue.dequeue()", YELLOW,          is_dequeue and not is_done),
            ("    print(node)  # proses", YELLOW,           is_dequeue and not is_done),
            ("    for nb in graph[node]:", GREEN,           is_enqueue),
            ("      if nb not in visited:", GREEN,          is_enqueue),
            ("        visited.add(nb)", GREEN,              is_enqueue),
            ("        queue.enqueue(nb)", GREEN,            is_enqueue),
            ("  # Jalur terpendek ditemukan!", CYAN,        is_done and eng.found),
        ]

        ly3 = py3 + 42
        for (line, col, hl) in code_lines:
            if hl:
                rr(self.screen, lerpc(BG2, col, 0.12),
                   (px+6, ly3-2, pw-12, 17), r=4)
                rr(self.screen, col, (px+6, ly3-2, 3, 17), r=2)
            fc = col if hl else DIM
            txt(self.screen, line, self.fco, fc, px+14, ly3)
            ly3 += 17

        # ── Log panel
        py4 = py3 + ch + 10
        log_h = self.H - py4 - 10
        if log_h > 50:
            rr(self.screen, BG2, (px, py4, pw, log_h), r=16)
            txt(self.screen, "📜  Log", self.fmd, GRAY, px+14, py4+10)
            pygame.draw.line(self.screen, LINE_COL,
                             (px+10,py4+30),(px+pw-10,py4+30),1)
            ly4 = py4 + 38
            visible = max(1, (log_h-44)//17)
            for msg, col in self.engine.steps[-visible:]:
                if len(msg) > 55: msg = msg[:54]+"…"
                txt(self.screen, msg, self.fxs, col, px+12, ly4)
                ly4 += 17

        # ── Tombol graf
        self._draw_graph_buttons()
        # ── Kontrol
        self._draw_controls()
        # ── Hasil
        if eng.done and eng.found:
            self._draw_result_banner()

    def _draw_graph_buttons(self):
        bx = self.PANEL_X
        by = self.H - 46
        txt(self.screen, "Graf:", self.fxs, GRAY, bx, by+6)
        bx += 36
        for i, gname in enumerate(self.graph_names):
            active = (i == self.graph_idx)
            col = CYAN if active else GRAY
            rr(self.screen, lerpc(BG2, CYAN, 0.2) if active else CARD,
               (bx, by, 70, 24), r=8, border=1, bc=col)
            txt(self.screen, gname, self.fxs, col, bx+35, by+12, "center")
            bx += 76

    def _draw_controls(self):
        cy2 = self.H - 20
        items = [
            ("SPACE", "Langkah"),("A","Auto"),("R","Reset"),
            ("←/→","Ganti graf"),("ESC","Keluar"),
        ]
        cx2 = self.W - 10
        for key, desc in reversed(items):
            s = self.fxs.render(f"[{key}] {desc}", True, GRAY)
            cx2 -= s.get_width()
            self.screen.blit(s, (cx2, cy2))
            cx2 -= 18
        if self.auto_play:
            s = self.fxs.render("● AUTO ON", True, GREEN)
            self.screen.blit(s, (self.PANEL_X, cy2))

    def _draw_result_banner(self):
        eng  = self.engine
        path = " → ".join(eng.path)
        dist = len(eng.path)-1
        bx   = self.GRAPH_X
        by   = self.GRAPH_Y + self.GRAPH_H - 58
        bw   = self.GRAPH_W
        pulse= 0.5 + 0.5*math.sin(self.path_t*3)
        col  = lerpc(CYAN, GREEN, pulse)
        rr(self.screen, lerpc(BG2, col, 0.18), (bx, by, bw, 52), r=12,
           border=2, bc=col)
        txt(self.screen, f"🎯 Jalur terpendek ditemukan! Jarak: {dist} edge",
            self.fsm, col, bx+bw//2, by+10, "center")
        if len(path) <= 55:
            txt(self.screen, path, self.fmd, WHITE, bx+bw//2, by+30, "center")
        else:
            txt(self.screen, path[:55]+"…", self.fxs, WHITE, bx+bw//2, by+32, "center")

    def _draw_particles(self):
        for p in self.particles:
            p.draw(self.screen)

    # ── main loop ────────────────────────────────────────────────────
    def run(self):
        prev = time.time()
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
                        self.do_step()
                    elif k == pygame.K_a:
                        self.auto_play = not self.auto_play
                        self.auto_timer = 0.0
                    elif k == pygame.K_RIGHT:
                        self.graph_idx = (self.graph_idx+1) % len(self.graph_names)
                        self.reset()
                    elif k == pygame.K_LEFT:
                        self.graph_idx = (self.graph_idx-1) % len(self.graph_names)
                        self.reset()

            self.update(dt)
            self.draw()
            self.clock.tick(60)


# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    viz = BFSViz()
    viz.run()