# **************************************************************************** #
#                           This file is part of:                              #
#                                   METTLE                                     #
#                           https://bitsmiths.co.za                            #
# **************************************************************************** #
#  Copyright (C) 2015 - 2022 Bitsmiths (Pty) Ltd.  All rights reserved.        #
#   * https://bitbucket.org/bitsmiths_za/mettle.git                            #
#                                                                              #
#  Permission is hereby granted, free of charge, to any person obtaining a     #
#  copy of this software and associated documentation files (the "Software"),  #
#  to deal in the Software without restriction, including without limitation   #
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,    #
#  and/or sell copies of the Software, and to permit persons to whom the       #
#  Software is furnished to do so, subject to the following conditions:        #
#                                                                              #
#  The above copyright notice and this permission notice shall be included in  #
#  all copies or substantial portions of the Software.                         #
#                                                                              #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  #
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    #
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL     #
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  #
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     #
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         #
#  DEALINGS IN THE SOFTWARE.                                                   #
# **************************************************************************** #
from mettle.braze.tcp.tcp_header        import TcpHeader
from mettle.braze.tcp.socket_tcp_client import SocketTcpClient

from mettle.braze.rdc import Rdc

from mettle.io import IWriter, IReader, IStream
from mettle.io.big_endian_reader import BigEndianReader
from mettle.io.big_endian_writer import BigEndianWriter
from mettle.io.memory_stream     import MemoryStream

from mettle.braze.itransport import ITransport
from mettle.braze.rpc_header import RpcHeader
from mettle.braze.tcp.transport_client_settings import TransportClientSettings


class TransportClient(ITransport):
    """
    This the standard tcp transport client.
    """

    def __init__(self):
        """
        Constructor.
        """
        self._socket  = None


    def __del__(self):
        """
        Destructor.
        """
        self.destruct()


    def construct(self, settings: TransportClientSettings) -> None:
        """
        Initializes the transport client, connecting it to the server.

        :param settings: (mettle.braze.tcp.TransportClientSettings) The settings to connect with.
        """
        self.destruct()

        self._socket = SocketTcpClient(settings.host, settings.service, settings.timeout)


    def destruct(self) -> None:
        """
        Destorys the tranport freeing all resources.
        """
        if self._socket:
            self._socket.close()
            self._socket = None


    def signature(self) -> int:
        return int('0x0BA5E7C9', 16)


    def new_reader(self, stream: IStream) -> IReader:
        return BigEndianReader(stream)


    def new_writer(self, stream: IStream) -> IWriter:
        return BigEndianWriter(stream)


    def new_stream(self) -> IStream:
        return MemoryStream()


    def create_header(self) -> RpcHeader:
        return TcpHeader()


    def send(self, header: RpcHeader, data: bytearray) -> None:
        lenToSend = 0
        rdc       = None

        if data and data.size() > 0:
            rdc = Rdc()

            rdc.eat(data.bytes(), data.size(), data.size())
            rdc.compress()

            header.message_size    = rdc.length()
            header.compressed_size = rdc.compressed_length()

            if rdc.data_state() == Rdc.eDataState.Compressed:
                lenToSend = rdc.compressed_length()
            else:
                lenToSend = rdc.length()

        msHead  = MemoryStream()
        bigErw  = BigEndianWriter(msHead)

        header._serialize(bigErw, header._name())

        self._socket.open()

        self._socket.send(msHead.bytes())

        if rdc:
            self._socket.send_size(rdc.blob(), lenToSend)


    def send_error_message(self, header: RpcHeader, err_msg: str):
        pass


    def receive_header(self, header: RpcHeader) -> None:
        blob   = self._socket.receive()
        msHead = MemoryStream()

        msHead.eat(blob)

        bigEre = BigEndianReader(msHead)

        header._deserialize(bigEre, header._name())


    def receive(self, header: RpcHeader) -> IStream:
        if header.message_size < 1:
            return None

        if header.compressed_size != 0 and header.compressed_size != header.message_size:
            rdc = Rdc()
            mem = self._socket.read_size(header.compressed_size)

            rdc.eat(mem, header.message_size, header.compressed_size)

            if rdc.data_state() == Rdc.eDataState.Compressed:
                rdc.uncompress()

            data = rdc.blob()

            del rdc
            del mem
        else:
            data = self._socket.read_size(header.message_size)

        ms = MemoryStream()

        ms.eat(data)

        return ms


    def receive_error_message(self, header: RpcHeader) -> str:
        blob = self._socket.receive()
        ms   = MemoryStream()

        ms.eat(blob)

        reader = BigEndianReader(ms)

        reader.read_start("ServerException")
        err_msg = reader.read_string("ErrorMessage")
        reader.read_end("ServerException")

        return err_msg


    def terminate(self) -> None:
        pass


    def house_keeping(self) -> None:
        pass


    def wait_for_connection(self, time_out: float) -> bool:
        return False


    def client_address(self) -> str:
        return ''


    def get_socket(self) -> SocketTcpClient:
        return self._socket
