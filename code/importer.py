import os
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, *[os.pardir] * 3)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'simple_lms.settings'
import django
django.setup()

import csv
import json
from random import randint
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from core.models import Course, CourseMember, CourseContent, Comment

import time
start_time = time.time()

filepath = './dummy_data/'
skipped_members = 0
skipped_contents = 0
skipped_comments = 0

with open(filepath+'user-data.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        obj_create = []
        for num, row in enumerate(reader):
            if not User.objects.filter(username=row['username']).exists():
                obj_create.append(User(username=row['username'], 
                                         password=make_password(row['password']), 
                                         email=row['email'],
                                         first_name=row['firstname'],
                                         last_name=row['lastname']))
        User.objects.bulk_create(obj_create)

with open(filepath+'course-data.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    obj_create = []
    for num,row in enumerate(reader):
        if not Course.objects.filter(pk=num+1).exists():
            obj_create.append(Course(name=row['name'], price=row['price'],
                                  description=row['description'], 
                                  teacher=User.objects.get(pk=int(row['teacher']))))
    Course.objects.bulk_create(obj_create)


with open(filepath+'member-data.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    obj_create = []
    for num, row in enumerate(reader):
        if not CourseMember.objects.filter(pk=num+1).exists():
            course = Course.objects.filter(pk=int(row['course_id'])).first()
            user = User.objects.filter(pk=int(row['user_id'])).first()
            if not course or not user:
                skipped_members += 1
                continue
            obj_create.append(
                CourseMember(course_id=course, user_id=user, roles=row['roles'])
            )
    CourseMember.objects.bulk_create(obj_create)


with open(filepath+'contents.json') as jsonfile:
    comments = json.load(jsonfile)
    obj_create = []
    for num, row in enumerate(comments):
        if not CourseContent.objects.filter(pk=num+1).exists():
            course = Course.objects.filter(pk=int(row['course_id'])).first()
            if not course:
                skipped_contents += 1
                continue
            obj_create.append(
                CourseContent(
                    course_id=course,
                    video_url=row['video_url'],
                    name=row['name'],
                    description=row['description'],
                )
            )
    CourseContent.objects.bulk_create(obj_create)


with open(filepath+'comments.json') as jsonfile:
    comments = json.load(jsonfile)
    obj_create = []
    for num, row in enumerate(comments):
        if int(row['user_id']) > 50:
            row['user_id'] = randint(5, 40)
        if not Comment.objects.filter(pk=num+1).exists():
            content = CourseContent.objects.filter(pk=int(row['content_id'])).first()
            user = User.objects.filter(pk=int(row['user_id'])).first()
            if not content or not user:
                skipped_comments += 1
                continue
            obj_create.append(Comment(content_id=content, user_id=user, comment=row['comment']))
    Comment.objects.bulk_create(obj_create)

print(f"Skipped members: {skipped_members}")
print(f"Skipped contents: {skipped_contents}")
print(f"Skipped comments: {skipped_comments}")
print("--- %s seconds ---" % (time.time() - start_time))