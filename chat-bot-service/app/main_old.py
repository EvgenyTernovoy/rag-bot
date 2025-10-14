from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from .models import SearchRequest, SearchResponse
from .utils import (
    create_message_to_llm,
    format_results,
    get_index_and_metadata,
    get_model,
    reload_resources,
    run_llm,
)
from .security import sanitize_for_runtime
import os

app = FastAPI(title="FAISS Search Service", version="1.0.0")

RELOAD_TOKEN = os.getenv("RELOAD_TOKEN", "changeme")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/search", response_model=SearchResponse)
async def search_endpoint(request: SearchRequest):
    model = get_model()
    index, metadata = get_index_and_metadata()

    q_vec = model.encode([request.query], convert_to_numpy=True)
    D, I = index.search(q_vec, request.k)

    results = []
    for idx, dist in zip(I[0], D[0]):
        if idx == -1:
            continue
        item = metadata[idx].copy()
        item["score"] = float(dist)
        results.append(item)

    safe_results = sanitize_for_runtime(results)
    documents = format_results(safe_results)
    message_to_llm = create_message_to_llm(documents, request.query)

    llm_responese = run_llm(message_to_llm)
    print("llm_response in main:", llm_responese)

    return {"result": llm_responese}


@app.post("/reload")
async def reload_endpoint(x_reload_token: str = Header(None)):
    if x_reload_token != RELOAD_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
    reload_resources()
    return {"status": "reloaded"}
