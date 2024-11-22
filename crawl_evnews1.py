from argparse import ArgumentParser, Namespace
from copy import deepcopy
from multiprocessing.pool import Pool
from time import sleep
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests
import ujson as json
from bs4 import BeautifulSoup
from pandas import date_range
from tqdm import tqdm
from trafilatura import extract, fetch_url
from trafilatura.settings import DEFAULT_CONFIG

argparser = ArgumentParser("Crawl Naver news articles")
argparser.add_argument("--output-path", type=str, default="naver_news.json")
argparser.add_argument("--query", type=str, default="전기차")
argparser.add_argument("--start-date", type=str, default="2024.10.22")
argparser.add_argument("--end-date", type=str, default="2024.11.21")
argparser.add_argument("--num-workers", type=int, default=5)
argparser.add_argument("--max-trials", type=int, default=3)

TRAFILATURA_CONFIG = deepcopy(DEFAULT_CONFIG)
TRAFILATURA_CONFIG["DEFAULT"]["DOWNLOAD_TIMEOUT"] = "5"
TRAFILATURA_CONFIG["DEFAULT"]["MAX_REDIRECTS"] = "0"
TRAFILATURA_CONFIG["DEFAULT"]["MIN_OUTPUT_SIZE"] = "50"


def get_article_body(url: str) -> Optional[Dict[str, Any]]:
    try:
        downloaded = fetch_url(url, config=TRAFILATURA_CONFIG)
        extracted_news_content = extract(
            downloaded,
            output_format="json",
            include_tables=False,
            with_metadata=True,
            deduplicate=True,
            config=TRAFILATURA_CONFIG,
        )
        extracted_news_content = json.loads(extracted_news_content)
    except KeyboardInterrupt:
        exit()
    except:
        return None

    return extracted_news_content


def crawl_articles(args: Namespace) -> List[Dict[str, str]]:

    dates = date_range(args.start_date, args.end_date, freq="D")

    encoded_query = quote(args.query)

    crawled_urls = set()
    crawled_articles = []
    progress_bar = tqdm(total=len(dates))

    for date in dates:
        date_str = date.strftime("%Y%m%d")

        next_url = (
            "https://s.search.naver.com/p/newssearch/search.naver?"
            f"query={encoded_query}&sort=0related=0&"
            f"nso=so%3Ar%2Cp%3Afrom{date_str}to{date_str},a:all&where=news_tab_api"
        )

        num_trials = 0
        while next_url != "":
            try:
                request_result = requests.get(next_url)
                request_result = request_result.json()
            except KeyboardInterrupt:
                exit()
            except Exception as e:
                sleep(10)
                num_trials += 1
                if num_trials == args.max_trials:
                    break
                else:
                    continue

            contents = request_result["contents"]
            next_url = request_result["nextUrl"]

            article_urls = []
            for content in contents:
                content_soup = BeautifulSoup(content, features="lxml")
                news = content_soup.find("a", {"class": "news_tit"})
                news_url = news["href"]

                if news_url not in crawled_urls:
                    article_urls.append(news_url)

            with Pool(args.num_workers) as pool:
                for article_body in pool.imap_unordered(get_article_body, article_urls):
                    if article_body is not None:
                        crawled_articles.append(article_body)

            crawled_urls.update(article_urls)

            progress_bar.set_postfix(
                {"Date": date, "Num_articles": len(crawled_articles)}
            )

            sleep(0.5)

        progress_bar.update(1)

    return crawled_articles


if __name__ == "__main__":
    args = argparser.parse_args()

    crawled_articles = crawl_articles(args)

    with open(args.output_path, "w", encoding='utf-8') as f:
        json.dump(crawled_articles, f, ensure_ascii=False, indent=2)