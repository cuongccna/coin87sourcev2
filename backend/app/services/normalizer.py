import dateparser
from datetime import datetime, timezone
from app.core.logger import log

class DateNormalizer:
    @staticmethod
    def normalize_date(date_str: str) -> datetime:
        """
        Parse any date string to UTC datetime.
        """
        if not date_str:
            return datetime.now(timezone.utc)
            
        try:
            # Pylance might complain about settings type, ignoring for now as it's a dict
            dt = dateparser.parse(
                str(date_str),
                settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True}
            )
            
            if dt:
                return dt
            else:
                log.warning(f"Failed to parse date: {date_str}, using NOW.")
                return datetime.now(timezone.utc)
                
        except Exception as e:
            log.warning(f"Date parse error {date_str}: {e}")
            return datetime.now(timezone.utc)
