import re
import base64

def compress_html(html_content):
    """Compress HTML by removing unnecessary whitespace and optimizing code"""
    
    # Remove HTML comments
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)

    # Remove whitespace between tags
    html_content = re.sub(r'>\s+<', '><', html_content)

    # Remove leading/trailing whitespace from lines
    html_content = re.sub(r'^\s+', '', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'\s+$', '', html_content, flags=re.MULTILINE)

    # Collapse multiple spaces into one
    html_content = re.sub(r' +', ' ', html_content)

    # Remove spaces around = in attributes
    html_content = re.sub(r'\s*=\s*', '=', html_content)

    # Minify CSS in style tags
    html_content = minify_inline_css(html_content)

    # Remove empty lines
    html_content = re.sub(r'\n\s*\n', '\n', html_content)

    return html_content.strip()

def minify_inline_css(html_content):
    """Minify CSS within style tags and style attributes"""

    def minify_css(match):
        css = match.group(1)
        # Remove comments
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        # Remove whitespace
        css = re.sub(r'\s+', ' ', css)
        css = re.sub(r'\s*([{}:;,])\s*', r'\1', css)
        return f'<style>{css.strip()}</style>'

    # Minify style tags
    html_content = re.sub(r'<style[^>]*>(.*?)</style>', minify_css, html_content, flags=re.DOTALL | re.IGNORECASE)

    # Minify style attributes
    def minify_style_attr(match):
        style = match.group(1)
        style = re.sub(r'\s+', ' ', style)
        style = re.sub(r'\s*([{}:;,])\s*', r'\1', style)
        return f'style="{style.strip()}"'

    html_content = re.sub(r'style=["\']([^"\']+)["\']', minify_style_attr, html_content, flags=re.IGNORECASE)

    return html_content
