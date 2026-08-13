question = input()

relevant_chunks = search(question)

context = combine_chunks(relevant_chunks)

prompt = f"""
Answer the question using the provided context.

Context:
{context}

Question:
{question}
"""

response = gemini.generate_content(prompt)

print(response.text)