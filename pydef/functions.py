def cub(x):
    return x**3


lista = []
while True:
    x = (input("Introdu un element: "))
    if x == "0":
        break
    lista.append(int(x))
    

print(lista)
x = 1
for i in lista:
    print("Cubul numarului", x, ": ", cub(i))
    x +=1
