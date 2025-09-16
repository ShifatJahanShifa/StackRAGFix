from langchain_text_splitters import RecursiveCharacterTextSplitter

text = """Hello world!\nThis is a test of the recursive splitter.\nLet's see how it works.
"""

print(text)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=20,
    chunk_overlap=5,
    # separators=['\n', ' ', '']
)

# print(splitter._chunk_overlap, splitter._separators)
chunks = splitter.split_text(text)
for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1}, {len(chunk)}: {(chunk)}")
