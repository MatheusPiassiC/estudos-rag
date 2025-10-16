import argparse
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

from populate_db import get_embedding_function



CHROMA_PATH =  "C:/Users/mathe/Desktop/teste_rag/chroma_db"

PROMPT_TEMPLATE = """
Responda usando a língua: Português Brasileiro.
Seu objetivo é definir se uma determinada ação descrita na questão
vai contra as diretrizes da empresa Comp Júnior ou do Movimento Empresa
Júnior.
Foque em trazer apenas informações relevantes e relacionada à questão feita.
Caso você não consiga trazer uma repsosta válida, diga que não sabe,
e instrua sobre onde procurar mais informações.
Responda as quesões baseando-se também no seguinte contexto:

{context}

---

Responda a questão a seguir baseando-se apenas no contexto acima: {question}
"""

def query_rag(query_text: str):
    embedding_function =get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)

    model = OllamaLLM(model="mistral")
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)

    return response_text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)

if __name__ == "__main__":
    main()