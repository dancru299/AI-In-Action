# 🎒 Lab 4: Xây dựng AI Agent TravelBuddy ✈️🌍

## 📝 Giới thiệu
Dự án này là bài Lab 4 nằm trong chuỗi thực chiến xây dựng AI Agent. Mục tiêu của Lab là xây dựng một trợ lý du lịch thông minh (**TravelBuddy**) hoàn chỉnh, không chỉ là một chatbot thông thường mà là một **Agent** có "não" (phân tích yêu cầu) và "tay chân" (gọi công cụ) để thực hiện chuỗi hành động phức tạp.

---

## 🚀 Những gì đã hoàn thành

1. **Setup Môi Trường & API:**
   - Cài đặt đầy đủ `langchain`, `langgraph`, `openai`, `fastapi`, `uvicorn`.
   - Cấu hình file `.env` bảo mật API key.

2. **System Prompt (Não bộ):**
   - Định nghĩa hành vi (Persona), Rules, Constraints nghiêm ngặt cho Model qua file `system_prompt.txt` format XML.
   - Xử lý hoàn hảo các trường hợp: hỏi lại khi thiếu thông tin (khôn khéo không gọi tool dư thừa), từ chối câu hỏi ngoài luồng (refusal), chống prompt injection tốt.

3. **Cài đặt 3 Tools (Tay chân của AI):**
   - `search_flights`: Tìm vé máy bay, logic tự động đảo chiều đầu/cuối khi tra DB.
   - `search_hotels`: Lọc khách sạn theo ngân sách (budget) và tự động sort thứ tự xếp hạng (rating).
   - `calculate_budget`: Parse text tính toán, thêm khả năng tự động nhân giá tiền với số đêm lưu trú mà không bắt LLM phải xử lý sai lệch do nội suy.

4. **Tổ chức LangGraph (Vòng lặp nhận thức):**
   - Xây dựng state đồ thị kết nối Agent-Tool-Agent với `StateGraph` và `add_messages`.
   - Triển khai logic Agent tự quyết định lúc nào gọi tool, lúc nào ngừng để trả lời người dùng.
   - Thêm cơ chế **Retry tự động** làm cho Graph chịu tải tốt, chống lại các lỗi nghẽn mạng từ OpenAI (bắt lỗi 400 JSON parse).

5. **Giao diện Web UI (Mở rộng nâng cao):**
   - Chuyển đổi từ chạy terminal thô cứng sang giao diện cửa sổ Chat chuyên nghiệp bằng HTML/CSS/JS (Dark/Glass Theme).
   - Backend `FastAPI`.
   - Trải nghiệm giao tiếp thời gian thực, stream luồng suy nghĩ bằng công nghệ truyền phát **SSE (Server-Sent Events)**, phân tách các bước đang gọi Tool và Kết quả cuối cùng.

---

## 🧠 Kiến thức bắt buộc phải nắm được

Sau bài lab này, những core concepts cốt lõi và quan trọng nhất cần hiểu sâu gồm:

- **1. System Prompt (Quyền lực cốt lõi):** Cách định hình persona, thiết lập rules (ràng buộc hành vi) để tránh AI ảo giác (hallucination) cũng như từ chối khéo léo (refusal) thay vì bị sa đà đi lạc chủ đề.
- **2. Tools (Function Calling):** Hiểu bản chất thực sự của Tool. Chúng ta lập trình hàm Python, LLM sẽ phân tích logic và trả ra JSON xác định tên Tool cần dùng + Arguments. Framework (Langchain) bóc tách JSON này -> gọi hàm Python -> trả kết quả dạng Text/Message cho LLM đọc lại.
- **3. LangGraph (Vòng lặp vòng đời Agent):** Phá bỏ giới hạn của AI một chiều. Flow hoạt động liên tục (Multi-step reasoning):
  > 🧠 Agent nghĩ (Dữ liệu yêu cầu thiếu -> Gọi Tool) ➡️ 🔧 Khởi động Tools ➡️ 🔄 Nhận output từ Tools ➡️ 🧠 Agent nghĩ lại và xác nhận ➡️ 🗣 Trả kết quả chốt cho User.
- **4. Streaming & SSE (Event-Driven AI):** Các hệ thống Agent khi xử lý thường mất nhiều thời gian do chain nhiều tool. Nắm được tư duy streaming event từ State của graph xuống Backend và truyền tới Frontend, đảm bảo UX.

---

## 🔄 Luồng hoạt động chi tiết của phần mềm

1. **Người dùng nhập yêu cầu** trên Web UI (ví dụ: *"Tìm khách sạn Đà Nẵng rẻ nhất 3 đêm"*).
2. **Web gọi API `/chat`**: Gửi chuỗi nội dung trực tiếp tới FastAPI Backend (`app.py`).
3. **Graph Stream**: Một threads background được khởi tạo, đẩy dữ liệu (HumanMessage) vào State ban đầu của LangGraph.
4. **Agent Node (Lần 1)**:
   - Tự động chèn SystemMessage hướng dẫn vào đầu đoạn chat (nếu chưa có).
   - Call API của LLM (`gpt-4o-mini`). LLM phân tích, nhận thấy cần xài khách sạn -> trả ra kết quả có cấu trúc `AIMessage(tool_calls=[{name="search_hotels", args={...}}])`.
   - Streaming event này về UI (UI quay spinner màu tím báo "Đang nghĩ").
5. **Tool Node (Ngã rẽ điều kiện)**:
   - Langgraph thấy có `tool_calls` -> chuyển luồng dữ liệu sang node Tools.
   - Hàm Python `search_hotels` trong `tools.py` chạy -> lấy dữ liệu -> đóng gói vào `ToolMessage`.
   - Streaming event hoàn tất Tool về UI (hiển thị raw data của tool search).
6. **Agent Node (Lần 2 - Phản hồi lại)**:
   - LangGraph quay ngược vòng lặp về Node Agent, lần này gói Messages đã có kết quả tìm khách sạn.
   - LLM đọc được kết quả, soạn ra văn bản chuẩn format định sẵn: "Dưới đây là gợi ý khách sạn..." - tức `AIMessage(content="...")` không kèm tool_calls.
7. **Frontend Streaming**: UI bắt được `AIMessage` có content, ngừng spinner và hiển thị định dạng dạng Markdown cực kỳ tự nhiên. Vòng lặp Agent hoàn tất.

---

## 🧪 Cách khởi chạy dự án tại local

1. Kích hoạt môi trường ảo (nếu bạn sử dụng): 
   ```bash
   venv\Scripts\activate
   ```
2. Cài đặt các thư viện bắt buộc (FastAPI, Langchain, Uvicorn,...):
   ```bash
   pip install -r requirements.txt
   ```
3. Chạy Server LangGraph + Backend FastAPI:
   ```bash
   python app.py
   ```
4. Truy cập giao diện trực quan tại: **http://localhost:8000**
