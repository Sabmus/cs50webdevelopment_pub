""" Specifications:
https://cs50.harvard.edu/web/2020/projects/1/wiki/#specification
"""
from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
import random
import markdown2  # https://github.com/trentm/python-markdown2

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


# for the future
def markdown_to_html(content):
    pass


def entry(request, title):
    template = "encyclopedia/entry.html"
    entry = util.get_entry(title)
    if entry is None:
        return render(request, template_name=template, context={
            "content": "<h2>Entry not found.</h2>"
        })
    else:
        return render(request, template_name=template, context={
            "title": title,
            "content": markdown2.markdown(entry)
        })


def search(request):
    query = request.POST["q"]
    entry = util.get_entry(query)
    if entry is not None:
        return HttpResponseRedirect(reverse("entry", kwargs={'title': query}))
    else:
        entries = list(filter(lambda entry_: query in entry_, util.list_entries()))
        return render(request, "encyclopedia/search.html", context={
            "entries": entries
        })


def new_entry(request):
    template = "encyclopedia/new_entry.html"
    if request.method == "POST":
        title = request.POST["title"]
        content = request.POST["content"]
        entry = util.get_entry(title)
        if entry is None:
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("entry", kwargs={'title': title}))
        else:
            return render(request, template_name=template, context={
                "message": f"Error: the {title} page already exists."
            })

    return render(request, template_name=template, context={})


def edit_entry(request, title):
    template = "encyclopedia/edit_entry.html"
    entry = util.get_entry(title)

    if request.method == "POST":
        util.save_entry(title, request.POST["content"])
        return HttpResponseRedirect(reverse("entry", kwargs={'title': title}))

    return render(request, template_name=template, context={
        "title": title,
        "content": entry
    })


def random_page(request):
    random_entry = random.choice(util.list_entries())
    return HttpResponseRedirect(reverse("entry", kwargs={'title': random_entry}))
