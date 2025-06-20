from memvid import MemvidEncoder, MemvidRetriever


def save_pdf_in_vect_db(path, filename):
    encoder = MemvidEncoder()
    encoder.add_pdf(path)
    encoder.build_video(f"db/mp4/{filename}.mp4", f"db/json/{filename}.json")

def get_context_from_vect_db(filename, concept):
    retriever = MemvidRetriever(f"db/mp4{filename}.mp4", f"db/json/{filename}.json")
    results = retriever.search(concept, top_k=5)