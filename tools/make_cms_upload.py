#!/usr/bin/env python3
"""Build a package for adding a TPS task to CMS by hand, through AdminWebServer only
(no shell access to the CMS server, so cmsImportTask cannot be used).

usage (inside the task directory, after `tps gen`):
    python3 ../tools/make_cms_upload.py [statement.pdf]

It runs `tps export CMS 1` and produces <task>/cms-upload/ with:
    testcases-partN.zip      flat <codename>.in / <codename>.out, each < 70 MB (templates: *.in / *.out)
    managers/                grader.cpp, <task>.h, checker (static x86_64 binary, compiled here)
    attachments/<task>.zip   public package for contestants
    statement-fa.pdf         (if given)
    score_type_parameters.json   GroupMin parameters (anchored regexes)
    SETTINGS.md              every field to fill in the admin panel
Values mirror what CMS's own tps_task loader would set.
"""
import json, os, re, shutil, subprocess, sys, tempfile, zipfile

task_dir = os.getcwd()
if not os.path.isfile("problem.json"):
    sys.exit("run inside a TPS task directory")
pdf = sys.argv[1] if len(sys.argv) > 1 else None

out = os.path.join(task_dir, "cms-upload")
shutil.rmtree(out, ignore_errors=True)
tmp = tempfile.mkdtemp()
exp = os.path.join(tmp, "export")
subprocess.run(["tps", "export", "CMS", "1", "-a", "none", "-o", exp], check=True)

prob = json.load(open(os.path.join(exp, "problem.json")))
name = prob["code"]
os.makedirs(os.path.join(out, "managers"))
os.makedirs(os.path.join(out, "attachments"))

# managers
for f in os.listdir(os.path.join(exp, "graders")):
    shutil.copy(os.path.join(exp, "graders", f), os.path.join(out, "managers", f))
has_checker = os.path.isfile(os.path.join(exp, "checker", "checker.cpp"))
if has_checker:
    # same flags as CMS 1.5.1's tps loader
    subprocess.run(["g++", "-x", "c++", "-std=gnu++14", "-O2", "-static", "-o",
                    os.path.join(out, "managers", "checker"),
                    os.path.join(exp, "checker", "checker.cpp")], check=True)

# attachments
for f in os.listdir(os.path.join(exp, "attachments")):
    shutil.copy(os.path.join(exp, "attachments", f), os.path.join(out, "attachments", f))

# testcases: flat zips, each kept under ~70 MB (Tornado under AWS rejects bodies > 100 MB by default)
LIMIT = 70 * 1024 * 1024
tests = sorted(f[:-3] for f in os.listdir(os.path.join(exp, "tests")) if f.endswith(".in"))
parts, part, z = [], 0, None
for t in tests:
    if z is None or os.path.getsize(parts[-1]) > LIMIT:
        if z: z.close()
        part += 1
        parts.append(os.path.join(out, "testcases-part%d.zip" % part))
        z = zipfile.ZipFile(parts[-1], "w", zipfile.ZIP_DEFLATED)
    z.write(os.path.join(exp, "tests", t + ".in"), t + ".in")
    z.write(os.path.join(exp, "tests", t + ".out"), t + ".out")
    z.fp.flush()
z.close()

# GroupMin parameters (CMS uses regex.match, so anchor both ends)
params = []
for i, f in enumerate(sorted(os.listdir(os.path.join(exp, "subtasks")))):
    st = json.load(open(os.path.join(exp, "subtasks", f)))
    rx = "^(" + "|".join(re.escape(t) for t in st["testcases"]) + ")$"
    params.append([st["score"], rx])
json.dump(params, open(os.path.join(out, "score_type_parameters.json"), "w"))

if pdf:
    shutil.copy(pdf, os.path.join(out, "statement-fa.pdf"))

tt = json.loads(prob["task_type_params"])
compilation = tt.get("task_type_parameters_Batch_compilation", "alone")
mem_mib = prob["memory_limit"] // (1024 * 1024)
with open(os.path.join(out, "SETTINGS.md"), "w") as s:
    s.write(f"""# CMS admin settings for `{name}`

Task page (top part):
- Name: `{name}`
- Title: `{prob['name']}`
- Statement: language code `fa`, file `statement-fa.pdf`, then tick **Primary?**
- Attachments: upload `attachments/{name}.zip`
- Submission format: `{name}.%l`
- Feedback level: Full (or Restricted)
- Tokens: Disabled
- Maximum number of submissions: 50; Minimum interval between submissions: 60 (seconds)
- Score precision: {prob.get('score_precision', 2)}
- Score mode: **Use the sum over each subtask of the best result for that subtask across all submissions (IOI 2017-)**

Dataset part:
- Time limit: {prob['time_limit']} second(s); Memory limit: {mem_mib} MiB
- Task type: `{prob['task_type']}`
  - Compilation: {'Submissions are compiled with a grader' if compilation == 'grader' else 'Submissions are self-sufficient'}
  - I/O: input file and output file both **empty** (stdin/stdout)
  - Output evaluation: {'Outputs are compared by a comparator' if has_checker else 'Outputs compared with white diff'}
- Managers: upload every file in `managers/` ({', '.join(sorted(os.listdir(os.path.join(out, 'managers'))))})
- Score type: `GroupMin`
- Score type parameters: paste the content of `score_type_parameters.json`
- Testcases: "Add multiple testcases" once per archive: {', '.join(os.path.basename(p) for p in parts)},
  input template `*.in`, output template `*.out`, Public: untick (or tick only if you want full feedback on all)
  -> expect {len(tests)} testcases

Subtasks: {', '.join(f'{p[0]}' for p in params)} (total {sum(p[0] for p in params)})
""")
shutil.rmtree(tmp)
print("written", out)
