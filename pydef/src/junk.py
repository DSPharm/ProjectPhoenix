#def impartire(x, y):
    
print(ecuatie_gradul_2(3,-1,-2))


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

for z in range(len(lista)):
    print (z+1)
