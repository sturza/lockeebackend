from django.conf.urls import url
from portal import views

urlpatterns = [
    url(r'^login/$', views.Login.as_view(), name='login'),
    url(r'^register/$', views.Register.as_view(), name='register'),
    url(r'^my-locks/$', views.Display_My_Locks.as_view(), name='my-locks'),
    url(r'^logout/$', views.log_out, name='logout'),
    url(r'^add-lock/$', views.Add_Lock.as_view(), name='add-lock'),
    url(r'^share/(?P<lock_inner_id>[-\w]+)/$', views.share, name='share'),
    url(r'^generate/(?P<lock_inner_id>[-\w]+)/$', views.generate_code, name='generate'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^secret/register/$', views.andro_register),
    url(r'^secret/login/$', views.andro_login),
    url(r'^about/$', views.about, name='about'),
    url(r'^secret/get_locks/$', views.lock_query),
    url(r'^portal_mechanic/(?P<lock_inner_id>[-\w]+)/$', views.portal_mechanic, name='portal-mechanic'),
    url(r'^secret/verify_register/$', views.andro_verify),
    url(r'^arduino/register-lock/(?P<what_lock>[-\w]+)/$', views.arduino_register_lock, name='arduino-register-lock'),
    url(r'^arduino/post/$', views.arduino_mechanic, name='arduino-mechanic'),
]