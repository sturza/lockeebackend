from django.conf.urls import url
from portal import views

urlpatterns = [
    # Server
    url(r'^login/$', views.Login.as_view(), name='login'),
    url(r'^register/$', views.Register.as_view(), name='register'),
    url(r'^my-locks/$', views.Display_My_Locks.as_view(), name='my-locks'),
    url(r'^logout/$', views.log_out, name='logout'),
    url(r'^add-lock/$', views.Add_Lock.as_view(), name='add-lock'),
    url(r'^share/(?P<lock_nickname>[\w|\W]+)/$', views.share, name='share'),
    url(r'^generate/(?P<lock_nickname>[\w|\W]+)/$', views.generate_code, name='generate'),
    url(r'^mechanic/(?P<lock_nickname>[\w|\W]+)/$', views.portal_mechanic, name='portal-mechanic'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^about/$', views.about, name='about'),
    # Android
    url(r'^secret/register/$', views.andro_register),
    url(r'^secret/login/$', views.andro_login),
    url(r'^secret/get_locks/$', views.android_locks_query),
    url(r'^secret/verify_register/$', views.andro_verify),
    # Arduino
    url(r'^arduino/register-lock/(?P<what_lock>[-\w]+)/$', views.arduino_register_lock, name='arduino-register-lock'),
]