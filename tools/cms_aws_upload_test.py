#!/usr/bin/env python3
"""Upload a cms-upload/ package into a *test* CMS AdminWebServer through its web forms,
exactly the requests a browser sends when the steps of SETTINGS.md are done by hand.
Use it against a local/test CMS 1.5.1 to check the manual-upload procedure; never against the
contest server.

usage: cms_aws_upload_test.py <aws-base-url> <admin-user> <admin-password> <cms-upload-dir> <task-name>
"""
import html.parser
import json
import os
import re
import sys

import requests

base, user, password, pkg, name = sys.argv[1:6]
s = requests.Session()
s.trust_env = False  # local server: no proxy


def xsrf():
    return s.cookies.get("_xsrf")


def post(url, data=None, files=None):
    data = dict(data or {})
    data["_xsrf"] = xsrf()
    r = s.post(base + url, data=data, files=files, allow_redirects=True)
    r.raise_for_status()
    return r


s.get(base + "/login")
r = post("/login", {"username": user, "password": password, "next": "/"})
assert "logout" in r.text.lower(), "login failed"

# 1. create the task
r = post("/tasks/add", {"name": name})
m = re.search(r"/task/(\d+)", r.url)
assert m, "task not created: " + r.url
tid = m.group(1)
print("task id", tid)


def upload(url, field, path, extra=None):
    with open(path, "rb") as f:
        post(url, extra, {field: (os.path.basename(path), f)})
    print("uploaded", os.path.relpath(path, pkg), "->", url)


# 2. statement, attachment
upload("/task/%s/statements/add" % tid, "statement", os.path.join(pkg, "statement-fa.pdf"), {"language": "fa"})
for a in sorted(os.listdir(os.path.join(pkg, "attachments"))):
    upload("/task/%s/attachments/add" % tid, "attachment", os.path.join(pkg, "attachments", a))

page = s.get(base + "/task/%s" % tid).text
did = re.search(r'name="time_limit_(\d+)"', page).group(1)
print("dataset id", did)

# 3. managers and testcases
for f in sorted(os.listdir(os.path.join(pkg, "managers"))):
    upload("/dataset/%s/managers/add" % did, "manager", os.path.join(pkg, "managers", f))
for f in sorted(os.listdir(pkg)):
    if f.startswith("testcases-part") and f.endswith(".zip"):
        upload("/dataset/%s/testcases/add_multiple" % did, "archive", os.path.join(pkg, f),
               {"input_template": "*.in", "output_template": "*.out"})


# 4. the task form: start from what the page currently holds (like a browser), change our fields
class Form(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.fields, self.in_form, self.select, self.textarea = {}, False, None, None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form" and a.get("action", "").endswith("/task/%s" % tid):
            self.in_form = True
        if not self.in_form:
            return
        if tag == "input" and a.get("name") and a.get("type") not in ("submit", "reset", "file"):
            if a.get("type") == "checkbox":
                if "checked" in a:
                    self.fields[a["name"]] = a.get("value", "on")
            elif a.get("type") == "radio":
                if "checked" in a:
                    self.fields[a["name"]] = a.get("value")
            else:
                self.fields[a["name"]] = a.get("value", "")
        elif tag == "select":
            self.select = a.get("name")
        elif tag == "option" and self.select:
            if "selected" in a or self.select not in self.fields:
                self.fields[self.select] = a.get("value")
        elif tag == "textarea":
            self.textarea = a.get("name")
            self.fields[self.textarea] = ""

    def handle_data(self, data):
        if self.textarea:
            self.fields[self.textarea] += data

    def handle_endtag(self, tag):
        if tag == "form":
            self.in_form = False
        elif tag == "select":
            self.select = None
        elif tag == "textarea":
            self.textarea = None


form = Form()
form.feed(s.get(base + "/task/%s" % tid).text)
fields = form.fields
prefix = "TaskTypeOptions_%s_Batch_" % did
params = open(os.path.join(pkg, "score_type_parameters.json")).read()
settings = open(os.path.join(pkg, "SETTINGS.md")).read()
tl = re.search(r"\| Time limit \| `([0-9.]+)`", settings).group(1)
ml = re.search(r"\| Memory limit \| `(\d+)` MiB", settings).group(1)
title = re.search(r"\| Title \| `([^`]*)`", settings).group(1)
fields.update({
    "title": title,
    "primary_statement_fa": "on",
    "feedback_level": "full",
    "token_mode": "disabled",
    "max_submission_number": "50",
    "max_user_test_number": "50",
    "min_submission_interval": "60",
    "min_user_test_interval": "60",
    "score_precision": "2",
    "score_mode": "max_subtask",
    "time_limit_%s" % did: tl,
    "memory_limit_%s" % did: ml,
    "task_type_%s" % did: "Batch",
    prefix + "compilation": "grader",
    prefix + "io_0_inputfile": "",
    prefix + "io_1_outputfile": "",
    prefix + "output_eval": "comparator",
    "score_type_%s" % did: "GroupMin",
    "score_type_parameters_%s" % did: params,
})
missing = [k for k in (prefix + "compilation", prefix + "io_0_inputfile", prefix + "output_eval",
                       "score_mode", "primary_statement_fa") if k not in form.fields]
print("form fields not present on the page (would be a wrong field name):", missing or "none")
r = post("/task/%s" % tid, fields)
err = re.findall(r"Invalid field\(s\)[^<]*|ValueError[^<]*", r.text)
print("task form posted;", "errors: %s" % err if err else "no error notification on the page")
print(json.dumps({"task_id": int(tid), "dataset_id": int(did)}))
