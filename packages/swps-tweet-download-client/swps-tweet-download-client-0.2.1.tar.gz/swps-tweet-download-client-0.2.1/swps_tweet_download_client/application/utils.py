from typing import Iterable

from arrow import Arrow, arrow


def get_iterable_days(since: Arrow, until: Arrow) -> Iterable[Arrow]:
    return [
        it[0] for it in
        arrow.Arrow.span_range('day', since.datetime, until.datetime)
    ]
