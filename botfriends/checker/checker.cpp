// Checker for "botfriends" (CMS comparator protocol via TPS testlib:
// score on stdout, verdict + message on stderr, exit code 0).
//
// The contestant only reports a number (no certificate), so any value that
// differs from the jury's optimum is wrong -- including values below it:
// a smaller number without a plan to back it up cannot be "better".
#include "testlib.h"
#include <climits>
using namespace std;

const string output_secret = "t0Q7DJE3ZUUOPkegH41vFhj7WvbBJnJu";

int main(int argc, char* argv[]) {
	registerChecker("botfriends", argc, argv);
	// Line 1: secret (ouf mismatch -> Protocol Violation, i.e. 0 points).
	readBothSecrets(output_secret);
	// Line 2: grader status. The judge answer must say "OK"; for the
	// contestant output anything other than "OK" is a wrong answer.
	ans.readGraderResult();
	string status = ouf.readWord();
	if (status != "OK")
		quitf(_wa, "unexpected grader status '%s'", compress(status).c_str());
	ouf.eoln();

	// Line 3: the answer. Any parse error / out-of-range token on ouf -> WA.
	long long jury = ans.readLong(LLONG_MIN, LLONG_MAX, "jury answer");
	long long contestant = ouf.readLong(LLONG_MIN, LLONG_MAX, "answer");

	if (contestant != jury)
		quitf(_wa, "expected %lld, found %lld", jury, contestant);
	// quitf(_ok) also rejects any extra non-whitespace content in ouf.
	quitf(_ok, "answer is %lld", jury);
}
