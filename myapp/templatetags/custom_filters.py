from django import template
from django.utils.html import strip_tags
import html

register = template.Library()

@register.filter
def truncatewords_html(value, arg):
    """
    Truncates HTML content to a given number of words while preserving HTML structure.
    """
    try:
        length = int(arg)
    except ValueError:  # invalid literal for int()
        return value  # Fail silently.

    if not isinstance(value, str):
        value = str(value)

    # Strip HTML tags and count words
    plain_text = strip_tags(value)
    words = plain_text.split()
    if len(words) <= length:
        return value

    # Truncate words
    truncated_words = words[:length]
    truncated_text = ' '.join(truncated_words) + '...'

    # Reconstruct HTML with truncated content (simplified approach)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(value, 'html.parser')
    text_nodes = soup.find_all(string=True)
    current_pos = 0
    new_content = []

    for node in text_nodes:
        node_text = node.strip()
        if not node_text:
            continue
        node_words = node_text.split()
        if current_pos + len(node_words) <= length:
            new_content.append(str(node))
            current_pos += len(node_words)
        else:
            remaining_words = length - current_pos
            if remaining_words > 0:
                truncated_node = ' '.join(node_words[:remaining_words]) + '...'
                new_node = BeautifulSoup(f"<span>{truncated_node}</span>", 'html.parser').span
                new_content.append(str(new_node))
            break

    return ''.join(new_content) or truncated_text