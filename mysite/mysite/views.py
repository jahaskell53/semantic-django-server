from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from ratelimit.decorators import ratelimit

import requests
from bs4 import BeautifulSoup
import openai
import json
from decouple import config

from django.http import HttpResponse

def sem_src_on_query(query: str, url: str) -> list:
    openai.api_key = config('OPENAI_API_KEY')

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    website_text = soup.get_text()
    MAX_CHAR_COUNT = 1000
    MAX_SEGMENT_COUNT = 190
    segments_of_website = segmentize(website_text, MAX_CHAR_COUNT, MAX_SEGMENT_COUNT)

    def write_to_file_as_jsonl(array_of_sentences: list):
        with open('webpage.jsonl', 'w') as f:
            for sentence in array_of_sentences:
                dict = {'text': sentence}
                f.write(json.dumps(dict) + '\n')

    write_to_file_as_jsonl(segments_of_website)

    # for uploading document to document server
    # upload_response = openai.File.create(file=open("webpage.jsonl"), purpose="search")
    # print(upload_response.id)

    response_from_query: dict = openai.Engine('ada').search(
        search_model = "ada",
        query=query,
        max_rerank=5,
        documents=segments_of_website,
        return_metadata=False)

    list_of_docs = response_from_query['data']
    list_of_docs.sort(key=lambda object: object.score, reverse=True)
    print("highest result", segments_of_website[list_of_docs[0].document]) 
    print("second highest result", segments_of_website[list_of_docs[1].document]) 
    print("third highest result", segments_of_website[list_of_docs[2].document]) 
    NUM_OF_RESULTS = 3
    return [segments_of_website[list_of_docs[i].document] for i in range(NUM_OF_RESULTS)]

def segmentize(website_text, MAX_CHAR_COUNT, MAX_SEGMENT_COUNT):
    segments_of_website = []
    curr_char_count = 0
    curr_chars = ''
    total_segment_count = 0
    for curr_char in website_text:
        if total_segment_count > MAX_SEGMENT_COUNT:
            break
        curr_char_count+=1
        curr_chars += curr_char
        if curr_char_count > MAX_CHAR_COUNT:
            total_segment_count+=1
            segments_of_website.append(curr_chars)
            curr_chars = ''
            curr_char_count = 0
    return segments_of_website

def fake_response():
    return ['the', 'hello', 'and']

@csrf_exempt
@ratelimit(key='ip', rate='20/h', block=True)
def process_query_from_ext(request) -> JsonResponse:
    print(request)
    response: str = json.loads(HttpResponse(request).content.decode('utf-8'))
    if response['apiKey'] in json.loads(config('VALID_API_KEY_LIST')) and response['test'] is False:
        what_to_send = sem_src_on_query(response['query'], response['url'])
        return JsonResponse({'status': 'SUCCESS', 'message': 'Here are the results from the webpage', 'resultsArr': what_to_send})  
    if response['apiKey'] in json.loads(config('VALID_API_KEY_LIST')) and response['test'] is True:
        what_to_send = fake_response()
        return JsonResponse({'status': 'SUCCESS', 'message': 'Here are the fake results', 'resultsArr': what_to_send}, status=200) 
    return JsonResponse({'status': 'FAILURE', 'message': 'Invalid API Key', 'resultsArr': []}, status=401)
    