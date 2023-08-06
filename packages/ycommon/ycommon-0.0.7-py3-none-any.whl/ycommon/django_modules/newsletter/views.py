import logging

from django.http import JsonResponse

from .forms import NewsletterSignUpForm

def submit_newsletter_signup_form(request):
    if request.is_ajax():
        logging.info("AJAX")
        form = NewsletterSignUpForm(request.GET)
        if form.is_valid():
            logging.info("Form Valid")
            form.save()
            data = {
                "success": True,
            }
            return JsonResponse(data)
        else:
            logging.info("Form Not Valid")
            data = {
                "success": False,
            }
            return JsonResponse(data)
    else:
        logging.info("NOT AJAX")
        data = {
            "success": False,
        }
        return JsonResponse(data)
