#!/usr/bin/env python3
"""Run the official TPS loader of CMS (cmscontrib/loaders/tps.py from a CMS checkout, e.g. tag
v1.5.1) on a `tps export CMS 1 -a none` directory, without a database, and compare what it builds
with the manual-upload package written by tools/cms_upload.py.

The cms.* / cmscommon.* modules the loader imports are replaced by small recording stubs; the
loader code itself (parameter parsing, checker compilation, testcase and subtask handling) runs
unchanged.

usage: cms_loader_check.py <cms-checkout> <export-dir> <cms-upload-dir>
"""
import importlib.util
import json
import os
import re
import sys
import types
import zipfile

cms_dir, export_dir, upload_dir = sys.argv[1:4]


class Recorder:
    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs


def fake_module(name, **attrs):
    mod = types.ModuleType(name)
    mod.__dict__.update(attrs)
    sys.modules[name] = mod
    return mod


fake_module("cms", FEEDBACK_LEVEL_FULL="full", FEEDBACK_LEVEL_RESTRICTED="restricted",
            FEEDBACK_LEVEL_OI_RESTRICTED="oi_restricted")
fake_module("cms.db", **{n: type(n, (Recorder,), {})
                         for n in ("Task", "Dataset", "Manager", "Testcase", "Attachment", "Statement")})
fake_module("cmscommon")
fake_module("cmscommon.constants", SCORE_MODE_MAX_SUBTASK="max_subtask",
            SCORE_MODE_MAX="max", SCORE_MODE_MAX_TOKENED_LAST="max_tokened_last")
fake_module("cmscommon.datetime", make_timedelta=lambda x: x)
fake_module("cmscontrib")
fake_module("cmscontrib.loaders")


class TaskLoader:
    def __init__(self, path, file_cacher):
        self.path, self.file_cacher = path, file_cacher


fake_module("cmscontrib.loaders.base_loader", TaskLoader=TaskLoader)


class FileCacher:
    def put_file_from_path(self, path, description):
        return "file:" + path

    def put_file_content(self, content, description):
        return "content"


spec = importlib.util.spec_from_file_location("cmscontrib.loaders.tps",
                                              os.path.join(cms_dir, "cmscontrib", "loaders", "tps.py"))
tps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tps)

assert tps.TpsTaskLoader.detect(export_dir), "loader does not detect the export"
task = tps.TpsTaskLoader(export_dir, FileCacher()).get_task(get_statement=True)
assert task is not None, "loader returned None"
ds = task.active_dataset.kwargs
loader = {
    "name": task.kwargs["name"],
    "title": task.kwargs["title"],
    "submission_format": task.kwargs["submission_format"],
    "task_type": ds["task_type"],
    "task_type_parameters": ds["task_type_parameters"],
    "time_limit": ds["time_limit"],
    "memory_limit_bytes": ds["memory_limit"],
    "managers": sorted(ds["managers"]),
    "testcases": sorted(ds["testcases"]),
    "score_type": ds["score_type"],
    "attachments": sorted(task.kwargs["attachments"]),
}
print("official loader (CMS %s):" % os.path.basename(os.path.abspath(cms_dir)))
for k, v in loader.items():
    print("  %-22s %s" % (k, v if k != "testcases" else "%d testcases" % len(v)))

# ---- compare with the manual package
problems = []


def expect(cond, msg):
    print("  [%s] %s" % ("ok" if cond else "MISMATCH", msg))
    if not cond:
        problems.append(msg)


print("comparison with %s:" % upload_dir)
settings = open(os.path.join(upload_dir, "SETTINGS.md")).read()
expect("| Name | `%s` |" % loader["name"] in settings, "task name")
expect("| Title | `%s` |" % loader["title"] in settings, "title")
expect(loader["submission_format"] == ["%s.%%l" % loader["name"]]
       and "| Submission format | `%s.%%l` |" % loader["name"] in settings, "submission format")
expect(loader["task_type"] == "Batch" and "| Task type | `Batch` |" in settings, "task type Batch")
comp, io, ev = loader["task_type_parameters"]
expect(comp == "grader" and "Submissions are compiled with a grader" in settings, "compilation = grader")
expect(io == ["", ""] and "Input file | *(empty)*" in settings and "Output file | *(empty)*" in settings,
       "I/O = stdin/stdout")
expect(ev == "comparator" and "Outputs are compared by a comparator" in settings, "output evaluation = comparator")
expect("| Time limit | `%g` second(s) |" % loader["time_limit"] in settings, "time limit")
expect("| Memory limit | `%d` MiB |" % (loader["memory_limit_bytes"] // 2**20) in settings, "memory limit")
package_managers = sorted(os.listdir(os.path.join(upload_dir, "managers")))
expect(package_managers == loader["managers"], "managers %s" % package_managers)
expect(sorted(os.listdir(os.path.join(upload_dir, "attachments"))) == loader["attachments"], "attachments")

zipped = []
for f in sorted(os.listdir(upload_dir)):
    if f.startswith("testcases-part") and f.endswith(".zip"):
        with zipfile.ZipFile(os.path.join(upload_dir, f)) as z:
            zipped += z.namelist()
ins = sorted(n[:-3] for n in zipped if n.endswith(".in"))
outs = sorted(n[:-4] for n in zipped if n.endswith(".out"))
expect(ins == outs == loader["testcases"] and len(zipped) == 2 * len(ins), "testcases in zips (%d)" % len(ins))
expect("**%d testcases**" % len(ins) in settings, "testcase count in SETTINGS.md")

# subtasks: the loader's GroupMin parameters vs ours, compared by the testcases each one selects
expect(loader["score_type"] == "GroupMin" and "| Score Type | `GroupMin` |" in settings, "score type GroupMin")
ours = json.load(open(os.path.join(upload_dir, "score_type_parameters.json")))
theirs = [p for p in ds["score_type_parameters"] if p[0] > 0]


def selected(regex):
    return sorted(c for c in loader["testcases"] if re.compile(regex).match(c))


expect(len(ours) == len(theirs), "number of scored subtasks (%d)" % len(ours))
for i, (a, b) in enumerate(zip(ours, theirs), 1):
    expect(a[0] == b[0] and selected(a[1]) == selected(b[1]),
           "subtask %d: score %d, %d tests" % (i, a[0], len(selected(a[1]))))
expect(sum(p[0] for p in ours) == 100, "total score 100")
print("RESULT:", "all checks passed" if not problems else "%d mismatches" % len(problems))
sys.exit(1 if problems else 0)
