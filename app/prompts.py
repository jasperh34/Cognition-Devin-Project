#Prompt builder using issue keys (repo_url, issue_url, title, body)
#(Consulted ChatGPT for advice on how to build the best prompt)

def build_prompt(issue):
    return f"""
    You are working on this GitHub repository:
    {issue["repo_url"]}

    Remediate this GitHub issue:
    {issue["issue_url"]}

    Issue #{issue["issue_number"]}: {issue["title"]}

    Issue description:
    {issue["body"]}

    Criteria:
    - Create a new branch.
    - Make the smallest safe change that resolves the issue.
    - Add or update tests if appropriate.
    - Run the relevant targeted tests.
    - Open a pull request against the repository's main branch.
    - In the PR description, include:
        - summary of changes
        - tests run
        - assumptions or follow-up risks
    - Comment on the issue with the PR link if possible.

    Constraints:
    - Do not make broad unrelated refactors.
    - If blocked by permissions, missing context, or failing setup, explain exactly what is needed.
    """