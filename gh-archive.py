import urllib.request
import html.parser
import shutil
from pathlib import Path
import argparse
from argparse import ArgumentParser

GITHUB_URL = "https://github.com"


def url_open_decode(url: str):
    with urllib.request.urlopen(url) as response:
        encoding = response.headers.get_param("charset")
        return response.read().decode(encoding)


def find_list_pairs(key: str, list_pairs: list[tuple[str, str | None]]) -> str | None:
    d = dict(list_pairs)
    return d.get(key)


def get_repo_urls(user_name: str) -> list[str]:
    page_num = 1
    urls: list[str] = []
    while True:
        url = f"{GITHUB_URL}/{user_name}?page={page_num}&tab=repositories"
        html = url_open_decode(url)
        repo_url_parser = RepoUrlHTMLParser()

        repo_url_parser.feed(html)
        if not repo_url_parser.repo_urls:
            break

        urls += repo_url_parser.repo_urls

        page_num += 1

    return urls


def get_repo_archive_url(repo_url: str) -> str:
    repo_archive_url_parser = RepoArchiveUrlHTMLParser()
    html = url_open_decode(repo_url)
    repo_archive_url_parser.feed(html)
    return repo_archive_url_parser.archive_url


def download_archive(archive_url: str, dest_dir: str):
    repo_name = archive_url.lstrip(GITHUB_URL).split("/")[1]
    with urllib.request.urlopen(archive_url) as response:
        with open(Path(dest_dir, repo_name).with_suffix(".zip"), "wb") as file:
            shutil.copyfileobj(response, file)


class RepoUrlHTMLParser(html.parser.HTMLParser):
    def __init__(self, *, convert_charrefs: bool = True) -> None:
        self._repo_urls: list[str] = []
        super().__init__(convert_charrefs=convert_charrefs)

    @property
    def repo_urls(self):
        return self._repo_urls

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return

        itemprop = find_list_pairs("itemprop", attrs)
        if itemprop is None:
            return
        if itemprop != "name codeRepository":
            return

        url = find_list_pairs("href", attrs)
        if url is None:
            return

        if "github.com" not in url:
            url = GITHUB_URL + url

        self._repo_urls.append(url)


class RepoArchiveUrlHTMLParser(html.parser.HTMLParser):
    def __init__(self, *, convert_charrefs: bool = True) -> None:
        self._archive_url: str = ""
        super().__init__(convert_charrefs=convert_charrefs)

    @property
    def archive_url(self):
        return self._archive_url

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return

        a = find_list_pairs("data-hydro-click", attrs)
        if a is None:
            return
        if ("clone_or_download.click" not in a) or ("DOWNLOAD_ZIP" not in a):
            return

        url = find_list_pairs("href", attrs)
        if url is None:
            return

        self._archive_url = "https://github.com" + url


def parser_add_arguments(parser: ArgumentParser):
    parser.add_argument(
        "-u",
        "--user-name",
        help="the github username",
        metavar="<name>",
        action="store",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--dir",
        help="the directory to download the archives to",
        metavar="<dir>",
        action="store",
        required=True,
    )


def main():
    parser = argparse.ArgumentParser()
    parser_add_arguments(parser)
    args = parser.parse_args()

    try:
        print(f"creating the {args.dir} directory...")
        Path(args.dir).mkdir()
    except FileExistsError:
        print(f"the directory {args.dir} is not empty")
        exit(1)

    print("gettings all repos...")
    repo_urls = get_repo_urls(args.user_name)
    repo_count = len(repo_urls)
    print(f"found {repo_count} repos")

    for repo_num, repo_url in enumerate(repo_urls):
        archive_url = get_repo_archive_url(repo_url)
        print(f"downloading {archive_url}... ({repo_num + 1}/{repo_count})")
        download_archive(archive_url, args.dir)

    print("done")


if __name__ == "__main__":
    main()
