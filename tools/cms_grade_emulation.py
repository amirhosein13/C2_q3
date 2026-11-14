#!/usr/bin/env python3
"""Grade solutions the way CMS 1.5.1 grades this Batch+grader+comparator task, using only the
files of a cms-upload/ package (managers, testcase zips, score_type_parameters.json, SETTINGS.md).

  - compile: g++ -DEVAL -std=gnu++14 -O2 -pipe -static -s grader.cpp <task>.cpp  (the
    "C++14 / g++" language of CMS 1.5.1; headers among the managers are in the same directory)
  - run each test with stdin/stdout, wall-clock time limit and address-space limit from SETTINGS.md
    (no isolate sandbox: times are only indicative)
  - outcome: first stdout line of `./checker input correct_output user_output`
  - score: GroupMin over the regexes of score_type_parameters.json (min outcome x score)

usage: cms_grade_emulation.py <cms-upload-dir> <task-name> <solution.cpp>...
"""
import json
import os
import re
import resource
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

args = sys.argv[1:]
pkg, name, sols = args[0], args[1], [a for a in args[2:] if a.endswith(".cpp")]
settings = open(os.path.join(pkg, "SETTINGS.md")).read()
tl = float(re.search(r"\| Time limit \| `([0-9.]+)`", settings).group(1))
ml = int(re.search(r"\| Memory limit \| `(\d+)` MiB", settings).group(1))
params = json.load(open(os.path.join(pkg, "score_type_parameters.json")))

work = tempfile.mkdtemp(prefix="cms-emu-")
tests = os.path.join(work, "tests")
os.makedirs(tests)
for f in sorted(os.listdir(pkg)):
    if f.startswith("testcases-part") and f.endswith(".zip"):
        zipfile.ZipFile(os.path.join(pkg, f)).extractall(tests)
codenames = sorted(f[:-3] for f in os.listdir(tests) if f.endswith(".in"))


def limit():
    resource.setrlimit(resource.RLIMIT_AS, (ml * 2**20, ml * 2**20))
    resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))


print("TL %gs, ML %d MiB, %d tests, %d subtasks" % (tl, ml, len(codenames), len(params)))
for sol in sols:
    d = os.path.join(work, os.path.basename(sol)[:-4])
    os.makedirs(d)
    for m in os.listdir(os.path.join(pkg, "managers")):
        if m != "checker":
            shutil.copy(os.path.join(pkg, "managers", m), d)
    shutil.copy(sol, os.path.join(d, name + ".cpp"))
    c = subprocess.run(["g++", "-DEVAL", "-std=gnu++14", "-O2", "-pipe", "-static", "-s",
                        "-o", name, "grader.cpp", name + ".cpp"], cwd=d, capture_output=True)
    if c.returncode:
        print("%-28s COMPILATION FAILED" % os.path.basename(sol))
        continue
    outcome, worst = {}, 0.0
    for t in codenames:
        out = os.path.join(d, "out")
        with open(os.path.join(tests, t + ".in")) as fin, open(out, "w") as fout:
            try:
                st = time.time()
                r = subprocess.run(["./" + name], cwd=d, stdin=fin, stdout=fout,
                                   stderr=subprocess.DEVNULL, timeout=tl, preexec_fn=limit)
                worst = max(worst, time.time() - st)
                ok = r.returncode == 0
            except subprocess.TimeoutExpired:
                ok = False
        if not ok:
            outcome[t] = 0.0
            continue
        chk = subprocess.run([os.path.join(os.path.abspath(pkg), "managers", "checker"),
                              os.path.join(tests, t + ".in"), os.path.join(tests, t + ".out"), out],
                             capture_output=True, text=True)
        outcome[t] = float(chk.stdout.split("\n")[0])
    parts = []
    for score, rx in params:
        target = [t for t in codenames if re.compile(rx).match(t)]
        parts.append(score * min(outcome[t] for t in target))
    print("%-28s total %5g   subtasks %s   max time of passed runs %.2fs"
          % (os.path.basename(sol), sum(parts), " ".join("%g" % p for p in parts), worst))
shutil.rmtree(work)
