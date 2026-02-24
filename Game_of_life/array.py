#ARRAY
# Membuat array satu dimensi yang terdiri dari sejumlah elemen sesuai dengan nilai size, di mana setiap elemen pada awalnya diset ke nilai None. Nilai size harus lebih besar dari nol.
class Array:
    def __init__(self, size):
        if size <= 0:
            raise ValueError

        self.size = size
        self.data = [None] * size 

    def setitem(self, index, value): #Mengubah isi elemen array pada posisi indeks tertentu agar berisi nilai value
        if 0 <= index < self.size:
            self.data[index] = value
        else:
            raise IndexError

    def getitem(self, index): #Mengembalikan nilai yang tersimpan dalam array pada posisi indeks tertentu. 
        if 0 <= index < self.size:
            return self.data[index]
        else:
            raise IndexError

    def length(self): #Mengembalikan panjang atau jumlah elemen yang ada dalam array.
        return self.size
    
    def iterator(self): #Membuat dan mengembalikan sebuah iterator yang dapat digunakan untuk menelusuri (traverse) elemen-elemen dalam array.
        return iter(self.data)
    
    def clearing(self, value): #Mengosongkan array 
        for i in range(self.size): 
            self.data[i] = value

    def display(self):

        print(self.data)


arr = Array(5)

print("Array awal:")
arr.display()

arr.setitem(0, 10)
arr.setitem(1, 20)
arr.setitem(2, 30)

print("Array setelah diisi:")
arr.display()

print("Nilai index ke-1:", arr.getitem(1))
print("Panjang array:", arr.length())

print("\n Menelusuri dengan iterator:")
for item in arr.iterator():
    print(item)

print("\n Sebelum Clearing:")
arr.display()
arr.clearing(0)
print("\n Setelah Clearing:")
arr.display()


# 
