# TUGAS PRAKTIKUM - Big Integer ADT

# Big Integer dengan Singly Linked List

class Node:
    # Node untuk singly linked list
    def __init__(self, digit):
        self.digit = digit   # Menyimpan 1 digit (0-9)
        self.next = None     # Pointer ke node berikutnya


class BigIntegerLinkedList:

    def __init__(self, initValue="0"):
        # Membuat BigInteger dari string angka
        self.head = None
        self.negative = False

        # Cek tanda negatif
        s = str(initValue).strip()
        if s.startswith('-'):
            self.negative = True
            s = s[1:]
        elif s.startswith('+'):
            s = s[1:]

        # Hapus leading zeros kecuali "0"
        s = s.lstrip('0') or '0'

        # Simpan digit dari kanan ke kiri (LSD -> MSD)
        # Sehingga head = digit terkecil (LSD)
        for ch in reversed(s):
            self._append_digit(int(ch))

    # ── Helper: tambah node di akhir list ──
    def _append_digit(self, digit):
        new_node = Node(digit)
        if self.head is None:
            self.head = new_node
        else:
            curr = self.head
            while curr.next:
                curr = curr.next
            curr.next = new_node

    # ── Helper: ambil semua digit sebagai list (LSD first) ──
    def _get_digits(self):
        digits = []
        curr = self.head
        while curr:
            digits.append(curr.digit)
            curr = curr.next
        return digits  # index 0 = LSD

    # ── Helper: buat BigInteger dari list digit (LSD first) ──
    @staticmethod
    def _from_digits(digits, negative=False):
        # Buang trailing zeros (= leading zeros pada angka)
        while len(digits) > 1 and digits[-1] == 0:
            digits.pop()
        s = ''.join(str(d) for d in reversed(digits))
        if negative and s != '0':
            s = '-' + s
        return BigIntegerLinkedList(s)

    # toString(): mengembalikan representasi string

    def toString(self):
        digits = self._get_digits()  # LSD first
        result = ''.join(str(d) for d in reversed(digits))  # MSD first
        if self.negative and result != '0':
            return '-' + result
        return result

    def __repr__(self):
        return f"BigInteger({self.toString()})"

    # comparable(other): perbandingan logis
    # Mengembalikan -1, 0, atau 1

    def comparable(self, other):
        a = int(self.toString())
        b = int(other.toString())
        if a < b:
            return -1
        elif a > b:
            return 1
        return 0

    def __lt__(self, other):  return self.comparable(other) == -1
    def __le__(self, other):  return self.comparable(other) <= 0
    def __gt__(self, other):  return self.comparable(other) == 1
    def __ge__(self, other):  return self.comparable(other) >= 0
    def __eq__(self, other):  return self.comparable(other) == 0
    def __ne__(self, other):  return self.comparable(other) != 0

    # arithmetic(rhsInt): operasi aritmatika
    # Mendukung: +  -  *  //  %  **

    def arithmetic(self, rhsInt, op):
        a = int(self.toString())
        b = int(rhsInt.toString())
        ops = {
            '+':  lambda x, y: x + y,
            '-':  lambda x, y: x - y,
            '*':  lambda x, y: x * y,
            '//': lambda x, y: x // y,
            '%':  lambda x, y: x % y,
            '**': lambda x, y: x ** y,
        }
        if op not in ops:
            raise ValueError(f"Operasi tidak dikenal: {op}")
        result = ops[op](a, b)
        return BigIntegerLinkedList(str(result))

    def __add__(self, other):  return self.arithmetic(other, '+')
    def __sub__(self, other):  return self.arithmetic(other, '-')
    def __mul__(self, other):  return self.arithmetic(other, '*')
    def __floordiv__(self, other): return self.arithmetic(other, '//')
    def __mod__(self, other):  return self.arithmetic(other, '%')
    def __pow__(self, other):  return self.arithmetic(other, '**')

    # bitwise_ops(rhsInt): operasi bitwise
    # Mendukung: |  &  ^  <<  >>

    def bitwise_ops(self, rhsInt, op):
        a = int(self.toString())
        b = int(rhsInt.toString())
        ops = {
            '|':  lambda x, y: x | y,
            '&':  lambda x, y: x & y,
            '^':  lambda x, y: x ^ y,
            '<<': lambda x, y: x << y,
            '>>': lambda x, y: x >> y,
        }
        if op not in ops:
            raise ValueError(f"Operasi tidak dikenal: {op}")
        result = ops[op](a, b)
        return BigIntegerLinkedList(str(result))

    def __or__(self, other):    return self.bitwise_ops(other, '|')
    def __and__(self, other):   return self.bitwise_ops(other, '&')
    def __xor__(self, other):   return self.bitwise_ops(other, '^')
    def __lshift__(self, other):return self.bitwise_ops(other, '<<')
    def __rshift__(self, other):return self.bitwise_ops(other, '>>')

    # Assignment Combo Operators

    def __iadd__(self, other):
        result = self.arithmetic(other, '+')
        self.__dict__.update(result.__dict__)
        return self

    def __isub__(self, other):
        result = self.arithmetic(other, '-')
        self.__dict__.update(result.__dict__)
        return self

    def __imul__(self, other):
        result = self.arithmetic(other, '*')
        self.__dict__.update(result.__dict__)
        return self

    def __ifloordiv__(self, other):
        result = self.arithmetic(other, '//')
        self.__dict__.update(result.__dict__)
        return self

    def __imod__(self, other):
        result = self.arithmetic(other, '%')
        self.__dict__.update(result.__dict__)
        return self

    def __ipow__(self, other):
        result = self.arithmetic(other, '**')
        self.__dict__.update(result.__dict__)
        return self

    def __ilshift__(self, other):
        result = self.bitwise_ops(other, '<<')
        self.__dict__.update(result.__dict__)
        return self

    def __irshift__(self, other):
        result = self.bitwise_ops(other, '>>')
        self.__dict__.update(result.__dict__)
        return self

    def __ior__(self, other):
        result = self.bitwise_ops(other, '|')
        self.__dict__.update(result.__dict__)
        return self

    def __iand__(self, other):
        result = self.bitwise_ops(other, '&')
        self.__dict__.update(result.__dict__)
        return self

    def __ixor__(self, other):
        result = self.bitwise_ops(other, '^')
        self.__dict__.update(result.__dict__)
        return self

    # Visualisasi struktur linked list 
    def print_linked_list(self):
        """Tampilkan struktur linked list secara visual."""
        curr = self.head
        nodes = []
        while curr:
            nodes.append(f"[{curr.digit}|•]")
            curr = curr.next
        print("head -> " + " -> ".join(nodes) + " -> None")
        print(f"(merepresentasikan angka: {self.toString()})")


# Big Integer dengan Python List

class BigIntegerList:

    def __init__(self, initValue="0"):
        self.digits = []
        self.negative = False

        s = str(initValue).strip()
        if s.startswith('-'):
            self.negative = True
            s = s[1:]
        elif s.startswith('+'):
            s = s[1:]

        s = s.lstrip('0') or '0'

        # Simpan digit dari kanan ke kiri (LSD -> MSD)
        for ch in reversed(s):
            self.digits.append(int(ch))

    def toString(self):
        result = ''.join(str(d) for d in reversed(self.digits))
        if self.negative and result != '0':
            return '-' + result
        return result

    def __repr__(self):
        return f"BigIntegerList({self.toString()})"

    def comparable(self, other):
        a = int(self.toString())
        b = int(other.toString())
        return (a > b) - (a < b)  # -1, 0, 1

    def __lt__(self, other):  return self.comparable(other) == -1
    def __le__(self, other):  return self.comparable(other) <= 0
    def __gt__(self, other):  return self.comparable(other) == 1
    def __ge__(self, other):  return self.comparable(other) >= 0
    def __eq__(self, other):  return self.comparable(other) == 0
    def __ne__(self, other):  return self.comparable(other) != 0

    def arithmetic(self, rhsInt, op):
        a = int(self.toString())
        b = int(rhsInt.toString())
        ops = {'+': a+b, '-': a-b, '*': a*b, '//': a//b, '%': a%b, '**': a**b}
        if op not in ops:
            raise ValueError(f"Operasi tidak dikenal: {op}")
        return BigIntegerList(str(ops[op]))

    def __add__(self, other):      return self.arithmetic(other, '+')
    def __sub__(self, other):      return self.arithmetic(other, '-')
    def __mul__(self, other):      return self.arithmetic(other, '*')
    def __floordiv__(self, other): return self.arithmetic(other, '//')
    def __mod__(self, other):      return self.arithmetic(other, '%')
    def __pow__(self, other):      return self.arithmetic(other, '**')

    def bitwise_ops(self, rhsInt, op):
        a = int(self.toString())
        b = int(rhsInt.toString())
        ops = {'|': a|b, '&': a&b, '^': a^b, '<<': a<<b, '>>': a>>b}
        if op not in ops:
            raise ValueError(f"Operasi tidak dikenal: {op}")
        return BigIntegerList(str(ops[op]))

    def __or__(self, other):     return self.bitwise_ops(other, '|')
    def __and__(self, other):    return self.bitwise_ops(other, '&')
    def __xor__(self, other):    return self.bitwise_ops(other, '^')
    def __lshift__(self, other): return self.bitwise_ops(other, '<<')
    def __rshift__(self, other): return self.bitwise_ops(other, '>>')

    # Assignment Combo Operators
    def __iadd__(self, other):
        r = self.arithmetic(other, '+'); self.__dict__.update(r.__dict__); return self
    def __isub__(self, other):
        r = self.arithmetic(other, '-'); self.__dict__.update(r.__dict__); return self
    def __imul__(self, other):
        r = self.arithmetic(other, '*'); self.__dict__.update(r.__dict__); return self
    def __ifloordiv__(self, other):
        r = self.arithmetic(other, '//'); self.__dict__.update(r.__dict__); return self
    def __imod__(self, other):
        r = self.arithmetic(other, '%'); self.__dict__.update(r.__dict__); return self
    def __ipow__(self, other):
        r = self.arithmetic(other, '**'); self.__dict__.update(r.__dict__); return self
    def __ilshift__(self, other):
        r = self.bitwise_ops(other, '<<'); self.__dict__.update(r.__dict__); return self
    def __irshift__(self, other):
        r = self.bitwise_ops(other, '>>'); self.__dict__.update(r.__dict__); return self
    def __ior__(self, other):
        r = self.bitwise_ops(other, '|'); self.__dict__.update(r.__dict__); return self
    def __iand__(self, other):
        r = self.bitwise_ops(other, '&'); self.__dict__.update(r.__dict__); return self
    def __ixor__(self, other):
        r = self.bitwise_ops(other, '^'); self.__dict__.update(r.__dict__); return self


if __name__ == "__main__":

    #Big Integer dengan Singly Linked List
    a = BigIntegerLinkedList("45839")
    b = BigIntegerLinkedList("12345")

    print("\n Struktur Linked List")
    print("a =", a.toString(), "->", end=" ")
    a.print_linked_list()
    print("b =", b.toString(), "->", end=" ")
    b.print_linked_list()

    print("\n toString()")
    print("a.toString() =", a.toString())
    print("b.toString() =", b.toString())

    print("\n comparable()")
    print(f"a.comparable(b) = {a.comparable(b)}  (1 = a lebih besar)")
    print(f"a > b  : {a > b}")
    print(f"a < b  : {a < b}")
    print(f"a == b : {a == b}")

    print("\n arithmetic()")
    print(f"a + b  = {a.arithmetic(b, '+').toString()}")
    print(f"a - b  = {a.arithmetic(b, '-').toString()}")
    print(f"a * b  = {a.arithmetic(b, '*').toString()}")
    print(f"a // b = {a.arithmetic(b, '//').toString()}")
    print(f"a % b  = {a.arithmetic(b, '%').toString()}")
    print(f"a ** 2 = {a.arithmetic(BigIntegerLinkedList('2'), '**').toString()}")

    print("\n bitwise_ops()")
    x = BigIntegerLinkedList("60")   # 0b111100
    y = BigIntegerLinkedList("13")   # 0b001101
    print(f"x={x.toString()}, y={y.toString()}")
    print(f"x | y  = {x.bitwise_ops(y, '|').toString()}")
    print(f"x & y  = {x.bitwise_ops(y, '&').toString()}")
    print(f"x ^ y  = {x.bitwise_ops(y, '^').toString()}")
    print(f"x << 2 = {x.bitwise_ops(BigIntegerLinkedList('2'), '<<').toString()}")
    print(f"x >> 2 = {x.bitwise_ops(BigIntegerLinkedList('2'), '>>').toString()}")

    print("\n")
    print("Assignment Combo Operators (Linked List)")

    c = BigIntegerLinkedList("100")
    d = BigIntegerLinkedList("30")
    print(f"c = {c.toString()}, d = {d.toString()}")

    c += d;  print(f"c += d   -> c = {c.toString()}")
    c -= d;  print(f"c -= d   -> c = {c.toString()}")
    c *= d;  print(f"c *= d   -> c = {c.toString()}")
    c //= d; print(f"c //= d  -> c = {c.toString()}")
    c %= d;  print(f"c %= d   -> c = {c.toString()}")

    e = BigIntegerLinkedList("2")
    c = BigIntegerLinkedList("3")
    c **= e; print(f"3 **= 2  -> c = {c.toString()}")

    f = BigIntegerLinkedList("60")
    g = BigIntegerLinkedList("2")
    f <<= g; print(f"60 <<= 2 -> f = {f.toString()}")
    f >>= g; print(f"240 >>= 2-> f = {f.toString()}")

    h = BigIntegerLinkedList("60")
    i = BigIntegerLinkedList("13")
    h |= i;  print(f"60 |= 13 -> h = {h.toString()}")
    h = BigIntegerLinkedList("60")
    h &= i;  print(f"60 &= 13 -> h = {h.toString()}")
    h = BigIntegerLinkedList("60")
    h ^= i;  print(f"60 ^= 13 -> h = {h.toString()}")

    print("\n")
    print("Big Integer dengan Python List")

    p = BigIntegerList("99999999999999999999")   # lebih dari 19 digit!
    q = BigIntegerList("1")
    print(f"p          = {p.toString()}")
    print(f"q          = {q.toString()}")
    print(f"p + q      = {(p + q).toString()}")
    print(f"p.digits   = {p.digits}  (index 0 = LSD)")

    print("\n Operator Python List - combo assignment")
    p += q
    print(f"p += q     -> p = {p.toString()}")
    print("\nSelesai")