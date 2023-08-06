``aiobtclientrpc`` provides low-level access to the RPC protocols of BitTorrent
clients. It is supposed to be the basis for a high-level library. If you want to
use this directly, you need to read the documentation or source code of each
client.

Check out `aiobtclientapi`_ for a high-level API.

.. _aiobtclientapi: https://codeberg.org/ormaybe/aiobtclientapi

Features
--------

* Tunnel the client connection through a proxy (SOCKS5, SOCKS4, HTTP tunnel)
* Event handlers, e.g. when a torrent was added (Deluge only)
* (Re-)Connect automatically on any RPC method call and disconnect automatically
  when used as a context manager
* Keep track of the connection status and provide changes to a callback

| Documentation: https://aiobtclientrpc.readthedocs.io/
| Repository: https://codeberg.org/ormaybe/aiobtclientrpc
| Package: https://pypi.org/project/aiobtclientrpc/

Supported BitTorrent Clients
----------------------------

* `Deluge`_
* `qBittorrent`_
* `Transmission`_ (daemon)
* `rTorrent`_

.. _Deluge: https://www.deluge-torrent.org/
.. _qBittorrent: https://www.qbittorrent.org/
.. _Transmission: https://transmissionbt.com/
.. _rTorrent: https://rakshasa.github.io/rtorrent/

License
-------

`GPLv3+ <https://www.gnu.org/licenses/gpl-3.0.en.html>`_
