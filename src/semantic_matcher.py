# src/semantic_matcher.py
import os
import json
from sentence_transformers import SentenceTransformer
from utils import rank_chunks, format_output
from keybert import KeyBERT

class SemanticMatcher:
    def __init__(self, model_name="all-mpnet-base-v2"):
        print(f"🔍 Loading model: {model_name}")
        # Initialize the SentenceTransformer model
        self.model = SentenceTransformer(model_name, cache_folder='models')
        self.keyword_model = KeyBERT(model=model_name)

    def embed(self, text):
        return self.model.encode([text], convert_to_tensor=True)

    def embed_chunks(self, chunks):
        return self.model.encode([c["chunk_text"] for c in chunks], convert_to_tensor=True)

    def extract_dynamic_keywords(self, task_text, top_n=6):
        keywords = self.keyword_model.extract_keywords(task_text, stop_words='english', top_n=top_n)
        return [kw[0] for kw in keywords]   # keywords are only returned

    def match(self, persona, task, chunks, keywords=None, threshold=0.45, max_chunks=5):
        query = f"{persona['role']}: {task['task']}"
        query_embedding = self.embed(query)
        chunk_embeddings = self.embed_chunks(chunks)

        if keywords is None:
            keywords = self.extract_dynamic_keywords(task['task'])

        ranked = rank_chunks(
            query_embedding=query_embedding,
            chunk_embeddings=chunk_embeddings,
            chunks=chunks,
            threshold=threshold,
            keywords=keywords,
            max_chunks=max_chunks
        )
        return ranked

    def run_for_collection(self, collection_path):
        print(f"\n🚀 Running semantic matcher for collection: {collection_path}")

        # Load config
        with open(os.path.join(collection_path, "challenge1b_input.json"), "r", encoding="utf-8") as f:
            config = json.load(f)

        persona = config["persona"]
        task = config["job_to_be_done"]

        # Load chunks
        chunks_path = os.path.join(collection_path, "processed_chunks", f"{os.path.basename(collection_path)}_all_chunks_for_b1.json")
        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        # Dynamically extract keywords from the task
        keywords = self.extract_dynamic_keywords(task['task'])

        # Match
        ranked = self.match(persona, task, chunks, keywords=keywords)

        # Format results
        extracted_sections = []
        subsection_analysis = []

        for chunk, score, rank in ranked:
            # FIX 1: Use correct key name for document filename
            formatted = format_output(chunk["document_filename"], chunk, rank, chunk["page_number"], score)
            formatted["matched_keywords"] = [kw for kw in keywords if kw.lower() in chunk["chunk_text"].lower()]
            extracted_sections.append({
                "document": formatted["document"],
                "section_title": formatted["section_title"],
                "importance_rank": formatted["importance_rank"],
                "page_number": formatted["page_number"]
            })
            subsection_analysis.append({
                "document": formatted["document"],
                "refined_text": chunk["chunk_text"],
                "page_number": formatted["page_number"]
            })

        output_data = {
            "metadata": {
                # FIX 2: Use filenames directly from the input config
                "input_documents": [d["filename"] for d in config["documents"]],
                "persona": persona["role"],
                "job_to_be_done": task["task"]
            },
            "extracted_sections": extracted_sections,
            "subsection_analysis": subsection_analysis
        }

        # Save to output
        out_path = os.path.join(collection_path, "challenge1b_output.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=4)
        print(f"✅ Semantic match results saved to: {out_path}")
