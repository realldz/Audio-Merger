from dataclasses import dataclass, field

# Default prompt for AI standardization
DEFAULT_AI_PROMPT = """Bạn là một trợ lý chuyên gia về âm nhạc Việt Nam. Hãy dọn dẹp và chuẩn hóa danh sách các bài hát dưới đây theo các quy tắc sau:
1. Giữ nguyên timestamp ở đầu mỗi dòng.
2. Chuyển tên bài hát thành tiếng Việt có dấu, đúng chính tả và viết hoa chữ cái đầu mỗi từ.
3. Chỉ giữ lại tên chính của bài hát bằng cách loại bỏ các thông tin không cần thiết. Các thông tin cần loại bỏ bao gồm, nhưng không giới hạn ở:
   - Ghi chú về phiên bản hoặc chất lượng: Ví dụ: "Lofi", "Remix", "Cover", "Ver.2", "- Copy", "(1)".
   - Ghi chú kỹ thuật hoặc sản xuất: Ví dụ: "Vcpmc", "(Vocal Nam)", "Beat".
   - Các tiền tố định danh: Ví dụ: các chuỗi trong ngoặc đơn ở đầu tên như `(6_28)`.
   - Đặc biệt, hãy tìm và loại bỏ tất cả các từ khóa trong danh sách sau đây nếu chúng xuất hiện: {custom_keywords}

Dữ liệu cần chuẩn hóa:
```{log_content}```

LƯU Ý QUAN TRỌNG: Chỉ được trả về nội dung của danh sách đã chuẩn hóa. Tuyệt đối không thêm bất kỳ lời chào, câu giới thiệu, giải thích hay các ký tự định dạng nào khác."""

@dataclass
class AudioFile:
    path: str
    title: str
    display_name: str
    is_pinned: bool = False

@dataclass
class LogSettings:
    level: str = 'INFO'
    handler: str = 'file'
    file_name: str = 'audio_merger.log'
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

@dataclass
class Settings:
    output_folder: str = ''
    output_file: str = ''
    log_file: str = ''
    silence_thresh: float = -50.0
    chunk_size: int = 10
    gemini_api_key: str = ''
    gemini_model_name: str = 'gemini-1.5-flash-latest'
    custom_keywords: str = ''
    is_advanced_prompt_mode: bool = False
    custom_prompt: str = field(default=DEFAULT_AI_PROMPT)
    log: LogSettings = field(default_factory=LogSettings)