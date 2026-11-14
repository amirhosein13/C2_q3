#!/usr/bin/env python3
"""Prepare a TPS task for manual upload through the CMS 1.5.1 admin panel (AdminWebServer).

Run inside a TPS task directory, after `tps gen`:
    python3 ../tools/cms_upload.py statement/<task>-fa.pdf

Output: <task>/cms-upload/
    managers/                  files to add as dataset managers
    testcases-partN.zip        flat <codename>.in / <codename>.out, each archive < 70 MB
    score_type_parameters.json GroupMin parameters [[score, "^(...)$"], ...]
    attachments/<task>.zip     public package (from `tps make-public`, via the exporter)
    statement-fa.pdf
    SETTINGS.md                value of every admin-panel field for this task

Facts taken from the CMS v1.5.1 sources (tag v1.5.1 of github.com/cms-dev/cms):
  - cms/grading/tasktypes/Batch.py: compilation "grader" compiles "grader.%l" plus every manager
    whose extension is a source/header of the language; the comparator must be a manager named
    exactly "checker"; it is run as `./checker input.txt res.txt <user output>` and must print
    the score on stdout and the message on stderr (cms/grading/steps/trusted.py).
  - cmscontrib/loaders/tps.py compiles checker.cpp with `g++ -x c++ -std=gnu++14 -O2 -static`.
  - cms/grading/scoretypes/abc.py (ScoreTypeGroup): parameters [[score, regex], ...];
    a testcase belongs to a subtask iff re.compile(regex).match(codename) -> anchor with ^(...)$.
  - cms/server/admin/handlers/dataset.py + cmscommon/importers.py: "Add multiple testcases"
    turns the templates into ^...(.*)...$ regexes over the zip member names (default
    templates are "input.*" / "output.*", so they must be changed to "*.in" / "*.out").
  - config/nginx.conf.sample: client_max_body_size 100M for /aws/ -> keep each zip < 70 MB.
Only Batch tasks are supported; other task types stop with an error.
"""
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import zipfile
import zlib

ZIP_LIMIT = 70 * 1000 * 1000  # below 70 MB in both decimal and binary units


def die(msg):
    sys.exit("error: " + msg)


def run(cmd, **kw):
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True, **kw)


def elf_info(path):
    """Return (is_x86_64_elf, is_static) by reading the ELF header and program headers."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:4] != b"\x7fELF" or data[4] != 2 or data[5] != 1:
        return False, False
    e_machine = struct.unpack_from("<H", data, 18)[0]
    e_phoff = struct.unpack_from("<Q", data, 32)[0]
    e_phentsize, e_phnum = struct.unpack_from("<HH", data, 54)
    has_interp = has_dynamic = False
    for i in range(e_phnum):
        p_type = struct.unpack_from("<I", data, e_phoff + i * e_phentsize)[0]
        has_interp |= p_type == 3   # PT_INTERP
        has_dynamic |= p_type == 2  # PT_DYNAMIC
    return e_machine == 62, not (has_interp or has_dynamic)


def deflated_size(path):
    """Size of the file inside a ZIP_DEFLATED archive (same settings as zipfile), plus header slack."""
    co = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -15)
    n = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            n += len(co.compress(chunk))
    return n + len(co.flush()) + 512


def main():
    if not os.path.isfile("problem.json"):
        die("run this inside a TPS task directory")
    pdf = sys.argv[1] if len(sys.argv) > 1 else None
    if pdf and not os.path.isfile(pdf):
        die("statement pdf not found: " + pdf)
    if not os.path.isfile(os.path.join("tests", "mapping")):
        die("tests/ not generated; run `tps gen` first")

    task_dir = os.getcwd()
    out = os.path.join(task_dir, "cms-upload")
    exp_name = ".cms-export-protocol1"
    exp = os.path.join(task_dir, exp_name)
    shutil.rmtree(out, ignore_errors=True)
    shutil.rmtree(exp, ignore_errors=True)
    # protocol 1: the only format the official tps_task loader of CMS 1.5.1 parses
    run(["tps", "export", "CMS", "1", "-a", "none", "-o", exp_name])

    prob = json.load(open(os.path.join(exp, "problem.json")))
    name = prob["code"]
    if prob["task_type"] != "Batch":
        die("task type %s is not supported by this script" % prob["task_type"])
    tt = json.loads(prob["task_type_params"] or "{}")
    with_grader = tt.get("task_type_parameters_Batch_compilation", "alone") == "grader"
    checker_src = os.path.join(exp, "checker", "checker.cpp")
    has_checker = os.path.isfile(checker_src)

    os.makedirs(os.path.join(out, "managers"))
    os.makedirs(os.path.join(out, "attachments"))

    # ---- managers
    managers = []
    if with_grader:
        for f in ("grader.cpp", name + ".h"):
            src = os.path.join(exp, "graders", f)
            if not os.path.isfile(src):
                die("missing grader file in export: " + f)
            shutil.copy(src, os.path.join(out, "managers", f))
            managers.append(f)
    if has_checker:
        # the exporter copies checker/*.cpp and *.h, so testlib.h sits next to checker.cpp
        run(["g++", "-x", "c++", "-std=gnu++14", "-O2", "-static",
             "-o", os.path.join(out, "managers", "checker"), checker_src])
        is64, static = elf_info(os.path.join(out, "managers", "checker"))
        if not (is64 and static):
            die("checker is not a static x86-64 ELF executable")
        managers.append("checker")

    # ---- attachments (public package) and secret leak check
    secrets = set()
    for f in os.listdir(os.path.join(exp, "graders")) if with_grader else []:
        secrets |= set(re.findall(r'"([A-Za-z0-9]{24,})"', open(os.path.join(exp, "graders", f)).read()))
    if has_checker:
        secrets |= set(re.findall(r'"([A-Za-z0-9]{24,})"', open(checker_src).read()))
    att_dir = os.path.join(exp, "attachments")
    attachments = sorted(os.listdir(att_dir)) if os.path.isdir(att_dir) else []
    for f in attachments:
        with zipfile.ZipFile(os.path.join(att_dir, f)) as z:
            for member in z.namelist():
                body = z.read(member)
                for s in secrets:
                    if s.encode() in body:
                        die("secret string leaks into attachment %s:%s" % (f, member))
                if b"BEGIN SECRET" in body or b"END SECRET" in body:
                    die("secret markers left in attachment %s:%s" % (f, member))
        shutil.copy(os.path.join(att_dir, f), os.path.join(out, "attachments", f))

    # ---- testcases, flat names, each archive below ZIP_LIMIT.
    # zip members are deflated independently, so the archive size is the sum of the members'
    # raw-deflate sizes plus per-member headers; compute it before choosing the split.
    tdir = os.path.join(exp, "tests")
    codenames = sorted(f[:-3] for f in os.listdir(tdir) if f.endswith(".in"))
    for c in codenames:
        if not os.path.isfile(os.path.join(tdir, c + ".out")):
            die("missing output for test " + c)
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", c):
            die("unexpected character in testcase codename " + c)
    parts, cur, cur_size = [], [], 0
    for c in codenames:
        sz = deflated_size(os.path.join(tdir, c + ".in")) + deflated_size(os.path.join(tdir, c + ".out"))
        if sz > ZIP_LIMIT:
            die("single test %s is larger than the archive limit" % c)
        if cur and cur_size + sz > ZIP_LIMIT:
            parts.append(cur)
            cur, cur_size = [], 0
        cur.append(c)
        cur_size += sz
    if cur:
        parts.append(cur)
    zips = []
    for i, part in enumerate(parts, 1):
        zp = os.path.join(out, "testcases-part%d.zip" % i)
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
            for c in part:
                z.write(os.path.join(tdir, c + ".in"), c + ".in")
                z.write(os.path.join(tdir, c + ".out"), c + ".out")
        if os.path.getsize(zp) >= ZIP_LIMIT:
            die("%s is not below the size limit" % zp)
        zips.append((os.path.basename(zp), len(part), os.path.getsize(zp)))

    # ---- GroupMin parameters, in subtask index order, verified like CMS does (re.match)
    subtasks = []
    for f in os.listdir(os.path.join(exp, "subtasks")):
        st = json.load(open(os.path.join(exp, "subtasks", f)))
        idx = int(f.split("-", 1)[0])
        subtasks.append((idx, f[:-5].split("-", 1)[1], st["score"], st["testcases"]))
    subtasks.sort()
    # CMS 1.5.1 labels subtasks by position ("Subtask 1", "Subtask 2", ... in
    # ScoreTypeGroup.compute_score), so a score-0 samples group would shift every label by one.
    # Leave score-0 groups out; their tests stay scored inside the subtasks that include them.
    dropped = [s for s in subtasks if s[2] == 0]
    subtasks = [s for s in subtasks if s[2] > 0]
    params = [[score, "^(" + "|".join(re.escape(t) for t in tests) + ")$"]
              for _, _, score, tests in subtasks]
    covered = set()
    for (_, sname, _, tests), (_, rx) in zip(subtasks, params):
        got = [c for c in codenames if re.compile(rx).match(c)]
        if sorted(got) != sorted(tests):
            die("regex of subtask %s does not select exactly its tests" % sname)
        covered |= set(got)
    if covered != set(codenames):
        die("tests not covered by any scored subtask: %s" % sorted(set(codenames) - covered))
    total = sum(p[0] for p in params)
    if total != 100:
        die("subtask scores sum to %s, not 100" % total)
    json.dump(params, open(os.path.join(out, "score_type_parameters.json"), "w"))

    if pdf:
        shutil.copy(pdf, os.path.join(out, "statement-fa.pdf"))

    write_settings(out, prob, name, with_grader, has_checker, managers, attachments,
                   zips, len(codenames), subtasks, dropped, bool(pdf))
    shutil.rmtree(exp)
    print("written", out)
    for z, n, size in zips:
        print("  %s: %d tests, %d bytes" % (z, n, size))


def write_settings(out, prob, name, with_grader, has_checker, managers, attachments,
                   zips, ntests, subtasks, dropped, has_pdf):
    mem = prob["memory_limit"] // 2**20
    L = []
    w = L.append
    w("# Admin-panel settings for `%s` (CMS 1.5.1)\n" % name)
    w("Field labels are copied from the CMS v1.5.1 admin templates.\n")
    w("## 1. Create the task")
    w("Tasks → create a new task → **Name**: `%s`.\n" % name)
    w("## 2. Task configuration (top of the task page)")
    w("| Field | Value |")
    w("|---|---|")
    w("| Name | `%s` |" % name)
    w("| Title | `%s` |" % prob["name"])
    if has_pdf:
        w("| Statements | [add] → Language code: `fa` → file `statement-fa.pdf` → Upload; then tick **Primary?** next to `fa` |")
    for a in attachments:
        w("| Attachments | [add] → `attachments/%s` |" % a)
    w("| Submission format | `%s.%%l` |" % name)
    w("| Feedback level | `Full` (or `Restricted` to show less) |")
    w("| Token mode | `Disabled` |")
    w("| Maximum number of submissions | `50` (your choice) |")
    w("| Maximum number of user tests | `50` (your choice) |")
    w("| Minimum interval between submissions | `60` seconds (your choice) |")
    w("| Minimum interval between user tests | `60` seconds (your choice) |")
    w("| Score decimal places | `%d` |" % prob.get("score_precision", 2))
    w("| Score mode | **Use the sum over each subtask of the best result for that subtask across all submissions (IOI 2017-)** (not the default) |")
    w("")
    w("## 3. Dataset configuration (the active dataset on the same page)")
    w("| Field | Value |")
    w("|---|---|")
    w("| Time limit | `%g` second(s) |" % prob["time_limit"])
    w("| Memory limit | `%d` MiB |" % mem)
    w("| Task type | `Batch` |")
    w("| Compilation | %s |" % ("Submissions are compiled with a grader" if with_grader else "Submissions are self-sufficient"))
    w("| I/O (blank for stdin/stdout): Input file | *(empty)* |")
    w("| I/O (blank for stdin/stdout): Output file | *(empty)* |")
    w("| Output evaluation | %s |" % ("Outputs are compared by a comparator" if has_checker else "Outputs compared with white diff"))
    w("| Managers | [add] once per file in `managers/`: %s (names must stay exactly like this) |"
      % ", ".join("`%s`" % m for m in managers))
    w("| Score Type | `GroupMin` |")
    w("| Score type parameters | paste the whole content of `score_type_parameters.json` |")
    w("")
    w("Then press **Update** at the bottom of the page.\n")
    w("## 4. Testcases")
    w("On the task page → **Add multiple testcases**, once per archive:\n")
    w("| Field | Value |")
    w("|---|---|")
    w("| Archive (a zip file containing files only) | %s |" % ", ".join("`%s`" % z[0] for z in zips))
    w("| Public | unticked |")
    w("| Overwrite existing testcases | unticked |")
    w("| Input file names template | `*.in` (default `input.*` is wrong) |")
    w("| Output file names template | `*.out` (default `output.*` is wrong) |")
    w("")
    w("Expected total: **%d testcases** (%s)." % (ntests, ", ".join("%s: %d" % (z[0], z[1]) for z in zips)))
    w("")
    w("## 5. Subtasks (GroupMin)")
    w("Order of steps: upload the testcases (section 4) before relying on these parameters;")
    w("CMS only checks that the parameters are valid JSON when saving, a regex that matches no")
    w("testcase fails later, at scoring time.\n")
    w("| label shown by CMS | statement subtask | TPS name | score | tests |")
    w("|---|---|---|---|---|")
    for k, (idx, sname, score, tests) in enumerate(subtasks, 1):
        w("| Subtask %d | %d | %s | %d | %d |" % (k, idx, sname, score, len(tests)))
    w("\nTotal: %d." % sum(s[2] for s in subtasks))
    for idx, sname, score, tests in dropped:
        w("\nThe score-0 group `%s` (%d tests) is not listed: CMS 1.5.1 numbers subtasks by position, "
          "so listing it would shift every label. Its tests are still evaluated inside the subtasks "
          "that include them." % (sname, len(tests)))
    w("\n## 6. Contest")
    w("Contest page → Tasks → add `%s`. Allowed languages: a C++ (g++) language only; the grader is C++." % name)
    open(os.path.join(out, "SETTINGS.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
