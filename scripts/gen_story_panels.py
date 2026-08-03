#!/usr/bin/env python3
"""Generate story panels for the Pokébola story arc via gemini-3.1-flash-image.
Character references passed as inline images; prompts use visual descriptions
ONLY — no character names (per user instruction). Skip-if-exists + retry."""
import base64, json, os, sys, time, urllib.request

KEY = None
for line in open(os.path.expanduser('~/.hermes/.env')):
    if line.startswith('GEMINI_API_KEY='):
        KEY = line.strip().split('=', 1)[1]
assert KEY, 'GEMINI_API_KEY not found'

MODEL = 'gemini-3.1-flash-image'
URL = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}'
ASSETS = os.path.join(os.path.dirname(__file__), '..', 'assets')

GUARD = ('No text, no words, no letters, no speech bubbles, no sound-effect words. '
         'Colorful children\'s book illustration, soft cartoon style, warm friendly lighting.')
HERO = ('the small yellow mouse-like creature from the reference image '
        '(round body, long ears with black tips, red cheeks, lightning-bolt shaped tail)')
CAT = ('the cream-colored cat-like creature from the reference image '
       '(walks upright on two legs, curly whiskers, big eyes)')
WOMAN = ('the tall woman from the reference image '
         '(very long magenta hair, white uniform with a red letter-free front, white boots)')

PANELS = [
    ('story_intro.png', [ 'pikachu.png', 'meowth.png', 'jessie.png' ],
     f'Night scene in a small cozy village with little houses and warm windows. '
     f'Two sneaky cartoon thieves tiptoeing away down a path carrying a big brown sack, '
     f'red-and-white round balls spilling out of the sack onto the path: {CAT} and {WOMAN}. '
     f'In the foreground {HERO} hides behind a bush, watching them with a worried but cute '
     f'expression, NOT terrified. The thieves look sneaky and funny, NOT scary. {GUARD}'),
    ('story_recover.png', ['pikachu.png'],
     f'Sunny meadow scene with soft green hills. {HERO} stands proudly on a little grassy hill, '
     f'lifting one red-and-white round ball high above its head with both paws, big happy smile, '
     f'sparkles around the ball. Cheerful triumphant mood. {GUARD}'),
    ('story_finale.png', ['pikachu.png'],
     f'Festive daytime village square with colorful bunting flags strung between little houses. '
     f'{HERO} jumps for joy in the middle of the square, six red-and-white round balls arranged '
     f'in a neat row on the grass in front of it, colorful confetti in the air, cheerful mood. {GUARD}'),
]

def b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def gen(out_path, refs, prompt, attempt=1):
    parts = [{'inlineData': {'mimeType': 'image/png', 'data': b64(os.path.join(ASSETS, r))}} for r in refs]
    parts.append({'text': prompt})
    body = json.dumps({
        'contents': [{'parts': parts}],
        'generationConfig': {'responseModalities': ['TEXT', 'IMAGE'],
                             'imageConfig': {'aspectRatio': '16:9'}},
    }).encode()
    req = urllib.request.Request(URL, data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.load(r)
    for part in resp['candidates'][0]['content'].get('parts', []):
        if 'inlineData' in part:
            with open(out_path, 'wb') as f:
                f.write(base64.b64decode(part['inlineData']['data']))
            return True
    raise KeyError('no image part in response')

for name, refs, prompt in PANELS:
    out = os.path.join(ASSETS, name)
    if os.path.exists(out):
        print('SKIP', name); continue
    for attempt in range(1, 5):
        try:
            gen(out, refs, prompt, attempt)
            print('OK', name, f'({os.path.getsize(out)//1024}KB)')
            break
        except Exception as e:
            print(f'RETRY {attempt}', name, type(e).__name__, str(e)[:120])
            time.sleep(20 * attempt)
    time.sleep(1)
print('DONE')
