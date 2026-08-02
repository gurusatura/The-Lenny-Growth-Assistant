import os

# Path relative to this file: backend/app/../data/transcript.txt
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSCRIPT_PATH = os.path.join(BASE_DIR, "data", "transcript.txt")

def load_transcript() -> str:
    """Reads the raw transcript text from transcript.txt."""
    if not os.path.exists(TRANSCRIPT_PATH):
        raise FileNotFoundError(f"Transcript file not found at: {TRANSCRIPT_PATH}")
    with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

def chunk_by_words(text: str, chunk_size: int = 100, overlap: int = 20) -> list[str]:
    """
    Splits text into chunks based on a target word count, with an overlap between consecutive chunks.
    
    :param text: The input document text to chunk.
    :param chunk_size: The maximum number of words allowed in each chunk.
    :param overlap: The number of overlapping words between consecutive chunks.
    :return: A list of text chunks.
    """
    # Clean up double/multiple spacing and trailing spaces
    cleaned_text = " ".join(text.split())
    words = cleaned_text.split()
    
    chunks = []
    
    # If the text has fewer words than the chunk size, return the whole text as one chunk
    if len(words) <= chunk_size:
        return [cleaned_text]
        
    # We step by (chunk_size - overlap) to ensure the overlap is maintained
    step = chunk_size - overlap
    
    # Slide a window across the list of words
    for i in range(0, len(words), step):
        # Select current slice of words
        chunk_slice = words[i:i + chunk_size]
        # Rejoin back into a single string
        chunk_str = " ".join(chunk_slice)
        chunks.append(chunk_str)
        
        # If we've reached or gone past the end of the words list, terminate the loop
        if i + chunk_size >= len(words):
            break
            
    return chunks

if __name__ == "__main__":
    raw_data = load_transcript()
    print("--- Loaded Raw Data from transcript.txt ---")
    print(f"Total length of raw text: {len(raw_data)} characters")
    
    # Chunk raw text by words (e.g., chunk size of 80 words, 15 words overlap)
    chunks = chunk_by_words(raw_data, chunk_size=80, overlap=15)
    
    print(f"\n--- Created {len(chunks)} Chunks ---")

    for index, chunk in enumerate(chunks, 1):
        print(f"\n[Chunk {index} - Word count: {len(chunk.split())} words]")
        print(chunk)
        print("-" * 50)