import java.util.*;
/** Kiểm tra tính đúng đắn: mọi CUTOFF, nhiều kích thước (kể cả 0,1,2), so với Arrays.sort. */
public class TestMerge {
    public static void main(String[] args) {
        Random r = new Random(1);
        int checks = 0;
        int[] sizes = {0,1,2,3,5,7,8,10,11,15,16,17,100,1000,4097};
        for (int n : sizes) for (int c : Bench.CUTOFFS) for (int rep = 0; rep < 5; rep++) {
            int[] raw = new int[n];
            for (int i = 0; i < n; i++) raw[i] = r.nextInt(rep == 0 ? 5 : 1000000);
            int[] exp = raw.clone(); Arrays.sort(exp);
            Integer[] b = new Integer[n]; for (int i = 0; i < n; i++) b[i] = raw[i];
            Merge.sort(b, c);
            int[] p = raw.clone(); MergeInt.sort(p, c);
            for (int i = 0; i < n; i++)
                if (b[i] != exp[i] || p[i] != exp[i]) throw new AssertionError("n=" + n + " cutoff=" + c);
            checks++;
        }
        System.out.println("OK: " + checks + " test cases passed");
    }
}
