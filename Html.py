def div_title(text):
    return f'<br><br><div class="section-title">{str(text)}</div>' if text else ''


def div_h3(text):
    return f'<br><h3>{str(text)}</h3>' if text else ''

def div_ul_start():
    return '<ul class="bullet">'


def div_li(text, link=None):
    if text and link:
        return f'<li><a href="{link}" target="_blank">{text}</a></li>'
    elif text:
        return f'<li>{text}</li>'
    return ''


def div_ul_end():
    return '</ul>'


def div_youtube(video_link):
    if not video_link: return ''
    return f'<iframe width="100%" height="400px" src="https://www.youtube-nocookie.com/embed/{video_link}" ' \
           f'frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" ' \
           f'allowfullscreen></iframe><br><br>'
