#!/usr/bin/env python3

import threading
import queue

__queued = queue.Queue()

exit_flag = threading.Event()

def publish(topic, *args, **kvargs):
    global __queued
    __queued.put({
        "topic": topic,
        "args": args,
        "kvargs": kvargs,
    })


__map = {}

def subscribe(topic, callback):
    global __map
    if topic not in __map:
        __map[topic] = []
    __map[topic].append(callback)


def dispatching_thread(q, m):
    global exit_flag
    while not exit_flag.is_set():
        msg = q.get()
        topic = msg["topic"]
        args = msg["args"]
        kvargs = msg["kvargs"]

        if topic not in m: continue

        for callback in m[topic]:
            try:
                callback(*args, **kvargs)
            except Exception as e:
                print(e)
        if msg == "exit":
            break
    print("Event dispatcher: finished.")
t = threading.Thread(target=dispatching_thread, args=(__queued, __map))
t.start()
