from django.http import HttpResponseRedirect


class BaseQRType:
    """
    Abstract base for all QR content type handlers.

    Subclasses must set `type_id` and implement `get_destination()` or
    override `respond()` if a landing page is needed instead of a redirect.
    """

    type_id: str = None
    is_static: bool = False       # True → encode payload directly (WiFi, plain text)
    has_landing_page: bool = False  # True → render a hosted page instead of redirect

    def __init__(self, qr_code):
        self.qr = qr_code
        self.data: dict = qr_code.type_data

    # ------------------------------------------------------------------ #
    #  Core interface                                                       #
    # ------------------------------------------------------------------ #

    def get_destination(self) -> str:
        """Return the final URL or content string."""
        raise NotImplementedError

    def to_qr_content(self) -> str:
        """
        Return the string that gets encoded into the QR matrix.
        Dynamic types encode the short URL; static types encode the payload.
        """
        if self.is_static:
            return self.get_destination()
        return self.qr.get_redirect_url()

    def respond(self, request):
        """
        Called by the redirect view after access checks + scan logging.
        Default: HTTP 302 redirect to get_destination().
        Landing-page types should override this.
        """
        return HttpResponseRedirect(self.get_destination())

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def get(self, key, default=None):
        return self.data.get(key, default)

    def validate(self) -> list[str]:
        """Return a list of validation error strings (empty = valid)."""
        return []
