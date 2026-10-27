# Quy ước test report

## Phán định từng bước

| Kết quả | Khi nào |
|---|---|
| **PASS** | Thực tế khớp kỳ vọng. Lệch nhỏ không ảnh hưởng kỳ vọng thì ghi `**PASS** (kèm ghi chú)` và đưa vào bảng bug/quan sát. |
| **FAIL** | Không khớp kỳ vọng, kể cả khi lỗi nằm ở dữ liệu test hoặc tiền điều kiện. Ghi lý do trong ngoặc, ví dụ `**FAIL** (tiền điều kiện không thoả; app render đúng)`, `**FAIL** (sai fixture; app đúng)`. |
| **BLOCKED** | Không thực hiện được bước (môi trường chết, bước trước chặn). Không được coi là PASS. |

Phải tách bạch "app sai" với "dữ liệu/tiền điều kiện sai" trong cột Thực tế. Người đọc summary cần biết đây là lỗi sản phẩm hay lỗi của chính bộ test.

## Kết quả tổng

- **PASS**: mọi bước có mã Vxx đều PASS, đạt §5 của test case, artifact đủ.
- **FAIL**: có bước bắt buộc FAIL hoặc thiếu artifact.
- **BLOCKED**: không chạy hết được vì môi trường (test plan §8.0).
- EV: PASS/FAIL theo ngưỡng QLT (QLT-01 ≥ 8/10, QLT-02 ≥ 8/10, QLT-03 ≥ 9/10, QLT-04 ≥ 9/10 hoặc ≥ 90%), không theo từng câu.

## Mức độ bug (S1–S4)

| Mức | Định nghĩa trong dự án này | Ví dụ |
|---|---|---|
| **S1** Blocker | Chặn luồng chính hoặc mất dữ liệu: không upload/chat/xoá được, app crash, lộ API key | Upload PDF hợp lệ ra traceback; xoá 1 tài liệu làm mất tài liệu khác |
| **S2** Critical | Chức năng chính sai kết quả nhưng còn đường đi; vi phạm bảo mật/NFR quan trọng | Chat trả lời bịa không có nguồn; tài liệu đã xoá vẫn được trích dẫn; nội dung PDF xuất hiện trong log |
| **S3** Major | Sai so với FR/AC nhưng không chặn luồng; thông báo sai; dữ liệu test sai | Thông báo lỗi tiếng Anh thay vì tiếng Việt; lỗi file mất dấu sau khi xử lý; fixture không đúng mô tả |
| **S4** Minor | Hiển thị, câu chữ, trải nghiệm nhỏ; quan sát ngoài phạm vi | Banner lỗi cũ không tự tắt; gợi ý "200MB" trong khi giới hạn là 25 MB |

Theo test plan §6.2/§7.0: bug S1/S2 phải được fix và retest trước khi sang cycle sau. Exit criteria yêu cầu không còn bug S1/S2 đang mở.

## Bug ID

- `BUG-<CASE không gạch>-<NN>`, ví dụ `BUG-ST02-01`. Đánh số tăng dần trong từng case.
- Quan sát ngoài phạm vi case (không tính là fail của case): `OBS-<CASE>-<NN>`.
- Gặp lại bug đã ghi ở case khác: dùng **lại ID cũ** và thêm "(lặp lại)", ví dụ `OBS-ST01-03 (lặp lại)`. Không tạo ID mới.
- Mô tả theo trình tự: hiện tượng → kỳ vọng (dẫn FR/AC/BR) → nguyên nhân nghi ngờ (file/hàm nếu đọc được code, không sửa) → ảnh hưởng.

## Ảnh và video

- Tên ảnh: `V<nn>[a-z]?-<mo-ta-khong-dau-gach-noi>.png`, ví dụ `V03-chip-san-sang.png`, `V02b-sau-xu-ly-2-pdf.png`.
- Mỗi mã Vxx trong bảng bước của test case phải có ít nhất 1 ảnh. Mã dạng dải `V03–V12` cần đủ từng ảnh.
- Muốn chụp cả danh sách dài trong một ảnh thì có thể tạm `zoom` sidebar bằng JS rồi trả về như cũ, nhưng phải ghi vào bảng sai lệch.
- Ghi thông số video: độ dài, độ phân giải, fps.

### Nhãn URL khi công cụ quay không thấy thanh địa chỉ

Chạy trong trang (sau mỗi lần điều hướng/reload phải chạy lại):

```js
(() => {
  if (document.getElementById('__url_badge')) return;
  const b = document.createElement('div');
  b.id = '__url_badge';
  Object.assign(b.style, {position:'fixed', right:'8px', bottom:'8px', zIndex:2147483647,
    background:'rgba(0,0,0,.75)', color:'#fff', font:'12px/1.4 monospace', padding:'4px 8px',
    borderRadius:'4px', pointerEvents:'none'});
  document.body.appendChild(b);
  const tick = () => { b.textContent = location.href; };
  tick(); setInterval(tick, 500);
})();
```

## Văn phong

- Viết tiếng Việt có dấu, câu ngắn. Giữ nguyên chữ hiển thị trên UI trong ngoặc kép.
- Dùng giá trị cụ thể thay cho tính từ: "Sau ~2 giây", "points 3 → 4", không viết "nhanh", "nhiều".
- Không viết hoa/tô đậm tràn lan. Chỉ tô đậm phán định và các cụm then chốt.
