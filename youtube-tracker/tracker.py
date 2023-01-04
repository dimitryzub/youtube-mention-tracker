'''
SerpApi demo project by Dmitriy Zub, Developer Advocate at SerpApi.
Contact: dimitryzub@gmail.com

Project idea:
The idea of this project is placed around similar tool called Mention but for videos only.
I've decided to translate this ideas to extract mentions from videos itself.

Why? For example, if you want to track if someone said certain keywords like "Serp Api" or "new javascript framework"
and you want understand what's the new framework is. Another example is a keyword like "bad <company-name> service".
This is direct feedback from a customer on which the company can reflect.

Limitations:
1. No support for filenames with emojies.
2. No support for saving files longer than 60 minutes. Longer transcript.

Things to improve:
1. Async videos download or reading audio as a stream instead of saving?
2. Transcribing as a stream. Whisper can't do it at the time this demo is written. https://github.com/openai/whisper/discussions/2#discussioncomment-3702403
3. Run searches with cron job. Identify new videos for the same query(ies). 
4. Speed up Pagination with multithreading (?). Commented out in the code to show how its done. https://github.com/serpapi/google-search-results-python#batch-asynchronous-searches
5. Remove code duplication. Like creating centered button, SAVE_OPTION conditions (lines 258-311)
'''

from urllib.parse import (parse_qsl, urlsplit)
from serpapi import YoutubeSearch
from pytube import YouTube
import pytube.exceptions as exceptions
from queue import Queue
import streamlit as st
import whisper
import re, os, time
import subprocess
import pathlib
from stqdm import stqdm
import math, base64
import pandas as pd
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

VIDEOS_DOWNLOAD_PATH = pathlib.Path(__file__).parent.resolve() / 'videos' 
print(pathlib.Path().absolute())

if VIDEOS_DOWNLOAD_PATH.exists():  
    subprocess.run(['rm', '-rf', f'{VIDEOS_DOWNLOAD_PATH}']) # remove videos on each new run

# create videos folder if not exist. Temporary store videos.
if not VIDEOS_DOWNLOAD_PATH.exists():
    os.makedirs('videos', exist_ok=True)


def main():
    # TODO: add a blog post link to "SerpApi Demo Project"
    footer_modified = '''
            <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                .footer {
                    position: fixed;
                    left: 0;
                    bottom: 0;
                    width: 100%;
                    background-color: white;
                    color: black;
                    text-align: center;
                    font-size: 8px;
                }
            </style>
            <div class="footer">
                <p align="center" style="padding-top: 200px;">SerpApi Demo Project (<a href="https://github.com/dimitryzub/youtube-mention-tracker">repo</a>)<br>Made with <a href="https://streamlit.io/">Streamlit</a>, <a href="http://serpapi.com/">SerpApi</a>, <a href="https://github.com/pytube/pytube">PyTube</a>, <a href="https://github.com/openai/whisper">Whisper</a> 🧡</p>
            </div>
    '''
    st.markdown(footer_modified, unsafe_allow_html=True) 
    
    st.title('📺YouTube Videos Mention Tracker')
    st.markdown(body="This demo parses, downloads and transcribes YouTube videos to find target mention(s) inside the video(s). It's similar to [Mention](https://mention.com/en/) but for videos.")
    
    if 'visibility' not in st.session_state:
        st.session_state.visibility = 'visible'
        st.session_state.disabled = False

    SEARCH_QUERY: str = st.text_input(label='Search query', placeholder='Data Nerd', help='Multiple search queries is not supported')      # used to parsing youtube videos
    TARGET_KEYWORD: str = st.text_input(label='Target keyword', placeholder='SQL', help='Multiple target keywords is not supported')  # used for in the speech recognition
    NUMBER_OF_VIDEOS_TO_ANALYZE: int = st.slider(label='Number of videos to analyze', min_value=1, max_value=20, help='By default, extracted videos will be no longer than 20 minutes. Its done by filtering YouTube results with [`sp`](https://serpapi.com/youtube-search-api#api-parameters-advanced-youtube-parameters-sp) URL parameter.')
    SAVE_OPTION = st.selectbox(label='Choose file format to save', options=(None, 'CSV'), help='By default data wont be saved. Choose CSV or JSON format if you want to save the results.')
    # PAGINATION = st.checkbox(label='Enable pagination') # increase amount of videos to parse

    # submit button
    col1, col2, col3 , col4, col5 = st.columns(5)
    with col1:
        pass
    with col2:
        pass
    with col4:
        pass
    with col5:
        pass
    with col3:
        submit_button_holder = st.empty()
        submit_search = submit_button_holder.button(label='Find mentions') # centered button
    
    if submit_search and not SEARCH_QUERY:
        st.error(body='Looks like you click a button without a search query. Please enter a search query 👆')
        st.stop()
        
    if submit_search and SEARCH_QUERY and NUMBER_OF_VIDEOS_TO_ANALYZE:
        search_queue = Queue()

        params = {
            'api_key': os.getenv('SERPAPI_API_KEY'),  # https://serpapi.com/manage-api-key
            'engine': 'youtube',                      # search engine
            'sp': 'EgIYAw%253D%253D',                 # filter to control length of the video: https://serpapi.com/youtube-search-api#api-parameters-advanced-youtube-parameters-sp
            'device': 'desktop',                      # device type
            'search_query': SEARCH_QUERY,             # search query
            'async': True                             # async batch requests
        }

        search = YoutubeSearch(params)                # where data extraction happens
        results = search.get_dict()                   # JSON -> Python dict
        
        search_queue.put(results)

        videos = []
        
        with st.spinner(text='Parsing YouTube Videos...'):
            while not search_queue.empty():
                result = search_queue.get()
                search_id = result['search_metadata']['id']

                # print(f'Get search from archive: {search_id}')
                search_archived = search.get_search_archive(search_id) # where all extracted data is stored and accessed
                
                # print(f"Search ID: {search_id}, Status: {search_archived['search_metadata']['status']}")

                if re.search(r'Cached|Success', search_archived['search_metadata']['status']):
                    for video_result in search_archived.get('video_results', []):
                        if video_result.get('title') not in videos:
                            # can't contain emojies in the file name
                            title = video_result.get('title') \
                                .replace('|', '')\
                                .replace('/', '')\
                                .replace('?', '')\
                                .replace(':', '')\
                                .replace('<', '')\
                                .replace('>', '')\
                                .replace('\\','')\
                                .replace('', '') \
                                .replace('*', '')
                            videos.append({
                                'title': title,
                                'link': video_result.get('link'),
                                'file_path': f"{title}.mp4"
                            })
                            
                        if len(videos) == NUMBER_OF_VIDEOS_TO_ANALYZE:
                            print(f'downloading {len(videos)} videos')
                            break
                    
                    # increase amount of videos to parse
                    # if PAGINATION:    
                    #     if 'next' in search_archived.get('serpapi_pagination', {}):
                    #         search.params_dict.update(dict(parse_qsl(urlsplit(search_archived['serpapi_pagination']['next']).query)))
                            
                    #         new_page_result = search.get_dict() # new results from updated (next) page
                    #         search_queue.put(new_page_result)   # add to queue results from updated (next) page
                else:
                    # print(f'Requeue search: {search_id}')
                    search_queue.put(result)
                
        parsing_is_success = st.success('Done parsing 🎉')
        time.sleep(1)
        
        if parsing_is_success:
            parsing_is_success.empty()

            with st.spinner(text='Downloading YouTube Videos...'):
                download_info = st.info(body='Note: downloading speed depends on video length (the longer the video the more time it take to download) and your internet speed 📡')
                
                # https://discuss.streamlit.io/t/stqdm-a-tqdm-like-progress-bar-for-streamlit/10097
                for video in stqdm(videos):
                    youtube_downloader = YouTube(url=video['link'])
                    print(f'Downloading {video["link"]}')
                    
                    try: 
                        # download only audio from youtube video
                        # relace is the `filename` is used to to replace not allowed characters
                        youtube_downloader.streams \
                            .filter(only_audio=True) \
                            .first() \
                            .download(
                                output_path=VIDEOS_DOWNLOAD_PATH,
                                filename=video['file_path']
                                )
                    except exceptions.LiveStreamError: 
                        print(f"Video {video['link']} is a livestream, couldn't download.")
                        pass
                    except exceptions.VideoUnavailable:
                        print(f'Video {video["link"]} unavailable, skipping.')
                        pass
                    
            downloading_videos_success = st.success('Done downloading 🎉')
            
            time.sleep(5)
            downloading_videos_success.empty()
            download_info.empty()
            submit_button_holder.empty()
        
        # transcribe with whisper 
        transcript_data = []
        
        if VIDEOS_DOWNLOAD_PATH.exists():
           with st.spinner(text='Transcribing Videos...'):
                transcript_note = st.info(body='Note: it may take some time to process all audio files, especially if video is 20+ minutes long.')
               
                # iterate through video files to transcribe
                model = whisper.load_model('base')

                for video in videos:
                    mp4_file_path = f'~/youtube-mention-tracker/videos/{video["file_path"]}'
                    transcribed_audio = model.transcribe(mp4_file_path, fp16=False)

                    # generic check to check if transcibe text is present to do further tasks
                    # it could be [] or str: "... ... ... ... ...", if it's a song with no text
                    if transcribed_audio['text']:
                        for segment in transcribed_audio['segments']:
                            if TARGET_KEYWORD in segment['text'].lower():
                                transcript_data.append({
                                    'video_title': video['title'],
                                    'timestamp_url': f'{video["link"]}&t={math.floor(segment["start"])}', # <url>&t=488s
                                    # 'timestamp': segment['start'],
                                    'text': segment['text']
                                })
                                # print(segment)
                                # print(f'Found target keyword from {video["title"]}, timestamp: {segment["start"]}')
                                # print(f'Text: {segment["text"]}')
                    else: pass
                    
        transcipt_success = st.success('Done transcribing 🎉')
        
        time.sleep(4)
        transcript_note.empty()
        transcipt_success.empty()
        
        transcribed_results_info = st.markdown(body='#### Transcribed results')
        TRANSCRIPT_TABLE = st.table(data=transcript_data)
       
        time.sleep(3)
        
        # start over
        with col1:
            pass
        with col2:
            pass
        with col4:
            pass
        with col5:
            pass
        with col3:
            start_over_button_holder = st.empty()
            start_over_button = st.button(label='Start over') # centered button
        
        if SAVE_OPTION == 'CSV' and transcript_data: 
            # save to CSV with Pandas
            save_csv(df=transcript_data) # draw a download CSV anchor tag  
            
            start_over_info_holder = st.empty()
            start_over_info_holder.error(body="To rerun the script, click on the 'Start over' button, or refresh the page.")
            
            if start_over_button:  
                subprocess.run(['rm', '-rf', f'{VIDEOS_DOWNLOAD_PATH}'])
                
                TRANSCRIPT_TABLE.empty()
                transcribed_results_info.empty()
                start_over_button_holder.empty() 
                start_over_info_holder.empty()
                
        if SAVE_OPTION == 'CSV' and not transcript_data:
            TRANSCRIPT_TABLE.empty()
            transcribed_results_info.empty()
            
            no_data_holder = st.empty()
            no_data_holder.error('No target keyword found. Click *Start Over* button and try different keyword.')
                
            if start_over_button:  
                subprocess.run(['rm', '-rf', f'{VIDEOS_DOWNLOAD_PATH}'])
                
                no_data_holder.empty()
                start_over_button_holder.empty()
            
        if SAVE_OPTION is None and transcript_data:
            start_over_info_holder = st.empty()
            start_over_info_holder.error(body="To rerun the script, click on the 'Start over' button, or refresh the page.")
            
            if start_over_button:  
                subprocess.run(['rm', '-rf', f'{VIDEOS_DOWNLOAD_PATH}'])
                
                TRANSCRIPT_TABLE.empty()
                transcribed_results_info.empty()
                start_over_button_holder.empty() 
                start_over_info_holder.empty()
                
        if SAVE_OPTION is None and not transcript_data:
            TRANSCRIPT_TABLE.empty()
            transcribed_results_info.empty()
            
            no_data_holder = st.empty()
            no_data_holder.error('No target keyword found. Click *Start Over* button and try different keyword.')   
            
            if start_over_button:  
                subprocess.run(['rm', '-rf', f'{VIDEOS_DOWNLOAD_PATH}'])
                
                TRANSCRIPT_TABLE.empty()
                no_data_holder.empty()
                transcribed_results_info.empty()
                start_over_button_holder.empty()

def save_csv(df): 
    # https://stackoverflow.com/a/68071190/15164646
    csv_file = pd.DataFrame(data=df).to_csv(index=False)
    b64_csv_file = base64.b64encode(csv_file.encode()).decode()
    
    href = f'<a href="data:file/csv;base64,{b64_csv_file}" download="youtube-transcript.csv" >Download CSV</a>'
    st.markdown(href, unsafe_allow_html=True)


if __name__ == '__main__':
    main()