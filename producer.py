import argparse
import io
from datetime import datetime, timedelta
from time import time, sleep

import matplotlib.pyplot as plt
import numpy as np
import pika


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("exchange_name")
    parser.add_argument("format", nargs="?", default="png")
    args = parser.parse_args()

    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.exchange_declare(exchange=args.exchange_name, exchange_type="fanout")

    period = timedelta(seconds=0.1)
    wakeup = time()

    while True:
        f, ax = plt.subplots()

        # << put your plotting work here >>
        ax.plot(np.sin(wakeup + np.linspace(0, 2 * np.pi, 100)))
        ax.set_title(datetime.now().isoformat(timespec="milliseconds"))

        buf = io.BytesIO()
        f.savefig(buf, format=args.format)
        plt.close(f)

        properties = pika.BasicProperties(content_type="image/" + args.format)
        channel.basic_publish(exchange=args.exchange_name, routing_key="", body=buf.getvalue(), properties=properties)

        wakeup += period.total_seconds()
        dt = wakeup - time()
        # print(f"SLEEP {dt:6.3f}")

        if dt > 0:
            sleep(dt)
        else:
            # if we missed the deadline, cut the loss and move on
            wakeup = time()
