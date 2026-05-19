import pandas as pd
import os

CSV_IN    = 'jlpt_grammar_fixed.csv'
BASIC_OUT = 'anki_basic.txt'
CLOZE_OUT = 'anki_cloze.txt'

df = pd.read_csv(CSV_IN, header=None, encoding='utf-8-sig', dtype=str)

def c(s):
    """NaN → 빈 문자열 + strip"""
    if pd.isna(s) or str(s).strip() in ('', 'nan'):
        return ''
    return str(s).strip()

# ── 출력 파일 초기화 ─────────────────────────────────────────────────────────
with open(BASIC_OUT, 'w', encoding='utf-8') as fb:
    fb.write('#separator:tab\n#html:true\n#notetype:Basic\n#columns:Front\tBack\tTags\n')
with open(CLOZE_OUT, 'w', encoding='utf-8') as fc:
    fc.write('#separator:tab\n#html:true\n#notetype:Cloze\n#columns:Text\tTags\n')

note_counts = {
    'grammar': 0, 'system_table': 0,
    'paradigm_verb_A': 0, 'paradigm_verb_B': 0,
    'paradigm_iadj': 0, 'paradigm_naadj': 0,
}

# ── 행별 처리 ────────────────────────────────────────────────────────────────
with open(BASIC_OUT, 'a', encoding='utf-8') as fb, \
     open(CLOZE_OUT, 'a', encoding='utf-8') as fc:

    for _, row in df.iterrows():
        ct      = c(row[10])
        item_no = c(row[0])
        level   = c(row[1])
        tags    = f"{level} {item_no}"

        # ────────────────────────────────────────────────────────────────────
        # grammar — 일반 문법 카드 (Basic)
        # ────────────────────────────────────────────────────────────────────
        if ct == 'grammar':
            grammar = c(row[2])
            conn    = c(row[3])
            meaning = c(row[4])
            ex1     = c(row[5]); ex1_tr = c(row[6])
            ex2     = c(row[7]); ex2_tr = c(row[8])
            expl    = c(row[9])

            front = f"<b>{grammar}</b><br>{conn}" if conn else f"<b>{grammar}</b>"

            back_parts = []
            if meaning:
                back_parts.append(meaning)
            if ex1:
                back_parts.append(f"{ex1}<br>{ex1_tr}" if ex1_tr else ex1)
            if ex2:
                back_parts.append(f"{ex2}<br>{ex2_tr}" if ex2_tr else ex2)
            if expl:
                back_parts.append(f"<i>{expl}</i>")
            back = '<hr>'.join(back_parts)

            fb.write(f"{front}\t{back}\t{tags}\n")
            note_counts['grammar'] += 1

        # ────────────────────────────────────────────────────────────────────
        # system_table — 체계 표 (Basic, HTML 테이블)
        # ────────────────────────────────────────────────────────────────────
        elif ct == 'system_table':

            if item_no == 'N5-005':
                TH = 'style="padding:4px 10px;background:#eef"'
                TD = 'style="padding:4px 10px;text-align:center"'
                front = (
                    '<b>こそあど指示語</b> — 빈칸을 채우시오<br><br>'
                    '<table border="1" style="border-collapse:collapse">'
                    f'<tr><th {TH}></th><th {TH}>사물</th><th {TH}>장소</th><th {TH}>지정 수식</th></tr>'
                    f'<tr><td {TD}>가까운</td><td {TD}>( )</td><td {TD}>( )</td><td {TD}>( ) + 명사</td></tr>'
                    f'<tr><td {TD}>중간</td><td {TD}>( )</td><td {TD}>( )</td><td {TD}>( ) + 명사</td></tr>'
                    f'<tr><td {TD}>먼</td><td {TD}>( )</td><td {TD}>( )</td><td {TD}>( ) + 명사</td></tr>'
                    f'<tr><td {TD}>불명(의문)</td><td {TD}>( )</td><td {TD}>( )</td><td {TD}>( ) + 명사</td></tr>'
                    '</table>'
                )
                back = (
                    '<table border="1" style="border-collapse:collapse">'
                    f'<tr><th {TH}></th><th {TH}>사물</th><th {TH}>장소</th><th {TH}>지정 수식</th></tr>'
                    f'<tr><td {TD}>가까운</td><td {TD}>これ</td><td {TD}>ここ</td><td {TD}>この</td></tr>'
                    f'<tr><td {TD}>중간</td><td {TD}>それ</td><td {TD}>そこ</td><td {TD}>その</td></tr>'
                    f'<tr><td {TD}>먼</td><td {TD}>あれ</td><td {TD}>あそこ</td><td {TD}>あの</td></tr>'
                    f'<tr><td {TD}>불명(의문)</td><td {TD}>どれ</td><td {TD}>どこ</td><td {TD}>どの</td></tr>'
                    '</table>'
                    '<br>※ どれ・どこ・どの는 의문형이기도 함'
                )
                fb.write(f"{front}\t{back}\t{tags}\n")
                note_counts['system_table'] += 1

            elif item_no == 'N5-006':
                TH = 'style="padding:4px 10px;background:#eef"'
                TD = 'style="padding:4px 10px;text-align:center"'
                rows_f = [
                    ('누구', '사람'),
                    ('무엇', '사물'),
                    ('어디', '장소'),
                    ('언제', '시간'),
                    ('어느 것', '선택'),
                    ('얼마나', '수량·금액'),
                    ('어떤', '성질·종류'),
                    ('왜 / 어떻게', '이유·방법'),
                ]
                rows_b = [
                    ('누구',        'だれ（誰）',              '사람'),
                    ('무엇',        '何（なに・なん）',         '사물'),
                    ('어디',        'どこ',                    '장소'),
                    ('언제',        'いつ',                    '시간'),
                    ('어느 것',     'どれ',                    '선택'),
                    ('얼마나',      'いくつ・いくら',            '수량·금액'),
                    ('어떤',        'どんな',                  '성질·종류'),
                    ('왜 / 어떻게', 'どうして・どうやって・どう', '이유·방법'),
                ]
                front = (
                    '<b>基本疑問詞</b> — 빈칸을 채우시오<br><br>'
                    '<table border="1" style="border-collapse:collapse">'
                    f'<tr><th {TH}>의미</th><th {TH}>의문사</th><th {TH}>용법</th></tr>'
                    + ''.join(
                        f'<tr><td {TD}>{k}</td><td {TD}>( )</td><td {TD}>{v}</td></tr>'
                        for k, v in rows_f
                    )
                    + '</table>'
                )
                back = (
                    '<table border="1" style="border-collapse:collapse">'
                    f'<tr><th {TH}>의미</th><th {TH}>의문사</th><th {TH}>용법</th></tr>'
                    + ''.join(
                        f'<tr><td {TD}>{k}</td><td {TD}>{jp}</td><td {TD}>{v}</td></tr>'
                        for k, jp, v in rows_b
                    )
                    + '</table>'
                    '<br>※ こそあど 체계의 의문형(どれ・どこ・どの)과 연계'
                )
                fb.write(f"{front}\t{back}\t{tags}\n")
                note_counts['system_table'] += 1

        # ────────────────────────────────────────────────────────────────────
        # paradigm_verb — 動詞活用 Cloze
        # ────────────────────────────────────────────────────────────────────
        elif ct == 'paradigm_verb':

            # ── 세트 A: 활용형별 4노트 (c1 단일) ─────────────────────────
            SET_A = [
                ('ない형',          '読まない', '食べない', 'しない',  'こない'),
                ('ます형',          '読みます', '食べます', 'します',  'きます'),
                ('사전형（기본형）', '読む',     '食べる',   'する',    'くる'),
                ('의지형（～よう）', '読もう',   '食べよう', 'しよう',  'こよう'),
            ]
            for form, g5, g1, suru, kuru in SET_A:
                text = (
                    f"{form}:<br>"
                    f"5단(読む)　 → {{{{c1::{g5}}}}}<br>"
                    f"1단(食べる) → {{{{c1::{g1}}}}}<br>"
                    f"する　　　 → {{{{c1::{suru}}}}}<br>"
                    f"くる　　　 → {{{{c1::{kuru}}}}}"
                )
                short = form.split('（')[0]
                fc.write(f"{text}\t{tags} 세트A {short}\n")
                note_counts['paradigm_verb_A'] += 1

            # ── 세트 B: て형・た형 7노트 (c1=て형, c2=た형) ──────────────
            SET_B = [
                (
                    'B1', 'く어미',
                    '5단 동사 く 어미 — て형・た형<br>'
                    '（※ 예외: 行く → <b>いって</b> / <b>いった</b>）<br><br>'
                    '書く → て형: {{c1::書いて}}　た형: {{c2::書いた}}<br><br>'
                    '규칙: く → い + て/た'
                ),
                (
                    'B2', 'ぐ어미',
                    '5단 동사 ぐ 어미 — て형・た형<br><br>'
                    '泳ぐ → て형: {{c1::泳いで}}　た형: {{c2::泳いだ}}<br><br>'
                    '규칙: ぐ → い + で/だ'
                ),
                (
                    'B3', 'す어미',
                    '5단 동사 す 어미 — て형・た형<br><br>'
                    '話す → て형: {{c1::話して}}　た형: {{c2::話した}}<br><br>'
                    '규칙: す → し + て/た'
                ),
                (
                    'B4', 'むぬぶ어미',
                    '5단 동사 む/ぬ/ぶ 어미 — て형・た형<br>'
                    '（※ ぬ어미는 현대어에서 死ぬ 한 개뿐）<br><br>'
                    '読む → て형: {{c1::読んで}}　た형: {{c2::読んだ}}<br>'
                    '死ぬ → て형: {{c1::死んで}}　た형: {{c2::死んだ}}<br>'
                    '飛ぶ → て형: {{c1::飛んで}}　た형: {{c2::飛んだ}}<br><br>'
                    '규칙: む/ぬ/ぶ → ん + で/だ'
                ),
                (
                    'B5', 'つるう어미',
                    '5단 동사 つ/る/う 어미 — て형・た형<br><br>'
                    '待つ → て형: {{c1::待って}}　た형: {{c2::待った}}<br>'
                    '帰る → て형: {{c1::帰って}}　た형: {{c2::帰った}}<br>'
                    '買う → て형: {{c1::買って}}　た형: {{c2::買った}}<br><br>'
                    '규칙: つ/る/う → っ + て/た'
                ),
                (
                    'B6', '1단',
                    '1단 동사 — て형・た형<br><br>'
                    '食べる → て형: {{c1::食べて}}　た형: {{c2::食べた}}<br><br>'
                    '규칙: 어간 + て/た'
                ),
                (
                    'B7', '불규칙',
                    '불규칙 동사 — て형・た형<br><br>'
                    'する → て형: {{c1::して}}　た형: {{c2::した}}<br>'
                    'くる → て형: {{c1::きて}}　た형: {{c2::きた}}'
                ),
            ]
            for bid, blabel, text in SET_B:
                fc.write(f"{text}\t{tags} 세트B {bid} {blabel}\n")
                note_counts['paradigm_verb_B'] += 1

        # ────────────────────────────────────────────────────────────────────
        # paradigm_iadj — い形容詞活用 Cloze (1노트)
        # ────────────────────────────────────────────────────────────────────
        elif ct == 'paradigm_iadj':
            text = (
                'い형용사 활용 (高い 기준):<br><br>'
                '부정형　　 → {{c1::高くない}}<br>'
                '과거형　　 → {{c2::高かった}}<br>'
                '부정과거형 → {{c3::高くなかった}}<br>'
                '부사형　　 → {{c4::高く}}<br><br>'
                '※ いい → よくない / よかった / よくなかった / よく'
            )
            fc.write(f"{text}\t{tags}\n")
            note_counts['paradigm_iadj'] += 1

        # ────────────────────────────────────────────────────────────────────
        # paradigm_naadj — な形容詞活用 Cloze (1노트)
        # ────────────────────────────────────────────────────────────────────
        elif ct == 'paradigm_naadj':
            text = (
                'な형용사 활용 (静か 기준):<br><br>'
                '명사수식형　→ {{c1::静かな}} + 명사<br>'
                '부사형　　　→ {{c2::静かに}}<br>'
                '과거(보통)　→ {{c3::静かだった}}<br>'
                '과거(정중)　→ {{c4::静かでした}}<br>'
                '부정(보통)　→ {{c5::静かじゃない}}<br>'
                '부정(정중)　→ {{c6::静かじゃないです}}'
            )
            fc.write(f"{text}\t{tags}\n")
            note_counts['paradigm_naadj'] += 1

# ── 검증 ────────────────────────────────────────────────────────────────────
print('=== 검증 ===')

with open(BASIC_OUT, encoding='utf-8') as f:
    basic_data = [l for l in f if not l.startswith('#') and l.strip()]
with open(CLOZE_OUT, encoding='utf-8') as f:
    cloze_data = [l for l in f if not l.startswith('#') and l.strip()]

# 탭 분리 필드 수 확인
basic_ok = all(len(l.rstrip('\n').split('\t')) == 3 for l in basic_data)
cloze_ok = all(len(l.rstrip('\n').split('\t')) == 2 for l in cloze_data)
print(f'[{"O" if basic_ok else "X"}] anki_basic.txt 필드 수(3) 일치')
print(f'[{"O" if cloze_ok else "X"}] anki_cloze.txt 필드 수(2) 일치')

expected_basic = note_counts['grammar'] + note_counts['system_table']
expected_cloze = (note_counts['paradigm_verb_A'] + note_counts['paradigm_verb_B']
                  + note_counts['paradigm_iadj'] + note_counts['paradigm_naadj'])
print(f'[{"O" if len(basic_data)==expected_basic else "X"}] basic 노트 수: {len(basic_data)} (예상 {expected_basic})')
print(f'[{"O" if len(cloze_data)==expected_cloze else "X"}] cloze 노트 수: {len(cloze_data)} (예상 {expected_cloze})')

# cloze 구문 확인 ({{c 포함 여부)
cloze_valid = all('{{c' in l for l in cloze_data)
print(f'[{"O" if cloze_valid else "X"}] cloze 노트 전체에 {{{{c... 구문 존재')

print()
print('=== 처리 완료 ===')
print(f'anki_basic.txt  : {len(basic_data)}노트')
print(f'  grammar       : {note_counts["grammar"]}')
print(f'  system_table  : {note_counts["system_table"]}')
print(f'anki_cloze.txt  : {len(cloze_data)}노트')
print(f'  paradigm_verb A: {note_counts["paradigm_verb_A"]} (카드 {note_counts["paradigm_verb_A"]}장)')
print(f'  paradigm_verb B: {note_counts["paradigm_verb_B"]} (카드 {note_counts["paradigm_verb_B"]*2}장)')
print(f'  paradigm_iadj  : {note_counts["paradigm_iadj"]} (카드 4장)')
print(f'  paradigm_naadj : {note_counts["paradigm_naadj"]} (카드 6장)')
total_cards = (note_counts["paradigm_verb_A"]
               + note_counts["paradigm_verb_B"] * 2
               + 4 + 6)
print(f'  Cloze 카드 합계: {total_cards}장')
print()
print('출력 파일:')
print('  anki_basic.txt')
print('  anki_cloze.txt')
