from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate

from app.components.llm import load_llm
from app.components.vector_store import load_vector_db
from app.config.config import HUGGINGFACE_REPO_ID, HF_TOKEN
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

CUSTOM_PROMPT_TEMPLATE = """ Answer the following medical questions in 2-3 lines maximum using only the the information provided in the context

Context:
{context}

Question:
{input}

Answer:
"""

def custom_prompt():
    return PromptTemplate(template=CUSTOM_PROMPT_TEMPLATE, input_variables=["context", "input"])

def get_retrieval_chain():
    try:
        logger.info("Loading vector store for context")
        db = load_vector_db()
        if db is None:
            raise CustomException("Vector store not present")
        
        retriever = db.as_retriever(search_kwargs={"k": 1})
        
        llm = load_llm()
        if llm is None:
            raise CustomException("LLM not loaded")

        document_chain = create_stuff_documents_chain(llm, custom_prompt())
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        logger.info("successfully created the retrieval chain...")
        return retrieval_chain
    
    except Exception as e:
        error_message = CustomException("Failed to make retrieval chain", e)
        logger.error(str(error_message))
        raise error_message
