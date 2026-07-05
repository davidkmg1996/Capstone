"""
input: disease name, plant name
calls geminiAPI to get further information abotu the disease
    treatment
    future prevention
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

def gemini_disease_elaboration(disease_name, plant_name, client):
    
    prompt = f"For the plant disease {disease_name}, and the plant type {plant_name}, provide recommendations on how best to treat this aflicted plant, as well as prevention strategies for the future."
    prompt += " Provide citations for any information that is pulled from the web, and include a list of sources at the end with URLs."

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
    description="Take disease name and a plant name from input"
)
parser.add_argument("disease_name", type=str)
parser.add_argument("plant_name", type=str)
args = parser.parse_args()
disease_name = args.disease_name
plant_name = args.plant_name

client = genai.Client(api_key="AIzaSyDmU4LIqBRonbzJHLMr1yujWwYdBWEWCGc")
response = gemini_disease_elaboration(disease_name, plant_name, client)
print_with_sources(response=response)