import logging
import urllib

from OpenSSL import crypto  # type: ignore

from . import utils

_logger = logging.getLogger(__name__)


class NoUniqueIdentifierException(Exception):
    """If not valid RFC founded in the certificate"""


class NoIssuerException(Exception):
    """If not valid Issuer founded in the certificate"""


class CertificateHandler:
    cert: str
    key: str
    password: bytes

    unique_identifier: str
    certificate: crypto.X509
    key_pem: str
    cert_pem: str

    def __init__(self, cert_binary: bytes, key_binary: bytes, password: bytes):
        self.cert = utils.binary_to_utf8(cert_binary)
        self.key = utils.binary_to_utf8(key_binary)
        self.password = password
        self._load_certs()
        self._compute_data_from_cert()

    def _load_certs(self):
        """Loads the PEM version of the certificate and key file, also loads the crypto certificate

        Convert the `cert` and `key` from DER to PEM and creates the real certificate (X509)
        """
        self.key_pem = utils.der_to_pem(self.key, cert_type="ENCRYPTED PRIVATE KEY")
        self.cert_pem = utils.der_to_pem(self.cert, cert_type="CERTIFICATE")
        self.certificate = crypto.load_certificate(crypto.FILETYPE_PEM, self.cert_pem)

    def _compute_data_from_cert(self):
        """Gets the RFC and Issuer directly from the certificate"""
        self._get_rfc_from_cert()
        self._get_issuer_from_cert()

    def _get_rfc_from_cert(self):
        """Gets the RFC from the certificate

        Raises:
            NoUniqueIdentifierException: If not RFC founded
        """
        subject_components = self.certificate.get_subject().get_components()
        for c in subject_components:
            if c[0] == b"x500UniqueIdentifier":
                self.unique_identifier = c[1].decode("UTF-8").split(" ")[0]
                _logger.debug("x500UniqueIdentifier %s loaded", self.unique_identifier)
                break
        else:
            raise NoUniqueIdentifierException()

    def _get_issuer_from_cert(self):
        """Gets the Issuer from the certificate

        Raises:
            NoIssuerException: If not Issuer founded
        """
        self.certificate.issuer = ",".join(
            f'{c[0].decode("UTF-8")}={urllib.parse.quote(c[1].decode("UTF-8"))}'
            for c in self.certificate.get_issuer().get_components()
        )

        if not self.certificate.issuer:
            raise NoIssuerException()
        _logger.debug("Issuer %s loaded", self.certificate.issuer)

    def sign(self, data: str) -> str:
        """Signs the `data` using SHA1 with the `key_pem` content"""
        _logger.debug("Signing %s", data)
        private_key = crypto.load_privatekey(
            crypto.FILETYPE_PEM, self.key_pem, passphrase=self.password
        )
        signed_data = crypto.sign(private_key, data, "sha1")
        return utils.binary_to_utf8(signed_data).replace("\n", "")
