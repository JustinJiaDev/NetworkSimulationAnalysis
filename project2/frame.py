class Frame(object):
    def __init__(
        self,
        bytes,
        scheduled_time,
        process_time,
        source,
        destination,
        is_ack,
        data_frame_size,
        data_frame_scheduled_time,
    ):
        self.bytes = bytes
        self.scheduled_time = scheduled_time
        self.process_time = process_time
        self.source = source
        self.destination = destination
        self.is_ack = is_ack
        self.data_frame_size = data_frame_size
        self.data_frame_scheduled_time = data_frame_scheduled_time
        self.is_dirty = False
