# Alerting and Notifications Workflow

The `alerting.yml` workflow acts as the central observability and notification engine for the entire CI/CD pipeline. 

Instead of adding notification logic to every single workflow, we use a **fan-in** architecture via the `workflow_run` trigger. This allows a single, unified alerting workflow to listen for the completion of all other pipelines and route the results to Slack and Jira.

## 1. Trigger Architecture: `workflow_run`

```yaml
on:
  workflow_run:
    workflows: 
      - "Docs checker -- documentation quality and completeness"
      - "Lints checker -- code quality and file hygiene"
      - "Security Checks"
    types: [completed]
    branches: ["main", "master"]
```

> [!TIP]
> **Why `workflow_run`?** 
> Decoupling notifications keeps your core workflows (Lints, Docs, Security) clean and focused strictly on validation. It also prevents duplicate notification code across multiple files.

## 2. Slack Integration (Success & Failure)

The workflow contains two separate jobs for Slack notifications: one for success, and one for failure. Both rely on a standard `curl` POST request to a Slack Webhook.

```yaml
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    # ...
    run: |
      curl -X POST -H 'Content-type: application/json' \
        --data '{
          "text": "🚨 *${{ github.event.workflow_run.name }}* failed!\nBranch: `${{ github.event.workflow_run.head_branch }}`\nAuthor: ${{ github.event.workflow_run.actor.login }}"
        }' \
        ${{ secrets.SLACK_WEBHOOK_URL }}
```

**Key Features:**
- **Dynamic Context**: It extracts the exact name of the failed pipeline (`workflow_run.name`), the branch, and the author who broke the build.
- **Visual Cues**: Uses emojis (🚨 for failure, ✅ for success) for rapid visual parsing in the Slack channel.

## 3. Automated Jira Ticketing (Pure API Approach)

When a CI pipeline fails, we want an immediate, trackable bug ticket created on the Jira board. 

Initially, this was attempted using Atlassian's official GitHub Actions (`gajira-login` and `gajira-create`). However, those actions suffer from known compatibility issues with newer Jira **Team-managed** projects, often failing silently with a generic `Failed to create issue` error.

To ensure 100% reliability and capture explicit API error messages, we utilize a **pure `curl` implementation** directly against the Jira v2 REST API.

### The Curl Implementation

```yaml
    steps:
      - name: "Create Jira Issue via API"
        run: |
          curl --request POST \
            --url "${{ secrets.JIRA_BASE_URL }}/rest/api/2/issue" \
            --user "${{ secrets.JIRA_USER_EMAIL }}:${{ secrets.JIRA_API_TOKEN }}" \
            --header 'Accept: application/json' \
            --header 'Content-Type: application/json' \
            --data '{
            "fields": {
              "project": {
                "key": "SHM"
              },
              "summary": "CI Failed: ${{ github.event.workflow_run.name }}",
              "description": "Pipeline *${{ github.event.workflow_run.name }}* failed.\nBranch: ${{ github.event.workflow_run.head_branch }}\nAuthor: ${{ github.event.workflow_run.actor.login }}\nRun: ${{ github.event.workflow_run.html_url }}",
              "issuetype": {
                "name": "Task"
              }
            }
          }'
```

### Breakdown of the API Request

> [!IMPORTANT]
> **Authentication Secrets Required**
> 1. `JIRA_BASE_URL`: Must include the protocol, e.g., `https://sorahealthmanagement.atlassian.net`
> 2. `JIRA_USER_EMAIL`: The Atlassian account email address.
> 3. `JIRA_API_TOKEN`: Generated via Atlassian account security settings.

1. **Authentication (`--user`)**: Jira uses Basic Auth consisting of your email and API token separated by a colon. `curl` handles the base64 encoding automatically.
2. **Project Key (`SHM`)**: This targets the specific board. It must be the exact short-code used in Jira (e.g., `SHM-1`).
3. **Issue Type (`Task`)**: Team-managed projects typically default to `Task` rather than `Bug`. If you change your board configuration, this value must exactly match an available issue type.
4. **Summary**: The title of the ticket, injected dynamically with the name of the workflow that failed.
5. **Description**: A multi-line breakdown providing the developer with context, including the branch, the author, and a direct `html_url` link back to the failed GitHub Actions log.

> [!NOTE]
> **Why pure `curl` is better here:**
> If a required field is missing or an issue type is invalid, the Jira REST API returns a detailed JSON object explaining exactly what went wrong (e.g., `{"errors":{"issuetype":"issue type is invalid"}}`), whereas the action wrapper obscures this data.
