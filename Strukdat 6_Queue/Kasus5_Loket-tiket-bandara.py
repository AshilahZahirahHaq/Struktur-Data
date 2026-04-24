import pygame
import random
import sys

# ==========================================
# KONFIGURASI PARAMETER SIMULASI (Sesuai Gambar)
# ==========================================
NUM_MINUTES = 1000       # Total menit simulasi
BETWEEN_TIME = 2         # Rata-rata 1 penumpang tiba tiap 2 menit
SERVICE_TIME = 5         # Waktu layanan tiap penumpang adalah 5 menit
INITIAL_AGENTS = 2       # Jumlah agen awal (Di gambar disebutkan insight 2 -> 3)

# Konfigurasi Visual Pygame
WIDTH, HEIGHT = 800, 600
FPS = 60
TICK_SPEED = 100 # ms per 1 menit waktu simulasi (semakin kecil, simulasi semakin cepat)

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 150, 255)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
GRAY = (200, 200, 200)
DARK_BLUE = (10, 30, 80)

# ==========================================
# STRUKTUR DATA SIMULASI
# ==========================================
class Penumpang:
    def __init__(self, id_penumpang, waktu_tiba):
        self.id = id_penumpang
        self.waktu_tiba = waktu_tiba

class AgenTiket:
    def __init__(self, id_agen):
        self.id = id_agen
        self.penumpang_saat_ini = None
        self.waktu_selesai = 0

    def is_free(self):
        return self.penumpang_saat_ini is None

class SimulasiBandara:
    def __init__(self, num_agents):
        self.agen_list = [AgenTiket(i) for i in range(num_agents)]
        self.queue = []
        self.waktu_sekarang = 0
        self.total_wait = 0
        self.num_served = 0
        self.id_counter = 0

    # R1: Jika penumpang tiba -> enqueue
    def tangani_kedatangan(self):
        prob = 1.0 / BETWEEN_TIME
        if random.random() < prob:
            self.id_counter += 1
            penumpang_baru = Penumpang(self.id_counter, self.waktu_sekarang)
            self.queue.append(penumpang_baru)

    # R2: Jika agen free & queue tidak kosong -> dequeue, layani
    def tangani_mulai_layanan(self):
        for agen in self.agen_list:
            if agen.is_free() and len(self.queue) > 0:
                penumpang = self.queue.pop(0) # Dequeue
                waktu_tunggu = self.waktu_sekarang - penumpang.waktu_tiba
                self.total_wait += waktu_tunggu
                self.num_served += 1
                
                agen.penumpang_saat_ini = penumpang
                agen.waktu_selesai = self.waktu_sekarang + SERVICE_TIME

    # R3: Jika transaksi selesai -> penumpang keluar, agen free
    def tangani_selesai_layanan(self):
        for agen in self.agen_list:
            if not agen.is_free() and self.waktu_sekarang >= agen.waktu_selesai:
                agen.penumpang_saat_ini = None

    # 3 Aturan per tick waktu
    def jalankan_satu_menit(self):
        self.tangani_kedatangan()
        self.tangani_mulai_layanan()
        self.tangani_selesai_layanan()
        self.waktu_sekarang += 1

    def get_avg_wait(self):
        if self.num_served == 0:
            return 0
        return self.total_wait / self.num_served

    def tambah_agen(self):
        self.agen_list.append(AgenTiket(len(self.agen_list)))
        
    def kurangi_agen(self):
        if len(self.agen_list) > 1:
            # Hanya hapus agen yang sedang free jika memungkinkan
            for agen in self.agen_list:
                if agen.is_free():
                    self.agen_list.remove(agen)
                    return
            self.agen_list.pop() # Paksa hapus dari ujung jika sibuk semua


# ==========================================
# FUNGSI UTAMA & LOOP ANIMASI PYGAME
# ==========================================
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simulasi Loket Tiket Bandara (Animasi)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 20)
    font_bold = pygame.font.SysFont("arial", 22, bold=True)
    font_large = pygame.font.SysFont("arial", 30, bold=True)

    simulasi = SimulasiBandara(INITIAL_AGENTS)
    
    last_tick_time = pygame.time.get_ticks()
    running = True
    pause = False

    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pause = not pause
                elif event.key == pygame.K_UP:
                    simulasi.tambah_agen()
                elif event.key == pygame.K_DOWN:
                    simulasi.kurangi_agen()

        # Update Logika Simulasi berdasarkan waktu nyata
        current_time_ms = pygame.time.get_ticks()
        if not pause and current_time_ms - last_tick_time > TICK_SPEED:
            simulasi.jalankan_satu_menit()
            last_tick_time = current_time_ms

        # Render Visual
        screen.fill(WHITE)
        
        # Header / Judul
        title = font_large.render("Simulasi Loket Tiket Bandara", True, DARK_BLUE)
        screen.blit(title, (20, 20))
        
        # Instruksi & Insight
        instruksi1 = font.render(f"[SPACE] Pause/Resume", True, BLACK)
        instruksi2 = font_bold.render(f"Insight: Tekan [UP] untuk tambah agen (2 -> 3) !", True, RED)
        instruksi3 = font.render(f"[DOWN] Kurangi agen", True, BLACK)
        screen.blit(instruksi1, (WIDTH - 250, 20))
        screen.blit(instruksi2, (WIDTH - 450, 50))
        screen.blit(instruksi3, (WIDTH - 250, 80))

        # Panel Statistik
        pygame.draw.rect(screen, GRAY, (20, 80, 300, 130), border_radius=10)
        stat1 = font.render(f"Waktu Simulasi (Menit): {simulasi.waktu_sekarang}", True, BLACK)
        stat2 = font.render(f"Jumlah Agen Tiket: {len(simulasi.agen_list)}", True, BLACK)
        stat3 = font.render(f"Penumpang Dilayani: {simulasi.num_served}", True, BLACK)
        avg_wait = simulasi.get_avg_wait()
        stat4 = font_bold.render(f"Rata-rata Tunggu: {avg_wait:.2f} menit", True, RED if avg_wait > 5 else DARK_BLUE)
        
        screen.blit(stat1, (30, 90))
        screen.blit(stat2, (30, 120))
        screen.blit(stat3, (30, 150))
        screen.blit(stat4, (30, 180))

        # Gambar Agen Tiket (Loket)
        start_x_agen = 50
        y_agen = 250
        gap_agen = 120
        
        for i, agen in enumerate(simulasi.agen_list):
            x_agen = start_x_agen + (i * gap_agen)
            # Meja Agen
            pygame.draw.rect(screen, DARK_BLUE, (x_agen, y_agen, 80, 80), border_radius=10)
            txt_agen = font.render(f"A-{agen.id+1}", True, WHITE)
            screen.blit(txt_agen, (x_agen + 20, y_agen + 10))
            
            # Status Agen
            if agen.is_free():
                status = font.render("FREE", True, GREEN)
                screen.blit(status, (x_agen + 15, y_agen + 40))
            else:
                status = font.render("SIBUK", True, RED)
                screen.blit(status, (x_agen + 10, y_agen + 35))
                # Gambar Penumpang yang sedang dilayani
                pygame.draw.circle(screen, BLUE, (x_agen + 40, y_agen + 110), 15)
                txt_p = font.render(str(agen.penumpang_saat_ini.id), True, WHITE)
                screen.blit(txt_p, (x_agen + 32, y_agen + 100))

        # Gambar Garis Pembatas
        pygame.draw.line(screen, BLACK, (0, 400), (WIDTH, 400), 2)
        q_title = font_bold.render(f"Antrian Penumpang (Queue Length: {len(simulasi.queue)})", True, BLACK)
        screen.blit(q_title, (20, 410))

        # Gambar Queue (Antrean Penumpang)
        start_x_q = 50
        y_q = 480
        gap_q = 40
        
        for i, penumpang in enumerate(simulasi.queue):
            # Agar antrian terlihat melingkar jika terlalu panjang (Snake pattern)
            row = i // 18
            col = i % 18
            
            x_pos = start_x_q + (col * gap_q)
            if row % 2 != 0: # Baris ganjil berbalik arah
                 x_pos = start_x_q + ((17 - col) * gap_q)
                 
            y_pos = y_q + (row * gap_q)

            pygame.draw.circle(screen, BLUE, (x_pos, y_pos), 15)
            txt_p = font.render(str(penumpang.id), True, WHITE)
            # Menyesuaikan posisi teks ke tengah lingkaran
            txt_rect = txt_p.get_rect(center=(x_pos, y_pos))
            screen.blit(txt_p, txt_rect)

        if pause:
            pause_txt = font_large.render("PAUSED", True, RED)
            screen.blit(pause_txt, (WIDTH//2 - 50, HEIGHT//2))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()