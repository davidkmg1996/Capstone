"""
input: "plant_name" symptom1,symptom2,etc(no spaces)
"""

import argparse
import requests
from google import genai
from google.genai import types

def print_with_sources(response):
    text = response.text

    metadata = response.candidates[0].grounding_metadata
    chunks = metadata.grounding_chunks  #array of chunks
        #chunk: id: string, web: {uri, title}, retrieved_context: {text: "the text pulled from this source", text2, etc.}
        #web.title, web.uri
        #retrieved_content.text
    supports = metadata.grounding_supports  #associate text segments to websites, array of supports
        #support: segment: {start_index, end_index, text: "excerpt from response""},
                #grounding_chunk_indices: [list of indices that map the list of segments to chunks],
                # confidence: float

    #whenever a support appears in text, insert citation number directly after
    for support in supports:
        cited_text = support.segment.text
        
        citation=""
        for index in support.grounding_chunk_indices:
            if citation=="":
                citation += f"{index}"
            else:
                citation += f", {index}"
        citation = " (" + citation + ")"

        replacement_text = cited_text + citation
        text = text.replace(support.segment.text, replacement_text)

    disclaimer = "The following information was generated with Gemini AI. We recommend verifying the factuality of this response by checking the cited sources via the links below.\n\n"
    print(disclaimer +text, "\n\nSources:")
    if chunks:
        for i, chunk in enumerate(chunks):
            url = resolve_url(chunk.web.uri)
            print(f"[{i+1}] {chunk.web.title}: {url}")
    else:
        print("No web sources.")

def gemini_diagnosis(plant_name, symptoms, client):
    prompt = f"Identify the most likely disease affecting a {plant_name} with the following symptoms: {', '.join(symptoms)} affecting the plant's leaves."
    prompt += " Provide a list of the five most likely diseases if there are that many likely candidates."
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )
    return response

def resolve_url(redirect_url):
    try:
        r = requests.head(redirect_url, allowredirects=True, timeout=5)
        return r.url
    except:
        return redirect_url



parser = argparse.ArgumentParser(
    description="Take plant name and list of symptoms from input"
)
parser.add_argument("plant_name", type=str)
parser.add_argument("symptoms", type=str, help="Comma-separated list of symptoms")
args = parser.parse_args()
plant_name = args.plant_name
symptoms = [symptom.strip() for symptom in args.symptoms.split(",")]

client = genai.Client(api_key="AIzaSyDmU4LIqBRonbzJHLMr1yujWwYdBWEWCGc")
response = gemini_diagnosis(plant_name, symptoms, client)
print_with_sources(response=response)



"""
prompt="Tell me about how to identify and treat the plant disease Septoria Leaf Blight."
prompt+=" Accompany all statements of fact with an appropriate source from which that fact was taken."
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )
)
print_with_sources(response=response)
"""

"""
RAG with Gemini API:
Ingestion: You upload files (PDFs, DOCX, TXT, etc.) to a File Search Store.
Processing: Gemini automatically chunks the text, generates embeddings, and indexes them in a managed vector store.
Retrieval: When you send a prompt, you simply attach the file_search tool. Gemini automatically searches your store for relevant snippets.
Generation: The model uses the retrieved context to answer your question and provides citations pointing back to the source documents.
"""

"""
{
  "Plant": "Almond",
  "Probability": 0.1746,
  "Management": "No management info",
  "Classification": "unknown"
}
"""

'''
create separate function called gemini_api_call in ESTest.py file
'''