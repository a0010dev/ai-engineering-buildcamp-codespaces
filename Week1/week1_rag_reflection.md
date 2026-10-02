# Week 1 — Document processing and RAG

During Week 1 of the AI Engineering Buildcamp, I processed the books listed in
`books.csv`: I downloaded their PDFs, converted them to Markdown with
`markitdown`, split the text into overlapping chunks, and built a searchable
RAG index with `minsearch` and OpenAI.

My main takeaway is that chunking depends on the unit being passed to the
chunker. In my pipeline, `size=100` and `step=50` mean 100 non-empty lines per
chunk with 50 lines of overlap, so the chunk size should be checked against the
actual document structure.

My next step is to evaluate retrieval quality with representative questions and
adjust the chunk size, overlap, and number of retrieved chunks based on the
results.

Notebook: [`books_rag.ipynb`](books_rag.ipynb)

Course: <https://maven.com/alexey-grigorev/from-rag-to-agents>
