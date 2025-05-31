def handle_client(conn, addr, BUFFER_SIZE, process_message):
    """
        Handles communication with a connected client over a socket.

        This function continuously listens for messages from the given client socket.
        It assembles incoming data into complete messages separated by newline characters (`\n`),
        and passes each complete message to a user-provided `process_message` callback function.

        When the client disconnects or an error occurs, any remaining partial message is
        processed before the connection is closed.

        Parameters:
            conn (socket.socket): The socket object connected to the client.
            addr (tuple): The address of the connected client, typically (host, port).
            BUFFER_SIZE (int): The size of the buffer for receiving data (in bytes).
            process_message (Callable[[socket.socket, str, tuple], None]):
                A callback function that handles each complete message.
                It receives the client socket, the message string, and the client address.

        Behavior:
            - Receives incoming data using `conn.recv(BUFFER_SIZE)`.
            - Buffers incomplete messages until a newline (`\n`) is found.
            - Splits and processes each message individually by calling `process_message()`.
            - Catches and logs exceptions during communication.
            - On disconnection, processes any remaining partial message (last 3 words).
            - Closes the connection in the `finally` block.

        Exceptions:
            Any exceptions during the communication loop are caught and printed,
            but do not halt execution of the server.
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