from langchain_huggingface import HuggingFaceEndpoint
from app.config.config import HF_TOKEN, HUGGINGFACE_REPO_ID

from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

def load_llm(huggingface_repo_id: str = HUGGINGFACE_REPO_ID, hf_token: str = HF_TOKEN):
    try:
        logger.info("Loading LLM from HuggingFace")
        
        llm = HuggingFaceEndpoint(
            repo_id=huggingface_repo_id,
            provider="auto",
            huggingfacehub_api_token=hf_token,
            max_new_tokens=512,
            temperature=0.3,
        )

        logger.info("LLM loaded successfully")

        return llm
    
    except Exception as e:
        error_message = CustomException("Failed to load LLM", e)
        logger.error(str(error_message))
        raise error_message