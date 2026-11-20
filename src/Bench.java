import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * Chương trình đo thời gian mergesort theo CUTOFF.
 *
 * Cách dùng: java Bench <thư mục data> <file csv ra> <boxed|prim> <phase: main|extra>
 *
 * Thiết kế đo (xem báo cáo):
 *  - Dữ liệu đọc từ file (cố định, tái lập được). Mỗi lần chạy sao chép dữ liệu gốc ra mảng mới (không tính giờ).
 *  - Khởi động (warm-up) JIT trước khi đo.
 *  - Mỗi "vòng" đo, mỗi CUTOFF chạy đúng 1 lần trên cùng một bộ dữ liệu; thứ tự các CUTOFF được xáo ngẫu nhiên
 *    mỗi vòng (interleaving) để trôi nhiễu của máy/JIT/GC không dồn vào một CUTOFF nào.
 *  - Sau mỗi lần sort kiểm tra mảng đã sắp xếp (ngoài đoạn tính giờ).
 */
public class Bench {
    static final int[] CUTOFFS = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,16,18,20,24,28,32,40,48,64,96,128};

    static int[] readInts(Path p, int n) throws IOException {
        int[] a = new int[n];
        try (BufferedReader br = Files.newBufferedReader(p)) {
            for (int i = 0; i < n; i++) a[i] = Integer.parseInt(br.readLine().trim());
        }
        return a;
    }

    // ---- một lần chạy, trả về nanos ----
    static long runBoxed(Integer[] master, int cutoff) {
        Integer[] a = master.clone();
        long t0 = System.nanoTime();
        Merge.sort(a, cutoff);
        long t = System.nanoTime() - t0;
        if (!Merge.isSorted(a)) throw new IllegalStateException("not sorted, cutoff=" + cutoff);
        return t;
    }
    static long runPrim(int[] master, int cutoff) {
        int[] a = master.clone();
        long t0 = System.nanoTime();
        MergeInt.sort(a, cutoff);
        long t = System.nanoTime() - t0;
        if (!MergeInt.isSorted(a)) throw new IllegalStateException("not sorted, cutoff=" + cutoff);
        return t;
    }

    public static void main(String[] args) throws Exception {
        Path dir = Paths.get(args[0]);
        Path out = Paths.get(args[1]);
        boolean boxed = args[2].equals("boxed");
        String phase = args[3];

        // cấu hình: {kiểu dữ liệu, n, số file(seed), số vòng}
        List<Object[]> configs = new ArrayList<>();
        if (phase.equals("main")) {
            configs.add(new Object[]{"random", 10_000, 5, 100});
            configs.add(new Object[]{"random", 100_000, 5, 50});
            configs.add(new Object[]{"random", 1_000_000, 5, 30});
        } else {
            for (String t : new String[]{"fewdistinct", "nearlysorted", "reversed"}) {
                configs.add(new Object[]{t, 100_000, 1, 30});
                configs.add(new Object[]{t, 1_000_000, 1, 10});
            }
        }

        Random rnd = new Random(12345);
        try (PrintWriter pw = new PrintWriter(Files.newBufferedWriter(out))) {
            pw.println("mode,type,n,file,cutoff,round,nanos");
            for (Object[] cfg : configs) {
                String type = (String) cfg[0];
                int n = (Integer) cfg[1], nfiles = (Integer) cfg[2], rounds = (Integer) cfg[3];

                Integer[][] mb = new Integer[nfiles][];
                int[][] mp = new int[nfiles][];
                for (int f = 0; f < nfiles; f++) {
                    int[] raw = readInts(dir.resolve(type + "_" + n + "_" + f + ".txt"), n);
                    mp[f] = raw;
                    mb[f] = new Integer[n];
                    for (int i = 0; i < n; i++) mb[f][i] = raw[i];
                }

                // warm-up: ~ 3 vòng đầy đủ các cutoff trên dữ liệu này, không ghi lại
                int warm = (n >= 1_000_000) ? 2 : 4;
                for (int w = 0; w < warm; w++)
                    for (int c : CUTOFFS) {
                        if (boxed) runBoxed(mb[w % nfiles], c); else runPrim(mp[w % nfiles], c);
                    }
                System.gc();

                List<Integer> order = new ArrayList<>();
                for (int c : CUTOFFS) order.add(c);

                for (int r = 0; r < rounds; r++) {
                    int f = r % nfiles;
                    Collections.shuffle(order, rnd);
                    for (int c : order) {
                        long t = boxed ? runBoxed(mb[f], c) : runPrim(mp[f], c);
                        pw.println((boxed ? "boxed" : "prim") + "," + type + "," + n + "," + f + "," + c + "," + r + "," + t);
                    }
                    pw.flush();
                }
                System.err.println("done " + (boxed ? "boxed" : "prim") + " " + type + " n=" + n);
            }
        }
    }
}
