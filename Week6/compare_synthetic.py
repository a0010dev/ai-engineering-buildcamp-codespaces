"""Compare judge labels on synthetic and manually designed scenarios."""

import argparse
import json
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def summarize(rows):
    if not rows or any(row.get('judge_label') not in {'good', 'bad'} for row in rows):
        raise ValueError('Every scenario must have a valid judge label')
    by_type = defaultdict(lambda: {'total': 0, 'bad': 0})
    bad = 0
    for row in rows:
        is_bad = row['judge_label'] == 'bad'
        bad += is_bad
        by_type[row['type']]['total'] += 1
        by_type[row['type']]['bad'] += is_bad
    return {
        'total': len(rows), 'bad': bad, 'bad_percentage': 100 * bad / len(rows),
        'by_type': {
            kind: {**counts, 'bad_percentage': 100 * counts['bad'] / counts['total']}
            for kind, counts in sorted(by_type.items())
        },
        'bad_without_tool_calls': sum(
            row['judge_label'] == 'bad' and not any(
                part.get('part_kind') == 'tool-call' for part in row.get('tools', [])
            ) for row in rows
        ),
    }


def compare(manual_path, synthetic_path, output_path):
    manual = json.loads(Path(manual_path).read_text(encoding='utf-8'))
    synthetic = json.loads(Path(synthetic_path).read_text(encoding='utf-8'))
    report = {'manual': summarize(manual), 'synthetic': summarize(synthetic)}
    Path(output_path).write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manual', type=Path, default=BASE_DIR / 'results_judged_improved.json')
    parser.add_argument('--synthetic', type=Path, default=BASE_DIR / 'synthetic_results_judged.json')
    parser.add_argument('--output', type=Path, default=BASE_DIR / 'synthetic_comparison.json')
    args = parser.parse_args()
    compare(args.manual, args.synthetic, args.output)
