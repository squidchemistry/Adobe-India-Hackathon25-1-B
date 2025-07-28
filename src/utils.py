from sentence_transformers import util
import numpy as np


def rank_chunks(query_embedding, chunk_embeddings, chunks, threshold=0.45, keywords=None, max_chunks=5):
    """
    Ranks chunks by cosine similarity. If all scores are below threshold, fallback to keyword matching.
    Returns a list of (chunk, score, rank) tuples.
    """
   # to calculate cosine similarity scores
    scores = util.cos_sim(query_embedding, chunk_embeddings)[0].cpu().numpy()
    # chunks are sorted based on their scores
    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    # fallback happens if all scores are below the threshold
    if keywords and all(score < threshold for _, score in ranked):
        keyword_scores = []
        # iterate over each chunk
        for chunk in chunks:
            text = chunk.get("chunk_text", "")
            match_count = sum(kw.lower() in text.lower() for kw in keywords)
            keyword_scores.append(match_count)
        # chunks are sorted based on keyword match count
        ranked = sorted(zip(chunks, keyword_scores), key=lambda x: x[1], reverse=True)
        ranked = [(chunk, float(score)) for chunk, score in ranked]
    else:
        ranked = [(chunk, float(score)) for chunk, score in ranked]
    
    ranked = [(chunk, score, rank+1) for rank, (chunk, score) in enumerate(ranked)]
    if max_chunks:
        ranked = ranked[:max_chunks]
    return ranked


def confidence_level(score):
    if score >= 0.75: # if scores if greater than or equal to 0.75 then confidence is high
        return "high"
    elif score >= 0.5:
        return "medium"
    return "low"     # if score is less than 0.5 then confidence is low


def format_output(document, chunk, rank, page, score=None):
    output = {
        "document": document,
        "section_title": chunk["chunk_text"][:60] + ("..." if len(chunk["chunk_text"]) > 60 else ""),
        "importance_rank": rank,
        "page_number": page,
        "chunk_id": chunk.get("chunk_id"),
    }
    if score is not None:
        output["relevance_score"] = round(score, 3)
        output["confidence"] = confidence_level(score)
    return output
