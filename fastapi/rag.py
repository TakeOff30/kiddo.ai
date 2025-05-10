import fitz
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
import weaviate

model = SentenceTransformer('all-MiniLM-L6-v2') # embedding output is 384 dimensions
client = weaviate.Client("http://weaviate:8080") # weaviate client
# Weaviate client is used to connect to the Weaviate instance running on localhost:8080

client.schema.create_class({ ## Create a class in Weaviate to store the chunks of text
    "class": "NoteChunks",
    "vectorizer": "none",
    "properties": [
        {
            "name": "text",
            "dataType": ["text"]
        },
    ]
})

def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Initialize an empty string to store the text
    text = ""

    # Iterate through each page in the PDF
    for page_num in range(len(pdf_document)):
        # Get the page
        page = pdf_document[page_num]
        
        # Extract text from the page
        text += page.get_text()

    # Close the PDF document
    pdf_document.close()

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
    # Extract text from the PDF
    text = extract_text_from_pdf(pdf_path)

    # Chunk the text into smaller pieces
    chunks = chunk_text(text, chunk_size=5)

    # Embed the chunks
    embeddings = embed_chunks(chunks)

    # Store the chunks and their embeddings in Weaviate
    for i, chunk in enumerate(chunks):
        client.data_object.create(
            data_object={ "text": chunk },          
            class_name="NoteChunks",
            vector=embeddings[i].tolist(),  # Convert numpy array to list
        )
        
def query_notes(question):
    question_embedding = model.encode([question])[0] #embed the array of questions and return only the first one

    # Perform a vector search in Weaviate
    result = client.query.get(
        class_name="NoteChunks",
        properties=["text"],
        vector=question_embedding.tolist(), 
        limit=5,  # Number of results to return
    ).do()

    # Extract the text from the results
    notes = [item["text"] for item in result["data"]["Get"]["NoteChunks"]]

    return notes