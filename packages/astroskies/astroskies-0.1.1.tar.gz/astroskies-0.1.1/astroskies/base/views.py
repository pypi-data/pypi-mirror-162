from calendar import c
from django.http import HttpResponse


def index(request):
    html = "<html><body><strong>System infoa:</strong><br/><p>"+request.user_agent.browser.family+"</p></body></html>"
    return HttpResponse(html)
