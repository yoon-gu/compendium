#!/usr/bin/env python3
import re
import subprocess
from pathlib import Path
import yaml

REPO = Path('/Users/yoon-gu/repos/compendium')
HEADER = REPO / 'papers-tex' / 'pandoc-korean-header.tex'

PAPERS = [
    {
        'slug': 'interpolating-ar-diffusion-lm',
        'md': REPO / 'content' / 'papers' / 'interpolating-ar-diffusion-lm.md',
        'title_suffix': '(Block Diffusion: Interpolating Between Autoregressive and Diffusion Language Models — 한국어 PDF판)',
    },
    {
        'slug': 'diffusion-lm-controllable',
        'md': REPO / 'content' / 'papers' / 'diffusion-lm-controllable.md',
        'title_suffix': '(Diffusion-LM Improves Controllable Text Generation — 한국어 PDF판)',
    },
]


def load_frontmatter_and_body(path: Path):
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        raise ValueError(f'{path} missing frontmatter')
    _, fm, body = text.split('---\n', 2)
    meta = yaml.safe_load(fm)
    return meta, body


def clean_body(body: str, slug: str) -> str:
    body = re.sub(r"> \*\*짧은 요약\*\*은 .*?\n>\n", "", body, flags=re.S)
    body = body.replace(
        "**PDF 다운로드**\n\n- [arxiv 원문 PDF](/compendium/papers/" + slug + "-original.pdf)\n- 한국어 번역본 PDF는 추후 업로드 예정\n\n",
        ""
    )
    body = body.replace(
        "**PDF 다운로드**\n\n- [arxiv 원문 PDF](/compendium/papers/" + slug + "-original.pdf)\n- 한국어 번역본 PDF는 추후 업로드 예정 (`papers-tex/" + slug + "/` 에 한국어 LaTeX 작업 진행 중)\n\n",
        ""
    )
    body = re.sub(r"\\citet\{([^}]+)\}", r"[\1]", body)
    body = re.sub(r"\\citep\{([^}]+)\}", r"[\1]", body)
    body = re.sub(r"\\cite\{([^}]+)\}", r"[\1]", body)
    body = re.sub(r"\(/compendium/", "(https://yoon-gu.github.io/compendium/", body)
    return body.strip() + "\n"


def build_pdf(slug: str, md_path: Path, title_suffix: str):
    meta, body = load_frontmatter_and_body(md_path)
    workdir = REPO / 'papers-tex' / slug
    workdir.mkdir(parents=True, exist_ok=True)
    temp_md = workdir / 'korean-translation.md'
    tex_out = workdir / 'main.tex'
    pdf_out = REPO / 'static' / 'papers' / f'{slug}.pdf'

    title = f"{meta['title']} {title_suffix}"
    author = meta.get('author', '') + "\\\\한국어 번역: Compendium (https://yoon-gu.github.io/compendium/)"
    cleaned = clean_body(body, slug)
    temp_md.write_text(cleaned, encoding='utf-8')

    common = [
        'pandoc', str(temp_md),
        '--standalone',
        '--from', 'markdown+tex_math_dollars+tex_math_single_backslash+raw_tex',
        '--toc',
        '--number-sections',
        '--pdf-engine=xelatex',
        '-H', str(HEADER),
        '-V', f'title={title}',
        '-V', f'author={author}',
        '-V', 'date=',
        '-V', 'linkcolor=blue',
        '-V', 'urlcolor=blue',
    ]

    subprocess.run(common + ['-o', str(tex_out)], check=True, cwd=workdir)
    subprocess.run(common + ['-o', str(pdf_out)], check=True, cwd=workdir)


def main():
    for paper in PAPERS:
        build_pdf(paper['slug'], paper['md'], paper['title_suffix'])
        print(f"built {paper['slug']}")


if __name__ == '__main__':
    main()
