from assisted_editing.models.editing_queue_item import (
    EditingQueueItem,
)


class EditingQueue:
    """
    File d'attente des montages assistés.
    """

    # ==================================================

    def __init__(self):

        self._items: list[EditingQueueItem] = []

    # ==================================================

    def add(
        self,
        item: EditingQueueItem,
    ):

        self._items.append(item)

    # ==================================================

    def pop(self) -> EditingQueueItem | None:

        if not self._items:
            return None

        return self._items.pop(0)

    # ==================================================

    def clear(self):

        self._items.clear()

    # ==================================================

    def count(self) -> int:

        return len(self._items)

    # ==================================================

    def empty(self) -> bool:

        return len(self._items) == 0

    # ==================================================

    def items(self):

        return list(self._items)