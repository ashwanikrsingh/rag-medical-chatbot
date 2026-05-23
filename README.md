# RAG Medical Chatbot

A Flask-based medical question answering chatbot that uses Retrieval-Augmented Generation (RAG). The app loads medical PDF content, creates a FAISS vector store with Hugging Face sentence embeddings, retrieves relevant context, and sends that context to a Groq-hosted LLM to generate a short answer.

This project is intended for learning and prototyping. It should not be used as a replacement for professional medical advice.

## What This App Does

The application has two main flows:

1. Ingestion flow
   - Reads PDF files from `data/`
   - Splits documents into chunks
   - Creates embeddings using `sentence-transformers/all-MiniLM-L6-v2`
   - Stores the vectors locally in `vectorstore/db_faiss`

2. Chat flow
   - Serves a web chat UI with Flask
   - Accepts a medical question from the user
   - Loads the FAISS vector store
   - Retrieves the most relevant document chunk
   - Sends the question and retrieved context to Groq
   - Displays the LLM response in the browser

## Tech Stack

- Python 3.14
- Flask for the web application
- LangChain for the RAG chain
- FAISS for local vector search
- Hugging Face sentence transformers for embeddings
- Groq for LLM inference
- uv for dependency management
- Docker for containerization
- GitHub Actions for CI/CD
- Aqua Trivy for container vulnerability scanning
- AWS ECR for container image publishing

## Project Structure

```text
app/
  application.py              # Flask app and routes
  components/
    data_loader.py            # PDF ingestion and vector store creation
    pdf_loader.py             # PDF loading and text chunking
    embeddings.py             # Hugging Face embedding model
    vector_store.py           # FAISS save/load logic
    retriever.py              # LangChain retrieval chain
    llm.py                    # Groq LLM setup
  config/
    config.py                 # Environment/config values
  templates/
    index.html                # Chat UI
data/                         # Source PDF files
vectorstore/db_faiss/         # Generated FAISS vector store
Dockerfile                    # App container image
.dockerignore                 # Docker build exclusions
.github/workflows/            # GitHub Actions workflows
```

## Environment Variables

Create a `.env` file in the project root for local development:

```env
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_huggingface_token_here
HF_PROVIDER=together
```

Required:

- `GROQ_API_KEY`: used by `langchain_groq.ChatGroq` to call the LLM.

Optional:

- `HF_TOKEN`: useful if Hugging Face access is needed.
- `HF_PROVIDER`: defaults to `together` in `app/config/config.py`.

Do not commit `.env`. It is intentionally ignored by `.dockerignore` and should be passed to containers at runtime.

## Local Setup With uv

Install dependencies:

```bash
uv sync
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Or run commands directly through uv:

```bash
uv run python --version
```

## Create the Vector Store

Put your medical PDF files inside `data/`, then run:

```bash
uv run python app/components/data_loader.py
```

This creates the FAISS index under:

```text
vectorstore/db_faiss/
```

The chatbot needs this vector store to answer questions from your documents.

## Run the App Locally

Start the Flask app:

```bash
uv run python app/application.py
```

Open:

```text
http://localhost:5000
```

## Run With Docker

Build the image:

```bash
docker build -t rag-medical-chatbot .
```

Run the container with environment variables from `.env`:

```bash
docker run --env-file .env -p 5000:5000 rag-medical-chatbot
```

Open:

```text
http://localhost:5000
```

If you do not bake `data/` or `vectorstore/` into the image, mount them as volumes:

```bash
docker run --env-file .env \
  -p 5000:5000 \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/vectorstore:/app/vectorstore" \
  rag-medical-chatbot
```

## GitHub Actions CI/CD

The workflow in `.github/workflows/docker-image.yml` does the following:

1. Builds the Docker image.
2. Scans the image with Aqua Trivy.
3. Fails the workflow if Trivy finds vulnerabilities.
4. Pushes the image to AWS ECR only when the scan passes.

Required GitHub secret:

```text
AWS_ROLE_TO_ASSUME
```

Example:

```text
arn:aws:iam::<account-id>:role/<github-actions-ecr-role>
```

Optional GitHub repository variables:

```text
AWS_REGION=eu-central-1
ECR_REPOSITORY=rag-medical-chatbot
```

Add them in GitHub:

```text
Repository Settings
-> Secrets and variables
-> Actions
```

Use repository variables for non-sensitive values and secrets for credentials or role ARNs.

## Notes

- The app runs on port `5000`.
- The current LLM is `llama-3.1-8b-instant` through Groq.
- The current embedding model is `sentence-transformers/all-MiniLM-L6-v2`.
- The retriever currently fetches `k=1` relevant chunk for each question.
- If the FAISS vector store is missing, create it with `app/components/data_loader.py` before using the chat.
