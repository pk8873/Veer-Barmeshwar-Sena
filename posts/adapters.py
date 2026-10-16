from allauth.account.adapter import DefaultAccountAdapter


class ClosedAccountAdapter(DefaultAccountAdapter):
    """Keep password-based public registration closed; Google sign-in remains enabled."""

    def is_open_for_signup(self, request):
        return False
