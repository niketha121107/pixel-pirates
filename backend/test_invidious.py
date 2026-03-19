import requests

# Try Piped instances
piped_instances = [
    'https://pipedapi.kavin.rocks',
    'https://pipedapi.adminforge.de',
    'https://api.piped.projectsegfau.lt',
    'https://pipedapi.in.projectsegfau.lt',
    'https://watchapi.whatever.social',
    'https://pipedapi.leptons.xyz',
]
for inst in piped_instances:
    try:
        r = requests.get(f'{inst}/search', params={'q': 'Python tutorial programming', 'filter': 'videos'}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            items = data.get('items', [])
            if items:
                first = items[0]
                url = first.get('url', '')
                vid_id = url.split('=')[-1] if '=' in url else url.split('/')[-1]
                print(f'OK: {inst} - {len(items)} results, first: {vid_id} - {first.get("title", "")[:50]}')
            else:
                print(f'EMPTY: {inst}')
        else:
            print(f'FAIL: {inst} - HTTP {r.status_code}')
    except Exception as e:
        print(f'ERR: {inst} - {str(e)[:80]}')
