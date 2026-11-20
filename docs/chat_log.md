# Log làm việc với AI (Claude) — tóm tắt



**Yêu cầu của sinh viên:** Làm thí nghiệm tìm CUTOFF tốt nhất cho mergesort (đề đính kèm: bài giảng Stacks & Queues, Mergesort, Quicksort). Được dùng AI để thảo luận, viết script, dựng bộ test; mergesort phải dựng từ bài giảng. Nộp: báo cáo, mã + script, bộ dữ liệu, log chat.

**Các bước AI đã làm**
1. Đọc slide Mergesort (trang `merge`, `sort`, cải tiến CUTOFF `if (hi <= lo + CUTOFF - 1) Insertion.sort(...)`) và slide Quicksort (cùng cải tiến CUTOFF).
2. Chọn Java; cài `Merge.java` theo đúng mã trong slide (CUTOFF làm tham số), `Insertion.java` (dạng chuẩn Sedgewick–Wayne), biến thể `int[]` cho thí nghiệm phụ; viết `TestMerge.java` (1875 case so với `Arrays.sort`).
3. Thiết kế thí nghiệm: 25 giá trị CUTOFF (có 7, 10); n = 10⁴, 10⁵, 10⁶; 5 file ngẫu nhiên mỗi n + 3 loại dữ liệu phụ; warm-up JIT; mỗi vòng xáo ngẫu nhiên thứ tự CUTOFF; kiểm tra mảng đã sắp; đo `nanoTime`.
4. Sinh dữ liệu bằng `gen_data.py` (seed cố định), chạy `run_all.sh` trên máy cá nhân của sinh viên (i5-13450HX, Windows 11, Java 25).
5. Phân tích bằng `analyze.py`: trung bình, độ lệch chuẩn, CI95, trung vị, hiệu ghép cặp so với CUTOFF tốt nhất, kiểm định Wilcoxon; vẽ 4 đồ thị.
6. Viết báo cáo, nêu rõ hạn chế (nhiễu đo trên laptop, chưa hiệu chỉnh so sánh bội).

**Kết quả chính (máy sinh viên):** vùng tối ưu ≈ 12–40 (ước lượng điểm 20); CUTOFF 7 và 10 chậm hơn ≈ 3.5–6% (số liệu nhiễu).

**Lần chạy trên máy sinh viên:** sinh viên chạy `run_all.sh` + `analyze.py` trên máy cá nhân (sửa lỗi mã hoá UTF-8 khi ghi `tables.md` trên Windows); AI viết lại báo cáo dựa trên thư mục `results/` do sinh viên gửi và cấu hình máy sinh viên cung cấp.
