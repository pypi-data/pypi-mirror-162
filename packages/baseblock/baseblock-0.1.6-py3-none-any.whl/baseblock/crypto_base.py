#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Crytography Base Functions """


from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken

enc = "utf-8"


class CryptoBase(object):
    """ Crytography Base Functions """

    def __init__(self):
        """
        Created:
            2-Mar-2022
            craigtrim@gmail.com
            *   https://github.com/craigtrim/baseblock/issues/1
        """
        self._key = "vYuJ9Y4_FtIlClfTsvIiMTDg4x-Xco_FeGWxNpo_7Sw="

    def encrypt_str(self,
                    some_input: str) -> str:
        """ Encrypt a String

        Args:
            some_input (str): any input string

        Returns:
            str: the encrypted string
        """
        return self.encrypt(some_input.encode(enc))

    def encrypt(self,
                message: bytes) -> str:
        """ Encrypt Bytes

        Args:
            message (bytes): any input bytes

        Returns:
            str: the encrypted string
        """
        f = Fernet(self._key)
        return str(f.encrypt(message))

    def decrypt_str(self,
                    some_input: str) -> str or None:
        """ Decrypt a String

        Args:
            some_input (str): any input string

        Raises:
            ValueError: the encrypted token is invalid

        Returns:
            str or None: the decrypted string if the encrypted token is valid
        """
        return self.decrypt(some_input.encode(enc))

    def decrypt(self,
                message: bytes) -> str:
        """ Decrypt Bytes

        Args:
            message (bytes): any input bytes

        Raises:
            ValueError: the encrypted token is invalid

        Returns:
            str: the decrypted string
        """
        try:
            f = Fernet(self._key)
            return f.decrypt(message).decode(enc)
        except InvalidToken as e:
            raise ValueError('Invalid Token')


def main(param1, param2):
    def _action():
        if param1 == "encrypt":
            return CryptoBase().encrypt_str(param2)
        elif param1 == "decrypt":
            return CryptoBase().decrypt_str(param2)
        else:
            raise NotImplementedError("\n".join([
                "Unknown Param: {}".format(param1)]))

    print(_action())


if __name__ == "__main__":
    import plac

    plac.call(main)
