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
from .log import log_request

app = FastAPI(title="RAG Search Service", version="1.0.0")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/search", response_model=SearchResponse)
async def search_endpoint(request: SearchRequest):
    model = get_model()
    index, metadata = get_index_and_metadata()

    q_vec = model.encode([request.query], convert_to_numpy=True)
    D, I = index.search(q_vec, 15)

    results = []
    for idx, dist in zip(I[0], D[0]):
        if idx == -1:
            continue
        item = metadata[idx].copy()
        item["score"] = float(dist)
        results.append(item)

    safe_results = sanitize_for_runtime(results)
    documents = format_results(safe_results, 2000)

    message_to_llm = create_message_to_llm(documents, request.query)

    llm_responese = run_llm(message_to_llm)
    print("llm_response in main:", llm_responese)

    # 📌 Логируем запрос и ответ
    log_request(request.query, results, llm_responese)

    return {"result": llm_responese}
