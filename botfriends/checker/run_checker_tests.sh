#!/bin/bash
# Runs checker.exe on hand-made outputs for sample 01 (answer 12).
# Expected verdict is the file-name prefix: ok_ -> score 1, wa_ -> 0 "Output isn't correct",
# pv_ -> 0 "Protocol Violation". Run "make" in this directory first.
set -euo pipefail
cd "$(dirname "$0")"
in=../public/examples/01.in
ans=$(mktemp)
printf 't0Q7DJE3ZUUOPkegH41vFhj7WvbBJnJu\nOK\n12\n' > "${ans}"
fail=0
for f in tests/*.out; do
	n=$(basename "${f}" .out)
	err=$(mktemp)
	score=$(./checker.exe "${in}" "${ans}" "${f}" 2> "${err}")
	verdict=$(head -1 "${err}")
	case "${n}" in
		ok_*) want_score=1; want="Output is correct";;
		wa_*) want_score=0; want="Output isn't correct";;
		pv_*) want_score=0; want="Protocol Violation";;
		*) echo "unknown prefix: ${n}"; exit 2;;
	esac
	if [ "${score}" == "${want_score}" ] && [ "${verdict}" == "${want}" ]; then res=PASS; else res=FAIL; fail=1; fi
	printf "%-5s %-22s score=%s  %s | %s\n" "${res}" "${n}" "${score}" "${verdict}" "$(sed -n 2p "${err}")"
	rm -f "${err}"
done
rm -f "${ans}"
exit "${fail}"
