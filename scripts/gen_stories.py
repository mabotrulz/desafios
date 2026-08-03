#!/usr/bin/env python3
"""Generate 15 fullscreen (9:16) storybook panels: 3 stories x (2 intro + 1 recover + 2 finale).
Character sprites passed as visual references; prompts use visual descriptions ONLY (no names).
PNGs land in /tmp/storygen, converted JPEGs go to assets/. Skip-if-exists + retry."""
import base64, json, os, time, urllib.request

KEY = None
for line in open(os.path.expanduser('~/.hermes/.env')):
    if line.startswith('GEMINI_API_KEY='):
        KEY = line.strip().split('=', 1)[1]
assert KEY, 'GEMINI_API_KEY not found'

MODEL = 'gemini-3.1-flash-image'
URL = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}'
ASSETS = os.path.join(os.path.dirname(__file__), '..', 'assets')
TMP = '/tmp/storygen'
os.makedirs(TMP, exist_ok=True)

GUARD = ('No text, no words, no letters, no speech bubbles, no sound-effect words. '
         'Colorful children\'s book illustration, soft cartoon style, warm friendly lighting, '
         'tall portrait composition.')
HERO = ('the small yellow mouse-like creature from the reference image '
        '(round body, long ears with black tips, red cheeks, lightning-bolt shaped tail)')
CAT = ('the cream-colored cat-like creature from the reference image '
       '(walks upright on two legs, curly whiskers, big eyes)')
WOMAN = ('the tall woman from the reference image '
         '(very long magenta hair, white uniform with a red letter-free front, white boots)')
TR = f'{CAT} and {WOMAN}'

PANELS = [
    # ---- Story 1: the stolen Poké Balls ----
    ('s1_intro1', ['pikachu.png'],
     f'Sunny morning in a small cozy village square with little houses and warm windows. '
     f'{HERO} plays happily on the grass next to six red-and-white round balls lined up in a row, '
     f'birds in the sky, peaceful joyful mood. {GUARD}'),
    ('s1_intro2', ['pikachu.png', 'meowth.png', 'jessie.png'],
     f'Night scene in a small cozy village. Two sneaky cartoon thieves tiptoeing away down a path '
     f'carrying a big brown sack, red-and-white round balls spilling out onto the path: {TR}. '
     f'In the foreground {HERO} hides behind a bush, watching them with a worried but cute expression, '
     f'NOT terrified. The thieves look sneaky and funny, NOT scary. {GUARD}'),
    ('s1_recover', ['pikachu.png'],
     f'Sunny meadow with soft green hills. {HERO} stands proudly on a little grassy hill, lifting one '
     f'red-and-white round ball high above its head with both paws, big happy smile, sparkles around '
     f'the ball. Cheerful triumphant mood. {GUARD}'),
    ('s1_finale1', ['pikachu.png'],
     f'Daytime village square. {HERO} gently places red-and-white round balls back onto a wooden stand '
     f'in the middle of the square while happy villagers clap and smile, warm sunlight, heartwarming '
     f'mood. {GUARD}'),
    ('s1_finale2', ['pikachu.png'],
     f'Festive daytime village square with colorful bunting between little houses. {HERO} jumps for joy '
     f'in the middle of the square, six red-and-white round balls arranged in a neat row on the grass, '
     f'colorful confetti in the air, cheerful celebration mood. {GUARD}'),
    # ---- Story 2: the magic berries festival ----
    ('s2_intro1', ['pikachu.png'],
     f'Festive daytime village getting ready for a berry festival: wooden tables with bowls full of '
     f'round colorful berries (red, blue and purple), colorful bunting strung between houses. '
     f'{HERO} bounces excitedly beside the tables, mouth open with joy. {GUARD}'),
    ('s2_intro2', ['pikachu.png', 'meowth.png', 'jessie.png'],
     f'Evening village scene. Two sneaky cartoon thieves tiptoeing away carrying a giant woven basket '
     f'overflowing with round colorful berries, berries dropping on the path behind them: {TR}. '
     f'In the foreground {HERO} runs after them with a determined but cute expression. '
     f'Funny, NOT scary. {GUARD}'),
    ('s2_recover', ['pikachu.png'],
     f'Sunny orchard with leafy trees. {HERO} stands proudly on a grassy hill, lifting one big round '
     f'purple berry above its head with both paws, big happy smile, sparkles around the berry. '
     f'Cheerful triumphant mood. {GUARD}'),
    ('s2_finale1', ['pikachu.png'],
     f'Festival village square at golden sunset. {HERO} carefully places round colorful berries back '
     f'into bowls on the wooden festival tables, smiling villagers around, warm golden light, '
     f'heartwarming mood. {GUARD}'),
    ('s2_finale2', ['pikachu.png'],
     f'Night berry festival in full swing: glowing paper lanterns, garlands, villagers dancing around '
     f'tables full of berry treats, {HERO} dancing happily in the middle with a berry in each paw, '
     f'confetti in the air. Joyful celebration mood. {GUARD}'),
    # ---- Story 3: the lighthouse star crystals ----
    ('s3_intro1', ['pikachu.png'],
     f'Coastal village at dusk beside a calm sea, a tall white lighthouse on a cliff with a big glowing '
     f'golden star-shaped crystal on top lighting the ocean, little fishing boats with lanterns. '
     f'{HERO} sits on the wooden dock admiring the light, peaceful cozy mood. {GUARD}'),
    ('s3_intro2', ['pikachu.png', 'meowth.png', 'jessie.png'],
     f'Night coastal scene: the lighthouse on the cliff is dark. Two sneaky cartoon thieves tiptoe away '
     f'along the cliff path carrying a big glowing golden star-shaped crystal inside a cloth sack, '
     f'golden light leaking out: {TR}. In the foreground {HERO} watches from behind a wooden barrel, '
     f'worried but cute, NOT terrified. Sneaky and funny, NOT scary. {GUARD}'),
    ('s3_recover', ['pikachu.png'],
     f'Clifftop under a starry night sky. {HERO} stands proudly lifting a glowing golden star-shaped '
     f'crystal above its head with both paws, warm golden light on its happy face, sparkles. '
     f'Triumphant mood. {GUARD}'),
    ('s3_finale1', ['pikachu.png'],
     f'Night scene at the top of a white lighthouse: {HERO} carefully places a glowing golden '
     f'star-shaped crystal back into its metal holder, warm beams of light starting to shine out, '
     f'gentle wonder mood. {GUARD}'),
    ('s3_finale2', ['pikachu.png'],
     f'Night coastal village celebration: the lighthouse shining bright golden beams over the sea, '
     f'fishing boats with lanterns returning safely, villagers cheering on the dock, {HERO} jumping '
     f'for joy in front, sparkling lights in the sky. Joyful, safe, cozy mood. {GUARD}'),
]

def b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def gen(out_path, refs, prompt):
    parts = [{'inlineData': {'mimeType': 'image/png', 'data': b64(os.path.join(ASSETS, r))}} for r in refs]
    parts.append({'text': prompt})
    body = json.dumps({
        'contents': [{'parts': parts}],
        'generationConfig': {'responseModalities': ['TEXT', 'IMAGE'],
                             'imageConfig': {'aspectRatio': '9:16'}},
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

done = 0
for name, refs, prompt in PANELS:
    out = os.path.join(TMP, name + '.png')
    if os.path.exists(out):
        print('SKIP', name); done += 1; continue
    for attempt in range(1, 5):
        try:
            gen(out, refs, prompt)
            print('OK', name, f'({os.path.getsize(out)//1024}KB)')
            done += 1
            break
        except Exception as e:
            print(f'RETRY {attempt}', name, type(e).__name__, str(e)[:120], flush=True)
            time.sleep(20 * attempt)
    time.sleep(1)
print(f'DONE {done}/{len(PANELS)}')
