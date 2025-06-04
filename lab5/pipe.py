
from multiprocessing import Process, Pipe
import time

def sorter(conn):
    if conn.poll(3):
        data = conn.recv()
        data.sort()
        conn.send(data)
    conn.close()

if __name__ == '__main__':
    with open('numbers.txt', 'r') as f:
        numbers = list(map(int, f.read().strip().split()))

    arr1 = numbers[:100]
    arr2 = numbers[100:]

    parent_conn1, child_conn1 = Pipe()
    parent_conn2, child_conn2 = Pipe()

    p2 = Process(target=sorter, args=(child_conn1,))
    p3 = Process(target=sorter, args=(child_conn2,))

    p2.start()
    p3.start()

    parent_conn1.send(arr1)
    parent_conn2.send(arr2)

    sorted1 = sorted2 = None

    while True:
        if sorted1 is None and parent_conn1.poll(0.1):
            sorted1 = parent_conn1.recv()
        if sorted2 is None and parent_conn2.poll(0.1):
            sorted2 = parent_conn2.recv()
        if sorted1 is not None and sorted2 is not None:
            break

    final_sorted = sorted(sorted1 + sorted2)

    print("Sorted array (pipe):")
    print(final_sorted)

    p2.join()
    p3.join()
