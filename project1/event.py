class Event(object):
    def __init__(self, time, packet, type, prev_event, next_event):
        self.time = time
        self.packet = packet
        self.type = type
        self.prev = prev_event
        self.next = next_event
