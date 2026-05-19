import pandas as pd
import csv
import os
from datetime import datetime

# ── 설정 ────────────────────────────────────────────────────────────────────
CSV_IN  = 'jlpt_grammar.csv'
CSV_OUT = 'jlpt_grammar_fixed.csv'
REVIEW  = 'review.md'
BATCH   = 90

CONCEPT_KEYWORDS = ['活用', '指示語', '疑問詞', '基本形']

# 확정 카드타입 맵 (항목번호 → card_type)
FIXED_CARD_TYPE = {
    'N5-005': 'system_table',
    'N5-006': 'system_table',
    'N5-034': 'paradigm_verb',
    'N5-035': 'paradigm_iadj',
    'N5-038': 'paradigm_naadj',
}

# ── review.md 초기화 ─────────────────────────────────────────────────────────
now = datetime.now().strftime('%Y-%m-%d %H:%M')
review_lines = [
    '# JLPT Grammar CSV — 처리 로그\n',
    f'\n생성일시: {now}\n',
    '대상 파일: jlpt_grammar.csv\n',
    '\n---\n',
]

def review_entry(item_no, row_idx, etype, reason, before, after, card_type):
    lines = [
        f'\n## [{item_no}] 행 {row_idx}\n',
        f'\n- **유형**: {etype}\n',
        f'- **판단 근거**: {reason}\n',
        f'- **처리 전**: {before}\n',
        f'- **처리 후**: {after}\n',
        f'- **card_type**: {card_type}\n',
        '\n---\n',
    ]
    review_lines.extend(lines)

# ── 원본 로드 ────────────────────────────────────────────────────────────────
df_all = pd.read_csv(CSV_IN, header=None, encoding='utf-8-sig', dtype=str)
total_rows = len(df_all)
num_batches = (total_rows + BATCH - 1) // BATCH
print(f'원본 총 행 수: {total_rows}')
print(f'배치 수: {num_batches} (90행 × {num_batches}회)')
print()

# ── 출력 파일 초기화 ─────────────────────────────────────────────────────────
if os.path.exists(CSV_OUT):
    os.remove(CSV_OUT)

# 전체 통계
stats = {'type1': 0, 'type2': 0, 'type3': 0}
card_type_dist = {
    'grammar': 0, 'system_table': 0,
    'paradigm_verb': 0, 'paradigm_iadj': 0, 'paradigm_naadj': 0,
}

# ── 배치 처리 ────────────────────────────────────────────────────────────────
for batch_no in range(num_batches):
    start = batch_no * BATCH
    end   = min(start + BATCH, total_rows)
    df    = df_all.iloc[start:end].copy().reset_index(drop=True)

    b_type1 = b_type2 = b_type3 = 0
    card_types = []

    for i, row in df.iterrows():
        abs_idx   = start + i          # 원본 절대 인덱스
        item_no   = str(row[0]).strip()
        grammar   = str(row[2]).strip() if pd.notna(row[2]) else ''
        conn      = str(row[3]).strip() if pd.notna(row[3]) else ''

        # ── 유형 1 판정 ────────────────────────────────────────────────────
        has_concept = any(kw in grammar for kw in CONCEPT_KEYWORDS)
        starts_tilde = grammar.startswith('～')
        has_plus_tilde = '+ ～' in conn

        if starts_tilde and has_concept and not has_plus_tilde:
            # 확정 오류: ～ 제거 + 지정 card_type
            fixed_grammar = grammar.lstrip('～')
            ct = FIXED_CARD_TYPE.get(item_no, 'grammar')
            df.at[i, 2] = fixed_grammar
            review_entry(
                item_no, abs_idx,
                '확정 오류',
                f'문법항목이 ～+CONCEPT_KEYWORD 형식이고 접속방법에 "+ ～" 없음',
                grammar, fixed_grammar, ct,
            )
            card_types.append(ct)
            b_type1 += 1
            stats['type1'] += 1

        # ── 유형 2 판정 ────────────────────────────────────────────────────
        elif not has_concept and (
            pd.isna(row[2]) or grammar == '' or grammar == 'nan'
        ):
            # 문법항목 비어있는 경우
            ct = 'grammar'
            review_entry(
                item_no, abs_idx,
                '판단 처리',
                '문법항목이 비어있어 card_type=grammar 부여',
                grammar, '변경 없음', ct,
            )
            card_types.append(ct)
            b_type2 += 1
            stats['type2'] += 1

        elif not has_concept and all(
            pd.isna(row[j]) or str(row[j]).strip() in ('', 'nan')
            for j in [5, 6, 7, 8]
        ):
            # 예문 열이 모두 비어있는 경우
            ct = 'grammar'
            review_entry(
                item_no, abs_idx,
                '판단 처리',
                '예문 열(5~8)이 모두 비어있어 card_type=grammar 부여',
                grammar, '변경 없음', ct,
            )
            card_types.append(ct)
            b_type2 += 1
            stats['type2'] += 1

        # ── 유형 3 (정상) ─────────────────────────────────────────────────
        else:
            ct = 'grammar'
            card_types.append(ct)
            b_type3 += 1
            stats['type3'] += 1

        card_type_dist[ct] = card_type_dist.get(ct, 0) + 1

    df[10] = card_types

    # 배치 누적 저장
    write_header = (batch_no == 0 and not os.path.exists(CSV_OUT))
    df.to_csv(
        CSV_OUT,
        mode='a',
        header=False,
        index=False,
        quoting=csv.QUOTE_ALL,
        encoding='utf-8-sig',
    )

    print(f'배치 {batch_no+1:02d} | row {start}~{end-1} | '
          f'유형1={b_type1} 유형2={b_type2} 유형3={b_type3}')

# ── review.md 저장 ──────────────────────────────────────────────────────────
with open(REVIEW, 'w', encoding='utf-8') as f:
    f.writelines(review_lines)

# ── 검증 ────────────────────────────────────────────────────────────────────
print()
print('=== 검증 ===')

df_out = pd.read_csv(CSV_OUT, header=None, encoding='utf-8-sig', dtype=str)
ok_count = len(df_out) == total_rows
print(f'[{"O" if ok_count else "X"}] 총 처리 행 수 일치: {len(df_out)} (원본 {total_rows})')

fixed_ids = {'N5-005', 'N5-006', 'N5-034', 'N5-035', 'N5-038'}
tilde_check_rows = df_out[df_out[0].isin(fixed_ids)]
all_fixed = all(
    not str(row[2]).startswith('～') for _, row in tilde_check_rows.iterrows()
)
print(f'[{"O" if all_fixed else "X"}] 확정 오류 5개 수정 완료')
for _, row in tilde_check_rows.iterrows():
    print(f'   {row[0]}: 문법항목={row[2]}, card_type={row[10]}')

no_empty_ct = df_out[10].notna().all() and (df_out[10] != '').all()
print(f'[{"O" if no_empty_ct else "X"}] card_type 빈 행 없음')

remaining = df_out[df_out[2].apply(
    lambda g: any(kw in str(g) for kw in CONCEPT_KEYWORDS)
    and str(g).startswith('～')
)]
print(f'[{"O" if len(remaining)==0 else "X"}] CONCEPT_KEYWORDS + ～ 잔존 없음: {len(remaining)}건')

review_ok = os.path.exists(REVIEW)
print(f'[{"O" if review_ok else "X"}] review.md 생성 확인')

# ── 최종 요약 ────────────────────────────────────────────────────────────────
total_processed = stats['type1'] + stats['type2'] + stats['type3']
print()
print('=== 처리 완료 ===')
print(f'총 처리 행: {total_processed}')
print(f'유형 1 (확정 수정): {stats["type1"]}건')
print(f'유형 2 (판단 처리): {stats["type2"]}건')
print(f'유형 3 (정상):      {stats["type3"]}건')
print('card_type 분포:')
for ct, n in card_type_dist.items():
    if n > 0:
        print(f'  {ct+":":<20} {n}')
print('출력 파일:')
print('  jlpt_grammar_fixed.csv')
print('  review.md')
