from __future__ import annotations
from cmarkgfm import github_flavored_markdown_to_html
from django.views import generic
from django.template.loader import get_template
from html.parser import HTMLParser

class _HTMLTagParser(HTMLParser):
    def __init__(self, searched_tag):
        super().__init__()
        self.searched_tag = searched_tag
        self.match = False
        self.data = None

    def handle_starttag(self, tag, attributes):
        self.match = tag == self.searched_tag

    def handle_data(self, data):
        if self.match:
            self.data = data
            self.match = False


def _find_html_tag_content(html: str, tag: str):
    parser = _HTMLTagParser(tag)
    parser.feed(html)
    return parser.data


class MarkdownTemplateView(generic.TemplateView):
    extends = "base.html"

    def render_to_response(self, context, **response_kwargs):
        markdown_template = get_template(self.template_name)
        markdown_text = markdown_template.render(context, self.request)
        html_content = github_flavored_markdown_to_html(markdown_text)

        new_context = {}
        new_context["extends"] = self.extends
        new_context["title"] = _find_html_tag_content(html_content, "h1")
        new_context["html_content"] = html_content
        return super().render_to_response(new_context, **response_kwargs)

    def get_template_names(self):
        return ["_content.html"] # located in main/templates
