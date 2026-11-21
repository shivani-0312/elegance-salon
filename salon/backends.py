import ssl
from django.core.mail.backends.smtp import EmailBackend

class UnverifiedEmailBackend(EmailBackend):
    """Custom backend that disables SSL certificate verification (for dev only)."""
    def open(self):
        if self.connection:
            return False
        try:
            ssl_context = ssl._create_unverified_context()
            self.connection = self.connection_class(
                self.host,
                self.port,
                local_hostname=self.local_hostname,
                timeout=self.timeout,
                context=ssl_context,
            )
            if self.use_tls:
                self.connection.starttls(context=ssl_context)
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except Exception:
            if not self.fail_silently:
                raise
            return False
