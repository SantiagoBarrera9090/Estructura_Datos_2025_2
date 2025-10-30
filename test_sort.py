from sorting import merge_sort_linkedlist, quick_sort_linkedlist
from structures import LinkedList

# crear lista de numeros como objetos simples
class X:
    def __init__(self,v):
        self.v=v
    def __repr__(self):
        return f'X({self.v})'

ll=LinkedList()
for v in [5,1,3,2,4]:
    ll.append(X(v))

print('Original: ', [x for x in ll])
ms=merge_sort_linkedlist(ll, keyfn=lambda r: r.v)
print('Merge sorted:', [x for x in ms])
qs=quick_sort_linkedlist(ll, keyfn=lambda r: r.v)
print('Quick sorted:', [x for x in qs])
