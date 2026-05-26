"""
=============================================================
Tugas: Analisis & Desain Algoritma Sorting Lanjutan
Implementasi: AdvancedSorter + ExprHeapSorter
=============================================================
"""

import math
from typing import List, Optional
from collections import deque


# =============================================================
# BAGIAN 1: ADVANCED SORTER
# =============================================================

class ListNode:
    def __init__(self, data, next=None):
        self.data = data
        self.next = next

    def __repr__(self):
        return f"ListNode({self.data})"


class AdvancedSorter:
    """
    Modul pengurutan yang mendukung:
      1. Array Merge Sort (Virtual Sublists + Single tmpArray)  --> O(n log n) waktu, O(n) ruang
      2. Linked List Merge Sort (Fast-Slow + Dummy Merge)       --> O(n log n) waktu, O(log n) ruang
      3. Quick Sort (Median-of-Three Pivot + Fallback)          --> O(n log n) rata-rata
    """

    def __init__(self):
        pass

    # =========================================================
    # 1. ARRAY MERGE SORT (Virtual Sublists + Single tmpArray)
    # =========================================================

    def sort_array(self, arr: List[int]) -> List[int]:
        """
        Mengurutkan array secara ascending menggunakan Merge Sort.
        Hanya mengalokasikan SATU tmpArray berukuran n di awal.
        Tidak membuat sublist fisik di setiap rekursi.

        Kompleksitas Waktu : O(n log n)
        Kompleksitas Ruang : O(n)  -- hanya satu tmpArray

        Args:
            arr: List integer yang akan diurutkan (in-place)

        Returns:
            arr yang sudah terurut ascending
        """
        if len(arr) <= 1:
            return arr
        tmp_array = [0] * len(arr)   # Satu-satunya alokasi tambahan
        self._rec_merge_sort(arr, 0, len(arr) - 1, tmp_array)
        return arr

    def _rec_merge_sort(self, arr: List[int], first: int, last: int, tmp_array: List[int]):
        """
        Rekursi Merge Sort menggunakan indeks virtual (bukan slice fisik).
        Parameter first..last mendefinisikan sublist yang sedang diproses.

        Tidak ada pembuatan array baru di sini -- semua operasi bekerja
        pada rentang indeks di arr dan tmp_array yang sama.
        """
        if first >= last:
            return

        mid = (first + last) // 2

        # Rekursi kiri: arr[first..mid]
        self._rec_merge_sort(arr, first, mid, tmp_array)
        # Rekursi kanan: arr[mid+1..last]
        self._rec_merge_sort(arr, mid + 1, last, tmp_array)
        # Gabungkan dua virtual sublist yang sudah terurut
        self._merge_virtual(arr, first, mid, last, tmp_array)

    def _merge_virtual(self, arr: List[int], left_start: int, mid: int,
                       right_end: int, tmp_array: List[int]):
        """
        Menggabungkan dua virtual sublist yang bersebelahan:
          Kiri  : arr[left_start .. mid]
          Kanan : arr[mid+1 .. right_end]

        Menggunakan tmp_array sebagai buffer sementara.
        Operasi STABLE: elemen kiri diutamakan saat nilai sama (arr[a] <= arr[b]).
        Hasil disalin kembali ke arr[left_start .. right_end].

        Tidak ada alokasi memori tambahan di sini.
        """
        # Salin segmen yang akan dimerge ke tmp_array
        for k in range(left_start, right_end + 1):
            tmp_array[k] = arr[k]

        a = left_start        # pointer ke sublist kiri (di tmp_array)
        b = mid + 1           # pointer ke sublist kanan (di tmp_array)
        k = left_start        # pointer hasil di arr

        # Merge utama: ambil elemen terkecil dari kiri atau kanan
        while a <= mid and b <= right_end:
            # STABLE: gunakan <= sehingga elemen kiri diprioritaskan saat sama
            if tmp_array[a] <= tmp_array[b]:
                arr[k] = tmp_array[a]
                a += 1
            else:
                arr[k] = tmp_array[b]
                b += 1
            k += 1

        # Sisa elemen kiri (jika ada)
        while a <= mid:
            arr[k] = tmp_array[a]
            a += 1
            k += 1

        # Sisa elemen kanan (jika ada)
        # Catatan: jika sisa kanan, posisinya sudah benar di arr -- tidak perlu salin.
        # Namun karena kita sudah salin ke tmp_array, kita salin kembali untuk konsistensi.
        while b <= right_end:
            arr[k] = tmp_array[b]
            b += 1
            k += 1

    # =========================================================
    # 2. LINKED LIST MERGE SORT (Fast-Slow + Dummy Merge)
    # =========================================================

    def sort_linked_list(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Mengurutkan Singly Linked List menggunakan Merge Sort.
        - Hanya memodifikasi pointer .next
        - Tidak mengalokasikan node baru (kecuali 1 dummy node di _merge_linked_lists)
        - Stable sort

        Kompleksitas Waktu : O(n log n)
        Kompleksitas Ruang : O(log n)  -- hanya stack rekursi

        Args:
            head: node pertama linked list

        Returns:
            head baru dari linked list yang sudah terurut
        """
        # Base case: list kosong atau satu elemen -> sudah terurut
        if head is None or head.next is None:
            return head

        # Split menjadi dua sublist menggunakan fast-slow pointer
        right_head = self._split_linked_list(head)
        left_head = head   # head sudah diputus dari right_head

        # Rekursi pada masing-masing sublist
        left_sorted  = self.sort_linked_list(left_head)
        right_sorted = self.sort_linked_list(right_head)

        # Gabungkan dua sublist yang sudah terurut
        return self._merge_linked_lists(left_sorted, right_sorted)

    def _split_linked_list(self, head: ListNode) -> Optional[ListNode]:
        """
        Memisahkan linked list menjadi dua bagian di tengah.

        Teknik Fast-Slow Pointer (Floyd's Tortoise and Hare):
          - midPoint  bergerak 1 langkah per iterasi (tortoise)
          - curNode   bergerak 2 langkah per iterasi (hare)
          Ketika hare mencapai ujung, tortoise berada di tengah.

        Setelah fungsi:
          - Sublist kiri  : head   .. midPoint    (midPoint.next = None)
          - Sublist kanan : return value (awal dari bagian kanan)

        Tidak ada alokasi memori baru.

        Returns:
            head dari sublist kanan
        """
        # Inisialisasi sesuai petunjuk:
        # midPoint mulai di head, curNode mulai di head.next
        # sehingga untuk list genap, kita mendapat split [n/2] dan [n/2]
        midPoint = head
        curNode  = head.next

        # Gerakkan hingga curNode atau curNode.next mencapai None
        while curNode is not None and curNode.next is not None:
            midPoint = midPoint.next   # maju 1
            curNode  = curNode.next.next  # maju 2

        # midPoint sekarang di node tengah
        right_head      = midPoint.next   # head sublist kanan
        midPoint.next   = None            # putus link -> sublist kiri berakhir di midPoint

        return right_head

    def _merge_linked_lists(self, listA: Optional[ListNode],
                            listB: Optional[ListNode]) -> Optional[ListNode]:
        """
        Menggabungkan dua sorted linked list menjadi satu sorted linked list.

        Teknik Dummy Node + Tail Reference:
          - dummy  : node sentinel O(1), tidak dihitung sebagai node data baru
          - tail   : referensi ke node terakhir hasil merge
          Tidak ada alokasi node baru -- hanya memanipulasi pointer .next yang sudah ada.

        STABLE: listA diutamakan saat nilai sama (listA.data <= listB.data).

        Kompleksitas Waktu : O(n+m) per pemanggilan
        Kompleksitas Ruang : O(1)  -- hanya 2 variabel (dummy, tail)

        Returns:
            head dari merged list (= dummy.next)
        """
        # Dummy node sebagai sentinel -- satu-satunya "alokasi" yang diizinkan
        dummy = ListNode(0)
        tail  = dummy

        # Selama kedua list masih ada elemen
        while listA is not None and listB is not None:
            # STABLE: ambil kiri saat sama (<=)
            if listA.data <= listB.data:
                tail.next = listA
                listA     = listA.next
            else:
                tail.next = listB
                listB     = listB.next
            tail = tail.next   # geser tail ke node yang baru ditambahkan

        # Sambungkan sisa list yang belum habis (hanya satu yang bisa non-None)
        tail.next = listA if listA is not None else listB

        return dummy.next   # skip dummy, kembalikan head sebenarnya

    # =========================================================
    # 3. QUICK SORT PARTITION (Median-of-Three Pivot)
    # =========================================================

    def partition_quick(self, arr: List[int], first: int, last: int) -> int:
        """
        Partisi Quick Sort dengan pivot Median-of-Three.

        Strategi Median-of-Three:
          - Kandidat pivot: arr[first], arr[mid], arr[last]
          - Pilih median dari tiga nilai tersebut
          - Tukar median ke posisi first sebagai pivot
          - Jalankan partisi standar (Lomuto/Hoare style)

        Keuntungan vs pivot naif:
          - Menghilangkan worst-case untuk data terurut/terbalik
          - Pivot selalu bukan ekstrem minimum/maksimum dari tiga sampel

        Catatan Stabilitas:
          Partisi Quick Sort secara inheren TIDAK stable karena swap
          dapat mengubah urutan relatif elemen bernilai sama.
          Untuk kebutuhan stable sort, gunakan _merge_virtual.

        Returns:
            Indeks final pivot setelah partisi
        """
        mid = (first + last) // 2

        # === Pilih median dari tiga kandidat ===
        # Urutkan arr[first], arr[mid], arr[last] secara in-place
        # menggunakan maksimal 3 swap, lalu ambil arr[first] sebagai pivot

        # Pastikan arr[first] <= arr[mid]
        if arr[first] > arr[mid]:
            arr[first], arr[mid] = arr[mid], arr[first]

        # Pastikan arr[first] <= arr[last]
        if arr[first] > arr[last]:
            arr[first], arr[last] = arr[last], arr[first]

        # Sekarang arr[first] adalah minimum dari tiga.
        # Pastikan arr[mid] <= arr[last]
        if arr[mid] > arr[last]:
            arr[mid], arr[last] = arr[last], arr[mid]

        # arr[mid] sekarang adalah median -- tukar ke posisi first sebagai pivot
        arr[first], arr[mid] = arr[mid], arr[first]

        # === Partisi standar (Lomuto variant) ===
        pivot = arr[first]
        left  = first + 1
        right = last

        while True:
            # Geser left ke kanan selama arr[left] <= pivot
            while left <= right and arr[left] <= pivot:
                left += 1
            # Geser right ke kiri selama arr[right] > pivot
            while left <= right and arr[right] > pivot:
                right -= 1

            if left > right:
                break   # pointer bertemu -- partisi selesai

            # Tukar elemen yang salah sisi
            arr[left], arr[right] = arr[right], arr[left]
            left  += 1
            right -= 1

        # Tempatkan pivot ke posisi finalnya (right)
        arr[first], arr[right] = arr[right], arr[first]

        return right   # indeks final pivot

    def quick_sort_recursive(self, arr: List[int], first: int, last: int,
                              depth: int = 0):
        """
        Rekursi Quick Sort dengan:
          - Median-of-Three pivot (via partition_quick)
          - Depth limiter: jika depth > 2*log2(n), fallback ke Merge Sort
            untuk mencegah kompleksitas O(n²)

        Args:
            arr   : array yang sedang diurutkan
            first : indeks awal subarray
            last  : indeks akhir subarray
            depth : kedalaman rekursi saat ini
        """
        if first >= last:
            return

        n = last - first + 1   # ukuran subarray saat ini

        # === Depth Limiter (Introsort-style fallback) ===
        max_depth = int(2 * math.log2(len(arr))) if len(arr) > 1 else 0
        if depth > max_depth:
            # Fallback ke Merge Sort (guaranteed O(n log n))
            sub = arr[first:last + 1]
            self.sort_array(sub)
            arr[first:last + 1] = sub
            return

        # Partisi dan dapatkan posisi pivot
        pivot_idx = self.partition_quick(arr, first, last)

        # Rekursi pada dua partisi
        self.quick_sort_recursive(arr, first,          pivot_idx - 1, depth + 1)
        self.quick_sort_recursive(arr, pivot_idx + 1,  last,          depth + 1)

    def sort_array_quicksort(self, arr: List[int]) -> List[int]:
        """
        Interface publik untuk Quick Sort dengan Median-of-Three + fallback.

        Returns:
            arr yang sudah terurut (in-place)
        """
        if len(arr) <= 1:
            return arr
        self.quick_sort_recursive(arr, 0, len(arr) - 1)
        return arr


# =============================================================
# BAGIAN 2: EXPRESSION HEAP SORTER
# =============================================================

class ExprHeapSorter:
    """
    Menggabungkan tiga modul dari Bab 13:
      1. Expression Tree Builder & Evaluator
      2. In-Place Max-Heap Construction
      3. Heapsort In-Place
      4. Complete Tree Validator
    """

    def __init__(self, expr_str: str):
        self.expr   = expr_str
        self.values = []

    # =========================================================
    # 1. EXPRESSION TREE BUILDER & EVALUATOR
    # =========================================================

    def parse_and_evaluate(self) -> List[int]:
        """
        Membangun pohon ekspresi dari string terparentheses penuh,
        mengevaluasi, dan mengembalikan list nilai integer.

        Catatan: untuk ekspresi tunggal (contoh "((8*5)+(9/(7-4)))"),
        fungsi ini mengembalikan [hasil_evaluasi]. Untuk penggunaan
        dengan banyak nilai, tambahkan lebih banyak ekspresi atau
        gunakan add_value() secara manual.

        Returns:
            List berisi hasil evaluasi ekspresi
        """
        # Bersihkan spasi dan buat deque token
        tokens = deque(c for c in self.expr if c != ' ')
        root   = self._build_tree(tokens)
        result = self._eval_tree(root)
        self.values = [int(result)]
        return self.values

    def _build_tree(self, tokens: deque) -> Optional[dict]:
        """
        Membangun pohon ekspresi secara rekursif dari antrian token.

        Format input: ekspresi terparentheses penuh, misalnya:
          ((8 * 5) + (9 / (7 - 4)))

        Algoritma (sesuai Listing 13.9):
          - Jika token saat ini '(' :
              - Build subtree kiri (rekursi)
              - Ambil operator sebagai node
              - Build subtree kanan (rekursi)
              - Konsumsi ')'
              - Return node operator dengan left & right
          - Jika token adalah angka:
              - Return node leaf dengan nilai tersebut
          - Jika token adalah ')' atau None:
              - Return None (base case)

        Node direpresentasikan sebagai dict:
          {'val': <operator atau int>, 'left': <node>, 'right': <node>}
        """
        if not tokens:
            return None

        token = tokens.popleft()

        # Token '(' -> ini adalah ekspresi biner (operand op operand)
        if token == '(':
            left_node = self._build_tree(tokens)    # bangun subtree kiri

            # Ambil operator
            if not tokens:
                raise ValueError("Token tidak valid: operator tidak ditemukan setelah '('")
            operator = tokens.popleft()
            if operator not in ('+', '-', '*', '/'):
                raise ValueError(f"Token tidak valid: '{operator}' bukan operator")

            right_node = self._build_tree(tokens)   # bangun subtree kanan

            # Konsumsi ')' penutup
            if tokens and tokens[0] == ')':
                tokens.popleft()
            # else: diabaikan (beberapa format tidak memiliki ')' eksplisit di akhir)

            return {
                'val'  : operator,
                'left' : left_node,
                'right': right_node
            }

        # Token ')' -> dikonsumsi oleh pemanggil, tidak perlu diproses
        elif token == ')':
            return None

        # Token angka (bisa multi-digit, termasuk negatif)
        else:
            # Kumpulkan digit yang berurutan (untuk angka multi-digit)
            num_str = token
            while tokens and tokens[0].isdigit():
                num_str += tokens.popleft()

            try:
                return {
                    'val'  : int(num_str),
                    'left' : None,
                    'right': None
                }
            except ValueError:
                raise ValueError(f"Token tidak valid: '{num_str}' bukan angka")

    def _eval_tree(self, node: Optional[dict]):
        """
        Evaluasi pohon ekspresi secara postorder (kiri -> kanan -> root).

        Traversal Postorder:
          - Evaluasi subtree kiri
          - Evaluasi subtree kanan
          - Terapkan operator pada kedua hasil

        Mengapa postorder menghasilkan notasi postfix otomatis:
          Karena operator dikunjungi SETELAH kedua operand -- persis
          definisi notasi postfix (Reverse Polish Notation).

        Returns:
            Nilai numerik hasil evaluasi (float/int)

        Raises:
            ValueError: jika terjadi pembagian dengan nol
            ValueError: jika node adalah None (ekspresi tidak lengkap)
        """
        if node is None:
            raise ValueError("Node kosong -- ekspresi tidak lengkap atau tidak valid")

        # Leaf node: kembalikan nilai langsung
        if node['left'] is None and node['right'] is None:
            return node['val']

        # Evaluasi rekursif kedua subtree
        left_val  = self._eval_tree(node['left'])
        right_val = self._eval_tree(node['right'])

        op = node['val']

        if op == '+':
            return left_val + right_val
        elif op == '-':
            return left_val - right_val
        elif op == '*':
            return left_val * right_val
        elif op == '/':
            if right_val == 0:
                raise ValueError("Pembagian dengan nol (division by zero)")
            return left_val / right_val   # gunakan float division
        else:
            raise ValueError(f"Operator tidak dikenal: '{op}'")

    def _build_postfix_string(self, node: Optional[dict]) -> str:
        """
        Menghasilkan notasi postfix (RPN) dari pohon ekspresi.
        Digunakan untuk verifikasi traversal postorder.

        Kedalaman maksimum stack rekursi = O(h) di mana h adalah tinggi pohon.
        """
        if node is None:
            return ''
        if node['left'] is None and node['right'] is None:
            return str(node['val'])

        left_str  = self._build_postfix_string(node['left'])
        right_str = self._build_postfix_string(node['right'])
        return f"{left_str} {right_str} {node['val']}"

    def _build_inorder_string(self, node: Optional[dict]) -> str:
        """
        Menghasilkan notasi infix dengan kurung eksplisit.
        Diperlukan karena inorder tanpa kurung ambigu.
        """
        if node is None:
            return ''
        if node['left'] is None and node['right'] is None:
            return str(node['val'])

        left_str  = self._build_inorder_string(node['left'])
        right_str = self._build_inorder_string(node['right'])
        return f"({left_str} {node['val']} {right_str})"

    def add_value(self, val: int):
        """Tambah nilai manual ke self.values (untuk pengujian heap)."""
        self.values.append(val)

    # =========================================================
    # 2 & 3. IN-PLACE HEAPSORT
    # =========================================================

    def heapsort_inplace(self, arr: List[int]) -> List[int]:
        """
        Mengurutkan array secara ascending menggunakan In-Place Heapsort.

        Dua Fase:
          Fase 1 - Build Max-Heap:
            Iterasi dari node non-leaf terakhir (n//2 - 1) ke akar (0),
            panggil sift_down untuk setiap node. Ini membangun max-heap
            dari daun ke atas dalam O(n).

          Fase 2 - Extract & Sort:
            Swap arr[0] (max) dengan arr[end], kurangi heap_size,
            sift_down dari akar. Ulangi n-1 kali.

        Kompleksitas Waktu : O(n log n)
        Kompleksitas Ruang : O(1)  -- hanya variabel indeks & counter

        Tidak diizinkan: list.sort(), sorted(), heapq, array tambahan.

        Returns:
            arr yang sudah terurut ascending (in-place)
        """
        n = len(arr)
        if n <= 1:
            return arr

        # === Fase 1: Build max-heap ===
        # Mulai dari node non-leaf terakhir, iterasi ke atas
        # n//2 - 1 adalah indeks parent dari node terakhir
        for i in range(n // 2 - 1, -1, -1):
            self._sift_down(arr, n, i)

        # === Fase 2: Extract max satu per satu ===
        for end in range(n - 1, 0, -1):
            # Swap root (max saat ini) dengan elemen terakhir heap
            arr[0], arr[end] = arr[end], arr[0]
            # Pulihkan heap property untuk heap yang dikecilkan (ukuran = end)
            self._sift_down(arr, end, 0)

        return arr

    def _sift_down(self, arr: List[int], heap_size: int, idx: int):
        """
        Memulihkan heap order property dengan mendorong node ke bawah.

        Algoritma:
          - Hitung indeks anak kiri (2*idx+1) dan kanan (2*idx+2)
          - Temukan largest di antara: idx, left, right
          - Jika largest != idx: swap, lanjutkan dari posisi baru
          - Ulangi hingga node berada di posisi yang benar atau jadi leaf

        Jumlah perbandingan maksimum = 2 * ⌊log₂(heap_size)⌋
        (2 perbandingan per level: left vs right, lalu parent vs pemenang)

        Args:
            arr       : array yang merepresentasikan heap
            heap_size : ukuran heap yang aktif (elemen setelahnya sudah terurut)
            idx       : indeks node yang akan di-sift-down
        """
        while True:
            largest = idx
            left    = 2 * idx + 1
            right   = 2 * idx + 2

            # Perbandingan 1: apakah anak kiri lebih besar dari node saat ini?
            if left < heap_size and arr[left] > arr[largest]:
                largest = left

            # Perbandingan 2: apakah anak kanan lebih besar dari pemenang sementara?
            if right < heap_size and arr[right] > arr[largest]:
                largest = right

            # Jika node saat ini sudah terbesar, heap property terpenuhi
            if largest == idx:
                break

            # Swap dan lanjutkan dari posisi baru
            arr[idx], arr[largest] = arr[largest], arr[idx]
            idx = largest

    # =========================================================
    # 4. COMPLETE TREE VALIDATOR
    # =========================================================

    def is_complete_tree(self, arr: List[int]) -> bool:
        """
        Memvalidasi apakah array memenuhi properti Complete Binary Tree.

        Properti Complete Binary Tree:
          Semua level terisi penuh kecuali mungkin level terakhir,
          dan level terakhir diisi dari kiri ke kanan (tanpa "lubang").

        Pendekatan berbasis indeks array:
          Untuk array berukuran n, pemetaan ke pohon biner adalah:
            - Node di indeks i
            - Anak kiri  di 2*i+1
            - Anak kanan di 2*i+2

          Complete binary tree TIDAK memiliki "lubang":
          artinya, jika node di indeks i ada (i < n), maka semua
          node di indeks 0..i-1 juga harus ada.

          Cara deteksi lubang:
          Iterasi level-by-level. Setelah menemukan node None pertama
          (indeks >= n), semua node berikutnya harus juga None.
          Jika ditemukan node non-None setelah node None -> ada lubang.

        Catatan: array yang sudah terurut (hasil heapsort) biasanya BUKAN
        max-heap, tapi masih bisa merupakan complete binary tree secara struktur.

        Returns:
            True  jika merupakan complete binary tree
            False jika ada "lubang" dalam pemetaan
        """
        n = len(arr)
        if n == 0:
            return True

        # BFS-style traversal menggunakan indeks
        found_none = False   # apakah sudah menemukan "celah" pertama

        for i in range(n):
            left  = 2 * i + 1
            right = 2 * i + 2

            # Periksa anak kiri
            if left < n:
                if found_none:
                    return False   # ada node setelah celah -> tidak complete
            else:
                found_none = True   # indeks left >= n -> celah pertama ditemukan

            # Periksa anak kanan
            if right < n:
                if found_none:
                    return False
            else:
                found_none = True

        return True

    def is_max_heap(self, arr: List[int]) -> bool:
        """
        Validasi tambahan: apakah array memenuhi properti Max-Heap.
        Setiap parent harus >= kedua anaknya.

        Returns:
            True jika arr adalah valid max-heap
        """
        n = len(arr)
        for i in range(n // 2):
            left  = 2 * i + 1
            right = 2 * i + 2
            if left < n and arr[i] < arr[left]:
                return False
            if right < n and arr[i] < arr[right]:
                return False
        return True


# =============================================================
# FUNGSI HELPER: Linked List Utilities
# =============================================================

def build_linked_list(data_list: list) -> Optional[ListNode]:
    """Membangun linked list dari Python list. Helper untuk testing."""
    if not data_list:
        return None
    head = ListNode(data_list[0])
    cur  = head
    for val in data_list[1:]:
        cur.next = ListNode(val)
        cur = cur.next
    return head


def linked_list_to_list(head: Optional[ListNode]) -> list:
    """Mengubah linked list ke Python list. Helper untuk testing."""
    result = []
    cur = head
    while cur:
        result.append(cur.data)
        cur = cur.next
    return result


# =============================================================
# DEMO & PENGUJIAN
# =============================================================

def demo_advanced_sorter():
    print("=" * 60)
    print("DEMO: AdvancedSorter")
    print("=" * 60)

    sorter = AdvancedSorter()

    # --- 1. Array Merge Sort ---
    print("\n[1] Array Merge Sort (Virtual Sublists + Single tmpArray)")
    test_cases_array = [
        [64, 34, 25, 12, 22, 11, 90],
        [5, 5, 3, 3, 1, 1, 2, 2],     # elemen duplikat (uji stabilitas)
        [1],                            # satu elemen
        [],                             # list kosong
        [3, 1, 4, 1, 5, 9, 2, 6, 5],
    ]
    for arr in test_cases_array:
        original = arr.copy()
        result   = sorter.sort_array(arr.copy())
        print(f"  Input : {original}")
        print(f"  Output: {result}")
        print(f"  Valid : {result == sorted(original)}")
        print()

    # --- 2. Linked List Merge Sort ---
    print("[2] Linked List Merge Sort (Fast-Slow + Dummy Merge)")
    test_cases_ll = [
        [4, 2, 7, 1, 9, 3],
        [5, 5, 3, 3],                  # duplikat
        [1],
        [2, 1],
        [9, 8, 7, 6, 5, 4, 3, 2, 1],  # descending
    ]
    for data in test_cases_ll:
        ll     = build_linked_list(data)
        sorted_ll = sorter.sort_linked_list(ll)
        result = linked_list_to_list(sorted_ll)
        print(f"  Input : {data}")
        print(f"  Output: {result}")
        print(f"  Valid : {result == sorted(data)}")
        print()

    # --- 3. Quick Sort ---
    print("[3] Quick Sort (Median-of-Three + Depth Limiter Fallback)")
    test_cases_qs = [
        [64, 34, 25, 12, 22, 11, 90],
        [9, 8, 7, 6, 5, 4, 3, 2, 1],   # descending (worst-case untuk pivot naif)
        [1, 2, 3, 4, 5, 6, 7, 8, 9],   # ascending
        [5, 5, 5, 5, 5],                # semua sama
    ]
    for arr in test_cases_qs:
        original = arr.copy()
        result   = sorter.sort_array_quicksort(arr.copy())
        print(f"  Input : {original}")
        print(f"  Output: {result}")
        print(f"  Valid : {result == sorted(original)}")
        print()


def demo_expr_heap_sorter():
    print("=" * 60)
    print("DEMO: ExprHeapSorter")
    print("=" * 60)

    # --- Ekspresi dari soal: ((8 * 5) + (9 / (7 - 4))) ---
    expr_str = "((8*5)+(9/(7-4)))"
    print(f"\n[1] Expression Tree: {expr_str}")

    ehs  = ExprHeapSorter(expr_str)
    toks = deque(c for c in expr_str if c != ' ')
    root = ehs._build_tree(toks)

    postfix = ehs._build_postfix_string(root)
    infix   = ehs._build_inorder_string(root)
    result  = ehs._eval_tree(root)

    print(f"  Notasi Postfix : {postfix}")
    print(f"  Notasi Infix   : {infix}")
    print(f"  Hasil Evaluasi : {result}")
    print(f"  Verifikasi     : 8*5 + 9/(7-4) = 40 + 3.0 = {8*5 + 9/(7-4)}")

    # --- Heapsort ---
    print("\n[2] In-Place Heapsort")
    test_arrays = [
        [10, 43, int(result), 7, 22, 55, 3, 18],
        [5, 1, 9, 3, 7, 2, 8, 4, 6],
        [1],
        [3, 3, 3],
    ]

    for arr in test_arrays:
        original = arr.copy()
        sorted_arr = ehs.heapsort_inplace(arr.copy())
        print(f"  Input  : {original}")
        print(f"  Output : {sorted_arr}")
        print(f"  Valid  : {sorted_arr == sorted(original)}")

        # Validasi complete tree
        is_ct = ehs.is_complete_tree(sorted_arr)
        print(f"  Complete Tree: {is_ct}")
        print()

    # --- Max-Heap Test ---
    print("[3] Max-Heap Validation")
    heap_arr = [15, 10, 12, 7, 8, 9, 11]
    print(f"  Array : {heap_arr}")
    print(f"  Is Max-Heap    : {ehs.is_max_heap(heap_arr)}")
    print(f"  Is Complete    : {ehs.is_complete_tree(heap_arr)}")

    not_heap = [5, 10, 3]
    print(f"\n  Array : {not_heap}")
    print(f"  Is Max-Heap    : {ehs.is_max_heap(not_heap)}")

    # --- Division by Zero Test ---
    print("\n[4] Error Handling: Division by Zero")
    expr_divzero = "((5/(3-3))+1)"
    try:
        ehs2  = ExprHeapSorter(expr_divzero)
        toks2 = deque(c for c in expr_divzero if c != ' ')
        root2 = ehs2._build_tree(toks2)
        ehs2._eval_tree(root2)
    except ValueError as e:
        print(f"  Ekspresi: {expr_divzero}")
        print(f"  Error   : {e}")


if __name__ == "__main__":
    demo_advanced_sorter()
    print()
    demo_expr_heap_sorter()
