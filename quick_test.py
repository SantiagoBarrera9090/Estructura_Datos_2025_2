from main import load_csv
from structures import AVLTree

if __name__ == '__main__':
    tree, ll, stk, q, stats = load_csv('BusinessData.csv')
    print('stats:', stats)
    idx = AVLTree(keyfn=lambda r: getattr(r, 'country', None))
    count = 0
    for rec in ll:
        idx.insert(rec)
    print('First 5 countries and counts:')
    c = 0
    for key, records in idx.items():
        print(key, records.size())
        c += 1
        if c >= 5:
            break
    print('Done')
