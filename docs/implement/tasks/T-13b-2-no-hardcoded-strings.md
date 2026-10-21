# T-13b-2 — Kiểm tra không có chuỗi giao diện viết cứng

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13b (P0) — "chuỗi tách khỏi mã, sẵn sàng i18n" |
| Sprint | S3 (chạy CI từ S3; sửa vi phạm dồn từ S2) |
| Tầng | TEST |
| Ước lượng | 0.75d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | F-03 |
| Chặn | — |

## Bối cảnh

US-13b yêu cầu toàn bộ giao diện có chuỗi tách khỏi mã. Cần một kiểm tra tự động, nếu không chuỗi viết cứng sẽ lọt vào dần.

## Phạm vi

**Làm:** test quét AST; sửa các vi phạm đang có.

## Đặc tả

`tests/unit/ui/test_no_hardcoded_strings.py`:

```text
for file in app/ui/**/*.py trừ app/ui/i18n/**:
    for node in ast.walk(parse(file)):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if có ký tự chữ cái tiếng Việt có dấu, hoặc
               (là đối số vị trí đầu tiên / label= / placeholder= / help= của st.* và có khoảng trắng + chữ cái):
                ghi vi phạm (file:line, chuỗi)
assert không có vi phạm (ngoại trừ allowlist tests/unit/ui/i18n_allowlist.txt: icon, key widget, CSS)
```

- Key widget (`key="chat.input"`), tên khoá `t("...")`, chuỗi định dạng kỹ thuật không bị tính.
- Thông báo lỗi khi test fail liệt kê `file:line` để sửa nhanh.

## Tiêu chí xong

- [ ] Test xanh trên toàn bộ `app/ui`.
- [ ] Thêm thử `st.button("Gửi")` vào một component → test đỏ.

## Tham chiếu

US-13b · Blueprint §3.8 (i18n) · F-03
