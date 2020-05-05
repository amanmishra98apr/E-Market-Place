from django.urls import path
from . import views
from django.conf.urls import url,include

urlpatterns = [
    url('register/',views.regPage),
    url('adduser/',views.adduser),
    url('loginPage/',views.loginPage),
    url('success/',views.success),
    url('LogOut/',views.LogOut),
    path("", views.index, name="ShopHome"),
    path("about/", views.about, name="AboutUs"),
    path("contact/", views.contact, name="ContactUs"),
    path("profile/",views.profile),
    path("OTPPage/",views.OTPPage),
    path('fun_otp_send/',views.fun_otp_send),
    path("updatePro/",views.updatePro),
    path("search/", views.search, name="Search"),
    path("products/<int:myid>", views.productView, name="ProductView"),
    path("checkout/", views.checkout, name="Checkout"),
    path("handlerequest/", views.handlerequest, name="HandleRequest"),

]
