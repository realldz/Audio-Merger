import google.generativeai as genai
from PyQt5.QtCore import QThread, pyqtSignal
from core.models import DEFAULT_AI_PROMPT

def fetch_available_models(api_key: str) -> tuple[bool, list[str] | str]:
    """
    Fetches a list of available generative models from the Google AI API.
    """
    if not api_key:
        return False, "Error: Gemini API Key is missing."
    
    try:
        genai.configure(api_key=api_key)
        model_list = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                model_list.append(m.name)
        return True, sorted(model_list)
    except Exception as e:
        return False, f"Could not fetch models: {str(e)}"

class FetchModelsThread(QThread):
    """A dedicated thread to fetch models without freezing the UI."""
    finished = pyqtSignal(tuple)

    def __init__(self, api_key: str, parent=None):
        super().__init__(parent)
        self.api_key = api_key

    def run(self):
        result = fetch_available_models(self.api_key)
        self.finished.emit(result)


def standardize_log(api_key: str, model_name: str, log_content: str, is_advanced: bool, custom_prompt: str, custom_keywords: str) -> tuple[bool, str]:
    """
    Standardizes the log content using the Gemini API.
    """
    if not api_key:
        return False, "Error: Gemini API Key is missing. Please provide it in the settings."
    
    if not model_name:
        return False, "Error: Gemini Model Name is not specified."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)

        if is_advanced:
            if '{log_content}' not in custom_prompt:
                return False, "Error: The custom prompt must include the placeholder `{log_content}`."
            final_prompt = custom_prompt.format(log_content=log_content)
        else:
            final_prompt = DEFAULT_AI_PROMPT.format(
                custom_keywords=custom_keywords or "(không có)",
                log_content=log_content
            )
        
        response = model.generate_content(final_prompt)
        clean_response = response.text.strip().replace('```', '')
        return True, clean_response

    except Exception as e:
        return False, f"An error occurred with the AI service: {str(e)}"

class StandardizeLogThread(QThread):
    """A dedicated thread to standardize the log without freezing the UI."""
    finished = pyqtSignal(tuple)

    def __init__(self, api_key, model_name, log_content, is_advanced, custom_prompt, custom_keywords, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.model_name = model_name
        self.log_content = log_content
        self.is_advanced = is_advanced
        self.custom_prompt = custom_prompt
        self.custom_keywords = custom_keywords

    def run(self):
        result = standardize_log(
            self.api_key, 
            self.model_name, 
            self.log_content, 
            self.is_advanced, 
            self.custom_prompt, 
            self.custom_keywords
        )
        self.finished.emit(result)