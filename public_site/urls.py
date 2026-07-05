from django.urls import path

from public_site import views

app_name = "public"

urlpatterns = [
    path("", views.home, name="home"),
    path("sessions/", views.session_list, name="session_list"),
    path("sessions/<int:pk>/book/", views.book_session, name="book_session"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("children/add/", views.add_child, name="add_child"),
    path("bookings/<int:pk>/success/", views.booking_success, name="booking_success"),
    path("bookings/<int:pk>/cancel/", views.booking_cancel, name="booking_cancel"),
    path("contact/", views.contact_form, name="contact"),
    path("<slug:slug>/", views.page_detail, name="page"),
]
