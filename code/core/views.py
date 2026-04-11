from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.db.models import Count, Min, Max, Avg
from core.models import Course, CourseContent, CourseMember, User
from django.db import IntegrityError
from django.contrib.auth.models import User


def index(request):
    courses = Course.objects.all().select_related("teacher")[:3]
    return render(request, "home.html", {"featured_courses": courses})


def testing(request):
    try:
        guru, created = User.objects.get_or_create(
            username="Agus_sumanto",
            defaults={
                "email": "agus@gmail.com",
                "first_name": "agus",
                "last_name": "sumanto",
            },
        )
        if created:
            guru.set_password("Rahasia")
            guru.save()

        Course.objects.get_or_create(
            name="Pemrograman Python",
            defaults={
                "description": "Belajar Python",
                "price": 500000,
                "teacher": guru,
            },
        )
        return HttpResponse("OK")
    except IntegrityError:
        return HttpResponse("Already initialized", status=200)


def allCourse(request):
    courses = Course.objects.all().select_related("teacher")
    if request.headers.get("Accept", "").startswith("application/json"):
        data_resp = []
        for course in courses:
            data_resp.append({
                "id": course.id,
                "name": course.name,
                "price": course.price,
                "teacher": {
                    "id": course.teacher.id,
                    "username": course.teacher.username,
                    "fullname": f"{course.teacher.first_name} {course.teacher.last_name}",
                },
            })
        return JsonResponse(data_resp, safe=False)
    return render(request, "courses.html", {"courses": courses})


def userProfile(request, user_id):
    user = User.objects.get(pk=user_id)
    courses = Course.objects.filter(teacher=user)
    if request.headers.get("Accept", "").startswith("application/json"):
        data_resp = {
            "username": user.username,
            "email": user.email,
            "fullname": f"{user.first_name} {user.last_name}",
            "courses": [
                {"id": c.id, "name": c.name, "price": c.price, "description": c.description}
                for c in courses
            ],
        }
        return JsonResponse(data_resp, safe=False)
    return render(request, "profile.html", {"user_obj": user, "courses": courses})


def courseStats(request):
    if request.headers.get("Accept", "").startswith("application/json"):
        courses = Course.objects.all()
        statistics = courses.aggregate(
            course_count=Count("*"),
            min_price=Min("price"),
            max_price=Max("price"),
            avg_price=Avg("price"),
        )
        cheapest_list  = Course.objects.filter(price=statistics["min_price"])
        expensive_list = Course.objects.filter(price=statistics["max_price"])
        popular_list   = Course.objects.annotate(member_count=Count("coursemember")).order_by("-member_count")[:3]
        unpopular_list = Course.objects.annotate(member_count=Count("coursemember")).order_by("member_count")[:3]
        return JsonResponse({
            "course_count": statistics["course_count"],
            "min_price": statistics["min_price"],
            "max_price": statistics["max_price"],
            "avg_price": statistics["avg_price"],
            "cheapest_courses":  [c.name for c in cheapest_list],
            "expensive_courses": [c.name for c in expensive_list],
            "popular_courses":   [c.name for c in popular_list],
            "unpopular_courses": [c.name for c in unpopular_list],
        }, safe=False)

    statistics = Course.objects.all().aggregate(
        course_count=Count("*"),
        min_price=Min("price"),
        max_price=Max("price"),
        avg_price=Avg("price"),
    )
    cheapest_list  = Course.objects.filter(price=statistics["min_price"])
    expensive_list = Course.objects.filter(price=statistics["max_price"])
    popular_list   = Course.objects.annotate(member_count=Count("coursemember")).order_by("-member_count")[:3]

    total_user             = User.objects.count()
    users_with_courses     = User.objects.filter(coursemember__isnull=False).distinct().count()
    users_without_courses  = User.objects.filter(coursemember__isnull=True).count()
    avg_courses_per_user   = (
        CourseMember.objects.values("user_id")
        .annotate(course_count=Count("course_id"))
        .aggregate(avg_course=Avg("course_count"))["avg_course"]
    )
    top_user = (
        CourseMember.objects.values("user_id", "user_id__username")
        .annotate(course_count=Count("course_id"))
        .order_by("-course_count")
        .first()
    )
    users_without_enrollments = User.objects.exclude(
        id__in=CourseMember.objects.values_list("user_id", flat=True)
    ).values_list("username", flat=True)

    context = {
        "course_stats": {
            "course_count":      statistics["course_count"],
            "min_price":         statistics["min_price"],
            "max_price":         statistics["max_price"],
            "avg_price":         statistics["avg_price"],
            "cheapest_courses":  [c.name for c in cheapest_list],
            "expensive_courses": [c.name for c in expensive_list],
            "popular_courses":   popular_list,
        },
        "user_stats": {
            "total_user":                  total_user,
            "users_with_courses":          users_with_courses,
            "users_without_courses":       users_without_courses,
            "avg_courses_per_user":        avg_courses_per_user,
            "top_user":                    top_user["user_id__username"] if top_user else None,
            "users_without_enrollments":   list(users_without_enrollments),
        },
    }
    return render(request, "stats.html", context)


def userCourseStats(request):
    total_user            = User.objects.count()
    users_with_courses    = User.objects.filter(coursemember__isnull=False).distinct().count()
    users_without_courses = User.objects.filter(coursemember__isnull=True).count()
    avg_courses_per_user  = (
        CourseMember.objects.values("user_id")
        .annotate(course_count=Count("course_id"))
        .aggregate(avg_course=Avg("course_count"))["avg_course"]
    )
    top_user = (
        CourseMember.objects.values("user_id", "user_id__username")
        .annotate(course_count=Count("course_id"))
        .order_by("-course_count")
        .first()
    )
    users_without_enrollments = User.objects.exclude(
        id__in=CourseMember.objects.values_list("user_id", flat=True)
    ).values_list("username", flat=True)

    return JsonResponse({
        "total_user":                 total_user,
        "users_with_courses":         users_with_courses,
        "users_without_courses":      users_without_courses,
        "avg_courses_per_user":       avg_courses_per_user,
        "top_user":                   top_user["user_id__username"] if top_user else None,
        "users_without_enrollments":  list(users_without_enrollments),
    })
    
def create_admin(request):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@gmail.com",
            password="admin"
        )
        return HttpResponse("Admin created!")
    return HttpResponse("Already exists")