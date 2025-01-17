from django.shortcuts import render
from .models import Table


def table_list(request):
    tables = Table.objects.all()
    return render(request, "tables/table_list.html", {"tables": tables})
