from math import log
import random
import host
import frame

# constants
# a host can sense the channel every 0.01 msec
MAX_FRAME_SIZE = 1544
ACK_FRAME_SIZE = 64
BITS_PER_BYTE = 8
WIRELESS_CAPACITY = (11 * (10 ** 6))  # 11 Mbps
BASE_TIME = 100  # 0.01 ms * BASE_TIME = 1 ms
TRANSMISSION_SPEED = (11 * (10 ** 6)) / ((10 ** 3) * BASE_TIME)
SIMULATION_TIME = 10 * (10 ** 3) * BASE_TIME  # 10 s
ACK_PROCESS_TIME = ACK_FRAME_SIZE * BITS_PER_BYTE / TRANSMISSION_SPEED
DEFAULT_DIFS = 0.1 * BASE_TIME  # 0.1 ms
DEFAULT_SIFS = 0.05 * BASE_TIME  # 0.05 ms


def generate_frame_size():
    u = random.random()
    return (-1 * log(1 - u)) * MAX_FRAME_SIZE


def generate_arrival_time(arrival_rate):
    u = random.random()
    return ((-1 / arrival_rate) * log(1 - u)) * (10 ** 3) * BASE_TIME


def generate_backoff_time(backoff_time_cap):
    u = random.random()
    return u * backoff_time_cap * BASE_TIME


def generate_process_time(bytes):
    return bytes * BITS_PER_BYTE / WIRELESS_CAPACITY * (10 ** 3) * BASE_TIME


def generate_destination(number_of_host):
    u = random.random()
    return int(u * number_of_host)


# configurations
backoff_time_cap = float(input("Please enter the backoff time cap (ms): "))
timeout = float(input("Please enter the timeout (ms): "))
arrival_rate = float(input("Please enter the arrival rate: "))
number_of_host = int(input("Please enter number of hosts: "))

# statistics
transmitted_bytes = 0
total_delay = 0

# initializations
hosts = []
arrival_times = []
channel = []
for i in range(number_of_host):
    hosts.append(host.Host(DEFAULT_DIFS, DEFAULT_SIFS))
    arrival_times.append(generate_arrival_time(arrival_rate))

# main
for current_time in range(SIMULATION_TIME):
    channel_is_idle = len(channel) == 0
    channel_has_conflict = len(channel) > 1
    # schedule data frames
    for i in range(number_of_host):
        current_host = hosts[i]
        arrival_time = arrival_times[i]
        if arrival_time <= 0:
            size = generate_frame_size()
            data_frame = frame.Frame(
                size,
                current_time,
                generate_process_time(size),
                i,
                generate_destination(number_of_host),
                False,
                size,
                current_time
            )
            current_host.schedule(data_frame)
            arrival_times[i] = generate_arrival_time(arrival_rate)
        else:
            arrival_times[i] -= 1
    # update frames in channel
    for current_frame in channel:
        current_frame.process_time -= 1
        current_frame.is_dirty = current_frame.is_dirty or channel_has_conflict
        if current_frame.process_time <= 0:
            if not current_frame.is_dirty:  # valid frame transferred
                if current_frame.is_ack:  # received ack frame
                    # complete timer
                    hosts[current_frame.destination].reset(
                        DEFAULT_DIFS,
                        DEFAULT_SIFS
                    )
                    transmitted_bytes += current_frame.data_frame_size
                    total_delay += current_frame.data_frame_scheduled_time
                else:  # received data frame
                    ack_frame = frame.Frame(
                        ACK_FRAME_SIZE,
                        current_time,
                        generate_process_time(ACK_FRAME_SIZE),
                        current_frame.destination,
                        current_frame.source,
                        True,
                        current_frame.bytes,
                        current_frame.scheduled_time
                    )
                    hosts[current_frame.destination].schedule(ack_frame)
    # remove delivered frames in channel
    channel[:] = [x for x in channel if x.process_time > 0]
    # send frames
    for current_host in hosts:
        size = generate_frame_size()
        current_frame = current_host.sent_frame(
            channel_is_idle,
            generate_backoff_time(backoff_time_cap),
            timeout * BASE_TIME,
            DEFAULT_DIFS,
            DEFAULT_SIFS
        )
        if current_frame is not None:
            channel.append(current_frame)

# results
simulation_time_in_seconds = SIMULATION_TIME / (10 ** 3) / BASE_TIME
total_delay_in_seconds = total_delay / (10 ** 3) / BASE_TIME
throughput = transmitted_bytes / simulation_time_in_seconds
average_delay = total_delay_in_seconds / throughput

print("--------------------------------------")
print("Throughput: " + str(throughput) + " bytes/s")
print("Average network delay: " + str(average_delay) + " s")
print("--------------------------------------")
