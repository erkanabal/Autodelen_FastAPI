from datetime import datetime
from fastapi import HTTPException
from typing import Optional

# Tarih formatı
DATETIME_FORMAT = "%Y-%m-%d %H:%M"

def parse_datetime_param(value: Optional[str]) -> Optional[datetime]:
    """
    Verilen tarih parametresini belirtilen formata dönüştürür.
    Eğer tarih geçersizse, 400 hata kodu ile geri döner.
    """
    if value is None:
        return None
    try:
        return datetime.strptime(value, DATETIME_FORMAT)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid datetime format: {value}. Expected format: {DATETIME_FORMAT}. Example: '2025-05-13 14:00'"
        )
