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

from mettle.io import IReader, IWriter, IStream

from .itransport_settings import ITransportSettings
from .rpc_header import RpcHeader


class ITransport:
    """
    This is the transport interface for mettle.braze.
    """

    def construct(self, settings: ITransportSettings) -> None:
        """
        Creates the transport object with all required params/settings.

        :param settings: The settings object required to construct the object.
        """
        pass


    def destruct(self) -> None:
        """
        Destructs the transport, freeing all resources.
        """
        pass


    def signature(self) -> int:
        """
        The unique signature of this transport.
        """
        pass


    def new_reader(self, stream: IStream) -> IReader:
        """
        Creates a reader object for this specific transport.

        :param stream: The stream object that the reader object will use.
        :return: The created reader object.
        """
        pass


    def new_writer(self, stream: IStream) -> IWriter:
        """
        Creates a writer object for this specific transport.

        :param sream: The stream object that the writer object will use.
        :return: The created writer object.
        """
        pass


    def new_stream(self) -> IStream:
        """
        Create a new stream to use.

        :return: The a new stream to use.
        """
        pass


    def create_header(self) -> RpcHeader:
        """
        Creates a header for this transport.

        :return: Returns a standard or overloaded object for the transport.
        """
        pass


    def send(self, head: RpcHeader, data: IStream) -> None:
        """
        Sends a header and a stream of data through the transport.

        :param header: The header.
        :param data: The stream of data to be written.
        """
        pass


    def send_error_message(self, head: RpcHeader, err_msg: str) -> None:
        """
        Sends a header and error message through the transport.

        :param header: The header.
        :param err_msg: The error message.
        """
        pass


    def receive_header(self, head: RpcHeader) -> None:
        """
        Receieves a header from the transport.

        :param header: The header to receive.
        """
        pass


    def receive(self, head: RpcHeader) -> IStream:
        """
        Receieves the body of a call from the transport.

        :param header: The header.
        :return: Stream that contains received data.
        """
        pass


    def receive_error_message(self, head: RpcHeader) -> str:
        """
        Receieves an error message from the transport.

        :param header: The header.
        :return: The error message that was received.
        """
        pass


    def terminate(self) -> None:
        """
        Tell the transport to terminate.
        """
        pass


    def house_keeping(self) -> None:
        """
        For server transport, perform house keeping
        """
        pass


    def wait_for_connection(self, time_out: float) -> bool:
        """
        For server transport, the max tme to wait for a client to connect.

        :param time_out: Time to wait in seconds for a connection.
        :return: True if a client connected, else False if time out.
        """
        pass


    def client_address(self) -> str:
        """
        For server transport, gets the address of the connecting client.

        :return: A string representation of the client address.
        """
        pass
