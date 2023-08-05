import time

import zmq
import zmq.devices

from easypubsub.logging import getLogger

_logger = getLogger("EasyPubSub.Proxy")


class Proxy:
    """The EasyPubSub Proxy acts as an intermediary between Publishers and Subscribers.

    Attributes:
        publishers_address (str): The address that publisher will use to connect to the Proxy.
        subscribers_address (str): The address that subscribers will use to connect to the Proxy.

    Example:
        >>> from easypubsub.proxy import Proxy
        >>> proxy = Proxy("tcp://localhost:5555", "tcp://localhost:5556")
        >>> proxy.launch()
        ...
        >>> proxy.stop()
    """

    def __init__(
        self,
        publishers_address: str,
        subscribers_address: str,
    ) -> None:
        self.ctx = zmq.Context.instance()

        self._proxy = zmq.devices.ThreadProxySteerable(
            in_type=zmq.XPUB, out_type=zmq.XSUB, ctrl_type=zmq.PAIR
        )

        self.publishers_address = publishers_address
        self.subscribers_address = subscribers_address

        self._proxy.bind_out(self.publishers_address)
        self._proxy.bind_in(self.subscribers_address)
        _logger.info(
            f"Proxy bound to {self.publishers_address} for publishers and {self.subscribers_address} for subscribers."
        )

        self._ctrl_iface = "tcp://127.0.0.1"
        self._ctrl_port: int = self._proxy.bind_ctrl_to_random_port(self._ctrl_iface)
        self._ctrl_socket = self.ctx.socket(zmq.PAIR)

    def launch(self) -> None:
        """Launch the Proxy.

        This method will launch the Proxy in a separate thread, and return immediately.
        To stop the Proxy, call the :meth:`Proxy.stop` method."""

        self._proxy.start()
        _logger.info("Proxy started.")

    def stop(self, timeout=5.0) -> None:
        """Stop the Proxy thread.

        Args:
            timeout (float): The maximum time, in seconds, to wait for the Proxy to stop.
            If the Proxy does not stop cleanly within this time, it will be terminated
            forcefully.
        """

        self._ctrl_socket.connect(f"{self._ctrl_iface}:{self._ctrl_port}")
        # Wait for the control socket to establish a connection with the Proxy.
        time.sleep(0.25)

        self._ctrl_socket.send(b"TERMINATE")
        _logger.info(
            f"Requesting termination of proxy. Will wait up to {timeout} seconds."
        )
        self._proxy.join(timeout=timeout)
        _logger.info("Proxy terminated.")
