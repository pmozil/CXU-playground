#!/usr/bin/env bash

set -e

BINARY="gzip"
OUT="gzip_benchmark.csv"
TMPDIR=$(mktemp -d)

echo "size_kb,decompress_time_sec" > "$OUT"

for ((kb=10; kb<=20480; kb+=10)); do
    file="$TMPDIR/input_${kb}k"
    gz="$file.gz"

    # Generate random file
    dd if=/dev/urandom of="$file" bs=1K count=$kb status=none

    # Compress
    gzip -c "$file" > "$gz"

    # Measure decompression time
    start=$(date +%s.%N)

    $BINARY -dc "$gz" > /dev/null

    end=$(date +%s.%N)

    time=$(echo "$end - $start" | bc)

    echo "$kb,$time" >> "$OUT"

    rm -f "$file" "$gz"

    echo "Processed ${kb}KB"
done

rm -rf "$TMPDIR"

echo "Benchmark complete. Results saved to $OUT"
