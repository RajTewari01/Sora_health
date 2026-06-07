# Mic-config.json Configuration

```json
{
    "ignorePatterns": [
        {
            "pattern": "^https://github.com/.*/(edit|new|upload)",
            "reason": "Ignore github url in readme docs <edit | new | upload> ",
            "type": "regex"
        },
        {
            "pattern": "^https?://\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}(\\?.*)?",
            "reason": "Ignore ip address in readme docs <http://[IP_ADDRESS]/>",
            "type": "regex"
        },
        {
            "pattern": "^https?://localhost(.*)?",
            "reason": "Ignore localhost url in readme docs <http://localhost(...)>",
            "type": "regex"
        }
    ],
    "replacementPatterns": [
        {
            "pattern": "^/docs/",
            "replacement": "https://github.com/RajTewari01/Sora_Health_System/tree/main/docs/"
        }
    ]
    ,
    "timeout": "10s",
    "retryOn429": true,
    "retryCount": 3,
    "aliveStatusCodes": [200, 206, 301, 302]
}
```
### Properties:

- **`ignorePatterns`**: 
  - **`^https://github.com/.*/(edit|new|upload)`**: Ignores GitHub URLs containing "edit", "new", or "upload". This is used to exclude links that point to GitHub's UI for editing, creating, or uploading files, as these are not actual external resources to be checked.
  - **`^https?://\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}(\\?.*)?`**: Ignores URLs that match an IPv4 address pattern (e.g., `http://[IP_ADDRESS]`). This is useful for skipping local IP addresses that might be referenced in documentation but are not valid public URLs.
  - **`^https?://localhost(.*)?`**: Ignores URLs starting with "localhost". This pattern is used to skip references to the local development server (e.g., `http://localhost:3000`).

- **`replacementPatterns`**: 
  - **`^/docs/`** with **`https://github.com/RajTewari01/Sora_Health_System/tree/main/docs/`**: This pattern replaces any occurrence of "/docs/" at the beginning of a string with the full URL to the docs directory on GitHub. This is likely used to ensure that local file paths within the documentation are converted to web-accessible URLs. From relative links to absolute links in markdown files.

- **`timeout`**: **`10s`** - Sets the timeout for HTTP requests to 10 seconds. If a resource does not respond within this time, the request is considered a failure.

- **`retryOn429`**: **`true`** - Enables automatic retries for HTTP requests that return a 429 "Too Many Requests" status code.

- **`retryCount`**: **`3`** - Specifies the maximum number of times to retry a failed request.

- **`aliveStatusCodes`**: **`[200, 206, 301, 302]`** - A list of HTTP status codes that are considered successful or "alive". These codes indicate that the resource is reachable and responding correctly. Any other status code will be treated as an error.

**How to Use**:
    - Add the `mic-config.json` file to your repository.
    - Configure the `ignorePatterns`, `replacementPatterns`, `timeout`, `retryOn429`, `retryCount`, and `aliveStatusCodes` as needed.
    - The `mic-config.json` file should be located in the directory of `./.github/mic-config.json`.

**Extra things which you should know**:

1. `httpHeaders (Passing Authentication)`
```json
"httpHeaders": [
  {
    "urls": ["https://internal-api.sorahealth.com"],
    "headers": {
      "Authorization": "Bearer YOUR_SECRET_TOKEN"
    }
  }
]
```
- If your documentation links to a private internal company server (like an internal Jira board or private Wiki), the bot won't be able to access it. You can actually give the bot a secret password/token to use!

2. `excludeFiles` (Skipping Folders)
```json
{
    "excludeFiles": [
        "docs/private-docs/",
        "docs/api-references/"
    ]
}
```
- If you have large folders of documentation (like API specs or legal docs) that change constantly or are just too big to check, you can tell the bot to completely ignore those folders.

3. `ignorePatterns (Skipping URLs)`
```json
{
  "pattern": "^https://api\\.example\\.com",
  "reason": "Ignore fake API documentation examples"
},
{
  "pattern": "^mailto:",
  "reason": "Don't try to validate email addresses"
}
```

#### File stucture:

```text
Sora_Health_System/
├── .github/
│   ├── workflows/
│   │   └── docs.yml
│   └── mic-config.json <-This is the file location for the configuration.
├── docs/
│   └── github/
│       └── mic-config.md
├── src/
│   ├── backend/
│   └── mobile/
└── README.md
```
- This shows the exact location of the `mic-config.json` file in the repository.
