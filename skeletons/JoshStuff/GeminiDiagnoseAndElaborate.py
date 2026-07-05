"""
Docstring for capstone_project.GeminiAPISecondOpinionAndNextSteps
This script combines my other two since they have so much overlap.
Input is a plant name and either a list of sumptoms (symptom1,symptom2,etc no spaces) or else a disease name, followed by one of the following arguments: "diagnosis" or "elaboration:.
    diagnosis corresponds to inputting an array of symnptoms, and will prompt Gemini to diagnose the plant.
    elaboration corresponds to inputting disease names, and will prompt Gemini to provide treatment recommendations and strategies for future prevention.
Both modes, diagnosis and elaboration, will include citations for any information pulled from the web, and a list of sources at the end with URLs.
"""

import argparse
from xmlrpc import client
import requests
from google import genai
from google.genai import types

elaboration_schema = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "required": ["items"]
}

def print_with_sources(disclaimer, response):
    #Insert in-text citations into the response text, and print a list of corresponding sources with URLs at the end.
        #in-text citations are just integers counting from 1, and correspond to the numbered list of sources at the end for easy user reference.
        #prepend a disclaimer for the user telling them the response is AI generated and they should verify each claim via the sources
    #change from print to the creation of strings that will be written to a JSON to be sent back to the frontend.

    #setup using google.genai.types module, 
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

    #print final message
    print(disclaimer +text, "\n\nSources:")
    if chunks:
        for i, chunk in enumerate(chunks):
            url = resolve_url(chunk.web.uri)
            print(f"[{i+1}] {chunk.web.title}: {url}")
    else:
        print("No web sources.")

def gemini_call(prompt, client, mode):
    #sends whatever prompt is to gemini, which searches the web as research before spitting {response} back out. Be sure prompt is correct for the mode/input (diagnosis vs elaboration)
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            response_mime_type="application/json",
            response_schema=elaboration_schema,
            temperature=0.2
        )
    )      
    return response

def resolve_url(redirect_url):
    #Takes a google redirect URL and returns the actual URL. Grounding chunks only provide the google redirect link, which isn't ideal for users.
    try:
        r = requests.head(redirect_url, allowredirects=True, timeout=5)
        return r.url
    except:
        return redirect_url
    #TODO this isn't working, figure out how to get the actual URL instead of the google middleman link

#TODO create proper prompt from input args depending on mode (diagnosis vs elaboration)

parser = argparse.ArgumentParser(
    description="Enter a plant name, either a comma-separated list of symptoms or disease names, and either 'diagnosis' or 'elaboration'"
)
parser.add_argument("plant_name", type=str, help="Name of the plant")
parser.add_argument("symptoms_or_disease", type=str, help="Either a comma-separated list of symptoms (symptom1,symptom2,etc no spaces) or else a disease name")
parser.add_argument("mode", type=str, choices=["diagnosis", "elaboration"], help="diagnosis for symptom input, elaboration for disease name input")
args = parser.parse_args()
plant_name = args.plant_name
symptoms_or_disease = args.symptoms_or_disease 
mode = args.mode

prompt = ""
if mode=="diagnosis":
    symptoms = [symptom.strip() for symptom in symptoms_or_disease.split(",")]
    prompt = f"Identify the most likely plant disease affecting a {plant_name} plant with the following symptoms: {', '.join(symptoms)} affecting the plant's leaves."
    prompt += " Provide a list of the five most likely plant diseases if there are that many likely candidates."
elif mode=="elaboration":
    disease_names = [name.strip() for name in symptoms_or_disease.split(",")]
    prompt = f"For the plant {plant_name}, provide recommendations on how best to treat each of the following plant diseases: {', '.join(disease_names)}"
    prompt +=", additionally, for each disease, provide details about its disease cycle, and prevention strategies for the future."

disclaimer = "The following information was generated with Gemini AI. We recommend verifying the factuality of this response by checking the cited sources via the links below.\n\n"
client = genai.Client(api_key="AIzaSyDmU4LIqBRonbzJHLMr1yujWwYdBWEWCGc")
response = gemini_call(prompt, client, mode)
print_with_sources(disclaimer=disclaimer, response=response)


'''
Changes That Need Made:
    output a JSON, key value pair with key being disease name and value being assessment.
    handle multiple diseases from one call.
    handle multiple diseases with one call to Gemini.
        set temperature low for more consistent formatting
    try out saving two different API keys to see if daily usage is tracked per key or per Google account.
'''