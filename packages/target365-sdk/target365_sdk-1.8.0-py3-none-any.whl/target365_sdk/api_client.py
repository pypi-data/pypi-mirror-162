from .helpers.http_client import HttpClient
from .models.lookup_result import LookupResult
from .models.keyword import Keyword
from .models.out_message import OutMessage
from .models.strex_merchant import StrexMerchant
from .models.in_message import InMessage
from .models.one_time_password import OneTimePassword
from .models.strex_transaction import StrexTransaction
from .models.public_key import PublicKey
from .models.oneclick_config import OneClickConfig
from .models.user_validity import UserValidity

name = "target365_sdk"

class ApiClient:
    PING = "api/ping"
    LOOKUP = "api/lookup"
    KEYWORDS = "api/keywords"
    OUT_MESSAGES = "api/out-messages"
    OUT_MESSAGE_EXPORT = "api/export/out-messages"
    IN_MESSAGES = "api/in-messages"
    PREPARE_MSISDNS = "api/prepare-msisdns"
    STREX_MERCHANTS = "api/strex/merchants"
    STREX_TRANSACTIONS = "api/strex/transactions"
    STREX_ONE_TIME_PASSWORDS = "api/strex/one-time-passwords"
    STREX_REGISTRATION_SMS = "api/strex/registrationsms"
    STREX_USER_INFO = "api/strex/validity"
    SERVER_PUBLIC_KEYS = "api/server/public-keys"
    CLIENT_PUBLIC_KEYS = "api/client/public-keys"
    ONECLICK_CONFIGS = "api/one-click/configs"

    NOT_FOUND = 404

    def __init__(self, base_uri, key_name, private_key):
        self.client = HttpClient(base_uri, key_name, private_key)

    def ping(self):
        """
        Pings the service and returns 'pong' string
        :return: string 'pong'.
        """

        response = self.client.get(self.PING)
        response.raise_for_status()

        return response.text  # returns the string "pong"

    def lookup(self, msisdn):
        """
        Looks up address info on a mobile phone number.
        :msisdn: Mobile phone number (required).
        :return: LookupResult object.
        """

        if msisdn is None:
            raise ValueError("msisdn")

        query = {"msisdn": msisdn}
        response = self.client.get_with_params(self.LOOKUP, query)

        if response.status_code == self.NOT_FOUND:
            return None

        response.raise_for_status()

        lookup_result = LookupResult(**response.json())
        return lookup_result

    def create_keyword(self, keyword):
        """
        Creates a new keyword.
        :keyword: Keyword object.
        :return: resulting keyword id string.
        """
        if keyword is None:
            raise ValueError("keyword")
        response = self.client.post(self.KEYWORDS, keyword)
        response.raise_for_status()

        return self._get_id_from_header(response.headers)

    def get_all_keywords(self, short_number_id=None, keyword=None, mode=None, tag=None):
        """
        Gets keywords.
        :short_number_id: Short number id to search on.
        :keyword: Keyword text to search for.
        :mode: Keyword mode to search for.
        :tag: Keyword tag to search for.
        :return: array of Keyword objects.
        """
        query = {}
        if short_number_id is not None:
            query["shortNumberId"] = short_number_id
        if keyword is not None:
            query["keywordText"] = keyword
        if mode is not None:
            query["mode"] = mode
        if tag is not None:
            query["tag"] = tag

        response = self.client.get_with_params(self.KEYWORDS, query)
        response.raise_for_status()
        return Keyword.from_list(response.json())

    def get_keyword(self, keyword_id):
        """
        Gets a keyword.
        :keyword_id: keyword id string.
        :return: Keyword object.
        """
        if keyword_id is None:
            raise ValueError("keywordId")

        response = self.client.get(self.KEYWORDS + "/" + keyword_id)
        if response.status_code == self.NOT_FOUND:
            return None

        response.raise_for_status()
        
        return Keyword(**response.json())

    def update_keyword(self, keyword):
        """
        Updates a keyword.
        :param keyword: Keyword object.
        """
        if keyword is None:
            raise ValueError("keyword")
        if keyword.keywordId is None:
            raise ValueError("keywordId")

        response = self.client.put(
            self.KEYWORDS + "/" + keyword.keywordId, keyword)

        response.raise_for_status()

    def delete_keyword(self, keyword_id):
        """
        Deletes a keyword.
        :keyword_id: Keyword id string.
        """
        if keyword_id is None:
            raise ValueError("keyword_id")

        response = self.client.delete(self.KEYWORDS + "/" + keyword_id)
        response.raise_for_status()

    def prepare_msisdns(self, msisdns):
        """
        Prepare MSISDNs for later sendings. This can greatly improve routing performance.
        :msisdns: MSISDNs to prepare as a string array.
        """
        if msisdns is None:
            raise ValueError("msisdns")

        response = self.client.post(self.PREPARE_MSISDNS, msisdns)
        response.raise_for_status()

    def create_out_message(self, out_message):
        """
        Creates a new out-message
        :out_message: OutMessage object.
        """
        if out_message is None:
            raise ValueError("out_message")

        response = self.client.post(self.OUT_MESSAGES, out_message)
        response.raise_for_status()

        return self._get_id_from_header(response.headers)

    def create_out_message_batch(self, out_messages):
        """
        Creates a new out-message batch.
        :out_messages: Array of OutMessage objects.
        """
        if out_messages is None:
            raise ValueError("out_messages")

        response = self.client.post(self.OUT_MESSAGES + "/batch", out_messages)
        response.raise_for_status()

    def get_out_message(self, transaction_id):
        """
        Gets an out-message by transaction id.
        :transaction_id: Transaction id string.
        :return: OutMessage object.
        """
        if transaction_id is None:
            raise ValueError("transactionId")

        response = self.client.get(self.OUT_MESSAGES + "/" + transaction_id)
        if response.status_code == self.NOT_FOUND:
            return None

        response.raise_for_status()

        return OutMessage(**response.json())

    def update_out_message(self, out_message):
        """
        Updates a future scheduled out-message.
        :out_message: OutMessage
        """
        if out_message is None:
            raise ValueError("out_message")
        if out_message.transactionId is None:
            raise ValueError("transactionId")

        response = self.client.put(self.OUT_MESSAGES + "/" + out_message.transactionId, out_message)
        response.raise_for_status()

    def delete_out_message(self, transaction_id):
        """
        Deletes a future sheduled out-message.
        :transaction_id: Out-message transaction id string.
        """
        if transaction_id is None:
            raise ValueError("transaction_id")

        response = self.client.delete(self.OUT_MESSAGES + "/" + transaction_id)
        response.raise_for_status()

    def get_out_message_export(self, from_date, to_date):
        """
        Gets out-message export in CSV format
        :from_date: From datetime in UTC
        :to_date: To datetime in UTC
        :return: string CSV data
        """
        query = {"from": from_date, "to": to_date}
        response = self.client.get_with_params(self.OUT_MESSAGE_EXPORT, query)
        response.raise_for_status()
        return response.text

    def get_in_message(self, short_number_id, transaction_id):
        """
        Gets an in-message.
        :short_number_id: string
        :transaction_id: string
        :return: InMessage object.
        """
        if short_number_id is None:
            raise ValueError("short_number_id")
        if transaction_id is None:
            raise ValueError("transaction_id")

        response = self.client.get(self.IN_MESSAGES + "/" + short_number_id + "/" + transaction_id)
        response.raise_for_status()
        return InMessage(**response.json())

    def get_strex_merchants(self):
        """
        Gets all merchant ids.
        :return: Array of StrexMerchant objects.
        """
        response = self.client.get(self.STREX_MERCHANTS)
        response.raise_for_status()
        return StrexMerchant.from_list(response.json())

    def get_strex_merchant(self, merchant_id):
        """
        Gets a strex merchant.
        :merchant_id: Merchant id string.
        :returns: StrexMerchant object.
        """
        if merchant_id is None:
            raise ValueError("merchant_id")

        response = self.client.get(self.STREX_MERCHANTS + "/" + merchant_id)

        if response.status_code == self.NOT_FOUND:
            return None

        response.raise_for_status()
        return StrexMerchant(**response.json())

    def save_strex_merchant(self, merchant):
        """
        Creates or updates a merchant.
        :merchant: StrexMerchant object.
        """
        if merchant is None:
            raise ValueError("merchant")
        if merchant.merchantId is None:
            raise ValueError("merchantId")

        response = self.client.put(self.STREX_MERCHANTS + "/" + merchant.merchantId, merchant)
        response.raise_for_status()

    def delete_strex_merchant(self, merchant_id):
        """
        DELETE /api/strex/merchants/{merchantId}
        Deletes a merchant
        :merchant_id: Merchant id string.
        """
        if merchant_id is None:
            raise ValueError("merchant_id")

        response = self.client.delete(self.STREX_MERCHANTS + "/" + merchant_id)
        response.raise_for_status()

    def create_one_time_password(self, one_time_password):
        """
        Creates a new one-time password.
        :one_time_password: OneTimePassword object.
        """

        if one_time_password is None:
            raise ValueError("one_time_password")
        if one_time_password.transactionId is None:
            raise ValueError("transactionId")
        if one_time_password.merchantId is None:
            raise ValueError("merchantId")
        if one_time_password.recipient is None:
            raise ValueError("recipient")
        if one_time_password.sender is None:
            raise ValueError("sender")
        if one_time_password.recurring is None:
            raise ValueError("recurring")

        response = self.client.post(self.STREX_ONE_TIME_PASSWORDS, one_time_password)
        response.raise_for_status()

    def get_one_time_password(self, transaction_id):
        """
        Gets a strex one-time password.
        :transaction_id: Transaction id string.
        :return: OneTimePassword object.
        """

        if transaction_id is None:
            raise ValueError("transaction_id")

        response = self.client.get(self.STREX_ONE_TIME_PASSWORDS + '/' + transaction_id)
        response.raise_for_status()
        return OneTimePassword(**response.json())

    def create_strex_transaction(self, transaction):
        """
        Creates a new strex transaction.
        :transaction: StrexTransaction object.
        :return: Transaction id string.
        """

        if transaction is None:
            raise ValueError("transaction")

        response = self.client.post(self.STREX_TRANSACTIONS, transaction)
        response.raise_for_status()
        return self._get_id_from_header(response.headers)

    def get_strex_transaction(self, transaction_id):
        """
        Gets a strex transaction.
        :transaction_id: Transaction id string.
        :return: StrexTransaction object.
        """

        if transaction_id is None:
            raise ValueError("transaction_id")

        response = self.client.get(self.STREX_TRANSACTIONS + '/' + transaction_id)
        response.raise_for_status()
        return StrexTransaction(**response.json())

    def reverse_strex_transaction(self, transaction_id):
        """
        Reverses a previous strex transaction.
        :transaction_id: Transaction id string.
        """

        if transaction_id is None:
            raise ValueError("transaction_id")

        response = self.client.delete(self.STREX_TRANSACTIONS + '/' + transaction_id)
        response.raise_for_status()

    def send_strex_registration_sms(self, strex_registration_sms):
        """
        Initiates Strex-registation by SMS.
        :strex_registration_sms: StrexRegistrationSms object.
        """

        if strex_registration_sms is None:
            raise ValueError("strex_registration_sms")

        response = self.client.post(self.STREX_REGISTRATION_SMS, strex_registration_sms)
        response.raise_for_status()

    def get_strex_user_info(self, merchant_id, recipient):
        """
        Gets Strex user validity.
        :merchant_id: Merchant id string.
        :recipient: MSISDN recipient string.
        :returns: UserValidity string.
        """

        if recipient is None:
            raise ValueError("recipient")

        query = {"recipient": recipient}

        if merchant_id is not None:
            query["merchantId"] = merchant_id

        response = self.client.get_with_params(self.STREX_USER_INFO, query)
        response.raise_for_status()
        return response.json();

    def get_server_public_key(self, key_name):
        """
        Gets a server public key.
        :key_name: public key name string.
        :return: PublicKey object.
        """

        if key_name is None:
            raise ValueError("key_name")

        response = self.client.get(self.SERVER_PUBLIC_KEYS + '/' + key_name)
        response.raise_for_status()
        return PublicKey(**response.json())

    def get_client_public_keys(self):
        """
        Gets all client public key.
        :return: Array of PublicKey objects.
        """
        response = self.client.get(self.CLIENT_PUBLIC_KEYS)
        response.raise_for_status()
        return PublicKey.from_list(response.json())

    def get_client_public_key(self, key_name):
        """
        Gets a client public key.
        :key_name: public key name string.
        :return: PublicKey object.
        """

        if key_name is None:
            raise ValueError("key_name")

        response = self.client.get(self.CLIENT_PUBLIC_KEYS + '/' + key_name)
        response.raise_for_status()
        return PublicKey(**response.json())

    def delete_client_public_key(self, key_name):
        """
        Deletes a client public key.
        :key_name: public key name string.
        :return:
        """

        if key_name is None:
            raise ValueError("key_name")

        response = self.client.delete(self.CLIENT_PUBLIC_KEYS + '/' + key_name)
        response.raise_for_status()

    def get_oneclick_config(self, config_id):
        """
        Gets a one-click config.
        :config_id: One-click config id string.
        :returns: OneClickConfig object.
        """

        if config_id is None:
            raise ValueError("config_id")

        response = self.client.get(self.ONECLICK_CONFIGS + "/" + config_id)

        if response.status_code == self.NOT_FOUND:
            return None

        response.raise_for_status()
        return OneClickConfig(**response.json())

    def save_oneclick_config(self, config):
        """
        Creates or updates a one-click config.
        :config: OneClickConfig object.
        """

        if config is None:
            raise ValueError("config")
        if config.configId is None:
            raise ValueError("configId")

        response = self.client.put(self.ONECLICK_CONFIGS + "/" + config.configId, config)
        response.raise_for_status()

    # noinspection PyMethodMayBeStatic,PyMethodMayBeStatic
    def _get_id_from_header(self, headers):
        """
        Returns the newly created resource's identifier from the Locaion header
        :returns: resource identifier
        """
        chunks = headers["Location"].split("/")
        return chunks[-1]
