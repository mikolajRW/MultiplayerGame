from multiprocessing import Process, Queue
import time

def sorter(q_in, q_out):
    try:
        data = q_in.get(timeout=3)
        data.sort()
        q_out.put(data)
    except Exception as e:
        print("Timeout or error:", e)

if __name__ == '__main__':
    with open('numbers.txt', 'r') as f:
        numbers = list(map(int, f.read().strip().split()))

    arr1 = numbers[:100]
    arr2 = numbers[100:]

    q1, q2 = Queue(), Queue()
    out1, out2 = Queue(), Queue()

    p2 = Process(target=sorter, args=(q1, out1))
    p3 = Process(target=sorter, args=(q2, out2))

    p2.start()
    p3.start()

    q1.put(arr1)
    q2.put(arr2)

    try:
        sorted1 = out1.get(timeout=3)
        sorted2 = out2.get(timeout=3)
    except Exception as e:
        print("Timeout or error while receiving sorted arrays:", e)
        sorted1 = sorted2 = []

    final_sorted = sorted(sorted1 + sorted2)

    print("Sorted array (queue):")
    print(final_sorted)

    p2.join()
    p3.join()
