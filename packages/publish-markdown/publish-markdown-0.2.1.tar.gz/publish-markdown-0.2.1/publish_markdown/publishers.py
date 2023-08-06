# Standard library
import json
import os
import sys
from urllib.parse import urlparse

# Packages
import frontmatter
import requests


class Medium:
    """
    API functions for posting an article to medium.com
    """

    def __init__(self):
        self.token = os.environ["MEDIUM_TOKEN"]
        self.user_id = os.environ.get("MEDIUM_USER_ID")

        if not self.user_id:
            self.user_id = self.get_user_id()

    def _request(self, url: str, method: str = "get", data: dict = {}):
        response = requests.request(
            url=url,
            method=method,
            data=json.dumps(data),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            }
        )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            response = error.response
            print(f"- [ERROR { response.status_code }]: { response.text }")
            sys.exit(1)

        return response

    def get_user_id(self):
        response = self._request(url="https://api.medium.com/v1/me")

        user_id = response.json()["data"]["id"]

        print(f"Found user ID: {user_id}")

        return user_id

    def post_article(self, title: str, body: str, tags: list = [], canonical_url: str = None):
        print(f"- Posting to medium.com")

        response = self._request(
            url=f"https://api.medium.com/v1/users/{self.user_id}/posts",
            method="post",
            data={
                "title": title,
                "contentFormat": 'markdown',
                "content": body,
                "canonicalUrl": canonical_url,
                "tags": tags,
                "publishStatus": 'public',
            }
        )

        published_url = response.json()["data"]["url"]

        print(f"- Article published at { published_url }")

        return published_url



class DEV:
    """
    API functions for posting an article to dev.to
    """

    def __init__(self):
        self.token = os.environ["DEV_TO_TOKEN"]

    def post_article(self, title: str, body: str, tags: list = [], canonical_url: str = None):
        print(f"- Posting article to dev.to")

        response = requests.post(
            "https://dev.to/api/articles",
            headers={
                "Content-Type": "application/json",
                "api-key": self.token,
            },
            data=json.dumps(
                {
                    "article": {
                        "title": title,
                        "tags": tags,
                        "published": True,
                        "canonical_url": canonical_url,
                        "body_markdown": body
                    }
                }
            )
        )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            response = error.response
            print(f"- [ERROR {response.status_code}]: {response.text}")
            sys.exit(1)

        published_url = response.json()["url"]

        print(f"- Article published at { published_url }")

        return published_url


class MarkdownArticle:
    """
    A representation of an article in a Markdown file, allowing you to:

    - Parse Markdown and frontmatter
    - Update "published_to" keys
    - Append a canonical_url to the markdown contents
    """

    def __init__(self, filepath, canonical_url=None):
        self.filepath = filepath
        self.canonical_url = canonical_url

    def _get_metadata(self, key):
        parsed_article = frontmatter.load(self.filepath)

        return parsed_article.get(key)


    @property
    def title(self):
        return self._get_metadata("title")

    @property
    def tags(self):
        return self._get_metadata("tags")

    @property
    def published_to(self):
        return self._get_metadata("published_to")

    @property
    def markdown(self):
        parsed_article = frontmatter.load(self.filepath)

        markdown = parsed_article.content

        # If there's a canonical_url, add a line to the beginning to say so.
        if self.canonical_url:
            scheme = urlparse(self.canonical_url).scheme

            friendly_url = self.canonical_url.removeprefix(f"{scheme}://")

            markdown = (
                "_Originally published at "
                f"[{ friendly_url }]({ self.canonical_url })_\n\n"
            ) + markdown

        return markdown

    def update_published_to(self, url):
        """
        Update markdown article to mention where it was published
        """

        domain = urlparse(url).netloc

        parsed_article = frontmatter.load(self.filepath)

        if "published_to" in parsed_article:
            parsed_article["published_to"][domain] = url
        else:
            parsed_article["published_to"] = {domain: url}

        print(f"- Added '{domain}' to 'published_to' metadata")

        frontmatter.dump(parsed_article, self.filepath)



def markdown_to_medium(filepath, canonical_url=None):
    article = MarkdownArticle(filepath, canonical_url)

    if article.published_to and "medium.com" in article.published_to:
        print("- Article was already published to medium.com")
        return

    published_url = Medium().post_article(
        title = article.title,
        body = f"# {article.title}\n\n{ article.markdown }",
        tags = article.tags,
        canonical_url = article.canonical_url,
    )

    article.update_published_to(published_url)

    return published_url


def markdown_to_DEV(filepath, canonical_url=None):
    article = MarkdownArticle(filepath, canonical_url)

    if article.published_to and "dev.to" in article.published_to:
        print("- Article was already published to dev.to")
        return

    published_url = DEV().post_article(
        title = article.title,
        body = article.markdown,
        tags = article.tags,
        canonical_url = article.canonical_url,
    )

    article.update_published_to(published_url)

    return published_url
