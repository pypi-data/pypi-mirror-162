from upyog.imports import *


__all__ = ["flatten", "uniqueify", "get_YYYY_MM_DD"]


def flatten(x: Any) -> List[Any]:
    flattened_list = []
    for item in x:
        if hasattr(item, "__iter__") and not isinstance(item, (str, bytes)):
            [flattened_list.append(i) for i in item]
        else:
            flattened_list.append(item)
    return flattened_list


def uniqueify(x: Collection) -> Collection:
    return sorted(list(set(x)))


def get_YYYY_MM_DD(sep="_") -> str:
    return datetime.now().strftime(f"%Y{sep}%m{sep}%d")
