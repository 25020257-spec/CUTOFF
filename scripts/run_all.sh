#!/usr/bin/env bash
# Chạy toàn bộ thí nghiệm. Dùng: bash scripts/run_all.sh   (từ thư mục gốc của project)
set -e
cd "$(dirname "$0")/.."
python3 scripts/gen_data.py data
mkdir -p build results
javac -d build src/*.java
java -cp build TestMerge
JOPT="-Xms3g -Xmx3g -XX:+UseParallelGC"
java $JOPT -cp build Bench data results/raw_boxed_main.csv  boxed main
java $JOPT -cp build Bench data results/raw_prim_main.csv   prim  main
java $JOPT -cp build Bench data results/raw_boxed_extra.csv boxed extra
echo ALL_DONE
