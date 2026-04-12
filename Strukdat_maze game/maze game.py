import tkinter as tk
from tkinter import ttk
import random
import math
from collections import deque

COLS     = 20
ROWS     = 15
CS       = 32        # ukuran sel (pixel)
M        = 14        # margin

W = COLS * CS + M * 2
H = ROWS * CS + M * 2

# Warna
C_BG      = "#1a1a2e"
C_OPEN    = "#0d2137"
C_WALL    = "#0f3460"
C_VISIT   = "#3d3060"   # sel dieksplorasi
C_PATH    = "#0f5040"   # jalur solusi
C_BORDER  = "#1D9E75"

class MazeModel:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.walls = [
            {'N': True, 'S': True, 'E': True, 'W': True}
            for _ in range(rows * cols)
        ]

    def idx(self, r, c):
        return r * self.cols + c

    def remove_wall(self, r, c, d):
        opp = {'N':'S','S':'N','E':'W','W':'E'}
        dr  = {'N':-1,'S':1,'E':0,'W':0}
        dc  = {'N':0,'S':0,'E':1,'W':-1}
        self.walls[self.idx(r,c)][d] = False
        nr, nc = r+dr[d], c+dc[d]
        if 0 <= nr < self.rows and 0 <= nc < self.cols:
            self.walls[self.idx(nr,nc)][opp[d]] = False

    def neighbors(self, r, c):
        result = []
        for d, dr, dc in [('N',-1,0),('S',1,0),('E',0,1),('W',0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                result.append((d, nr, nc))
        return result

    def open_neighbors(self, r, c):
        result = []
        for d, nr, nc in self.neighbors(r, c):
            if not self.walls[self.idx(r,c)][d]:
                result.append((nr, nc, d))
        return result

    def generate(self):
        visited = [False] * (self.rows * self.cols)
        stack   = [(0, 0)]
        visited[0] = True
        while stack:
            r, c = stack[-1]
            unvisited = [
                (d, nr, nc)
                for d, nr, nc in self.neighbors(r, c)
                if not visited[self.idx(nr, nc)]
            ]
            if unvisited:
                d, nr, nc = random.choice(unvisited)
                self.remove_wall(r, c, d)
                visited[self.idx(nr, nc)] = True
                stack.append((nr, nc))
            else:
                stack.pop()

    def bfs(self):
        """BFS dari (0,0) ke (ROWS-1,COLS-1). Kembalikan (explore_steps, path)."""
        parent = {(0,0): None}
        queue  = deque([(0,0)])
        steps  = []
        while queue:
            r, c = queue.popleft()
            steps.append((r, c))
            if r == self.rows-1 and c == self.cols-1:
                break
            for nr, nc, _ in self.open_neighbors(r, c):
                if (nr, nc) not in parent:
                    parent[(nr,nc)] = (r,c)
                    queue.append((nr,nc))
        # rekonstruksi jalur
        node = (self.rows-1, self.cols-1)
        path = []
        while node:
            path.append(node)
            node = parent.get(node)
        path.reverse()
        return steps, path

class MazeApp:
    def __init__(self, root):
        self.root  = root
        self.root.title("Maze Fox Solver")
        self.root.configure(bg="#0d0d1a")
        self.root.resizable(False, False)

        self.model       = None
        self.visited_set = set()
        self.path_set    = set()
        self.phase       = 'idle'   
        self.anim_timer  = None
        self.tick        = 0        # frame counter untuk animasi

        # Posisi rubah (canvas coords, smooth)
        self.fox_cx = M + CS // 2
        self.fox_cy = M + CS // 2
        self.fox_tx = self.fox_cx
        self.fox_ty = self.fox_cy
        self.fox_sx = self.fox_cx
        self.fox_sy = self.fox_cy
        self.fox_progress = 1.0
        self.fox_dir = 'E'   

        self._build_ui()
        self._new_maze()
        self._render_loop()

    def _build_ui(self):
        tk.Label(self.root,
                 text="MAZE FOX",
                 font=("Consolas", 15, "bold"),
                 bg="#0d0d1a", fg="#EF9F27").pack(pady=(12,4))

        self.canvas = tk.Canvas(self.root, width=W, height=H,
                                bg=C_BG, highlightthickness=0)
        self.canvas.pack(padx=M, pady=4)

        ctrl = tk.Frame(self.root, bg="#0d0d1a")
        ctrl.pack(pady=8)

        bs = dict(font=("Consolas",11,"bold"), relief="flat",
                  padx=16, pady=6, cursor="hand2", bd=0)

        self.btn_new = tk.Button(ctrl, text="⟳  New Maze",
                                 bg="#f5a623", fg="#0d0d1a",
                                 command=self._new_maze, **bs)
        self.btn_new.grid(row=0, column=0, padx=8)

        self.btn_solve = tk.Button(ctrl, text="▶  Solve",
                                   bg="#1D9E75", fg="#fff",
                                   command=self._solve, **bs)
        self.btn_solve.grid(row=0, column=1, padx=8)

        tk.Label(ctrl, text="Speed:", bg="#0d0d1a", fg="#aaa",
                 font=("Consolas",10)).grid(row=0, column=2, padx=(18,4))
        self.speed_var = tk.IntVar(value=5)
        ttk.Scale(ctrl, from_=1, to=10, variable=self.speed_var,
                  orient="horizontal", length=110).grid(row=0, column=3)

        self.status_var = tk.StringVar(value="Siap! Klik Solve untuk memulai.")
        tk.Label(self.root, textvariable=self.status_var,
                 font=("Consolas",10), bg="#0d0d1a", fg="#888").pack(pady=(0,10))

    def cell_center(self, r, c):
        return M + c*CS + CS//2, M + r*CS + CS//2

    def get_delay(self):
        v = self.speed_var.get()
        return max(15, (11-v)*28)

    def _set_buttons(self, busy):
        s = "disabled" if busy else "normal"
        self.btn_new.config(state=s)
        self.btn_solve.config(state=s)

    def _render_loop(self):
        self.tick += 1
        self._draw_frame()
        self.root.after(16, self._render_loop)   # ~60fps

    def _draw_frame(self):
        c = self.canvas
        c.delete("all")

        self._draw_maze_base()
        self._draw_visited()
        self._draw_path()
        self._draw_cheese()
        self._draw_start_flag()

        # interpolasi posisi rubah
        if self.fox_progress < 1.0:
            self.fox_progress = min(1.0, self.fox_progress + 0.18)
            p = self.fox_progress
            self.fox_cx = self.fox_sx*(1-p) + self.fox_tx*p
            self.fox_cy = self.fox_sy*(1-p) + self.fox_ty*p

        self._draw_fox(self.fox_cx, self.fox_cy, self.fox_dir, self.tick)

        if self.phase == 'done':
            self._draw_win_banner()

    def _draw_maze_base(self):
        c = self.canvas
        c.create_rectangle(0, 0, W, H, fill=C_BG, outline="")

        for r in range(ROWS):
            for col in range(COLS):
                x = M + col*CS
                y = M + r*CS
                c.create_rectangle(x+1, y+1, x+CS-1, y+CS-1,
                                   fill=C_OPEN, outline="")
                w = self.model.walls[self.model.idx(r, col)]
                lc = C_WALL
                lw = 2
                if w['N']:
                    c.create_line(x, y, x+CS, y, fill=lc, width=lw)
                if w['S']:
                    c.create_line(x, y+CS, x+CS, y+CS, fill=lc, width=lw)
                if w['W']:
                    c.create_line(x, y, x, y+CS, fill=lc, width=lw)
                if w['E']:
                    c.create_line(x+CS, y, x+CS, y+CS, fill=lc, width=lw)

        # border luar
        c.create_rectangle(M, M, M+COLS*CS, M+ROWS*CS,
                           outline=C_BORDER, width=2)

    def _draw_visited(self):
        c = self.canvas
        for i in self.visited_set:
            r, col = divmod(i, COLS)
            x = M + col*CS + 2
            y = M + r*CS + 2
            c.create_rectangle(x, y, x+CS-4, y+CS-4,
                               fill=C_VISIT, outline="")

    def _draw_path(self):
        c = self.canvas
        for i in self.path_set:
            r, col = divmod(i, COLS)
            x = M + col*CS + 2
            y = M + r*CS + 2
            c.create_rectangle(x, y, x+CS-4, y+CS-4,
                               fill=C_PATH, outline="")
            
    def _draw_cheese(self):
        cx, cy = self.cell_center(ROWS-1, COLS-1)
        s = CS * 0.40
        c = self.canvas
        # tubuh keju (segitiga tumpul)
        pts = [cx-s, cy-s*0.4,  cx+s, cy-s*0.4,  cx+s*0.65, cy+s*0.65,  cx-s*0.65, cy+s*0.65]
        c.create_polygon(pts, fill="#EF9F27", outline="#BA7517", width=1)
        # lubang
        for hx, hy, hr in [(-0.2,-0.05,0.13),(0.2,0.2,0.12),(-0.05,0.38,0.10),(0.38,0.05,0.11)]:
            c.create_oval(cx+hx*s*2-hr*s, cy+hy*s*2-hr*s,
                          cx+hx*s*2+hr*s, cy+hy*s*2+hr*s,
                          fill="#BA7517", outline="")
            
    def _draw_start_flag(self):
        cx, cy = self.cell_center(0, 0)
        cy -= CS * 0.1
        c = self.canvas
        c.create_polygon(cx-7, cy-11, cx+9, cy-5, cx-7, cy+1,
                         fill="#f5a623", outline="")
        c.create_line(cx-7, cy-11, cx-7, cy+12,
                      fill="#f5a623", width=2)


    def _draw_win_banner(self):
        c = self.canvas
        bx, by = W//2 - 130, H//2 - 30
        c.create_rectangle(bx, by, bx+280, by+60,
                           fill="#0F6E56", outline="#1D9E75", width=2)
        c.create_text(W//2, by+18,
                      text="FOX KELUAR DARI MAZE!",
                      font=("Consolas", 13, "bold"), fill="#E1F5EE")
        c.create_text(W//2, by+42,
                      text=f"Path: {self.path_len} steps | Explored: {self.explored_count} cells",
                      font=("Consolas", 10), fill="#9FE1CB")


    def _draw_fox(self, cx, cy, direction, tick):
        c = self.canvas
        flip   = -1 if direction == 'W' else 1
        s      = CS * 0.42
        bounce = math.sin(tick * 0.25) * 1.8
        leg_sw = math.sin(tick * 0.45) * s * 0.28

        def pt(lx, ly):
            return cx + lx*flip, cy + ly + bounce

        def fx(lx): return cx + lx*flip
        def fy(ly): return cy + ly + bounce

        # ekor
        tail_pts = [
            fx(-s*0.6), fy(s*0.3),
            fx(-s*1.3), fy(s*0.5),
            fx(-s*1.1), fy(-s*0.1),
        ]
        c.create_line(tail_pts[0], tail_pts[1],
                      tail_pts[2], tail_pts[3],
                      fill="#EF9F27", width=4, smooth=True, capstyle="round")
        c.create_oval(fx(-s*1.18)-s*0.15, fy(-s*0.18)-s*0.15,
                      fx(-s*1.18)+s*0.15, fy(-s*0.18)+s*0.15,
                      fill="#fff", outline="")

        # kaki (animasi)
        lw = 3
        for lx, sw_mul in [(s*0.28, 1),(s*0.52, -1),(-s*0.08, -1),(s*0.15, 1)]:
            x1, y1 = fx(lx), fy(s*0.42)
            x2, y2 = fx(lx + leg_sw*sw_mul*0.5), fy(s*0.85)
            c.create_line(x1, y1, x2, y2,
                          fill="#993C1D", width=lw, capstyle="round")

        # badan
        bx1, by1 = fx(-s*0.78), fy(-s*0.52)
        bx2, by2 = fx(s*0.78),  fy(s*0.52)
        c.create_oval(bx1, by1, bx2, by2, fill="#D85A30", outline="")

        # perut
        c.create_oval(fx(-s*0.28), fy(-s*0.28),
                      fx(s*0.58),  fy(s*0.48),
                      fill="#F5C4B3", outline="")

        # kepala
        c.create_oval(fx(s*0.22), fy(-s*0.55),
                      fx(s*1.28), fy(s*0.35),
                      fill="#D85A30", outline="")

        # moncong
        c.create_oval(fx(s*0.82), fy(-s*0.18),
                      fx(s*1.45), fy(s*0.32),
                      fill="#F5C4B3", outline="")

        # hidung
        c.create_oval(fx(s*1.28), fy(-s*0.06)-s*0.1,
                      fx(s*1.28)+s*0.18, fy(-s*0.06)+s*0.1,
                      fill="#1a1a2e", outline="")

        # mata
        c.create_oval(fx(s*0.75)-s*0.12, fy(-s*0.28)-s*0.12,
                      fx(s*0.75)+s*0.12, fy(-s*0.28)+s*0.12,
                      fill="#1a1a2e", outline="")
        c.create_oval(fx(s*0.80)-s*0.05, fy(-s*0.32)-s*0.05,
                      fx(s*0.80)+s*0.05, fy(-s*0.32)+s*0.05,
                      fill="#fff", outline="")

        # telinga kiri
        ear1 = [fx(s*0.42), fy(-s*0.5),
                fx(s*0.3),  fy(-s*0.95),
                fx(s*0.72), fy(-s*0.52)]
        c.create_polygon(ear1, fill="#D85A30", outline="")
        inner1 = [fx(s*0.43), fy(-s*0.54),
                  fx(s*0.34), fy(-s*0.84),
                  fx(s*0.64), fy(-s*0.56)]
        c.create_polygon(inner1, fill="#e94560", outline="")

        # telinga kanan
        ear2 = [fx(s*0.78), fy(-s*0.48),
                fx(s*0.72), fy(-s*0.90),
                fx(s*1.05), fy(-s*0.50)]
        c.create_polygon(ear2, fill="#D85A30", outline="")
        inner2 = [fx(s*0.80), fy(-s*0.52),
                  fx(s*0.76), fy(-s*0.80),
                  fx(s*0.98), fy(-s*0.54)]
        c.create_polygon(inner2, fill="#e94560", outline="")


    def _move_fox_to(self, r, col, direction=None):
        tx, ty = self.cell_center(r, col)
        self.fox_sx = self.fox_cx
        self.fox_sy = self.fox_cy
        self.fox_tx = tx
        self.fox_ty = ty
        self.fox_progress = 0.0
        if direction:
            self.fox_dir = direction

    def _get_dir(self, fr, fc, tr, tc):
        if tr < fr: return 'N'
        if tr > fr: return 'S'
        if tc < fc: return 'W'
        return 'E'

    def _new_maze(self):
        if self.anim_timer:
            self.root.after_cancel(self.anim_timer)
            self.anim_timer = None
        self.phase = 'idle'
        self.visited_set.clear()
        self.path_set.clear()
        self.model = MazeModel(ROWS, COLS)
        self.model.generate()
        cx, cy = self.cell_center(0, 0)
        self.fox_cx = cx; self.fox_cy = cy
        self.fox_tx = cx; self.fox_ty = cy
        self.fox_sx = cx; self.fox_sy = cy
        self.fox_progress = 1.0
        self.fox_dir = 'E'
        self.explored_count = 0
        self.path_len = 0
        self._set_buttons(False)
        self.status_var.set("Maze siap! Klik Solve untuk memulai.")

    def _solve(self):
        if self.phase not in ('idle', 'done'):
            return
        self.phase = 'exploring'
        self.visited_set.clear()
        self.path_set.clear()
        self._set_buttons(True)

        steps, path = self.model.bfs()
        self._solve_steps = steps
        self._solve_path  = path
        self._step_idx    = 0
        self._path_idx    = 0
        self.explored_count = 0
        self.path_len = 0

        # kembalikan rubah ke start
        cx, cy = self.cell_center(0, 0)
        self.fox_cx = cx; self.fox_cy = cy
        self.fox_tx = cx; self.fox_ty = cy
        self.fox_sx = cx; self.fox_sy = cy
        self.fox_progress = 1.0
        self.fox_dir = 'E'

        self._animate_explore()

    def _animate_explore(self):
        if self._step_idx >= len(self._solve_steps):
            self.visited_set.clear()
            self.phase = 'pathing'
            self.status_var.set("Jalur ditemukan! Rubah berlari ke tujuan...")
            self._path_idx = 0
            self.anim_timer = self.root.after(200, self._animate_path)
            return

        r, c = self._solve_steps[self._step_idx]
        if self._step_idx > 0:
            pr, pc = self._solve_steps[self._step_idx-1]
            d = self._get_dir(pr, pc, r, c)
        else:
            d = 'E'

        self.visited_set.add(self.model.idx(r, c))
        self._move_fox_to(r, c, d)
        self._step_idx += 1
        self.explored_count = self._step_idx
        self.status_var.set(
            f"Menjelajahi... ({self._step_idx}/{len(self._solve_steps)} sel)")

        self.anim_timer = self.root.after(self.get_delay(), self._animate_explore)

    def _animate_path(self):
        if self._path_idx >= len(self._solve_path):
            self.phase = 'done'
            self._set_buttons(False)
            self.status_var.set(
                f"Rubah menemukan keju! "
                f"Jalur: {self.path_len} langkah | "
                f"Dieksplorasi: {self.explored_count} sel")
            return

        r, c = self._solve_path[self._path_idx]
        if self._path_idx > 0:
            pr, pc = self._solve_path[self._path_idx-1]
            d = self._get_dir(pr, pc, r, c)
        else:
            d = self.fox_dir

        self.path_set.add(self.model.idx(r, c))
        self._move_fox_to(r, c, d)
        self._path_idx += 1
        self.path_len = self._path_idx

        self.anim_timer = self.root.after(
            int(self.get_delay() * 0.65), self._animate_path)


if __name__ == "__main__":
    root = tk.Tk()
    app  = MazeApp(root)
    root.mainloop()