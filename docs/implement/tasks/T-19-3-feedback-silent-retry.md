# T-19-3 — Ghi feedback lạc quan và thử lại ngầm

| Thuộc tính | Giá trị |
|---|---|
| Story | US-19 (P0) — Blueprint: "Lỗi ghi đánh giá → thử lại ngầm, không báo lỗi to" |
| Sprint | S4 |
| Tầng | UI |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-19-2 |
| Chặn | — |

## Bối cảnh

SADD §5.3.9: feedback 1 UPSERT, retry ngầm 3 lần, UI lạc quan. Feedback không được chặn luồng chính.

## Phạm vi

**Làm:** hàm `submit(svc, actor, answer_id, value, reason=None)` và hàng chờ `K.FB_PENDING`.

## Đặc tả

```python
def submit(svc, actor, aid, value, reason=None):
    st.session_state[f"fb.value:{aid}"] = value
    for delay in (0, 0.2, 0.5):
        time.sleep(delay)
        try: svc.feedback.upsert(actor, aid, FeedbackValue(value), reason); return
        except (NotFound, Invalid): return                   # lỗi nghiệp vụ: không thử lại
        except Exception: log.warning("feedback_retry", answer_id=str(aid))
    st.session_state.setdefault(K.FB_PENDING, {})[str(aid)] = (value, reason)   # thử lại ở lần chạy sau

def flush_pending_feedback(svc, actor):                       # gọi đầu chat_panel mỗi lần chạy toàn app
    for aid, (value, reason) in list(st.session_state.get(K.FB_PENDING, {}).items()):
        try: svc.feedback.upsert(actor, UUID(aid), FeedbackValue(value), reason); del st.session_state[K.FB_PENDING][aid]
        except Exception: pass
```

- Tổng thời gian chờ tối đa ~0.7 s trong lần bấm (chấp nhận được).
- Không hiển thị `st.error` khi lỗi; chỉ log warn.

## Tiêu chí xong

- [ ] Service giả lỗi 2 lần rồi thành công → lưu được, không hiện lỗi.
- [ ] Service giả lỗi liên tục → nằm trong pending; lần chạy sau service lành → được ghi.

## Test

`tests/unit/ui/test_feedback_retry.py`.

## Tham chiếu

SADD §5.3.5, §5.3.9 · Blueprint §3.6.3
