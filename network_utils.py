def handle_client(conn, addr, BUFFER_SIZE, process_message):
    """
        Handles communication with a connected client over a socket.

        This function continuously listens for messages from the given client socket.
        It assembles incoming data into complete messages separated by newline characters (`\n`),
        and passes each complete message to a user-provided `process_message` callback function.

        When the client disconnects or an error occurs, any remaining partial message is
        processed before the connection is closed.
    """


    print(f"[CONNECTED] {addr}")
    buffer = ""

    try:
        while True:
            data = conn.recv(BUFFER_SIZE).decode()
            if not data:
                break

            buffer += data
            while "\n" in buffer:
                message, buffer = buffer.split("\n", 1)
                message = message.strip()
                print(f"[RECEIVED FROM {addr}] {message}")
                process_message(conn, message, addr)

    except Exception as e:
        print(f"[ERROR] Client {addr}: {e}")
    finally:
        if buffer.strip():
            last_msg = buffer.strip().split(" ")[-3:]
            last_msg_str = " ".join(last_msg)
            print(f"[RECEIVED FROM {addr}] {last_msg_str}")
            process_message(conn, last_msg_str, addr)
        print(f"[DISCONNECTED] {addr}")
        conn.close()