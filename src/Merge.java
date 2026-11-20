/**
 * Mergesort top-down dựng từ bài giảng "2.2 Mergesort":
 *  - merge(a, aux, lo, mid, hi): copy sang aux rồi trộn ngược về a
 *  - sort(a, aux, lo, hi): đệ quy, với cải tiến CUTOFF sang insertion sort
 *      if (hi <= lo + CUTOFF - 1) { Insertion.sort(a, lo, hi); return; }
 * CUTOFF được truyền như tham số (thay vì static final) để một chương trình
 * thí nghiệm có thể quét nhiều giá trị. CUTOFF = 1 tương đương mergesort thuần
 * (đoạn 1 phần tử thì dừng, giống "if (hi <= lo) return").
 * Không dùng các cải tiến khác (kiểm tra đã sắp xếp, đổi vai aux/a) để chỉ đo riêng CUTOFF.
 */
@SuppressWarnings({"rawtypes", "unchecked"})
public class Merge {
    private static boolean less(Comparable v, Comparable w) { return v.compareTo(w) < 0; }

    private static void merge(Comparable[] a, Comparable[] aux, int lo, int mid, int hi) {
        for (int k = lo; k <= hi; k++)
            aux[k] = a[k];

        int i = lo, j = mid + 1;
        for (int k = lo; k <= hi; k++) {
            if      (i > mid)              a[k] = aux[j++];
            else if (j > hi)               a[k] = aux[i++];
            else if (less(aux[j], aux[i])) a[k] = aux[j++];
            else                           a[k] = aux[i++];
        }
    }

    private static void sort(Comparable[] a, Comparable[] aux, int lo, int hi, int cutoff) {
        if (hi <= lo + cutoff - 1) {
            Insertion.sort(a, lo, hi);
            return;
        }
        int mid = lo + (hi - lo) / 2;
        sort(a, aux, lo, mid, cutoff);
        sort(a, aux, mid + 1, hi, cutoff);
        merge(a, aux, lo, mid, hi);
    }

    public static void sort(Comparable[] a, int cutoff) {
        Comparable[] aux = new Comparable[a.length];
        sort(a, aux, 0, a.length - 1, cutoff);
    }

    public static boolean isSorted(Comparable[] a) {
        for (int i = 1; i < a.length; i++)
            if (less(a[i], a[i - 1])) return false;
        return true;
    }
}
