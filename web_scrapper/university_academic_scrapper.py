import logging
from bs4 import BeautifulSoup
from datetime import datetime
from template.notice_data import NoticeData
from utils.scrapper_type import ScrapperType
from utils.web_scrapper import WebScrapper
from config.logger_config import setup_logger
from config.db_config import get_collection

logger = setup_logger(__name__)


class UniversityAcademicScrapper(WebScrapper):
    """대학 학사공지 스크래퍼"""

    def __init__(self, url: str):
        super().__init__(url, ScrapperType.UNIVERSITY_ACADEMIC)

    def get_list_elements(self, soup: BeautifulSoup) -> list:
        """학사공지 목록의 HTML 요소들을 가져옵니다."""
        return soup.select(".list-tbody .normal-bg, .list-tbody .notice-bg")

    async def parse_notice_from_element(self, row) -> NoticeData:
        """HTML 요소에서 학사공지 정보를 추출합니다."""
        try:
            title_tag = row.select_one(".subject a")
            if not title_tag:
                return None

            title = title_tag.text.strip()
            link = title_tag["href"]
            if not link.startswith("http"):
                link = f"https://cs.kookmin.ac.kr/news/kookmin/academic/{link}"

            date = row.select_one(".date").text.strip()
            published = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=self.kst)

            return NoticeData(
                title=title,
                link=link,
                published=published,
                scrapper_type=self.scrapper_type,
            )
        except Exception as e:
            logger.error(f"공지사항 파싱 중 오류: {e}")
            return None
