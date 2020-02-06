def div_title(text, m2=False):
    if not m2: return f'<br><br><div class="section-title">{str(text)}</div>' if text else ''
    return f'<br><br><div class="section-title"><strong>{str(text)}</strong></div>' if text else ''


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
    return f'<iframe width="800" height="450" src="https://www.youtube-nocookie.com/embed/{video_link}" ' \
           f'frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" ' \
           f'allowfullscreen></iframe><br><br>'
