#!/usr/bin/env python3
"""Sinh bộ dữ liệu thí nghiệm (tái lập được: seed cố định).
Mỗi file: n số nguyên, mỗi dòng một số.
  random_<n>_<k>.txt       : số nguyên ngẫu nhiên đều trên [0, 2^31-1), 5 file (seed khác nhau) mỗi n
  fewdistinct_<n>_0.txt    : chỉ 10 giá trị khác nhau (nhiều khoá trùng)
  nearlysorted_<n>_0.txt   : mảng đã sắp, rồi hoán vị ngẫu nhiên 1% cặp
  reversed_<n>_0.txt       : giảm dần
"""
import random, sys, os
out = sys.argv[1] if len(sys.argv) > 1 else "data"
os.makedirs(out, exist_ok=True)

def write(name, arr):
    with open(os.path.join(out, name), "w") as f:
        f.write("\n".join(map(str, arr))); f.write("\n")

for n in (10_000, 100_000, 1_000_000):
    for k in range(5):
        rng = random.Random(1000 * n + k)
        write(f"random_{n}_{k}.txt", [rng.randrange(2**31 - 1) for _ in range(n)])

for n in (100_000, 1_000_000):
    rng = random.Random(7 * n)
    write(f"fewdistinct_{n}_0.txt", [rng.randrange(10) for _ in range(n)])
    a = list(range(n))
    for _ in range(n // 100):
        i, j = rng.randrange(n), rng.randrange(n)
        a[i], a[j] = a[j], a[i]
    write(f"nearlysorted_{n}_0.txt", a)
    write(f"reversed_{n}_0.txt", list(range(n, 0, -1)))
print("ok")
