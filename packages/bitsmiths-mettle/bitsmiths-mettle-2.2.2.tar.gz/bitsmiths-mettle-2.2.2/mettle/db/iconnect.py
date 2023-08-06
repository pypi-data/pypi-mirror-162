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
import datetime

from .statement import Statement


class IConnect:
    """
    Interface for a database connection object.
    """

    STMNT_TYPE_NA   = 0
    STMNT_TYPE_READ = 1
    STMNT_TYPE_CUD  = 2  # Create, Update, Delete


    def name(self) -> str:
        """
        The name of this database connection.

        :return: The name of this database connection.
        """
        raise NotImplementedError('name')


    def database_name(self) -> str:
        """
        Return the name of the database.
        """
        raise NotImplementedError('database_name')


    def commit(self) -> None:
        """
        Performs a database commit.
        """
        raise NotImplementedError('commit')


    def rollback(self) -> None:
        """
        Performs a database rollback.
        """
        raise NotImplementedError('rollback')


    def fetch(self, stmnt) -> bool:
        """
        Fetches the next row from the statement object.

        :param stmnt: (mettle.db.Statement) The database statement.
        :return: True if a row was fetched.
        """
        raise NotImplementedError('fetch')


    def connect_deft(self,
                     user     : str,
                     passwd   : str,
                     db_name  : str,
                     host     : str,
                     port     : int = 0,
                     schema   : str = None) -> None:
        """
        Connect to the database using common logon parameters.

        :param user: The user logging onto the database.
        :param passwd: Password for the user, if None it might be ignored.
        :param db_name: The database name to connect to.
        :param host: The host to connect to, if None, sometimes will auto assume local host.
        :param port: The port to connect to if specified.
        :param schema: Schema or namespace to auto connect to, note not every database support this.
        """
        raise NotImplementedError('connect_deft')


    def connect(self, connection_str: str) -> None:
        """
        Connect to the database using a database specific connection string.

        :param connection_str : A string with all the required connection information.
        """
        raise NotImplementedError('connect')


    def close(self) -> None:
        """
        Closes the database connection.
        """
        raise NotImplementedError('close')


    def execute(self, stmnt) -> 'IConnect':
        """
        Executes the provided statement.

        :param stmnt: (mettle.db.Statement) The statement to be executed.
        :return: Itself for convenience.
        """
        raise NotImplementedError('execute')


    def pre_get_sequence(self, stmtn, table: str, col: str, size: int) -> int:
        """
        Gets the next sequence number from the table if the database prior to insert.

        :param stmnt: (mettle.db.Statement) The database statement.
        :param table: The name of the table's who's sequence to get.
        :param col: The name of the column for the on the table of who's sequence to get.
        :param size: The sequence size, ie 4 for in32, 8 for int64
        :return: The sequence number if the next sequence was retreieved, else returns None or
                 raises an exception if this database instead gets sequence's post insert.
        """
        raise NotImplementedError('pre_get_sequence')


    def post_get_sequence(self, stmnt, table: str, col: str, size: int) -> int:
        """
        Gets the next sequence number from the table if the database post insert.

        param stmnt: (mettle.db.Statement) The database statement.
        param table: The name of the table's who's sequence to get.
        param col: The name of the column for the on the table of who's sequence to get.
        param size: The sequence size, ie 4 for in32, 8 for int64
        :return: The sequence number if the next sequence was retreieved, else returns None or
                 raises an exception if this database instead gets sequence's pre insert.
        """
        raise NotImplementedError('post_get_sequence')


    def get_timestamp(self) -> datetime.datetime:
        """
        Gets the current date & time from the database.

        :returns: The timestamp from the database.
        """
        raise NotImplementedError('connect_deft')


    def lock(self, stmnt: Statement = None) -> None:
        """
        Tell the database we are about to attempt a row lock.

        :param stmnt: The stmnt that we are locking for.
        """
        raise NotImplementedError('lock')


    def statement(self, name: str, stmnt_type: int = 0) -> Statement:
        """
        Creates a new Statement object for this database connection.

        :param name: The name of the statment.
        :param stmnt_type: Optionally provide the statement type.
        :return: Note the calling object must free/destroy this object.
        """
        raise NotImplementedError('statement')


    def date_4_sql_inject(self, src_date) -> str:
        """
        Converts a date object, into a query usable equivalent for this specific database.

        :param src_date: (datetime.date) The source date to be converted into a query compatiable string.
        :return: The resultent sql injectiable date string.
        """
        raise NotImplementedError('date_4_sql_inject')


    def datetime_4_sql_inject(self, src_datetime) -> str:
        """
        Converts a datetime object, into a query usable equivalent for this specific database.

        :param src_datetime: (datetime.datetime) The source datetime to be converted into a query compatiable string.
        :return: The resultent sql injectiable datetime string.
        """
        raise NotImplementedError('statement')


    def transaction_mode_get(self) -> bool:
        """
        Gets the auto transaction mode setting from the connection.

        :return: True if db connection is in auto transaction mode."
        """
        raise NotImplementedError('transaction_mode_get')


    def transaction_mode_set(self, mode: bool) -> None:
        """
        Sets the auto tranaction mode.

        :param mode: Turn the auto transaction mode on/off, not all db connectors support this.
        """
        raise NotImplementedError('transaction_mode_set')


    def backend_pid(self) -> int:
        """
        Get the backend process identifier for this db connection.

        :return: The process identifier for the current database connection, not all db connectors support this.
        """
        return -1
