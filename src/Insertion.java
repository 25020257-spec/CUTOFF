/**
 * Insertion sort cho đoạn a[lo..hi] (theo bài giảng Elementary Sorts, Sedgewick & Wayne).
 */
public class Insertion {
    @SuppressWarnings({"rawtypes", "unchecked"})
    private static boolean less(Comparable v, Comparable w) { return v.compareTo(w) < 0; }

    private static void exch(Object[] a, int i, int j) { Object t = a[i]; a[i] = a[j]; a[j] = t; }

    @SuppressWarnings("rawtypes")
    public static void sort(Comparable[] a, int lo, int hi) {
        for (int i = lo; i <= hi; i++)
            for (int j = i; j > lo && less(a[j], a[j - 1]); j--)
                exch(a, j, j - 1);
    }

    // Biến thể int[] (dùng cho thí nghiệm phụ)
    public static void sort(int[] a, int lo, int hi) {
        for (int i = lo; i <= hi; i++)
            for (int j = i; j > lo && a[j] < a[j - 1]; j--) {
                int t = a[j]; a[j] = a[j - 1]; a[j - 1] = t;
            }
    }
}
