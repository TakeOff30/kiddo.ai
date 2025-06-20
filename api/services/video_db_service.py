from memvid import MemvidEncoder, MemvidRetriever

def save_pdf_in_vect_db(path, filename):
    encoder = MemvidEncoder()
    encoder.add_pdf(path)
    encoder.build_video(f"api/video_vector_db_data/mp4/{filename}.mp4", f"api/video_vector_db_data/json/{filename}.json")

def get_context_from_vect_db(filename, concept):
    retriever = MemvidRetriever(f"api/video_vector_db_data/mp4{filename}.mp4", f"api/video_vector_db_data/json/{filename}.json")
    results = retriever.search(concept, top_k=5)
    return results