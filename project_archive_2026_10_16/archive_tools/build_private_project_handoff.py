"""Inventory and archive Light Equity material without changing source files."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

BASE = Path('E:/AI项目')
SPECS = [
    ('light-equity-soict-2026', 'research', 'frozen_research'),
    ('light_equity_project', 'history/abc_engine', 'historical_abc'),
    ('路线B_中文导师审阅定稿_工作包_2026_06_20', 'history/route_b_june', 'historical_route_b'),
    ('中文导师审阅定稿_工作包_2026_06_20', 'history/june_review', 'historical_review'),
    ('光权修复_论文工作包_2026-06-03', 'manuscripts/june_workbook', 'historical_manuscript'),
    ('paper_revision_work_2026_06_14', 'manuscripts/june_revision', 'historical_manuscript'),
    ('final_chinese_paper_package_2026_06_11', 'manuscripts/june_11_package', 'historical_manuscript'),
    ('光权修复论文和参考文献PDF_最终简化版', 'manuscripts/simplified_package', 'historical_manuscript'),
    ('paper_submission_audit_2026_06_09', 'reviews/submission_june_09', 'historical_review'),
    ('paper_second_round_integration_2026_06_09', 'manuscripts/second_round', 'historical_manuscript'),
    ('paper_audit_2026_06_10', 'reviews/audit_june_10', 'historical_review'),
    ('网页端AI审查_20文件包_2026_06_20', 'reviews/web_review_20', 'historical_review'),
    ('网页端AI审查_2文件版_2026_06_20', 'reviews/web_review_2', 'historical_review'),
    ('项目重启审查_2026-09-09', 'reviews/restart_september', 'restart_review'),
    ('项目总结', 'context/initial_handoff', 'project_context'),
    ('谢研组', 'context/team_evidence', 'team_evidence'),
    ('光照分析', 'validation/human_sunlight', 'human_visual_validation'),
    ('论文参考文献PDF', 'references/local_library', 'reference_archive'),
    ('光权修复_线上会议_2026-05-31', 'context/meeting_may_31', 'project_context'),
    ('谢研组_沿湖休闲片区_光权修复ABC真实重算交付包_2026-05-25', 'history/may_25_delivery', 'historical_abc'),
    ('AI光权修复系统_验证优化与Skill交付包_2026-05-29', 'history/may_29_validation', 'historical_abc'),
    ('peer-review-report', 'reviews/peer_review', 'historical_review'),
    ('ei-conference-evaluation', 'reviews/ei_evaluation', 'historical_review'),
]
ROOT_FILES = [
    '开会记录.txt', '建筑设计四（25-26）旧街区改造任务.docx',
    '技术组——光权修复_项目完整说明_终版.docx', '光权修复_终版执行大纲.docx',
    '光权修复_AI技术组项目计划.docx', '光权修复_技术组项目介绍（组员版）.docx',
    '光权修复_（最终）算法说明.docx', '光权修复技术组项目完整说明 & 任务安排（2026.04）.pdf',
    '20250212灌口镇灌口一二社区“1314”焕新计划.pdf',
    '250321灌口镇第一第二社区城中村改造节点征集.pdf',
    '灌口镇第一、第二社区城中村整治规划及项目策划-市级评审后修改.pdf',
    '光权修复AI项目完整介绍_给网页端AI_2026-06-05.txt',
    '光权修复项目介绍_给其他AI_2026-06-03.txt', 'SOICT_2026_PAPER_ASSETS_FEEDBACK.md',
    '建创坊技术组_A4过程册_光权修复项目_教师提交版_分页优化版.docx',
    '建创坊技术组_A4过程册_光权修复项目_2026-06-24_优化版.docx',
    '光权修复_汇报版.html', '光权修复_空间决策系统.html',
]
ALLOWED = {'.md', '.txt', '.py', '.rb', '.yaml', '.yml', '.json', '.csv', '.toml', '.ini',
           '.png', '.jpg', '.jpeg', '.svg', '.bmp', '.pdf', '.docx', '.tex', '.bib', '.sha256',
           '.html', '.ipynb', '.xlsx', '.xls', '.js', '.css', '.rst'}
RAW = {'.obj', '.dxf', '.dwg', '.skp', '.skb', '.3dm', '.gh', '.ghx', '.hbjson', '.ill',
       '.res', '.oct', '.rad', '.pts', '.wea', '.epw', '.mtl', '.dwl', '.dwl2'}
SKIP_DIRS = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv',
             'runtime_repeats', 'hb_batch', 'github_snapshot', 'data_raw', '_shared'}
FROZEN_RUN = 'baseline_20260909_clean'


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as handle:
        for part in iter(lambda: handle.read(1024 * 1024), b''):
            value.update(part)
    return value.hexdigest()


def exclusion(path, relative):
    if any(part in SKIP_DIRS or part.startswith('hb_radiance_') for part in relative.parts):
        return 'cache_or_simulation_intermediates'
    if path.suffix.lower() in RAW:
        return 'raw_geometry_sensor_or_radiance_source'
    if path.suffix.lower() not in ALLOWED:
        return 'not_a_selected_handoff_format'
    if path.stat().st_size > 45 * 1024 * 1024:
        return 'oversized_binary_inventory_only'
    if any(part.lower().startswith(('rendered', 'contact_sheet', 'page_renders')) for part in relative.parts):
        return 'render_cache'
    name = path.name.lower()
    if name.startswith(('~$', '.env')) or any(token in name for token in ('credential', 'secret', 'token_cache')):
        return 'local_credentials_or_temporary'
    if path.suffix.lower() in {'.csv', '.json', '.txt'}:
        if any(token in name for token in ('sensor_points', '传感点', '原始点位', 'point_results',
                                          'grid_points', '点位对齐', 'sunlight_hours', 'dark_zones',
                                          'gap_candidates', 'safe_routes', 'voxel_occupancy')):
            return 'sensor_or_point_coordinate_table'
    if path.suffix.lower() == '.csv':
        with path.open('r', encoding='utf-8-sig', errors='replace', newline='') as handle:
            header = next(csv.reader(handle), [])
        cols = {column.strip().lower() for column in header}
        spatial = {'x', 'y'} <= cols or {'point_x', 'point_y'} <= cols or {'sensor_x', 'sensor_y'} <= cols
        point = any('sensor' in column or 'grid_id' in column or 'point_id' in column for column in cols)
        if spatial and (point or not any('building' in column for column in cols)):
            return 'sensor_or_point_coordinate_table'
    if path.suffix.lower() == '.json' and path.stat().st_size < 5 * 1024 * 1024:
        text = path.read_text(encoding='utf-8-sig', errors='replace')
        if re.search(r'"(?:sensors|sensor_points|vertices|sensor_coordinates)"\s*:\s*\[', text):
            return 'embedded_raw_geometry_or_sensor_array'
    return ''


def scan():
    seen = set()
    for source_name, target_name, status in SPECS:
        source_root = BASE / source_name
        if not source_root.exists():
            continue
        for path in sorted(source_root.rglob('*')):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            relative = path.relative_to(source_root)
            yield path, Path(target_name) / relative, status, exclusion(path, relative)
    for name in ROOT_FILES:
        path = BASE / name
        if path.exists():
            yield path, Path('context/source_documents') / path.name, 'project_context', exclusion(path, Path(name))


def write_rows(path, rows, columns):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def extract_docx(path):
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with zipfile.ZipFile(path) as bundle:
        root = ET.fromstring(bundle.read('word/document.xml'))
    paragraphs = []
    for paragraph in root.findall('.//w:body//w:p', ns):
        value = ''.join(node.text or '' for node in paragraph.findall('.//w:t', ns))
        if value.strip():
            paragraphs.append(value)
    return '\n\n'.join(paragraphs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    items = list(scan())
    eligible = [row for row in items if not row[3]]
    summary = {'scanned_files': len(items), 'eligible_files_before_deduplication': len(eligible),
               'eligible_mib': round(sum(row[0].stat().st_size for row in eligible) / 1024**2, 2),
               'exclusions': dict(Counter(row[3] for row in items if row[3])),
               'largest': [(str(row[0].relative_to(BASE)), round(row[0].stat().st_size / 1024**2, 2))
                           for row in sorted(eligible, key=lambda row: row[0].stat().st_size, reverse=True)[:12]]}
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    if not args.output:
        return
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    copies, rows, hashes = [], [], {}
    extraction_errors = []
    for source, proposed, status, reason in items:
        row = {'source_relative_path': source.relative_to(BASE).as_posix(), 'status': status,
               'bytes': source.stat().st_size, 'source_mtime_utc': datetime.fromtimestamp(source.stat().st_mtime, timezone.utc).isoformat(),
               'action': 'excluded' if reason else 'copied', 'reason': reason,
               'archive_path': '', 'sha256': ''}
        if reason:
            rows.append(row)
            continue
        value = digest(source)
        row['sha256'] = value
        if value in hashes:
            row['action'] = 'duplicate_reference'
            row['archive_path'] = hashes[value]
        else:
            destination = output / proposed
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            relative = proposed.as_posix()
            hashes[value] = relative
            row['archive_path'] = relative
            copies.append((destination, relative))
            if destination.suffix.lower() == '.docx':
                try:
                    text = extract_docx(source)
                    text_path = output / 'readable_manuscripts' / proposed.with_suffix('.md')
                    text_path.parent.mkdir(parents=True, exist_ok=True)
                    text_path.write_text('# Archived Word Document\n\nSource: `' + relative + '`\n\n'
                                         + 'Status: historical text; reconcile every numeric claim against the frozen paper ledger.\n\n'
                                         + text + '\n', encoding='utf-8')
                except (OSError, zipfile.BadZipFile, ET.ParseError) as error:
                    extraction_errors.append({'source': row['source_relative_path'], 'error': str(error)})
        rows.append(row)
    columns = ['source_relative_path', 'archive_path', 'status', 'action', 'reason', 'bytes', 'sha256', 'source_mtime_utc']
    write_rows(output / 'indexes/FILE_INVENTORY.csv', rows, columns)
    write_rows(output / 'indexes/EXCLUDED_SOURCE_FILES.csv', [row for row in rows if row['action'] == 'excluded'], columns)
    write_rows(output / 'indexes/MANUSCRIPT_INDEX.csv', [row for row in rows if row['source_relative_path'].endswith(('.docx', '.tex', '.bib'))], columns)
    runs = []
    source_runs = [(BASE/'light_equity_project/outputs', 'historical_abc'),
                   (BASE/'light-equity-soict-2026/experiments', 'research')]
    for root, kind in source_runs:
        for run in sorted(root.iterdir()):
            if not run.is_dir():
                continue
            selected = [row for row in rows if row['source_relative_path'].startswith(run.relative_to(BASE).as_posix() + '/')]
            retained = [row for row in selected if row['action'] != 'excluded']
            summary_files = [row['archive_path'] for row in retained
                             if any(word in Path(row['source_relative_path']).name.lower() for word in ('summary', 'metrics', 'report', '汇总', '指标'))]
            runs.append({'run_id_or_directory': run.name, 'stage': kind,
                         'evidence_role': 'CURRENT_FROZEN' if run.name == FROZEN_RUN else 'HISTORICAL_OR_AUDIT_ONLY',
                         'source_relative_path': run.relative_to(BASE).as_posix(),
                         'inventoried_files': len(selected), 'retained_file_references': len(retained),
                         'summary_assets': json.dumps(sorted(set(summary_files)), ensure_ascii=False)})
    write_rows(output / 'indexes/EXPERIMENT_REGISTER.csv', runs, list(runs[0]))
    copied_bytes = sum(path.stat().st_size for path, _ in copies)
    summary.update({'unique_copied_files': len(copies), 'unique_copied_mib': round(copied_bytes/1024**2, 2),
                    'duplicate_references': sum(row['action']=='duplicate_reference' for row in rows),
                    'registered_run_directories': len(runs), 'docx_extraction_errors': extraction_errors})
    (output / 'indexes/ARCHIVE_BUILD_SUMMARY.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
