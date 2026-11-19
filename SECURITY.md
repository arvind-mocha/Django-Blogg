# Security review

Reviewed on November 19, 2026. This covers the repository code, configuration,
dependencies, and local container behavior; a deployed host/proxy was not audited.

| Finding | Resolution |
| --- | --- |
| A committed SQLite database contains 5 accounts and 54 posts; profile uploads and logs were also tracked | Removed these files from the current tree and published branch history; excluded them from future Git commits and image builds. Local copies are preserved. Cached or cloned copies still require follow-up; see below. |
| Django 3.1 and 2020-era dependencies | Upgraded to Django 5.2.19 LTS and current pinned dependencies; removed the unused AWS SDK/storage dependencies. The current requirements audit reported no known vulnerabilities. |
| Configuration depended on an old host and S3 credentials | Explicit environment configuration, local persistent media storage, no embedded secret or deployment hostname. Startup rejects missing/weak secrets and wildcard hosts. |
| Missing production transport settings | HTTPS redirects, secure cookies, HSTS, MIME-sniffing protection, frame denial, and same-origin referrer policy; explicitly relaxed settings only in the local example. |
| Unbounded profile images and client-provided names/metadata | Accept only JPEG/PNG/WebP, at most 5 MB and 16 million pixels; resize to 512 pixels, reencode to JPEG, strip metadata, and generate filenames. |
| Media unavailable with debug disabled; broad media serving is inappropriate | Serve only images referenced by profiles, with a fixed image MIME type, `nosniff`, and a sandbox policy. No generic directory/file endpoint. |
| Unquoted profile image attribute | Quoted the URL and use a static fallback avatar; personal media is no longer required for a new installation. |
| Logout link used GET | CSRF-protected POST form compatible with modern Django. |
| Legacy jQuery/Popper/Bootstrap JavaScript | Removed all three scripts; use a small local navigation script. Bootstrap CSS is vendored with its MIT license. |
| Public authentication endpoints have no application-level rate limit | Added an Nginx deployment example with authentication/general rate limits and upload limits. Operators must install these controls for public hosting. |
| Request URLs can disclose password-reset tokens in logs | Gunicorn logs method/status/duration only; the Nginx example also omits paths and query strings. Console email remains local-only configuration. |

Post update/delete views already enforce authentication and ownership. Tests now
verify those boundaries, CSRF, escaped content, registration/login/logout,
password reset, and media validation/serving. The container runs as a non-root
user with dropped capabilities and excludes `.env`, Git metadata, the old
database, uploads, logs, IDE files, and Python bytecode.

## Previously published data

Deleting a file in a new commit does **not** erase it from old commits, GitHub
caches, forks, or existing clones. The historical database includes password
hashes and account information. Treat those users' old passwords as compromised;
reset them on any live deployment, invalidate old sessions, and advise users
against reusing those passwords. Never publish a backup of the old database.

The settings-history pattern scan did not detect literal secret-key assignments,
literal email passwords, or AWS access-key identifiers. This is not proof that
all historical blobs are free of credentials. Rotate any credential known or
suspected to have been published, and generate a fresh signing key for a new
deployment.

With the owner's approval, `master` history was rewritten with `git-filter-repo`
and updated using a protected force push. The purge removed 55 private or
generated paths: databases, uploads, logs, bytecode, and IDE files. Verification
found no matching paths in the rewritten branch history, and the latest
application tree was identical before and after the rewrite. The local branch
was aligned and its old branch reflogs expired. Local data files were preserved.

**GitHub still serves a cached historical database URL. GitHub Support must remove
these cached references.** A private request draft and cleanup metadata are saved
in the ignored `backups/` directory of the working copy. Submit the draft through
[GitHub Support](https://support.github.com/) and follow their sensitive-data
removal process; a force push alone cannot remove these caches. Existing clones
must be replaced or carefully cleaned before further pushes so old data is not
reintroduced. Copies held by other people cannot be recalled.

## Operational requirements

- Keep `.env`, SMTP credentials, database volumes, backups, and console-email
  logs private. SMTP is required before enabling public password resets.
- Terminate HTTPS at a trusted proxy and keep the application port private.
  Only enable forwarded-header trust when the proxy overwrites incoming headers.
- Install the example proxy's request limits or equivalents. The application
  does not prevent sustained distributed login/registration abuse by itself.
- Profile pictures and blog posts are public. Do not upload private documents.
- Audit dependencies regularly and rebuild the base image. A successful Python
  dependency audit does not certify operating-system packages or future advisories.

References: [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/),
[Django upload security](https://docs.djangoproject.com/en/5.2/topics/security/#user-uploaded-content-security),
and [the Django 5.2.19 security release](https://www.djangoproject.com/weblog/2026/nov/03/security-releases/).
Historical cleanup guidance: [GitHub sensitive-data removal](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).
