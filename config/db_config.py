import os
import logging
from pymongo import MongoClient
from template.notice_data import NoticeData
from utils.scrapper_type import ScrapperType
from config.env_loader import load_env_file

logger = logging.getLogger(__name__)

IS_PROD = load_env_file()  # 환경 변수 로드


def get_database(db_name: str = None):
    """MongoDB 데이터베이스 연결을 반환합니다.

    Args:
        db_name (str, optional): 사용할 데이터베이스 이름.
            미지정시 환경변수의 DB_NAME 또는 기본값 사용
    """
    try:
        client = MongoClient(os.getenv("MONGODB_URI"))
        default_db = "dev-kookmin-feed" if not IS_PROD else "kookmin-feed"
        db_name = db_name or os.getenv("DB_NAME", default_db)
        return client[db_name]
    except Exception as e:
        logger.error(f"DB 연결 중 오류 발생: {e}")
        raise


def get_collection(scrapper_type: str, db_name: str = None):
    """공지사항 종류에 해당하는 컬렉션을 반환합니다."""
    db = get_database(db_name)
    return db[scrapper_type]


def close_database():
    """데이터베이스 연결을 종료합니다."""
    try:
        client = MongoClient(os.getenv("MONGODB_URI"))
        client.close()
    except Exception as e:
        logger.error(f"DB 연결 종료 중 오류 발생: {e}")


async def save_notice(
    notice: NoticeData, scrapper_type: ScrapperType, db_name: str = None
):
    """공지사항을 DB에 저장합니다."""
    try:
        collection = get_collection(scrapper_type.get_collection_name(), db_name)
        collection.insert_one(
            {
                "title": notice.title,
                "link": notice.link,
                "published": notice.published.isoformat(),
                "scrapper_type": scrapper_type.get_collection_name(),
            }
        )
    except Exception as e:
        logger.error(f"DB 저장 중 오류 발생: {e}")
