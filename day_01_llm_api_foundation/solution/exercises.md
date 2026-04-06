# Ngày 1 — Bài Tập & Phản Ánh
## Nền Tảng LLM API | Phiếu Thực Hành

**Thời lượng:** 1:30 giờ  
**Cấu trúc:** Lập trình cốt lõi (60 phút) → Bài tập mở rộng (30 phút)

---

## Phần 1 — Lập Trình Cốt Lõi (0:00–1:00)

Chạy các ví dụ trong Google Colab tại: https://colab.research.google.com/drive/172zCiXpLr1FEXMRCAbmZoqTrKiSkUERm?usp=sharing

Triển khai tất cả TODO trong `template.py`. Chạy `pytest tests/` để kiểm tra tiến độ.

**Điểm kiểm tra:** Sau khi hoàn thành 4 nhiệm vụ, chạy:
```bash
python template.py
```
Bạn sẽ thấy output so sánh phản hồi của GPT-4o và GPT-4o-mini.

---

## Phần 2 — Bài Tập Mở Rộng (1:00–1:30)

### Bài tập 2.1 — Độ Nhạy Của Temperature
Gọi `call_openai` với các giá trị temperature 0.0, 0.5, 1.0 và 1.5 sử dụng prompt **"Hãy kể cho tôi một sự thật thú vị về Việt Nam."**

**Bạn nhận thấy quy luật gì qua bốn phản hồi?** (2–3 câu)
> *Câu trả lời của bạn*
> **Trả lời:** Khi `temperature` tăng dần từ 0.0 lên 1.5, phản hồi của AI chuyển từ mức độ bảo thủ, lặp lại và dễ đoán (ở 0.0) sang trạng thái ngày càng linh hoạt, sáng tạo hơn, nhưng đôi lúc ngẫu hứng và có thể dính "ảo giác - hallucination" (ở 1.5).

**Bạn sẽ đặt temperature bao nhiêu cho chatbot hỗ trợ khách hàng, và tại sao?**
> *Câu trả lời của bạn*
> **Trả lời:** Tôi sẽ đặt trong khoảng `0.0` đến `0.3` (tuyến tính thấp). Lý do là vì chatbot chăm sóc khách hàng cần sự ổn định, kỷ luật và tính phản hồi chính xác cao dựa trên tài liệu nghiệp vụ, không được quyền sáng tạo bay bổng hay đưa ra thông tin sai lệch cho khách.

---

### Bài tập 2.2 — Đánh Đổi Chi Phí
Xem xét kịch bản: 10.000 người dùng hoạt động mỗi ngày, mỗi người thực hiện 3 lần gọi API, mỗi lần trung bình ~350 token.

**Ước tính xem GPT-4o đắt hơn GPT-4o-mini bao nhiêu lần cho workload này:**
> *Câu trả lời của bạn*
> **Trả lời:** Dựa trên bảng giá: gpt-4o là $0.01/1K tokens, mini là $0.0006/1K tokens. Suy ra `0.01 / 0.0006 ≈ 16.67`. Vậy GPT-4o sẽ đắt hơn khoảng **16.67 lần** (gần 17 lần) so với GPT-4o-mini trong mọi khối lượng công việc liên quan tới sinh văn bản output.

**Mô tả một trường hợp mà chi phí cao hơn của GPT-4o là xứng đáng, và một trường hợp GPT-4o-mini là lựa chọn tốt hơn:**
> *Câu trả lời của bạn*
> **Trả lời:** 
> - **GPT-4o xứng đáng:** Các bài toán phức tạp đòi hỏi khả năng tư duy và lập luận mảng rộng như viết/debug code phức tạp, phân tích dữ liệu học thuật hoặc xử lý tài liệu hợp đồng luật pháp chuyên sâu.
> - **GPT-4o-mini tốt hơn:** Lý tưởng cho tác vụ lặp lại quy mô lớn như phân loại mail, chuẩn hóa dữ liệu, chatbot hỏi đáp FAQ cơ bản, hoặc các web app có lượng traffic khổng lồ (vốn cần tối ưu chi phí gắt gao).

---

### Bài tập 2.3 — Trải Nghiệm Người Dùng với Streaming
**Streaming quan trọng nhất trong trường hợp nào, và khi nào thì non-streaming lại phù hợp hơn?** (1 đoạn văn)
> *Câu trả lời của bạn*
> **Trả lời:** Streaming đặc biệt quan trọng trong các ứng dụng giao tiếp với con người (như ChatGPT, UI Chatbot) hoặc tạo văn bản dài, vì việc xuất hiện chữ ngay lập tức giúp người dùng không cảm thấy bị "kẹt/treo máy", qua đó nâng cao rõ rệt trải nghiệm UX. Ngược lại, non-streaming lại phù hợp hơn cho giao tiếp Machine-to-Machine, quá trình chạy ẩn ở backend (auto-summary, cron-jobs) hoặc các API trích xuất JSON, vì ta chỉ cần toàn bộ cấu trúc dữ liệu kết quả hoàn chỉnh để máy tính xử lý tiếp chứ không cần chữ chạy theo thời gian thực.


## Danh Sách Kiểm Tra Nộp Bài
- [ ] Tất cả tests pass: `pytest tests/ -v`
- [ ] `call_openai` đã triển khai và kiểm thử
- [ ] `call_openai_mini` đã triển khai và kiểm thử
- [ ] `compare_models` đã triển khai và kiểm thử
- [ ] `streaming_chatbot` đã triển khai và kiểm thử
- [ ] `retry_with_backoff` đã triển khai và kiểm thử
- [ ] `batch_compare` đã triển khai và kiểm thử
- [ ] `format_comparison_table` đã triển khai và kiểm thử
- [ ] `exercises.md` đã điền đầy đủ
- [ ] Sao chép bài làm vào folder `solution` và đặt tên theo quy định 
