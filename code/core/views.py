from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Count, Min, Max, Avg
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from core.models import Course, CourseMember, CourseLike

# pylint: disable=no-member

def index(request):
    courses = Course.objects.all().select_related("teacher")[:3]
    statistics = Course.objects.all().aggregate(
        course_count=Count("*"),
        min_price=Min("price"),
        max_price=Max("price"),
        avg_price=Avg("price"),
    )
    return render(request, "home.html", {
        "featured_courses": courses,
        "stats": statistics,
    })


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

        demo_courses = [
            ("Базовий fade", "Техніка переходу і лінія контуру.", 4500),
            ("Гоління та догляд за бородою", "Підготовка шкіри, гоління, завершення.", 3900),
            ("Класичні чоловічі стрижки", "Схеми форм і робота ножицями.", 5200),
        ]
        for name, description, price in demo_courses:
            Course.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "price": price,
                    "teacher": guru,
                },
            )
        return HttpResponse("OK")
    except IntegrityError:
        return HttpResponse("Already initialized", status=200)


def allCourse(request):
    courses = Course.objects.all().select_related("teacher")
    if request.headers.get("Accept", "").startswith("application/json"):
        data_resp = [
            {
                "id": course.id,
                "name": course.name,
                "price": course.price,
                "teacher": {
                    "id": course.teacher.id,
                    "username": course.teacher.username,
                    "fullname": f"{course.teacher.first_name} {course.teacher.last_name}",
                },
            }
            for course in courses
        ]
        return JsonResponse(data_resp, safe=False)

    liked_ids = set()
    enrolled_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(
            CourseLike.objects.filter(user=request.user).values_list("course_id", flat=True)
        )
        enrolled_ids = set(
            CourseMember.objects.filter(user_id=request.user).values_list("course_id", flat=True)
        )
    return render(request, "courses.html", {
        "courses": courses,
        "liked_ids": liked_ids,
        "enrolled_ids": enrolled_ids,
    })


def courseDetail(request, course_id):
    course = get_object_or_404(Course.objects.select_related("teacher"), pk=course_id)
    liked_ids = set()
    enrolled_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(
            CourseLike.objects.filter(user=request.user).values_list("course_id", flat=True)
        )
        enrolled_ids = set(
            CourseMember.objects.filter(user_id=request.user).values_list("course_id", flat=True)
        )
    return render(request, "course_detail.html", {
        "course": course,
        "is_liked": course.id in liked_ids,
        "is_enrolled": course.id in enrolled_ids,
    })


def toggleLike(request, course_id):
    next_url = request.GET.get("next", f"/courses/{course_id}/")
    if not request.user.is_authenticated:
        return redirect(f"/login/?next={next_url}")
    like = CourseLike.objects.filter(course_id=course_id, user=request.user).first()
    if like:
        like.delete()
    else:
        CourseLike.objects.create(course_id=course_id, user=request.user)
    return redirect(next_url)


def toggleEnroll(request, course_id):
    next_url = request.GET.get("next", f"/courses/{course_id}/")
    if not request.user.is_authenticated:
        return redirect(f"/login/?next={next_url}")
    enrollment = CourseMember.objects.filter(course_id=course_id, user_id=request.user).first()
    if enrollment:
        enrollment.delete()
    else:
        CourseMember.objects.create(
            course_id_id=course_id,
            user_id=request.user,
            roles="std"
        )
    return redirect(next_url)


def userProfile(request, user_id):
    user = User.objects.get(pk=user_id)
    courses = Course.objects.filter(teacher=user)
    if request.headers.get("Accept", "").startswith("application/json"):
        return JsonResponse({
            "username": user.username,
            "email": user.email,
            "fullname": f"{user.first_name} {user.last_name}",
            "courses": [
                {
                    "id": c.id,
                    "name": c.name,
                    "price": c.price,
                    "description": c.description,
                }
                for c in courses
            ],
        }, safe=False)
    return render(request, "profile.html", {"user_obj": user, "courses": courses})


def courseStats(request):
    statistics = Course.objects.all().aggregate(
        course_count=Count("*"),
        min_price=Min("price"),
        max_price=Max("price"),
        avg_price=Avg("price"),
    )
    cheapest_list = Course.objects.filter(price=statistics["min_price"])
    expensive_list = Course.objects.filter(price=statistics["max_price"])
    popular_list = Course.objects.annotate(
        member_count=Count("coursemember")
    ).order_by("-member_count")[:3]
    unpopular_list = Course.objects.annotate(
        member_count=Count("coursemember")
    ).order_by("member_count")[:3]

    data_resp = {
        "course_count": statistics["course_count"],
        "min_price": statistics["min_price"],
        "max_price": statistics["max_price"],
        "avg_price": statistics["avg_price"],
        "cheapest_courses": [c.name for c in cheapest_list],
        "expensive_courses": [c.name for c in expensive_list],
        "popular_courses": [c.name for c in popular_list],
        "unpopular_courses": [c.name for c in unpopular_list],
    }
    if request.headers.get("Accept", "").startswith("application/json"):
        return JsonResponse(data_resp, safe=False)
    return render(request, "stats.html", {"stats": data_resp})


def userCourseStats(request):
    total_user = User.objects.count()
    users_with_courses = User.objects.filter(
        coursemember__isnull=False
    ).distinct().count()
    users_without_courses = User.objects.filter(
        coursemember__isnull=True
    ).count()
    avg_courses_per_user = (
        CourseMember.objects.values("user_id")
        .annotate(course_count=Count("course_id"))
        .aggregate(avg_course=Avg("course_count"))["avg_course"]
    )
    top_user = (
        CourseMember.objects
        .values("user_id", "user_id__username")
        .annotate(course_count=Count("course_id"))
        .order_by("-course_count")
        .first()
    )
    users_without_enrollments = User.objects.exclude(
        id__in=CourseMember.objects.values_list("user_id", flat=True)
    ).values_list("username", flat=True)

    return JsonResponse({
        "total_user": total_user,
        "users_with_courses": users_with_courses,
        "users_without_courses": users_without_courses,
        "avg_courses_per_user": avg_courses_per_user,
        "top_user": top_user["user_id__username"] if top_user else None,
        "users_without_enrollments": list(users_without_enrollments),
    })


def loginView(request):
    if request.user.is_authenticated:
        return redirect("/account/")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get("next") or "/account/")
    return render(request, "login.html", {"form": form})


def registerView(request):
    if request.user.is_authenticated:
        return redirect("/account/")
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("/account/")
    return render(request, "register.html", {"form": form})


def logoutView(request):
    logout(request)
    return redirect("/")


@login_required(login_url="/login/")
def accountView(request):
    enrolled_courses = Course.objects.filter(
        coursemember__user_id=request.user
    ).distinct()
    liked_courses = Course.objects.filter(
        likes__user=request.user
    ).distinct()
    return render(request, "account.html", {
        "enrolled_courses": enrolled_courses,
        "liked_courses": liked_courses,
    })


def create_admin(request):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@gmail.com",
            password="Admin1234!"
        )
        return HttpResponse("Admin created!")
    return HttpResponse("Already exists")