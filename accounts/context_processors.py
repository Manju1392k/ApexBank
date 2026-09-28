def bank_account_context(request):
    """
    Makes bank_account details accessible in templates for authenticated customers.
    """
    context = {}
    if request.user.is_authenticated and not request.user.is_staff:
        try:
            context['current_bank_account'] = request.user.bank_account
        except Exception:
            context['current_bank_account'] = None
    return context
