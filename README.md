# YouTube Mention(s) Tracker

<p align="center";><a href="https://dimitryzub-youtube-mention-tracke-youtube-trackertracker-qu7mh3.streamlit.app/">Streamlit YouTube Videos Mention Tracker Demo</a></p>

## Purpose/Idea

The main idea is taken from a great tool called [Mention](https://mention.com/en/). This demo shows the same idea but for YouTube videos only by transcribing videos (even if the video without captions). 

**Scenario**: user wants to track someone said certain keywords like "Serp Api". Or a query "switching from iphone to..." and target keyword like "poor" (for poor quality), or "No..." (no support for certain feature that android has) and similar keywords that may identify reasons of switching.

Another example is a certain search query in a company niche and a target keyword to look in those videos that may benefit company by getting more context out of it.

<details>
<summary>Things to improve</summary>

    1. Async videos download or reading audio as a stream instead of saving?
    2. Transcribing as a stream. Whisper can't do it at the time this demo is written. https://github.com/openai/whisper/discussions/2#discussioncomment-3702403
    3. Run searches with cron job. Identify new videos for the same query(ies). 
    4. Speed up pagination (if using) with multithreading (?). Commented out in the code to show how pagination done without multithreading. https://github.com/serpapi/google-search-results-python#batch-asynchronous-searches
    5. Remove code duplication. Like creating centered button, SAVE_OPTION conditions (lines 258-311)
</details> 

## Video Example

https://user-images.githubusercontent.com/78694043/210506842-bdf91d41-a9ad-4c1e-bac1-c2d871bcf597.mp4


This is how transcribed results (if any) would look like:

![transcribed-results](https://user-images.githubusercontent.com/78694043/210507490-37e2e799-842f-4a54-a189-d34b022bd23e.png)

## Usage

This section if you want to use your own API key. [The demo on `streamlit`](https://dimitryzub-youtube-mention-tracke-youtube-trackertracker-qu7mh3.streamlit.app/) doesn't require you to use any API key.

Clone repository:

```bash
$ git clone https://github.com/dimitryzub/youtube-mention-tracker.git
```

Install dependencies:

```bash
$ cd youtube-mention-tracker && pip install -r requriements.txt
```

Add [SerpApi api key](https://serpapi.com/manage-api-key) for current shell and all processes started from current shell:

```bash
# used to parse youtube videos, has a plan of 100 free searches
$ export SERPAPI_API_KEY=<your-api-key>
```

Run the app:

```bash
$ cd youtube-tracker && streamlit run tracker.py
```

<p align="center";>Sponsored by <a href="https://serpapi.com/">SerpApi</a> 🧡</p>