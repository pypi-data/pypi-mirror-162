# from django.shortcuts import render
from django.http import HttpResponse
from .models import Database
import json
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def db_config(request):
    """A function used to create a REASTful API to listing default
    configurations for each RDBMS type"""
    return HttpResponse(json.dumps(
        Database.configs(), indent=2), content_type="application/json")
