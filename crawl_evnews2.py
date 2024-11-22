from argparse import ArgumentParser, Namespace
from multiprocessing.pool import Pool
from time import sleep
from typing import Any, Dict, List, Optional
import requests
import json
from bs4 import BeautifulSoup
from tqdm import tqdm

argparser = ArgumentParser("Crawl Bobaedream news articles")
argparser.add_argument("--output-path", type=str, default="bobaedream_news.json")
argparser.add_argument("--start-no", type=int, default=227566)
argparser.add_argument("--num-articles", type=int, default=20000)
argparser.add_argument("--num-workers", type=int, default=10)
argparser.add_argument("--max-trials", type=int, default=3)

def get_article_body(article_no: int) -> Optional[Dict[str, Any]]:
    url = f"https://www.bobaedream.co.kr/view?code=nnews&No={article_no}&bm=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if "존재하지 않는 게시물" in response.text or "삭제된 게시물" in response.text:
            return None
            
        title_elem = soup.select_one(".writerProfile strong")
        content_elem = soup.select_one("#bodyCont") or soup.select_one(".bodyCont")
        date_elem = soup.select_one(".date")
        
        if not all([title_elem, content_elem, date_elem]):
            return None
            
        title = title_elem.text.strip()
        content = content_elem.text.strip()
        date = date_elem.text.strip()
        
        if "전기" in title or "전기" in content:
            return {
                "title": title,
                "content": content,
                "date": date,
                "url": url
            }
    except:
        return None
    
    return None

def crawl_articles(args: Namespace) -> List[Dict[str, Any]]:
    article_numbers = range(args.start_no, args.start_no - args.num_articles, -1)
    crawled_articles = []
    progress_bar = tqdm(total=args.num_articles)
    
    with Pool(args.num_workers) as pool:
        for article_body in pool.imap_unordered(get_article_body, article_numbers):
            progress_bar.update(1)
            if article_body is not None:
                crawled_articles.append(article_body)
                progress_bar.set_postfix(
                    {"Found_articles": len(crawled_articles)}
                )
            sleep(0.1)
    
    return crawled_articles

if __name__ == "__main__":
    try:
        args = argparser.parse_args([])
        crawled_articles = crawl_articles(args)
    except KeyboardInterrupt:
        print("\n프로그램이 중단되었습니다.")
    finally:
        if 'crawled_articles' in locals() and crawled_articles:
            print(f"\n전기차 관련 뉴스 {len(crawled_articles)}개를 찾았습니다.")
            with open(args.output_path, "w", encoding='utf-8') as f:
                json.dump(crawled_articles, f, ensure_ascii=False, indent=2)
            print(f"데이터가 {args.output_path}에 저장되었습니다.")