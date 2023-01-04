# YouTube Mention(s) Tracker

## Purpose/Idea

The main idea is taken from a great tool called [Mention](https://mention.com/en/). This demo shows the same idea but for YouTube videos only.

If you want to track someone said certain keywords like "Serp Api" or "new javascript framework"
and you want understand what's the new framework is, this is what this demo app will do. 

Another example is a keyword like "bad `company-name` service".
This is direct feedback from a customer on which the company can reflect.

## Video Example

https://user-images.githubusercontent.com/78694043/210506842-bdf91d41-a9ad-4c1e-bac1-c2d871bcf597.mp4


This is how transcribed results (if any) would look like:

![transcribed-results](https://user-images.githubusercontent.com/78694043/210507490-37e2e799-842f-4a54-a189-d34b022bd23e.png)

## Usage 

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