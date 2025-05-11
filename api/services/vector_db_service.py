import nltk # Importa il pacchetto base NLTK per primo
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from weaviate.classes.config import Property, DataType # Assicurati che DataType sia importato se lo usi
import weaviate

# --- Inizio Blocco Setup NLTK ---
# Controlla e scarica 'punkt' se necessario, prima di importare sent_tokenize globalmente.
try:
    # nltk.data.find è un modo per verificare se una risorsa è disponibile.
    # Solleva LookupError se non trova 'tokenizers/punkt'.
    nltk.data.find('tokenizers/punkt')
    print("Risorsa 'punkt' di NLTK già disponibile.")
except LookupError:
    print("Risorsa 'punkt' di NLTK non trovata. Tentativo di download in corso...")
    # quiet=True riduce l'output del download, puoi rimuoverlo per vedere più dettagli.
    nltk.download('punkt', quiet=False) 
    print("Download di 'punkt' completato.")
    # Verifica nuovamente dopo il download per sicurezza
    try:
        nltk.data.find('tokenizers/punkt')
        print("Risorsa 'punkt' ora disponibile dopo il download.")
    except LookupError:
        print("ERRORE CRITICO: Impossibile trovare 'punkt' anche dopo il tentativo di download.")
        print("Per favore, prova a eseguire manualmente in una console Python:")
        print("import nltk")
        print("nltk.download('punkt')")
        print("E controlla eventuali errori di permessi o di rete.")
        # Solleva un'eccezione per fermare lo script se 'punkt' è indispensabile.
        raise RuntimeError("Impossibile inizializzare la risorsa 'punkt' di NLTK.")
except Exception as e:
    # Cattura altri possibili errori durante il setup di NLTK (es. problemi di rete)
    print(f"Si è verificato un errore imprevisto durante il setup di NLTK 'punkt': {e}")
    raise # Rilancia l'eccezione per fermare lo script.
# --- Fine Blocco Setup NLTK ---

# Ora che siamo (ragionevolmente) sicuri che 'punkt' sia disponibile,
# possiamo importare sent_tokenize per l'uso globale nel modulo.
from nltk.tokenize import sent_tokenize

# --- Inizio Definizione Modelli e Client ---
# Inizializza il modello SentenceTransformer
# Nota: questo scaricherà il modello la prima volta che viene eseguito,
# il che potrebbe richiedere tempo e una connessione internet.
try:
    print("Caricamento del modello SentenceTransformer 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2') # L'output dell'embedding è di 384 dimensioni
    print("Modello SentenceTransformer caricato.")
except Exception as e:
    print(f"Errore durante il caricamento del modello SentenceTransformer: {e}")
    print("Assicurati di avere una connessione internet per il primo download del modello.")
    raise

# Connettiti all'istanza Weaviate locale
try:
    print("Connessione a Weaviate in corso...")
    client = weaviate.connect_to_local(
        host="localhost",  # Specifica l'host come stringa
        port=8080,
        grpc_port=50051,
        # Potresti voler aggiungere headers di autenticazione se Weaviate è protetto
        # headers={...}
    )
    print(f"Connesso a Weaviate. Server version: {client.get_meta()['version']}")
except Exception as e:
    print(f"Errore durante la connessione a Weaviate: {e}")
    print("Assicurati che Weaviate sia in esecuzione su localhost:8080.")
    raise
# --- Fine Definizione Modelli e Client ---


# --- Inizio Definizione Funzioni ---
def extract_text_from_pdf(pdf_path):
    """Estrae il testo da un file PDF."""
    print(f"Estrazione del testo dal PDF: {pdf_path}")
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n" # Aggiungi un newline tra le pagine per chiarezza
            # print(f"Estratto testo dalla pagina {i+1}") # Log opzionale per pagina
        print(f"Testo estratto con successo da {len(reader.pages)} pagine.")
    except FileNotFoundError:
        print(f"ERRORE: File PDF non trovato al percorso: {pdf_path}")
        return None
    except Exception as e:
        print(f"Errore durante l'elaborazione del PDF '{pdf_path}' con pypdf: {e}")
        return None
    return text.strip()


def chunk_text(text, chunk_size=5):
    """Divide il testo in chunk di un numero specificato di frasi."""
    if not text:
        print("Attenzione: testo vuoto fornito a chunk_text. Restituzione di una lista vuota.")
        return []
    
    print(f"Divisione del testo in chunk (dimensione chunk: {chunk_size} frasi)...")
    sentences = sent_tokenize(text)
    
    chunks = []
    current_chunk_sentences = []

    for sentence in sentences:
        current_chunk_sentences.append(sentence)
        if len(current_chunk_sentences) == chunk_size:
            chunks.append(" ".join(current_chunk_sentences).strip())
            current_chunk_sentences = []
    
    if current_chunk_sentences: # Aggiungi l'ultimo chunk se ci sono frasi rimanenti
        chunks.append(" ".join(current_chunk_sentences).strip())
    
    print(f"Testo diviso in {len(chunks)} chunks.")
    return chunks


def embed_chunks(chunks):
    """Crea embeddings per una lista di chunk di testo."""
    if not chunks:
        print("Attenzione: lista di chunk vuota fornita a embed_chunks. Restituzione di una lista vuota.")
        return []
    print(f"Creazione degli embeddings per {len(chunks)} chunks...")
    # show_progress_bar=True è utile per chunk lunghi o numerosi
    embeddings = model.encode(chunks, show_progress_bar=True)
    print("Embeddings creati.")
    return embeddings


def load_pdf_on_vector_db(pdf_path, collection_name="NoteChunks"):
    """Estrae testo da un PDF, lo divide in chunk, crea embeddings e li carica su Weaviate."""
    print(f"Caricamento del PDF '{pdf_path}' nel database vettoriale (collezione: {collection_name})...")
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print(f"Impossibile estrarre testo da '{pdf_path}'. Operazione interrotta.")
        return

    chunks = chunk_text(text, chunk_size=5)
    if not chunks:
        print("Nessun chunk generato dal testo. Operazione interrotta.")
        return

    embeddings = embed_chunks(chunks)
    if len(embeddings) == 0: # embeddings potrebbe essere una lista vuota o un array numpy
        print("Nessun embedding generato. Operazione interrotta.")
        return

    try:
        notes_collection = client.collections.get(collection_name)
        print(f"Inserimento di {len(chunks)} chunks nella collezione '{collection_name}'...")
        
        # Prepara gli oggetti per l'inserimento batch (più efficiente)
        data_objects = []
        for i, chunk_text_content in enumerate(chunks):
            data_objects.append(
                weaviate.DataObject(
                    properties={
                        "text": chunk_text_content, 
                        # Potresti voler aggiungere altre proprietà, come il nome del file sorgente
                        # "source_pdf": pdf_path 
                    },
                    vector=embeddings[i].tolist() # Assicurati che l'embedding sia una lista Python
                )
            )
        
        # Inserisci i dati in batch
        if data_objects:
            insert_response = notes_collection.data.insert_many(data_objects)
            print(f"Risposta dall'inserimento batch: {insert_response}")
            if insert_response.has_errors:
                print("ATTENZIONE: Si sono verificati errori durante l'inserimento batch:")
                for item_error in insert_response.errors:
                    print(f" - Indice {item_error.index}: {item_error.message}")
            else:
                print(f"{len(data_objects) - len(insert_response.errors)} chunks inseriti con successo.")
        else:
            print("Nessun oggetto dato da inserire.")

    except Exception as e:
        print(f"Errore durante l'interazione con la collezione Weaviate '{collection_name}': {e}")
        print("Assicurati che la collezione esista e che lo schema sia corretto.")
        print("Se la collezione non esiste, potresti doverla creare prima, ad esempio:")
        print(f"""
# client.collections.create(
# name="{collection_name}",
# properties=[
# Property(name="text", data_type=DataType.TEXT),
# # Property(name="source_pdf", data_type=DataType.TEXT), # Esempio di altra proprietà
# ],
# # vectorizer_config=None # Se fornisci i tuoi vettori
# # Se usi un vettorizzatore di Weaviate (es. text2vec-transformers), configuralo qui
# )
        """)


def query_notes(question, collection_name="NoteChunks", limit=3):
    """Interroga Weaviate per trovare i chunk di testo più simili a una domanda data."""
    print(f"Interrogazione della collezione '{collection_name}' con la domanda: '{question}'")
    if not question:
        print("Attenzione: domanda vuota fornita a query_notes.")
        return []
        
    try:
        question_embedding = model.encode([question])[0] # Ottieni l'embedding per la domanda
        
        notes_collection = client.collections.get(collection_name)
        
        print(f"Esecuzione della ricerca near_vector con limite {limit}...")
        results = notes_collection.query.near_vector(
            near_vector=question_embedding.tolist(), # Assicurati che sia una lista
            limit=limit,
            # return_metadata=weaviate.classes.query.MetadataQuery(distance=True) # Opzionale: per vedere la distanza
        )
        
        print(f"Trovati {len(results.objects)} risultati.")
        # Estrai solo la proprietà 'text' dagli oggetti restituiti
        # return [obj.properties["text"] for obj in results.objects]
        
        # Restituisci più informazioni, inclusa la distanza se richiesta
        extracted_results = []
        for obj in results.objects:
            result_item = {"text": obj.properties.get("text", "N/A")}
            # if obj.metadata and obj.metadata.distance is not None: # Se hai richiesto la distanza
            #     result_item["distance"] = obj.metadata.distance
            extracted_results.append(result_item)
        return extracted_results

    except Exception as e:
        print(f"Errore durante l'interrogazione della collezione Weaviate '{collection_name}': {e}")
        return []
# --- Fine Definizione Funzioni ---


# --- Esempio di Utilizzo (decommenta e adatta) ---
if __name__ == "__main__":
    print("\n--- Inizio Esempio di Utilizzo ---")
    
    # Assicurati che Weaviate sia in esecuzione e la collezione sia creata.
    # Se la collezione "NoteChunks" non esiste, puoi crearla una volta:
    COLLECTION_NAME = "NoteChunks"
    try:
        if not client.collections.exists(COLLECTION_NAME):
            print(f"Collezione '{COLLECTION_NAME}' non trovata. Tentativo di creazione...")
            client.collections.create(
                name=COLLECTION_NAME,
                properties=[
                    Property(name="text", data_type=DataType.TEXT),
                    # Property(name="source_pdf", data_type=DataType.TEXT), # Esempio
                ],
                # vectorizer_config=None # Se fornisci i tuoi vettori
            )
            print(f"Collezione '{COLLECTION_NAME}' creata con successo.")
        else:
            print(f"Collezione '{COLLECTION_NAME}' già esistente.")
    except Exception as e:
        print(f"Errore durante la verifica/creazione della collezione '{COLLECTION_NAME}': {e}")
        print("Potrebbe essere necessario creare la collezione manualmente o controllare la connessione a Weaviate.")
        # exit() # Esci se la collezione è indispensabile e non può essere creata

    # Percorso del file PDF da elaborare
    # SOSTITUISCI CON UN PERCORSO VALIDO A UN TUO FILE PDF
    pdf_file_path = "test.pdf" # <--- CAMBIA QUESTO PERCORSO! 
                                     # Crea un file 'test.pdf' nella stessa directory
                                     # o fornisci un percorso assoluto.

    # Verifica se il file PDF di esempio esiste
    import os
    if not os.path.exists(pdf_file_path):
        print(f"\nATTENZIONE: Il file PDF di esempio '{pdf_file_path}' non è stato trovato.")
        print("Per eseguire l'esempio completo, crea un file PDF con quel nome")
        print("o modifica la variabile 'pdf_file_path' con un percorso a un PDF esistente.")
    else:
        # Carica il PDF nel database vettoriale
        print(f"\n--- Caricamento PDF: {pdf_file_path} ---")
        load_pdf_on_vector_db(pdf_file_path, collection_name=COLLECTION_NAME)

    # Esempio di interrogazione
    print("\n--- Esempio di Interrogazione ---")
    example_question = "Quali sono i punti chiave del documento?" # Modifica con una domanda pertinente al tuo PDF
    
    if not os.path.exists(pdf_file_path): # Salta l'interrogazione se il PDF non è stato caricato
         print(f"Salto dell'interrogazione perché il PDF '{pdf_file_path}' non è stato trovato/caricato.")
    else:
        similar_notes = query_notes(example_question, collection_name=COLLECTION_NAME)
        if similar_notes:
            print(f"\nRisultati simili per la domanda: '{example_question}'")
            for i, note_info in enumerate(similar_notes):
                print(f"Risultato {i+1}:")
                print(f"  Testo: {note_info['text']}")
                # if "distance" in note_info: # Se hai richiesto la distanza
                #     print(f"  Distanza: {note_info['distance']:.4f}")
                print("-" * 20)
        else:
            print(f"Nessun risultato trovato per la domanda: '{example_question}'")

    print("\n--- Fine Esempio di Utilizzo ---")

    # Chiudi la connessione al client Weaviate quando hai finito
    try:
        client.close()
        print("\nConnessione a Weaviate chiusa.")
    except Exception as e:
        print(f"Errore durante la chiusura della connessione a Weaviate: {e}")

