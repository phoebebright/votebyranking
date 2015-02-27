from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from web.views import *

urlpatterns = patterns('',
    # Examples:
    url(r'^$', Ask.as_view(), name='home'),
    url(r'^$', Ask.as_view(), name='ask'),
    url(r'^save-answers/(?P<question_id>\d+)/$', 'web.views.save_answers', name='save-answers'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^update_order/(?P<question_id>\d+)/$', 'web.views.update_order', name="update_order"),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^login/$', 'django.contrib.auth.views.login', name="login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout',  {'next_page': '/'}, name="logout"),

    url(r'^convert/', include('lazysignup.urls')),

)+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
