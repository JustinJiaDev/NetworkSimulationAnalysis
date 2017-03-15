class Host(object):
    def __init__(self, difs, sifs):
        self.frames = []
        self.current_frame = None
        self.resent_times = 0
        self.reset(difs, sifs)

    def reset(self, difs, sifs):
        self.difs = difs
        self.sifs = sifs
        self.backoff = -1
        self.timeout = -1

    def schedule(self, frame):
        self.frames.append(frame)

    def sent_frame(
        self,
        channel_is_idle,
        backoff,
        timeout,
        default_difs,
        default_sifs
    ):
        if len(self.frames) == 0:  # is idle
            return
        if self.timeout != -1:  # waiting ack
            if self.timeout > 0:  # still waiting
                self.timeout -= 1
            else:  # waiting timeout
                if self.resent_times < 3:  # attempt to resent
                    self.backoff = backoff * (2 ** (self.resent_times + 1))
                    self.resent_times += 1
                    self.frames.insert(0, self.current_frame)
                else:  # discard frame
                    self.current_frame = None
                    self.resent_times = 0
                    self.reset(default_difs, default_sifs)
        else:  # check to send next frame
            if self.frames[0].is_ack is False:  # wants to send data frame
                if channel_is_idle:
                    if self.backoff == -1:  # is difs state
                        if self.difs > 0:
                            self.difs -= 1
                        else:
                            self.current_frame = self.frames.pop(0)
                            self.reset(default_difs, default_sifs)
                            self.timeout = timeout
                            return self.current_frame
                    else:  # is backoff state
                        if self.backoff > 0:
                            self.backoff -= 1
                        else:
                            self.current_frame = self.frames.pop(0)
                            self.reset(default_difs, default_sifs)
                            self.timeout = timeout
                            return self.current_frame
                else:
                    if self.backoff == -1:  # is difs state
                        self.backoff = backoff
                        self.difs = -1
            else:  # wants to send ack frame
                if self.sifs > 0:
                    self.sifs = -1
                else:
                    self.current_frame = self.frames.pop(0)
                    self.reset(default_difs, default_sifs)
                    return self.current_frame
