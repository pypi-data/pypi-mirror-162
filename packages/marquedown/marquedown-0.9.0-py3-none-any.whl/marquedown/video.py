import re


RE_YOUTUBE_VIDEO = re.compile(r'\!\[.+\]\(https\:\/\/(?:(?:www\.)?youtube\.com|youtu\.be)\/([0-9A-Za-z-_]+)(?: \"(.*)\")?\)')


def _repl_youtube_video(match: re.Match):
    video_id, title = match.group(1, 2)
    return (
        f'<iframe '
        f'class="mqd-video" '
        f'src="https://www.youtube.com/embed/{video_id}" '
        f'title={title or "" !r} '
        f'frameborder="0" '
        f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
        f'allowfullscreen>'
        f'</iframe>'
    )


def video(document: str):
    """Notation for videos from recognised
    video sharing platforms that allow embedding.

    Supported platforms: YouTube
    
    YouTube:
        Marquedown:
            ![dimweb](https://youtu.be/VmAEkV5AYSQ "An embedded YouTube video")
        
        HTML:
            <iframe
                class="mqd-video"
                src="https://www.youtube.com/embed/VmAEkV5AYSQ"
                title="An embedded YouTube video" frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen>
            </iframe>
    """

    # Embed all YouTube videos
    document = RE_YOUTUBE_VIDEO.sub(_repl_youtube_video, document)

    return document