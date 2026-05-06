"""
Advanced Linked List - Note Taking Application
================================================
Struktur data yang diimplementasikan:
  1. Multi-Linked List      : multiple tags per note (relasi many-to-many)
  2. Double Linked Sorted   : chronological & alphabetical views
  3. Circular Buffer        : sync status tracking (recent changes)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Optional


# ─────────────────────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────────────────────

class SyncStatus(Enum):
    SYNCED   = "SYNCED"
    PENDING  = "PENDING"
    CONFLICT = "CONFLICT"

class ChangeType(Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


# ─────────────────────────────────────────────────────────────
# MULTI-LINK: Penghubung Note <-> Tag (Many-to-Many)
# ─────────────────────────────────────────────────────────────

class TagLink:
    """
    Node perantara yang dimiliki NoteNode.
    Membentuk singly linked list: note → tag1 → tag2 → ... → None
    """
    def __init__(self, tag: "TagNode"):
        self.tag:  TagNode    = tag
        self.next: Optional[TagLink] = None


class NoteLink:
    """
    Node perantara yang dimiliki TagNode.
    Membentuk singly linked list: tag → note1 → note2 → ... → None
    """
    def __init__(self, note: "NoteNode"):
        self.note: NoteNode    = note
        self.next: Optional[NoteLink] = None


# ─────────────────────────────────────────────────────────────
# TAG NODE
# ─────────────────────────────────────────────────────────────

class TagNode:
    """
    Merepresentasikan sebuah tag.
    Menyimpan linked list semua NoteNode yang memiliki tag ini.
    """
    def __init__(self, name: str):
        self.tag_name:       str               = name
        self.note_list_head: Optional[NoteLink] = None  # list note dengan tag ini
        self.next:           Optional[TagNode]  = None  # global tag list

    def add_note(self, note: "NoteNode") -> None:
        """Tambahkan note ke daftar note milik tag ini (insert di head, O(1))."""
        link = NoteLink(note)
        link.next = self.note_list_head
        self.note_list_head = link

    def remove_note(self, note: "NoteNode") -> None:
        """Hapus note dari daftar note milik tag ini."""
        prev, curr = None, self.note_list_head
        while curr:
            if curr.note is note:
                if prev:
                    prev.next = curr.next
                else:
                    self.note_list_head = curr.next
                return
            prev, curr = curr, curr.next

    def get_notes(self) -> list["NoteNode"]:
        """Kembalikan semua note dengan tag ini sebagai list."""
        result, curr = [], self.note_list_head
        while curr:
            result.append(curr.note)
            curr = curr.next
        return result

    def __repr__(self) -> str:
        return f"TagNode('{self.tag_name}')"


# ─────────────────────────────────────────────────────────────
# NOTE NODE (node inti utama)
# ─────────────────────────────────────────────────────────────

class NoteNode:
    """
    Node utama yang merepresentasikan satu catatan (note).

    Memiliki:
      - tagHead            : head dari linked list TagLink (multi-link ke tags)
      - chrono_prev/next   : pointer doubly linked list urutan waktu
      - alpha_prev/next    : pointer doubly linked list urutan alfabet
      - sync_status        : status sinkronisasi
    """
    def __init__(self, note_id: int, title: str, content: str):
        self.id:          int        = note_id
        self.title:       str        = title
        self.content:     str        = content
        self.created_at:  datetime   = datetime.now()
        self.updated_at:  datetime   = datetime.now()

        # Multi-link: list tag milik note ini
        self.tag_head: Optional[TagLink] = None

        # Doubly linked sorted by waktu (chronological)
        self.chrono_prev: Optional[NoteNode] = None
        self.chrono_next: Optional[NoteNode] = None

        # Doubly linked sorted by judul (alphabetical)
        self.alpha_prev: Optional[NoteNode] = None
        self.alpha_next: Optional[NoteNode] = None

        self.sync_status: SyncStatus = SyncStatus.PENDING

    # ── Operasi Tag ──────────────────────────────────────────

    def add_tag_link(self, tag: TagNode) -> None:
        """Tambahkan TagLink ke note ini (insert di head, O(1))."""
        if self._has_tag(tag):
            return  # hindari duplikat
        link = TagLink(tag)
        link.next = self.tag_head
        self.tag_head = link

    def remove_tag_link(self, tag: TagNode) -> None:
        """Hapus TagLink untuk tag tertentu dari note ini."""
        prev, curr = None, self.tag_head
        while curr:
            if curr.tag is tag:
                if prev:
                    prev.next = curr.next
                else:
                    self.tag_head = curr.next
                return
            prev, curr = curr, curr.next

    def _has_tag(self, tag: TagNode) -> bool:
        curr = self.tag_head
        while curr:
            if curr.tag is tag:
                return True
            curr = curr.next
        return False

    def get_tags(self) -> list[TagNode]:
        """Kembalikan semua tag milik note ini sebagai list."""
        result, curr = [], self.tag_head
        while curr:
            result.append(curr.tag)
            curr = curr.next
        return result

    def __repr__(self) -> str:
        tags = [t.tag_name for t in self.get_tags()]
        return (f"NoteNode(id={self.id}, title='{self.title}', "
                f"tags={tags}, sync={self.sync_status.value})")


# ─────────────────────────────────────────────────────────────
# CHANGE RECORD (satu slot circular buffer)
# ─────────────────────────────────────────────────────────────

@dataclass
class ChangeRecord:
    note_id:     int
    note_title:  str
    change_type: ChangeType
    timestamp:   datetime
    sync_status: SyncStatus

    def __str__(self) -> str:
        ts = self.timestamp.strftime("%d %b %H:%M:%S")
        return (f"[{ts}] {self.change_type.value:<6} "
                f"#{self.note_id} '{self.note_title}' "
                f"→ {self.sync_status.value}")


# ─────────────────────────────────────────────────────────────
# SYNC BUFFER (circular buffer)
# ─────────────────────────────────────────────────────────────

class SyncBuffer:
    """
    Circular buffer berukuran tetap untuk mencatat N perubahan terakhir.

    Cara kerja:
      - tail  : slot berikutnya yang akan diisi
      - head  : slot record paling lama (di-overwrite saat buffer penuh)
      - count : jumlah record aktif (≤ MAX_SIZE)

    Semua operasi push/read adalah O(1).
    """

    def __init__(self, max_size: int = 10):
        self.max_size: int = max_size
        self.buffer:   list[Optional[ChangeRecord]] = [None] * max_size
        self.head:     int = 0
        self.tail:     int = 0
        self.count:    int = 0

    def push(self, record: ChangeRecord) -> None:
        """Tambahkan record baru. Jika penuh, overwrite yang paling lama."""
        self.buffer[self.tail] = record
        self.tail = (self.tail + 1) % self.max_size

        if self.count < self.max_size:
            self.count += 1
        else:
            # buffer penuh: geser head maju (buang yang paling lama)
            self.head = (self.head + 1) % self.max_size

    def get_recent(self) -> list[ChangeRecord]:
        """Kembalikan semua record dari paling lama ke paling baru."""
        result = []
        for i in range(self.count):
            idx = (self.head + i) % self.max_size
            result.append(self.buffer[idx])
        return result

    def is_empty(self) -> bool:
        return self.count == 0

    def is_full(self) -> bool:
        return self.count == self.max_size

    def print_all(self) -> None:
        print(f"\n{'─'*55}")
        print(f"  SYNC BUFFER  (kapasitas: {self.max_size}, terisi: {self.count})")
        print(f"{'─'*55}")
        records = self.get_recent()
        if not records:
            print("  (kosong)")
        for i, rec in enumerate(records):
            marker = "← terlama" if i == 0 else ("← terbaru" if i == len(records)-1 else "")
            print(f"  [{(self.head+i)%self.max_size}] {rec}  {marker}")
        print(f"  head={self.head}  tail={self.tail}  count={self.count}")


# ─────────────────────────────────────────────────────────────
# NOTE APP (manager utama)
# ─────────────────────────────────────────────────────────────

class NoteApp:
    """
    Manager utama aplikasi note-taking.

    Mengelola:
      - Doubly linked list sorted by waktu   (chrono_head/tail)
      - Doubly linked list sorted by judul   (alpha_head/tail)
      - Global tag list                      (tag_list_head)
      - Circular buffer perubahan            (sync_buf)
    """

    def __init__(self, buffer_size: int = 10):
        # Doubly linked sorted lists
        self.chrono_head: Optional[NoteNode] = None
        self.chrono_tail: Optional[NoteNode] = None
        self.alpha_head:  Optional[NoteNode] = None
        self.alpha_tail:  Optional[NoteNode] = None

        # Global tag list (singly linked)
        self.tag_list_head: Optional[TagNode] = None

        # Circular buffer
        self.sync_buf: SyncBuffer = SyncBuffer(buffer_size)

        self._next_id: int = 1

    # ══════════════════════════════════════════════════════════
    # OPERASI NOTE
    # ══════════════════════════════════════════════════════════

    def add_note(self, title: str, content: str) -> NoteNode:
        """
        Buat note baru dan masukkan ke kedua sorted list.
        Kompleksitas: O(n) karena perlu cari posisi insert yang tepat.
        """
        note = NoteNode(self._next_id, title, content)
        self._next_id += 1

        self._insert_chrono(note)
        self._insert_alpha(note)

        # Catat ke sync buffer
        self.sync_buf.push(ChangeRecord(
            note_id=note.id,
            note_title=note.title,
            change_type=ChangeType.CREATE,
            timestamp=note.created_at,
            sync_status=note.sync_status,
        ))

        print(f"  ✓ Note #{note.id} '{note.title}' ditambahkan.")
        return note

    def update_note(self, note: NoteNode,
                    title: Optional[str] = None,
                    content: Optional[str] = None) -> None:
        """
        Update isi/judul note.
        Jika judul berubah, posisi di alpha list perlu diperbarui.
        """
        title_changed = title and title != note.title

        if title_changed:
            self._remove_from_alpha(note)
        if title:
            note.title = title
        if content:
            note.content = content

        note.updated_at  = datetime.now()
        note.sync_status = SyncStatus.PENDING

        if title_changed:
            self._insert_alpha(note)

        self.sync_buf.push(ChangeRecord(
            note_id=note.id,
            note_title=note.title,
            change_type=ChangeType.UPDATE,
            timestamp=note.updated_at,
            sync_status=note.sync_status,
        ))
        print(f"  ✓ Note #{note.id} '{note.title}' diperbarui.")

    def delete_note(self, note: NoteNode) -> None:
        """
        Hapus note dari semua struktur.
        Kompleksitas: O(T) di mana T = jumlah tag note tsb.
        """
        # Lepas dari kedua sorted list
        self._remove_from_chrono(note)
        self._remove_from_alpha(note)

        # Lepas semua relasi tag
        curr = note.tag_head
        while curr:
            curr.tag.remove_note(note)
            curr = curr.next

        self.sync_buf.push(ChangeRecord(
            note_id=note.id,
            note_title=note.title,
            change_type=ChangeType.DELETE,
            timestamp=datetime.now(),
            sync_status=note.sync_status,
        ))
        print(f"  ✓ Note #{note.id} '{note.title}' dihapus.")

    def mark_synced(self, note: NoteNode) -> None:
        note.sync_status = SyncStatus.SYNCED
        self.sync_buf.push(ChangeRecord(
            note_id=note.id,
            note_title=note.title,
            change_type=ChangeType.UPDATE,
            timestamp=datetime.now(),
            sync_status=SyncStatus.SYNCED,
        ))

    def mark_conflict(self, note: NoteNode) -> None:
        note.sync_status = SyncStatus.CONFLICT

    # ══════════════════════════════════════════════════════════
    # OPERASI TAG (Multi-Link)
    # ══════════════════════════════════════════════════════════

    def add_tag_to_note(self, note: NoteNode, tag_name: str) -> None:
        """
        Tambahkan tag ke note.
        Buat TagNode baru jika belum ada (O(T_global) untuk cari).
        Tambahkan TagLink ke note dan NoteLink ke tag (O(1) masing-masing).
        """
        tag = self._find_or_create_tag(tag_name)
        note.add_tag_link(tag)
        tag.add_note(note)
        print(f"  ✓ Tag '{tag_name}' ditambahkan ke note #{note.id}.")

    def remove_tag_from_note(self, note: NoteNode, tag_name: str) -> None:
        """Lepas relasi tag dari note (O(T_note) + O(N_tag))."""
        tag = self._find_tag(tag_name)
        if not tag:
            print(f"  ✗ Tag '{tag_name}' tidak ditemukan.")
            return
        note.remove_tag_link(tag)
        tag.remove_note(note)
        print(f"  ✓ Tag '{tag_name}' dilepas dari note #{note.id}.")

    def get_notes_by_tag(self, tag_name: str) -> list[NoteNode]:
        """Kembalikan semua note dengan tag tertentu (O(N_tag))."""
        tag = self._find_tag(tag_name)
        return tag.get_notes() if tag else []

    # ══════════════════════════════════════════════════════════
    # VIEWS (traversal sorted lists)
    # ══════════════════════════════════════════════════════════

    def print_chronological(self, reverse: bool = False) -> None:
        """Tampilkan semua note urut waktu. reverse=True → terbaru dulu."""
        print(f"\n{'═'*55}")
        title = "CHRONOLOGICAL VIEW" + (" (terbaru dulu)" if reverse else " (terlama dulu)")
        print(f"  {title}")
        print(f"{'═'*55}")
        if reverse:
            curr = self.chrono_tail
            while curr:
                self._print_note_row(curr)
                curr = curr.chrono_prev
        else:
            curr = self.chrono_head
            while curr:
                self._print_note_row(curr)
                curr = curr.chrono_next

    def print_alphabetical(self, reverse: bool = False) -> None:
        """Tampilkan semua note urut alfabet. reverse=True → Z-A."""
        print(f"\n{'═'*55}")
        title = "ALPHABETICAL VIEW" + (" (Z→A)" if reverse else " (A→Z)")
        print(f"  {title}")
        print(f"{'═'*55}")
        if reverse:
            curr = self.alpha_tail
            while curr:
                self._print_note_row(curr)
                curr = curr.alpha_prev
        else:
            curr = self.alpha_head
            while curr:
                self._print_note_row(curr)
                curr = curr.alpha_next

    def print_notes_by_tag(self, tag_name: str) -> None:
        """Tampilkan semua note yang memiliki tag tertentu."""
        notes = self.get_notes_by_tag(tag_name)
        print(f"\n{'─'*55}")
        print(f"  Notes dengan tag '{tag_name}' ({len(notes)} note)")
        print(f"{'─'*55}")
        if not notes:
            print("  (tidak ada)")
        for note in notes:
            self._print_note_row(note)

    def print_all_tags(self) -> None:
        """Tampilkan semua tag beserta jumlah note-nya."""
        print(f"\n{'─'*55}")
        print("  ALL TAGS")
        print(f"{'─'*55}")
        curr = self.tag_list_head
        if not curr:
            print("  (belum ada tag)")
        while curr:
            notes = curr.get_notes()
            print(f"  #{curr.tag_name:<15} ({len(notes)} note): "
                  + ", ".join(f"'{n.title}'" for n in notes))
            curr = curr.next

    def print_recent_changes(self) -> None:
        """Tampilkan isi circular buffer (recent changes)."""
        self.sync_buf.print_all()

    # ══════════════════════════════════════════════════════════
    # HELPER: Doubly Linked List Operations
    # ══════════════════════════════════════════════════════════

    def _insert_chrono(self, note: NoteNode) -> None:
        """Insert note ke sorted list by created_at (ascending)."""
        if not self.chrono_head:
            self.chrono_head = self.chrono_tail = note
            return
        # Cari posisi: urut ascending by timestamp
        curr = self.chrono_head
        while curr and curr.created_at <= note.created_at:
            curr = curr.chrono_next

        if curr is None:
            # Insert di tail
            note.chrono_prev       = self.chrono_tail
            self.chrono_tail.chrono_next = note
            self.chrono_tail       = note
        elif curr is self.chrono_head:
            # Insert di head
            note.chrono_next       = self.chrono_head
            self.chrono_head.chrono_prev = note
            self.chrono_head       = note
        else:
            # Insert di tengah
            prev = curr.chrono_prev
            note.chrono_prev       = prev
            note.chrono_next       = curr
            prev.chrono_next       = note
            curr.chrono_prev       = note

    def _insert_alpha(self, note: NoteNode) -> None:
        """Insert note ke sorted list by title (ascending, case-insensitive)."""
        if not self.alpha_head:
            self.alpha_head = self.alpha_tail = note
            return
        curr = self.alpha_head
        while curr and curr.title.lower() <= note.title.lower():
            curr = curr.alpha_next

        if curr is None:
            note.alpha_prev       = self.alpha_tail
            self.alpha_tail.alpha_next = note
            self.alpha_tail       = note
        elif curr is self.alpha_head:
            note.alpha_next       = self.alpha_head
            self.alpha_head.alpha_prev = note
            self.alpha_head       = note
        else:
            prev = curr.alpha_prev
            note.alpha_prev       = prev
            note.alpha_next       = curr
            prev.alpha_next       = note
            curr.alpha_prev       = note

    def _remove_from_chrono(self, note: NoteNode) -> None:
        """Lepas note dari chrono list (O(1) karena punya prev/next)."""
        if note.chrono_prev:
            note.chrono_prev.chrono_next = note.chrono_next
        else:
            self.chrono_head = note.chrono_next

        if note.chrono_next:
            note.chrono_next.chrono_prev = note.chrono_prev
        else:
            self.chrono_tail = note.chrono_prev

        note.chrono_prev = note.chrono_next = None

    def _remove_from_alpha(self, note: NoteNode) -> None:
        """Lepas note dari alpha list (O(1) karena punya prev/next)."""
        if note.alpha_prev:
            note.alpha_prev.alpha_next = note.alpha_next
        else:
            self.alpha_head = note.alpha_next

        if note.alpha_next:
            note.alpha_next.alpha_prev = note.alpha_prev
        else:
            self.alpha_tail = note.alpha_prev

        note.alpha_prev = note.alpha_next = None

    # ══════════════════════════════════════════════════════════
    # HELPER: Tag Operations
    # ══════════════════════════════════════════════════════════

    def _find_tag(self, name: str) -> Optional[TagNode]:
        curr = self.tag_list_head
        while curr:
            if curr.tag_name == name:
                return curr
            curr = curr.next
        return None

    def _find_or_create_tag(self, name: str) -> TagNode:
        tag = self._find_tag(name)
        if tag:
            return tag
        tag = TagNode(name)
        # Insert di head global tag list (O(1))
        tag.next = self.tag_list_head
        self.tag_list_head = tag
        return tag

    # ══════════════════════════════════════════════════════════
    # HELPER: Display
    # ══════════════════════════════════════════════════════════

    def _print_note_row(self, note: NoteNode) -> None:
        ts   = note.created_at.strftime("%d %b %H:%M")
        tags = ", ".join(t.tag_name for t in note.get_tags())
        sync_icon = {"SYNCED": "✓", "PENDING": "○", "CONFLICT": "✗"}
        icon = sync_icon.get(note.sync_status.value, "?")
        print(f"  {icon} #{note.id:<3} {note.title:<22} "
              f"[{ts}]  tags: {tags or '-'}")


# ─────────────────────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────────────────────

def main():
    import time

    print("\n" + "="*55)
    print("Advanced Linked List\nNote Taking App")
    print("="*55)

    app = NoteApp(buffer_size=8)

    # ── 1. Tambah beberapa note ───────────────────────────────
    print("\n[1] TAMBAH NOTES")
    time.sleep(0.01)
    n1 = app.add_note("Belajar OOP",      "Encapsulation, inheritance, polymorphism")
    time.sleep(0.01)
    n2 = app.add_note("Meeting Notes",    "Agenda: sprint review & retrospective")
    time.sleep(0.01)
    n3 = app.add_note("Algoritma Sort",   "Bubble, merge, quick sort comparison")
    time.sleep(0.01)
    n4 = app.add_note("Resep Kopi",       "Rasio kopi:air = 1:15")
    time.sleep(0.01)
    n5 = app.add_note("Design Patterns",  "Singleton, Factory, Observer")

    # ── 2. Tambah tag ke note (multi-link) ───────────────────
    print("\n[2] TAMBAH TAGS")
    app.add_tag_to_note(n1, "kuliah")
    app.add_tag_to_note(n1, "pemrograman")
    app.add_tag_to_note(n1, "penting")

    app.add_tag_to_note(n2, "kerja")
    app.add_tag_to_note(n2, "penting")

    app.add_tag_to_note(n3, "kuliah")
    app.add_tag_to_note(n3, "pemrograman")
    app.add_tag_to_note(n3, "algoritma")

    app.add_tag_to_note(n4, "personal")
    app.add_tag_to_note(n4, "kuliner")

    app.add_tag_to_note(n5, "kuliah")
    app.add_tag_to_note(n5, "pemrograman")
    app.add_tag_to_note(n5, "penting")

    # ── 3. Views (sorted lists) ───────────────────────────────
    app.print_chronological()
    app.print_chronological(reverse=True)
    app.print_alphabetical()
    app.print_alphabetical(reverse=True)

    # ── 4. Cari notes by tag ──────────────────────────────────
    app.print_notes_by_tag("penting")
    app.print_notes_by_tag("pemrograman")
    app.print_notes_by_tag("kuliner")

    # ── 5. Semua tag ─────────────────────────────────────────
    app.print_all_tags()

    # ── 6. Circular buffer: sync status ──────────────────────
    print("\n[3] UPDATE & SYNC TRACKING")
    app.update_note(n2, title="Sprint Review Notes")
    app.mark_synced(n1)
    app.mark_conflict(n3)
    app.mark_synced(n5)

    app.print_recent_changes()

    # ── 7. Hapus note ────────────────────────────────────────
    print("\n[4] HAPUS NOTE")
    app.delete_note(n4)

    # Verifikasi setelah hapus
    app.print_alphabetical()
    app.print_notes_by_tag("personal")

    # ── 8. Uji buffer overflow ────────────────────────────────
    print("\n[5] UJI CIRCULAR BUFFER OVERFLOW")
    for i in range(6):
        dummy = app.add_note(f"Note Dummy {i+1}", "isi dummy")
        time.sleep(0.01)
    app.print_recent_changes()

    print("\n" + "="*55)
    print("  Demo selesai.")
    print("="*55 + "\n")


if __name__ == "__main__":
    main()