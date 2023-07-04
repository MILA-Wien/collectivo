"""Handle ABCD shift logic."""
from datetime import datetime

from dateutil.rrule import FR, MO, MONTHLY, SA, SU, TH, TU, WE, rrule


def get_abcd_occurences(
    week: str,
    day: str,
    min_date: datetime,
    max_date: datetime = None,
    count: int = None,
) -> rrule:
    """Get the occurences of a shift with ABCD repetition."""

    # Create dictionaries for translation to rrule parameters
    week_dict = {"A": 1, "B": 2, "C": 3, "D": 4}
    day_dict = {
        "MO": MO,
        "TU": TU,
        "WE": WE,
        "TH": TH,
        "FR": FR,
        "SA": SA,
        "SU": SU,
    }
    week_number = week_dict[week]
    weekday = day_dict[day]

    """Get the next occurence of the shift with ABCD repetition."""
    return rrule(
        MONTHLY,
        byweekday=weekday,
        byweekno=[
            x
            for x in range(
                week_number,
                52,
                4,
            )
        ],
        dtstart=min_date,
        until=max_date,
        count=count,
    )
