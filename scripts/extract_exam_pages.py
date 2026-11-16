from pathlib import Path
import hashlib, json
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / '工作底稿' / 'pages'
out.mkdir(parents=True, exist_ok=True)
manifest = []
for path in sorted((ROOT / '真题').glob('*.pdf')):
    year = int(path.name[:4])
    reader = PdfReader(path)
    directory = out / str(year)
    directory.mkdir(exist_ok=True)
    pages = []
    for index, page in enumerate(reader.pages, 1):
        target = directory / f'{index:02}.png'
        if not target.exists():
            if len(page.images) == 1:
                img = page.images[0].image.convert('RGB')
                img.thumbnail((2400, 2500))
                img.save(target)
            else:
                import pypdfium2 as pdfium
                doc = pdfium.PdfDocument(str(path))
                img = doc[index-1].render(scale=2.5).to_pil()
                img.thumbnail((2400, 2500))
                img.save(target)
        pages.append({'pdf_page': index, 'image': str(target.relative_to(ROOT))})
    manifest.append({'year':year,'file':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pages':pages})
    print(year, len(pages), flush=True)
(ROOT / '工作底稿' / 'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
