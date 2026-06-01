from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from core.views import (
    index,
    loginView,
    registerView,
    logoutView,
    accountView,
    testing,
    allCourse,
    courseDetail,
    toggleLike,
    toggleEnroll,
    userProfile,
    courseStats,
    userCourseStats,
    create_admin,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", loginView),
    path("register/", registerView),
    path("logout/", logoutView),
    path("account/", accountView),
    path("testing/", testing),
    path("courses/", allCourse),
    path("courses/<int:course_id>/", courseDetail),
    path("courses/<int:course_id>/like/", toggleLike),
    path("courses/<int:course_id>/enroll/", toggleEnroll),
    path("profile/<int:user_id>", userProfile),
    path("stats/", courseStats),
    path("course_stats", courseStats),
    path("user_course_stats", userCourseStats),
    path("", index),
    path("create-admin/", create_admin),
]

if getattr(settings, "SILK_ENABLED", False):
    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]