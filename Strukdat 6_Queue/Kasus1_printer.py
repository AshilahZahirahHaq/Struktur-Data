"""
Animasi Antrian Printer (FIFO Queue)
Visualisasi kode program dengan animasi terminal menggunakan Rich
"""

import time
from collections import deque
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.rule import Rule
from rich.align import Align
from rich import box
from rich.live import Live
from rich.layout import Layout
from rich.padding import Padding

console = Console()

# ── Ikon file berdasarkan ekstensi ──────────────────────────────────────────
FILE_ICONS = {
    "pdf":  "📄",
    "docx": "📝",
    "jpg":  "🖼️ ",
    "pptx": "📊",
    "xlsx": "📗",
    "txt":  "📃",
}

def get_icon(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    return FILE_ICONS.get(ext, "📁")


# ── Kelas Queue ─────────────────────────────────────────────────────────────
class PrinterQueue:
    def __init__(self):
        self._queue: deque = deque()

    def enqueue(self, document: str):
        self._queue.append(document)

    def dequeue(self) -> str:
        if self.isEmpty():
            raise IndexError("Antrian kosong!")
        return self._queue.popleft()

    def peek(self) -> str:
        return self._queue[0] if not self.isEmpty() else None

    def isEmpty(self) -> bool:
        return len(self._queue) == 0

    def size(self) -> int:
        return len(self._queue)

    def to_list(self) -> list:
        return list(self._queue)


# ── Render tampilan antrian ──────────────────────────────────────────────────
def render_queue_panel(queue: PrinterQueue, title="📋 Antrian Dokumen") -> Panel:
    items = queue.to_list()
    if not items:
        content = Align.center(
            Text("(antrian kosong)", style="dim italic"),
            vertical="middle"
        )
        return Panel(content, title=title, border_style="dim", height=8)

    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1), expand=True)
    table.add_column("No", style="dim", width=4, justify="right")
    table.add_column("Ikon", width=4)
    table.add_column("Nama Dokumen", style="white")
    table.add_column("Status", width=12, justify="right")

    for i, doc in enumerate(items):
        icon = get_icon(doc)
        if i == 0:
            style  = "bold cyan"
            status = Text("▶ berikutnya", style="bold cyan")
            no_txt = Text("1", style="bold cyan")
        else:
            style  = "white"
            status = Text(f"#{i+1}", style="dim")
            no_txt = Text(str(i + 1), style="dim")
        table.add_row(no_txt, icon, Text(doc, style=style), status)

    return Panel(table, title=f"{title}  [dim]({queue.size()} dokumen)[/dim]",
                 border_style="cyan")


def render_printer_panel(status: str, doc: str | None,
                         progress: int = 0, done_docs: list = []) -> Panel:
    lines = []

    # Status bar printer
    if doc:
        bar_filled = "█" * progress
        bar_empty  = "░" * (20 - progress)
        bar_color  = "green" if progress < 20 else "bright_green"
        lines.append(Text.assemble(
            ("🖨️  Sedang mencetak: ", "bold"),
            (doc, "bold yellow"),
        ))
        lines.append(Text.assemble(
            ("   [", "dim"),
            (bar_filled, bar_color),
            (bar_empty,  "dim"),
            (f"] {progress * 5}%", "dim"),
        ))
    else:
        lines.append(Text(f"🖨️  {status}", style="bold dim"))
        lines.append(Text("   [" + "░" * 20 + "] —", style="dim"))

    # Riwayat dokumen selesai
    if done_docs:
        lines.append(Text(""))
        lines.append(Text("✅ Selesai dicetak:", style="bold green"))
        for d in done_docs[-4:]:
            lines.append(Text(f"   {get_icon(d)} {d}", style="dim green"))

    from rich.console import Group
    content = Group(*lines)
    border = "green" if doc else "dim"
    return Panel(content, title="🖨️  Status Printer", border_style=border, height=10)


def render_code_panel(last_call: str) -> Panel:
    code = Text()
    code.append("printer_queue = ", style="white")
    code.append("Queue()\n\n", style="yellow")

    # Pewarnaan sederhana: sorot baris terakhir
    if "enqueue" in last_call:
        code.append("printer_queue.", style="white")
        code.append("enqueue", style="bold magenta")
        fname = last_call.split('"')[1] if '"' in last_call else "..."
        code.append(f'("{fname}")', style="yellow")
        code.append("  ← enqueue()\n", style="dim cyan")
    elif "dequeue" in last_call:
        code.append("doc = printer_queue.", style="white")
        code.append("dequeue", style="bold magenta")
        code.append("()", style="yellow")
        code.append("  ← dequeue()\n", style="dim cyan")
        code.append('print(f"Mencetak: {doc}")', style="dim")
    else:
        code.append("# Menunggu operasi...", style="dim")

    return Panel(code, title="💻 Kode Berjalan", border_style="magenta")


def render_log_panel(logs: list) -> Panel:
    t = Text()
    for entry in logs[-6:]:
        t.append(entry + "\n")
    return Panel(t, title="📜 Log Output", border_style="dim", height=10)


# ── Fungsi animasi utama ────────────────────────────────────────────────────
def animate_enqueue(queue: PrinterQueue, document: str,
                    logs: list, done_docs: list):
    """Animasi menambahkan dokumen ke antrian."""
    console.print(Rule(f"[cyan]enqueue(\"{document}\")[/cyan]", style="cyan"))

    # Frame animasi: dokumen "terbang masuk"
    frames = ["   ", "▷  ", "▶  ", "▶▷ ", "▶▶ ", "▶▶▷"]
    with Live(refresh_per_second=15, console=console) as live:
        for f in frames:
            txt = Text.assemble(
                (f"  {f} ", "cyan bold"),
                (f'"{document}"', "yellow bold"),
                (" masuk ke antrian...", "dim"),
            )
            live.update(Panel(txt, border_style="cyan", height=3))
            time.sleep(0.07)

    queue.enqueue(document)
    logs.append(f'[cyan]►[/cyan] enqueue("{document}") → posisi #{queue.size()}')

    # Render state terkini
    _render_state(queue, None, None, 0, logs, done_docs,
                  f'enqueue("{document}")')
    time.sleep(0.5)


def animate_dequeue(queue: PrinterQueue, logs: list, done_docs: list):
    """Animasi mencetak (dequeue) dokumen pertama."""
    if queue.isEmpty():
        console.print("[red]Antrian kosong![/red]")
        return

    doc = queue.dequeue()
    console.print(Rule(f"[green]dequeue() → \"{doc}\"[/green]", style="green"))
    logs.append(f'[green]►[/green] dequeue() → Mencetak: "{doc}"')

    # Animasi progress bar cetak
    STEPS = 20
    with Live(refresh_per_second=15, console=console) as live:
        for step in range(STEPS + 1):
            top = render_queue_panel(queue)
            mid = render_printer_panel("Mencetak...", doc, step, done_docs)
            cod = render_code_panel(f'dequeue("{doc}")')
            lg  = render_log_panel(logs)

            from rich.console import Group
            live.update(Group(top, mid, cod, lg))
            time.sleep(0.07)

    done_docs.append(doc)
    logs.append(f'[bright_green]✓[/bright_green] "{doc}" selesai dicetak!')
    console.print(f'[bright_green]  ✓ Mencetak: {doc}[/bright_green]')
    time.sleep(0.3)


def _render_state(queue, printer_status, doc, progress,
                  logs, done_docs, last_call=""):
    from rich.console import Group
    group = Group(
        render_queue_panel(queue),
        render_printer_panel(printer_status or "Menunggu...", doc, progress, done_docs),
        render_code_panel(last_call),
        render_log_panel(logs),
    )
    console.print(group)


# ── Program utama ───────────────────────────────────────────────────────────
def main():
    console.clear()
    console.print(Rule("[bold cyan]🖨️  Animasi Antrian Printer — FIFO Queue[/bold cyan]", style="cyan"))
    console.print()

    # Penjelasan konsep
    info = Panel(
        Text.assemble(
            ("Konsep: ", "bold"),
            ("Queue (antrian) adalah struktur data FIFO\n", "white"),
            ("  • enqueue() ", "bold magenta"), ("→ dokumen masuk ke belakang antrian\n", "dim"),
            ("  • dequeue() ", "bold magenta"), ("→ printer ambil dokumen paling depan\n", "dim"),
            ("  • Dokumen yang datang duluan, dicetak duluan\n", "dim"),
        ),
        border_style="dim", title="📖 FIFO — First In, First Out"
    )
    console.print(info)
    time.sleep(1.5)

    # Inisialisasi
    printer_queue = PrinterQueue()
    logs: list[str] = ["[dim]► printer_queue = Queue() → antrian dibuat[/dim]"]
    done_docs: list[str] = []

    console.print()
    console.print(Rule("[dim]Fase 1 — User mengirim dokumen (enqueue)[/dim]", style="dim"))
    time.sleep(0.8)

    # ── Enqueue 3 dokumen ──
    documents = ["laporan.pdf", "tugas.docx", "foto.jpg"]
    for doc in documents:
        animate_enqueue(printer_queue, doc, logs, done_docs)
        time.sleep(0.4)

    console.print()
    console.print(Rule("[dim]Fase 2 — Printer memproses antrian (dequeue)[/dim]", style="dim"))
    time.sleep(0.8)

    # ── Dequeue & cetak semua ──
    while not printer_queue.isEmpty():
        animate_dequeue(printer_queue, logs, done_docs)
        time.sleep(0.3)

    # Tampilan akhir
    console.print()
    console.print(Rule("[bold green]Semua dokumen selesai dicetak![/bold green]", style="green"))

    final = Panel(
        Text.assemble(
            ("Urutan cetak:\n", "bold"),
            *[(f"  {i+1}. {get_icon(d)} {d}\n", "green") for i, d in enumerate(done_docs)],
            ("\n✓ FIFO terbukti: dokumen pertama masuk = pertama dicetak", "bold green"),
        ),
        title="📋 Ringkasan", border_style="green"
    )
    console.print(final)

    # Tampilkan kode sumber lengkap
    console.print()
    console.print(Rule("[magenta]Kode Program Lengkap[/magenta]", style="magenta"))
    code_full = Panel(
        Text.assemble(
            ("from collections import deque\n\n", "dim"),
            ("class ", "bold cyan"), ("Queue:\n", "yellow"),
            ("    def ", "bold cyan"), ("__init__", "white"), ("(self):\n", "white"),
            ("        self._queue = deque()\n\n", "dim"),
            ("    def ", "bold cyan"), ("enqueue", "bold magenta"), ("(self, document):\n", "white"),
            ("        self._queue.append(document)\n\n", "dim"),
            ("    def ", "bold cyan"), ("dequeue", "bold magenta"), ("(self):\n", "white"),
            ("        return self._queue.popleft()\n\n", "dim"),
            ("    def ", "bold cyan"), ("isEmpty", "bold magenta"), ("(self):\n", "white"),
            ("        return len(self._queue) == 0\n\n", "dim"),
            ("# ── Main Program ──\n", "dim"),
            ("printer_queue = ", "white"), ("Queue", "yellow"), ("()\n\n", "white"),
            ("printer_queue.", "white"), ("enqueue", "bold magenta"), ('("laporan.pdf")\n', "yellow"),
            ("printer_queue.", "white"), ("enqueue", "bold magenta"), ('("tugas.docx")\n', "yellow"),
            ("printer_queue.", "white"), ("enqueue", "bold magenta"), ('("foto.jpg")\n\n', "yellow"),
            ("while not ", "bold cyan"), ("printer_queue.", "white"),
            ("isEmpty", "bold magenta"), ("():\n", "white"),
            ("    doc = printer_queue.", "white"), ("dequeue", "bold magenta"), ("()\n", "white"),
            ('    print(f"Mencetak: {doc}")\n', "dim"),
        ),
        title="💻 Source Code", border_style="magenta"
    )
    console.print(code_full)


if __name__ == "__main__":
    main()