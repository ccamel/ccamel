#!/usr/bin/env python3
"""Add open issues and pull requests from personal, non-fork, non-archived repositories to Project 3."""

import json
import re
import subprocess
import sys


OWNER = "ccamel"


def gh(*args):
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode:
        # Actions logs are public, so do not print stderr or repository names.
        if args[:2] == ("api", "graphql") and any(arg.startswith("query=mutation") for arg in args):
            operation = "adding item"
        elif args[:2] == ("api", "graphql"):
            operation = "reading project"
        elif args[-1].startswith("/user/repos?"):
            operation = "listing repositories"
        else:
            operation = "listing repository items"
        status = re.search(r"\bHTTP [1-5]\d\d\b", result.stderr)
        if "required scopes" in result.stderr or "missing required scopes" in result.stderr:
            detail = "missing token scopes"
        elif status:
            detail = status.group()
        else:
            detail = "no HTTP status available"
        raise RuntimeError(f"{operation} failed: {detail} (exit {result.returncode})")
    return result.stdout


def pages(endpoint):
    return json.loads(gh("api", "--paginate", "--slurp", endpoint))


def sync():
    query = """query($endCursor: String) {
      user(login: "ccamel") {
        projectV2(number: 3) {
          id
          items(first: 100, after: $endCursor) {
            nodes { content { ... on Issue { id } ... on PullRequest { id } } }
            pageInfo { hasNextPage endCursor }
          }
        }
      }
    }"""
    project_pages = json.loads(gh("api", "graphql", "--paginate", "--slurp", "-f", f"query={query}"))
    project_id = project_pages[0]["data"]["user"]["projectV2"]["id"]
    existing = {
        node["content"]["id"]
        for page in project_pages
        for node in page["data"]["user"]["projectV2"]["items"]["nodes"]
        if node["content"] and node["content"].get("id")
    }
    repositories = pages("/user/repos?affiliation=owner&per_page=100")
    added = 0
    for page in repositories:
        for repo in page:
            if repo["owner"]["login"].lower() != OWNER or repo["fork"] or repo["archived"]:
                continue
            endpoints = ("issues", "pulls") if repo["has_issues"] else ("pulls",)
            for endpoint in endpoints:
                for item_page in pages(f"/repos/{repo['full_name']}/{endpoint}?state=open&per_page=100"):
                    for item in item_page:
                        if (endpoint == "issues" and "pull_request" in item) or item["node_id"] in existing:
                            continue
                        gh(
                            "api", "graphql", "-f",
                            "query=mutation($projectId: ID!, $contentId: ID!) {"
                            " addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId})"
                            " { item { id } } }",
                            "-f", f"projectId={project_id}", "-f", f"contentId={item['node_id']}",
                        )
                        existing.add(item["node_id"])
                        added += 1
    print(f"Added {added} issues and pull requests to the project.")


if __name__ == "__main__":
    try:
        sync()
    except (RuntimeError, KeyError, TypeError, ValueError) as error:
        print(f"Project synchronization failed: {error}", file=sys.stderr)
        sys.exit(1)
