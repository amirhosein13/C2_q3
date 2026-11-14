#!/usr/bin/env python3
"""Dry-run of CMS's real TPS loader (cmscontrib/loaders/tps.py) on an exported task directory,
without a database: the cms.* modules it imports are replaced by small recording stubs.
It checks what cmsImportTask -L tps_task would build (task type parameters, managers incl.
checker compilation, testcases, GroupMin subtasks).  This is NOT a full CMS import test.

usage: cms_loader_dryrun.py <path-to-cms-checkout> <exported-task-dir>
"""
import importlib.util, json, sys, types

cms_src, task_dir = sys.argv[1], sys.argv[2]

class Rec:
    def __init__(self, *a, **k): self.args, self.kw = a, k

def stub(name, **attrs):
    m = types.ModuleType(name); m.__dict__.update(attrs); sys.modules[name] = m; return m

stub("cms", FEEDBACK_LEVEL_FULL="full", FEEDBACK_LEVEL_RESTRICTED="restricted",
     FEEDBACK_LEVEL_OI_RESTRICTED="oi_restricted")
stub("cms.db", **{n: type(n, (Rec,), {}) for n in
                  ["Task", "Dataset", "Manager", "Testcase", "Attachment", "Statement"]})
stub("cmscommon"); stub("cmscommon.constants", SCORE_MODE_MAX_SUBTASK="max_subtask")
stub("cmscontrib"); stub("cmscontrib.loaders")
base = types.ModuleType("cmscontrib.loaders.base_loader")
class TaskLoader:
    def __init__(self, path, file_cacher): self.path, self.file_cacher = path, file_cacher
base.TaskLoader = TaskLoader; sys.modules["cmscontrib.loaders.base_loader"] = base

spec = importlib.util.spec_from_file_location("cmscontrib.loaders.tps", cms_src + "/cmscontrib/loaders/tps.py")
tps = importlib.util.module_from_spec(spec); spec.loader.exec_module(tps)

class FC:
    def put_file_from_path(self, p, d): return "sha:" + p
    def put_file_content(self, c, d): return "sha:content"

loader = tps.TpsTaskLoader(task_dir, FC())
assert tps.TpsTaskLoader.detect(task_dir), "detect() failed"
task = loader.get_task(get_statement=True)
assert task is not None, "loader returned None"
ds = task.active_dataset.kw
print("task name/title:", task.kw["name"], "/", task.kw["title"])
print("statements:", sorted(task.kw.get("statements", {})))
print("attachments:", sorted(task.kw["attachments"]))
print("submission_format:", task.kw["submission_format"])
print("task_type:", ds["task_type"], ds["task_type_parameters"])
print("time/memory:", ds["time_limit"], ds["memory_limit"], "bytes")
print("managers:", sorted(ds["managers"]))
print("testcases:", len(ds["testcases"]))
print("score_type:", ds["score_type"])
for st in ds["score_type_parameters"]:
    print("   score", st[0], "| #tests", len(st[1].split("|")), "|", st[2] if len(st) > 2 else "")
print("total score:", sum(st[0] for st in ds["score_type_parameters"]))
