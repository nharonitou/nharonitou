"""Check the same token used by the cards; log scopes and aggregates only."""

import datetime
import json
import os
import urllib.error
import urllib.request


def request(path, payload=None):
    token = os.environ['CARDS_TOKEN']
    req = urllib.request.Request(
        'https://api.github.com/' + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={
            'Authorization': 'Bearer ' + token,
            'Accept': 'application/vnd.github+json',
            'Content-Type': 'application/json',
            'User-Agent': 'profile-card-access-check',
        },
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response), response.headers


def main():
    if not os.environ.get('CARDS_TOKEN'):
        raise SystemExit('::error::Add CARDS_TOKEN to this repository\'s Actions secrets.')
    user, headers = request('user')
    expected = os.environ['GITHUB_REPOSITORY_OWNER']
    if user['login'].lower() != expected.lower():
        raise SystemExit('::error::CARDS_TOKEN must belong to the profile repository owner.')
    scopes = {s.strip() for s in headers.get('X-OAuth-Scopes', '').split(',') if s.strip()}
    print('CARDS_TOKEN scopes: ' + ', '.join(sorted(scopes)))
    missing = []
    if 'repo' not in scopes:
        missing.append('repo')
    if not scopes.intersection({'read:user', 'user'}):
        missing.append('read:user')
    if not scopes.intersection({'read:org', 'write:org', 'admin:org'}):
        missing.append('read:org')
    if missing:
        raise SystemExit('::error::Use a classic token with these missing scopes: ' + ', '.join(missing))

    year = datetime.datetime.now(datetime.timezone.utc).year
    windows = []
    for y in range(int(user['created_at'][:4]), year + 1):
        end = f', to: "{y}-12-31T23:59:59Z"' if y < year else ''
        windows.append(f'''y{y}: contributionsCollection(from: "{y}-01-01T00:00:00Z"{end}) {{
          restrictedContributionsCount
          commitContributionsByRepository(maxRepositories: 100) {{
            contributions {{ totalCount }}
            repository {{ languages(first: 20) {{ edges {{ size node {{ name }} }} }} }}
          }}
        }}''')
    result, _ = request('graphql', {'query': 'query { viewer { ' + ' '.join(windows) + ' } }'})
    if result.get('errors'):
        # GraphQL error messages can name private repositories. Do not publish them.
        raise SystemExit('::error::GitHub refused part of the language query. Check organization access and token SSO authorization.')
    scores = {}
    restricted = 0
    entries = 0
    for window in result['data']['viewer'].values():
        restricted += window['restrictedContributionsCount']
        for item in window['commitContributionsByRepository']:
            repo = item['repository']
            if not repo:
                continue
            entries += 1
            languages = repo['languages']['edges']
            size = sum(lang['size'] for lang in languages)
            if not size:
                continue
            for lang in languages:
                name = lang['node']['name']
                scores[name] = scores.get(name, 0) + item['contributions']['totalCount'] * lang['size'] / size
    print(f'Visible repository/year entries: {entries}; restricted contributions: {restricted}')
    total = sum(scores.values())
    for name, score in sorted(scores.items(), key=lambda pair: -pair[1]):
        print(f'{name}: {100 * score / total:.3f}%')
    if restricted or len(scores) <= 1:
        print('::warning::Language coverage may be incomplete. Check token access to organization repositories, SSO authorization, commit email attribution, and GitHub language detection.')


if __name__ == '__main__':
    try:
        main()
    except urllib.error.HTTPError as error:
        raise SystemExit(f'::error::GitHub access check failed (HTTP {error.code}). Check CARDS_TOKEN validity and organization access.') from None
