#!/usr/bin/env python3
"""M1-2: fixed synthetic receipt triggered by owner-authored GitHub issue.

No dynamic code execution, commands from issues, OAuth export, or paid API.
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request

OWNER = "Mthamasia"
REPO = f"{OWNER}/mesa-m1-sandbox"
TITLE = "[MESA-LAB] M1-2: missão sintética automática"
CONTRACT = 'MESA-CODE-DEMO-V1\n{"task":"receipt_fixture_v1"}'
API = "https://api.github.com"


def api(method, path, payload=None):
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise RuntimeError("Missing scoped GitHub Actions token")
    data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode()
    request = urllib.request.Request(
        API + path, data=data, method=method,
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28",
                 "User-Agent": "mesa-m1-synthetic-v1",
                 **({"Content-Type": "application/json"} if data is not None else {})})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read()
            return json.loads(body.decode()) if body else {}
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"GitHub API {method} {path.split('?')[0]} returned HTTP {error.code}") from None


def verify(event):
    issue = event.get("issue", {})
    number = issue.get("number")
    if (os.environ.get("GITHUB_REPOSITORY") != REPO
            or os.environ.get("GITHUB_ACTOR") != OWNER
            or os.environ.get("GITHUB_EVENT_NAME") != "issues"
            or event.get("action") != "opened"
            or issue.get("user", {}).get("login") != OWNER
            or issue.get("title") != TITLE
            or (issue.get("body") or "").strip() != CONTRACT
            or type(number) is not int or not 1 <= number <= 999999):
        raise RuntimeError("Blocked: not an owner-authored, preapproved synthetic mission")
    return number


def set_output(branch, url, issue_number):
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as stream:
        stream.write(f"branch={branch}\npr_url={url}\n")
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as stream:
        stream.write(f"### MESA M1-2 | Issue #{issue_number}\n\nPR: {url}\n\n")
        stream.write("Template fixo, sem IA, sem API paga e sem acesso à VPS.\n")


def publish(number):
    branch = f"mesa/m1demo-{number}"
    source = f'''"""Synthetic receipt, no project/customer information."""


def mission_receipt():
    return {{"mission_id": "M1-DEMO-{number}", "kind": "synthetic", "validated": True}}
'''
    test = f'''"""Synthetic mission #{number} test cases."""
import unittest
from mesa_sandbox.m1demo_{number} import mission_receipt


class SyntheticMissionTests(unittest.TestCase):
    def test_id(self):
        self.assertEqual(mission_receipt()["mission_id"], "M1-DEMO-{number}")

    def test_properties(self):
        self.assertEqual(mission_receipt()["kind"], "synthetic")
        self.assertIs(mission_receipt()["validated"], True)


if __name__ == "__main__":
    unittest.main()
'''
    expected = [(f"mesa_sandbox/m1demo_{number}.py", source),
                (f"tests/test_m1demo_{number}.py", test)]
    # Stable branch, stable PR, no duplicates on rerun.
    existing = api("GET", f"/repos/{REPO}/pulls?state=all&head={OWNER}:{branch}&per_page=10")
    if existing:
        set_output(branch, existing[0]["html_url"], number)
        print(f"Reused existing PR #{existing[0]['number']}")
        return
    try:
        api("GET", f"/repos/{REPO}/git/ref/heads/{branch}")
        branch_exists = True
    except RuntimeError as exc:
        if not str(exc).endswith("HTTP 404"):
            raise
        branch_exists = False
    if not branch_exists:
        main = api("GET", f"/repos/{REPO}/git/ref/heads/main")
        api("POST", f"/repos/{REPO}/git/refs",
            {"ref": f"refs/heads/{branch}", "sha": main["object"]["sha"]})
    for path, data in expected:
        try:
            api("GET", f"/repos/{REPO}/contents/{path}?ref={branch}")
            continue
        except RuntimeError as exc:
            if not str(exc).endswith("HTTP 404"):
                raise
        api("PUT", f"/repos/{REPO}/contents/{path}", {
            "message": f"test(m1): fixed synthetic receipt for issue #{number}",
            "content": base64.b64encode(data.encode()).decode(),
            "branch": branch})
    pr = api("POST", f"/repos/{REPO}/pulls", {
        "title": f"MESA M1-2: recibo sintético automatizado #{number}",
        "head": branch, "base": "main", "draft": True,
        "body": f"Gerado pela missão #{number} com template FIXO, sem agente IA, "
                "sem credenciais de produção, API paga, VPS, merge ou deploy. "
                "A execução da Issue testa e audita em jobs separados de leitura."})
    set_output(branch, pr["html_url"], number)
    print(f"Opened draft PR #{pr['number']} from fixed template")


def main():
    with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as file:
        event = json.load(file)
    publish(verify(event))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        sys.exit(1)
