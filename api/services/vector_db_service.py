from nltk.tokenize import sent_tokenize
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from weaviate.classes.config import Property, DataType
import weaviate

model = SentenceTransformer('all-MiniLM-L6-v2') # embedding output is 384 dimensions
client = weaviate.connect_to_local(
    host="localhost",  # Use a string to specify the host
    port=8080,
    grpc_port=50051,
)

# Weaviate client is used to connect to the Weaviate instance running on localhost:8080

# client.collections.create(
#     name="NoteChunks",
#     properties=[
#         Property(name="name", data_type=DataType.TEXT),
#     ],
#     vectorizer_config=None  # No automatic vectorization
# )

def extract_text_from_pdf(pdf_path):
    # Inizializza una stringa vuota per memorizzare il testo
    text = ""
    
    try:
        # Apri il file PDF
        reader = PdfReader(pdf_path)
        
        # Itera attraverso ogni pagina nel PDF
        for page in reader.pages:
            # Estrai il testo dalla pagina e aggiungilo alla stringa complessiva
            text += page.extract_text() if page.extract_text() else ""
            
    except Exception as e:
        print(f"Errore durante l'elaborazione del PDF con pypdf: {e}")
        # Puoi decidere di restituire None o una stringa vuota in caso di errore,
        # o sollevare nuovamente l'eccezione a seconda delle tue necessità.
        return None 
        
    return text


#chunk_size  is the number of sentences in each chunk
def chunk_text(text, chunk_size=5):
    # Split the text into sentences
    sentences = sent_tokenize(text) #array of sentences
    
    # Initialize variables
    chunks = []
    current_chunk = ""

    current_chunk_index = 0
    # Iterate through each sentence
    for sentence in sentences:
        # If adding the next sentence exceeds the chunk size, save the current chunk and start a new one
        if current_chunk_index < chunk_size:
            current_chunk += sentence + " "
            current_chunk_index += 1           
        else:
            if current_chunk == chunk_size: #add the current_chunk to the list chunks
                chunks.append(current_chunk.strip())
            current_chunk_index = 0
            current_chunk = ""
    
    return chunks

def embed_chunks(chunks):
    return model.encode(chunks, show_progress_bar=True)

def load_pdf_on_vector_db(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text, chunk_size=5)
    embeddings = embed_chunks(chunks)

    # Store the chunks and their embeddings in Weaviate
    for i, chunk in enumerate(chunks):
        notes = client.collections.get("NoteChunks")
        notes.data.insert(
            properties={
                "text": chunk,
            },
            vector=embeddings[i].tolist(),
        )
        
def query_notes(question):
    question_embedding = model.encode([question])[0] #embed the array of questions and return only the first one
    notes = client.collections.get("NoteChunks")
    results = notes.query.near_vector(
        near_vector=question_embedding.tolist(),
        limit=3
    )
    return [obj.properties["text"] for obj in results.objects]