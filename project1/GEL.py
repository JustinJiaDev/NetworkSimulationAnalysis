import event


class GEL(object):
    def __init__(self):
        self.head = None

    def schedule(self, type, time, packet):
        new_event = event.Event(time, packet, type, None, None)
        self.insert(new_event)

    def insert(self, new_event):
        if self.head is None:
            self.head = new_event
            return None
        item = self.head
        if item.time > new_event.time:
            self.head = new_event
            new_event.next = item
            item.prev = new_event
            return new_event
        while item.next is not None and new_event.time > item.next.time:
            item = item.next
        new_event.prev = item
        new_event.next = item.next
        item.next = new_event
        if new_event.next is not None:
            new_event.next.prev = new_event
        return new_event

    def pop(self):
        if self.head is None:
            return None
        first_event = self.head
        if first_event.next is not None:
            first_event.next.prev = None
        self.head = first_event.next
        first_event.next = None
        return first_event

    def print_elements(self):
        item = self.head
        while item is not None:
            print(item.time)
            item = item.next
