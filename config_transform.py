import json
import shlex
from urllib.parse import parse_qs, urlparse


def _safe_json_loads(text):
    try:
        return json.loads(text)
    except Exception:
        return None


def _parse_cookie_string(cookie_text):
    cookies = {}
    for part in cookie_text.split(';'):
        item = part.strip()
        if not item or '=' not in item:
            continue
        k, v = item.split('=', 1)
        cookies[k.strip()] = v.strip()
    return cookies


def parse_curl_bash(curl_bash_text):
    """Parse browser copied curl(bash) text to url/headers/cookies/data."""
    if not curl_bash_text or not curl_bash_text.strip():
        return {}, {}, None, None

    normalized = (
        curl_bash_text
        .replace('\\\r\n', ' ')
        .replace('\\\n', ' ')
        .strip()
    )

    try:
        tokens = shlex.split(normalized, posix=True)
    except ValueError:
        return {}, {}, None, None

    if not tokens or tokens[0] != 'curl':
        return {}, {}, None, None

    headers = {}
    cookies = {}
    url = None
    data_raw = None

    i = 1
    while i < len(tokens):
        token = tokens[i]

        if token in ('-H', '--header') and i + 1 < len(tokens):
            header_line = tokens[i + 1]
            if ':' in header_line:
                key, value = header_line.split(':', 1)
                key = key.strip()
                value = value.strip()
                if key.lower() == 'cookie':
                    cookies.update(_parse_cookie_string(value))
                else:
                    headers[key] = value
            i += 2
            continue

        if token in ('-b', '--cookie') and i + 1 < len(tokens):
            cookies.update(_parse_cookie_string(tokens[i + 1]))
            i += 2
            continue

        if token in ('--data-raw', '--data', '--data-binary', '-d') and i + 1 < len(tokens):
            data_raw = tokens[i + 1]
            i += 2
            continue

        if not token.startswith('-') and url is None:
            url = token

        i += 1

    return headers, cookies, url, data_raw


def parse_sign_cid_from_url(url):
    if not url:
        return None, None

    parsed = urlparse(url)
    qs = parse_qs(parsed.query)

    sign = qs.get('sign', [None])[0]
    cid = qs.get('cid', [None])[0]

    parts = [x for x in parsed.path.split('/') if x]

    # /learn/space/{sign}/{sign}/{cid}/video/{video_id}
    # /learn/{sign}/{sign}/{cid}/video/{video_id}
    if 'learn' in parts:
        idx = parts.index('learn')
        tail = parts[idx + 1 :]
        if tail and tail[0] == 'space':
            tail = tail[1:]

        if len(tail) >= 3:
            sign = sign or tail[0]
            cid = cid or tail[2]

    return sign, cid


def parse_video_id_from_url(url):
    if not url:
        return None

    parsed = urlparse(url)
    parts = [x for x in parsed.path.split('/') if x]
    if 'video' in parts:
        vid_idx = parts.index('video')
        if vid_idx + 1 < len(parts):
            v = parts[vid_idx + 1]
            if v.isdigit():
                return int(v)
    return None


def parse_heartbeat_payload(payload):
    """Accept json string/dict/list and extract d,u,c,skuid,cc."""
    if payload is None or payload == '':
        return {}

    obj = payload
    if isinstance(payload, str):
        obj = _safe_json_loads(payload.strip())
        if obj is None:
            return {}

    event = None
    events = None
    if isinstance(obj, dict):
        if 'heart_data' in obj and isinstance(obj['heart_data'], list) and obj['heart_data']:
            events = [x for x in obj['heart_data'] if isinstance(x, dict)]
            if events:
                event = events[0]
        else:
            event = obj
    elif isinstance(obj, list) and obj:
        events = [x for x in obj if isinstance(x, dict)]
        if events:
            event = events[0]

    if not isinstance(event, dict):
        return {}

    result = {}
    for key in ('d', 'u', 'c', 'skuid', 'cc', 'classroomid'):
        if key in event:
            result[key] = event[key]

    # heart_data 往往包含多条事件，首条可能是 loadstart 且 d=0。
    # 这里提取最大 d，避免把默认时长错误识别为 0。
    if events:
        d_values = []
        for item in events:
            val = item.get('d')
            try:
                d_values.append(float(val))
            except (TypeError, ValueError):
                continue
        if d_values:
            result['d'] = max(d_values)

    return result


def parse_heartbeat_from_curl(curl_bash_text):
    if not curl_bash_text or not curl_bash_text.strip():
        return {}, {}, None

    headers, cookies, url, data_raw = parse_curl_bash(curl_bash_text)
    payload = {}
    if data_raw:
        payload = parse_heartbeat_payload(data_raw)
    return headers, cookies, payload


def build_runtime_config(
    curl_bash_text='',
    heartbeat_curl='',
    start_video_url='',
    end_video_url='',
    default_headers=None,
    default_cookies=None,
    default_sign='',
    default_cid='',
    default_video_start=0,
    default_video_end=0,
    default_d=3000,
    default_u=0,
    default_c=0,
    default_skuid=0,
    default_cc='',
):
    headers = dict(default_headers or {})
    cookies = dict(default_cookies or {})

    sign = str(default_sign) if default_sign is not None else ''
    cid = str(default_cid) if default_cid is not None else ''
    video_start = int(default_video_start) if default_video_start else 0
    video_end = int(default_video_end) if default_video_end else 0

    d = int(default_d) if default_d is not None else 3000
    u = int(default_u) if default_u is not None else 0
    c = int(default_c) if default_c is not None else 0
    skuid = int(default_skuid) if default_skuid is not None else 0
    cc = str(default_cc) if default_cc is not None else ''

    curl_headers, curl_cookies, curl_url, _ = parse_curl_bash(curl_bash_text)
    if curl_headers:
        headers = curl_headers
    if curl_cookies:
        cookies = curl_cookies

    sign1, cid1 = parse_sign_cid_from_url(curl_url)
    if sign1:
        sign = sign1
    if cid1:
        cid = str(cid1)

    hb_headers, hb_cookies, hb = parse_heartbeat_from_curl(heartbeat_curl)
    if hb_headers:
        headers = hb_headers
    if hb_cookies:
        cookies = hb_cookies
    if 'd' in hb:
        # heartbeat 样本通常来自某一个视频，时长可能偏小；
        # 保留默认 d 作为下限，避免长视频只推进一部分进度。
        try:
            parsed_d = int(float(hb['d']))
            d = max(d, parsed_d)
        except (TypeError, ValueError):
            pass
    if 'u' in hb:
        u = int(hb['u'])
    if 'c' in hb:
        c = int(hb['c'])
    if 'skuid' in hb:
        skuid = int(hb['skuid'])
    if 'cc' in hb:
        cc = str(hb['cc'])
    if 'classroomid' in hb and not cid:
        cid = str(hb['classroomid'])

    sign2, cid2 = parse_sign_cid_from_url(start_video_url)
    if sign2:
        sign = sign2
    if cid2:
        cid = str(cid2)

    video_id = parse_video_id_from_url(start_video_url)
    if video_id:
        video_start = video_id
        if not video_end:
            video_end = video_id

    sign3, cid3 = parse_sign_cid_from_url(end_video_url)
    if sign3:
        sign = sign3
    if cid3:
        cid = str(cid3)

    video_id_end = parse_video_id_from_url(end_video_url)
    if video_id_end:
        video_end = video_id_end

    return {
        'headers': headers,
        'cookies': cookies,
        'sign': sign,
        'cid': cid,
        'video_start': video_start,
        'video_end': video_end,
        'd': d,
        'u': u,
        'c': c,
        'skuid': skuid,
        'cc': cc,
    }
