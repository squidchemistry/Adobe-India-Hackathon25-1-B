# app.py

import streamlit as st
import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from semantic_matcher import SemanticMatcher
from utils import format_output

st.set_page_config(page_title="Persona-PDF Analyzer", layout="wide")

st.title("📄 Persona-Driven PDF Content Analyzer")
st.markdown("Select a PDF collection, view persona/task, and run semantic matching using Sentence Transformers.")

# Load collections
collections_dir = "collections"
collections = [c for c in os.listdir(collections_dir) if os.path.isdir(os.path.join(collections_dir, c))]

selected_collection = st.selectbox("Choose Collection", collections)

if selected_collection:
    collection_path = os.path.join(collections_dir, selected_collection)
    
    input_path = os.path.join(collection_path, "challenge1b_input.json")
    chunk_path = os.path.join(collection_path, "processed_chunks", f"{selected_collection}_all_chunks_for_b1.json")

    if not os.path.exists(input_path) or not os.path.exists(chunk_path):
        st.error("Input JSON or chunks file missing for selected collection.")
    else:
        with open(input_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        persona = config["persona"]
        task = config["job_to_be_done"]

        st.subheader("👤 Persona")
        st.json(persona)

        st.subheader("📝 Job to Be Done")
        st.json(task)

        if st.button("🚀 Run Semantic Matcher"):
            with st.spinner("Running semantic matching..."):
                matcher = SemanticMatcher()
                
                with open(chunk_path, "r", encoding="utf-8") as f:
                    chunks = json.load(f)

                keywords = ["budget", "train", "hotel", "restaurant", "lavender", "vineyard", "culture"]

                results = matcher.match(persona, task, chunks, keywords=keywords, max_chunks=5)

                extracted_sections = []
                subsection_analysis = []

                for chunk, score, rank in results:
                    formatted = format_output(chunk["document_filename"], chunk, rank, chunk["page_number"], score)
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

                st.success("✅ Matching Complete!")

                st.subheader("📌 Extracted Sections")
                for sec in extracted_sections:
                    st.markdown(f"**📄 {sec['document']} | Page {sec['page_number']} | Rank {sec['importance_rank']}**")
                    st.markdown(f"> {sec['section_title']}")

                st.subheader("📚 Refined Subsections")
                for sub in subsection_analysis:
                    st.markdown(f"**📄 {sub['document']} | Page {sub['page_number']}**")
                    st.code(sub['refined_text'], language="markdown")

                # Optional download
                output_data = {
                    "metadata": {
                        "input_documents": list(set([c["document_filename"] for c in chunks])),
                        "persona": persona["role"],
                        "job_to_be_done": task["task"]
                    },
                    "extracted_sections": extracted_sections,
                    "subsection_analysis": subsection_analysis
                }

                json_str = json.dumps(output_data, indent=4)
                st.download_button(
                    label="💾 Download Output JSON",
                    data=json_str,
                    file_name="challenge1b_output.json",
                    mime="application/json"
                )
