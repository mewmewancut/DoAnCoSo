from django.shortcuts import render
from django.utils import translation
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import translate_url

def home(request):
    return render(request, "home.html")

def set_language(request):
    """
    View to handle language switching.
    Redirects to the same page with the new language.
    """
    language = settings.LANGUAGE_CODE  # Default language
    
    if request.method == 'POST':
        language = request.POST.get('language', settings.LANGUAGE_CODE)
        if language in dict(settings.LANGUAGES):
            # Activate the language for this request
            translation.activate(language)
            # Store language preference in session (LocaleMiddleware uses 'django_language')
            request.session['django_language'] = language
            # Also set it in the response cookie
            response = HttpResponseRedirect(request.POST.get('next', request.GET.get('next', '/')))
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language, max_age=settings.LANGUAGE_COOKIE_AGE or 365*24*60*60)
            return response
    
    # Get the next URL or default to home
    next_url = request.POST.get('next', request.GET.get('next', '/'))
    
    # Translate the URL if possible
    if next_url:
        try:
            next_url = translate_url(next_url, language)
        except:
            pass
    
    return HttpResponseRedirect(next_url)
