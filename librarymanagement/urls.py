from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from library import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.home_view),

    path('adminclick', views.adminclick_view),
    path('studentclick', views.studentclick_view),

    path('studentsignup', views.studentsignup_view),
    path('adminlogin', LoginView.as_view(template_name='library/adminlogin.html')),
    path('studentlogin', LoginView.as_view(template_name='library/studentlogin.html')),
    path('returnbook/<int:id>/', views.returnbook, name='returnbook'),

    path('logout', LogoutView.as_view(template_name='library/index.html')),
    path('afterlogin', views.afterlogin_view),

    path('addbook', views.addbook_view),
    path('viewbook', views.viewbook_view),
    path('issuebook', views.issuebook_view),
    path('viewissuedbook', views.viewissuedbook_view),
    path('viewstudent', views.viewstudent_view),
    path('viewissuedbookbystudent', views.viewissuedbookbystudent, name='viewissuedbookbystudent'),

    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view),

    # Serve the desc.html file
    path('desc.html', serve, {'document_root': settings.STATICFILES_DIRS[0], 'path': 'desc.html'}),

    # RapidAPI endpoint
    path('add_volume_to_bookshelf/', views.add_volume_to_bookshelf, name='add_volume_to_bookshelf'),

    # Search Books endpoint
    path('search_books/', views.search_books, name='search_books'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
