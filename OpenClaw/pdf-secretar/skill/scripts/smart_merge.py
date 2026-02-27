#!/usr/bin/env python3
"""
Intelligent PDF merging using document signatures and learned patterns.
Signature: ordered list of meaningful words (with possible duplicates) from first N words.
"""
import sys, argparse, json, os, re, datetime
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any, Set

# Add workspace venv to path
def add_workspace_to_path():
    ws = Path.home() / ".openclaw" / "workspace"
    venv = ws / ".venv" / "lib" / "python3.12" / "site-packages"
    if venv.exists():
        sys.path.insert(0, str(venv))

def ensure_dependencies():
    try:
        import PyPDF2
        import requests
        return True
    except ImportError as e:
        print(f"ERROR: Missing dependency: {e}", file=sys.stderr)
        print("Install with: uv pip install PyPDF2 requests", file=sys.stderr)
        return False

# Constants
DEFAULT_PATTERN_DB = Path("/media/temp/.smart_merge/patterns.json")
MIN_SIMILARITY_DEFAULT = 0.6
OPENROUTER_MODEL = "arcee-ai/trinity-large-preview:free"
ALLOWED_BASE_DIR = Path("/media/temp").resolve()

# Stopwords (partial)
STOPWORDS = {
    "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то", "все", "она", "так", "его", "но", "да", "ты", "к", "у", "же", "вы", "за", "бы", "по", "только",
    "ее", "мне", "было", "вот", "от", "меня", "еще", "нет", "о", "из", "ему", "теперь", "когда", "даже", "ну", "вдруг", "ли", "если", "уже", "или", "ни", "быть", "был",
    "него", "до", "вас", "нибудь", "опять", "уж", "вам", "ведь", "там", "потом", "себя", "ничего", "ей", "может", "они", "тут", "где", "есть", "надо", "ней", "для", "мы",
    "тебя", "их", "чем", "была", "сам", "чтоб", "без", "будто", "чего", "раз", "тоже", "себе", "под", "будет", "ж", "тогда", "кто", "этот", "того", "потому", "этого", "какой",
    "совсем", "ним", "здесь", "этом", "один", "почти", "мой", "тем", "чтобы", "nee", "сейчас", "были", "куда", "зачем", "всех", "никогда", "можно", "при", "наконец", "два", "об",
    "другой", "хоть", "после", "над", "больше", "тот", "через", "эти", "нас", "про", "всего", "них", "какая", "много", "разве", "три", "эту", "моя", "впрочем", "хорошо", "свою",
    "этой", "перед", "иногда", "лучше", "чуть", "том", "нельзя", "такой", "им", "более", "всегда", "конечно", "всю", "между"
}

def is_allowed_path(path: Path) -> bool:
    """Проверяет, что путь находится внутри /media/temp."""
    try:
        resolved = path.resolve()
        return resolved.is_relative_to(ALLOWED_BASE_DIR)
    except Exception:
        return False

def extract_first_words(pdf_path: str, num_words: int = 300) -> str:
    from PyPDF2 import PdfReader
    try:
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            if len(reader.pages) == 0:
                return ""
            first_page = reader.pages[0]
            text = first_page.extract_text() or ""
            words = text.split()
            return " ".join(words[:num_words])
    except Exception as e:
        print(f"ERROR: extract_first_words {pdf_path}: {e}", file=sys.stderr)
        return ""

def clean_text(text: str) -> List[str]:
    """
    Оставляет только значимые слова и цифровые последовательности после маркеров номеров.
    Токены: буквы+цифры. Дубликаты сохраняются. Порядок сохраняется.
    """
    pattern = re.compile(r'\b[а-яА-ЯёЁa-zA-Z0-9]+\b')
    matches = list(pattern.finditer(text))
    if not matches:
        return []

    sentence_starts: Set[int] = {0}
    for m in re.finditer(r'(?<=[.!?])\s+([А-ЯA-Z])', text):
        sentence_starts.add(m.start(1))
    for m in re.finditer(r'(?<=\n\n)\s*([А-ЯA-Z])', text):
        sentence_starts.add(m.start(1))
    for m in re.finditer(r'(?<=\r\n\r\n)\s*([А-ЯA-Z])', text):
        sentence_starts.add(m.start(1))

    cleaned: List[str] = []
    name_suffixes = (
        "а","аго","ай","ая","бург","ев","евич","евна","евская","ево","ей","енка","енко",
        "ец","ёв","ея","и","ич","ична","ичи","ицы","ий","инична","инская","ия","ка",
        "ко","ная","нинская","ное","ов","ович","овка","овна","ово","овая","ой","поль",
        "полье","ск","ская","ский","ской","ское","ук","цк","цкая","цкий","цкой","цкое",
        "чук","ы","ь","ья","ый","ых","ын","юк","я","яго","янка","яя"
    )

    def has_number_marker(pos: int) -> bool:
        context_start = max(0, pos - 30)
        context = text[context_start:pos]
        marker_re = re.compile(r'(№|#|номер(?:а|ом)?)\s*$')
        return bool(marker_re.search(context))

    for m in matches:
        word = m.group()
        start = m.start()
        if word.isdigit():
            if has_number_marker(start):
                cleaned.append(word)
            continue
        if len(word) <= 3:
            continue
        tok_lower = word.lower()
        if tok_lower in STOPWORDS:
            continue
        is_first = start in sentence_starts
        has_digit = any(c.isdigit() for c in word)
        if not has_digit and not is_first and word[0].isupper() and any(tok_lower.endswith(suf) for suf in name_suffixes) and not word.isupper():
            continue
        cleaned.append(tok_lower)
    return cleaned

def get_document_signature(pdf_path: str, num_words: int = 300) -> List[str]:
    raw = extract_first_words(pdf_path, num_words)
    return clean_text(raw)

def jaccard_similarity(a: List[str], b: List[str]) -> float:
    set_a = set(a)
    set_b = set(b)
    if not set_a or not set_b:
        return 0.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union > 0 else 0.0

def load_patterns(db_path: Path) -> List[Dict[str, Any]]:
    if db_path.exists():
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except Exception as e:
            print(f"WARNING: load patterns: {e}", file=sys.stderr)
    return []

def save_patterns(db_path: Path, patterns: List[Dict[str, Any]]):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with open(db_path, 'w', encoding='utf-8') as fout:
        json.dump(patterns, fout, ensure_ascii=False, indent=2)

def find_matching_pattern(signatures: List[List[str]], patterns: List[Dict[str, Any]], min_similarity: float) -> Optional[List[int]]:
    n = len(signatures)
    best_pattern = None
    best_score = -1.0
    for pat in patterns:
        if len(pat.get("signatures", [])) != n:
            continue
        pat_sigs = pat["signatures"]
        scores = []
        for cs in signatures:
            max_sim = max(jaccard_similarity(cs, ps) for ps in pat_sigs)
            scores.append(max_sim)
        avg_sim = sum(scores) / len(scores) if scores else 0.0
        if avg_sim >= min_similarity and avg_sim > best_score:
            best_score = avg_sim
            best_pattern = pat
    if best_pattern:
        return best_pattern["order"]
    return None

def ask_model_for_order(docs_info: List[Tuple[str, List[str]]], mock: bool = False) -> Optional[List[int]]:
    import requests
    env_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if mock or not env_key:
        if not env_key:
            print("WARNING: No API key found, using mock model response", file=sys.stderr)
        indexed = list(enumerate(docs_info))
        indexed.sort(key=lambda x: (len(x[1][1]), Path(x[1][0]).name), reverse=True)
        return [idx for idx, _ in indexed]
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {env_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://openclaw.ai",
                "X-Title": "OpenClaw smart_merge"
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [{"role": "user", "content": build_prompt(docs_info)}],
                "temperature": 0.1,
                "max_tokens": 200
            },
            timeout=120
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"].strip()
        try:
            obj = json.loads(content)
            order = obj.get("order")
            if isinstance(order, list) and all(isinstance(i, int) for i in order):
                return order
        except json.JSONDecodeError:
            pass
        import re
        nums = re.findall(r'\b\d+\b', content)
        if len(nums) >= len(docs_info):
            order = [int(n) for n in nums[:len(docs_info)]]
            if set(order) == set(range(len(docs_info))):
                print(f"WARNING: model returned plain numbers, used as order: {order}", file=sys.stderr)
                return order
        print(f"ERROR: Could not parse order from model output: {content}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERROR: Request to model failed: {e}", file=sys.stderr)
        return None

def build_prompt(docs_info: List[Tuple[str, List[str]]]) -> str:
    prompt_lines = [
        "You are a document ordering assistant. Determine the logical order to merge these documents based on their content signatures.",
        "Rules (by priority):",
        "1. High priority: Find the main document (defines the sequence). Others that don't fit go to the end.",
        "2. Medium priority: Logical flow from fundamental to attachments/clarifications.",
        "3. Low priority: Find overall theme and fit documents into it.",
        "Return ONLY a valid JSON object with a single key 'order' containing a list of zero-based indices, e.g., {\"order\": [1,0,2]}.",
        "Do not include any extra text, explanation, or markdown. Pure JSON only.",
        "Documents (signatures are ordered by first occurrence, duplicates kept):"
    ]
    for idx, (name, sig) in enumerate(docs_info):
        sig_str = ", ".join(sig[:50])
        prompt_lines.append(f"{idx}: {Path(name).name} (signature: [{sig_str}])")
    return "\n".join(prompt_lines)

def merge_pdfs(file_list: List[str], output_path: str):
    from PyPDF2 import PdfReader, PdfWriter
    writer = PdfWriter()
    total_pages = 0
    for f in file_list:
        try:
            with open(f, 'rb') as fh:
                r = PdfReader(fh)
                for p in r.pages:
                    writer.add_page(p)
                    total_pages += 1
            print(f"Added: {Path(f).name} ({len(r.pages)} стр.)")
        except Exception as e:
            print(f"ERROR: add {f}: {e}", file=sys.stderr)
    with open(output_path, 'wb') as fout:
        writer.write(fout)
    print(f"Объединено: {len(file_list)} файлов, {total_pages} страниц -> {output_path}")

def main():
    add_workspace_to_path()
    if not ensure_dependencies():
        sys.exit(1)
    parser = argparse.ArgumentParser(description="Интеллектуальное объединение PDF по смыслу (сигнатуры + шаблоны)")
    parser.add_argument("--files", "-f", required=True, help="Маска файлов, например: '/media/temp/*.pdf'")
    parser.add_argument("--output", help="Выходной файл (если не указан, будет создан на основе первого документа, например: doc_merged.pdf)")
    parser.add_argument("--use-patterns", action=argparse.BooleanOptionalAction, default=True,
                        help="Использовать базу шаблонов (по умолчанию True). Отключить: --no-use-patterns")
    parser.add_argument("--pattern-db", default=str(DEFAULT_PATTERN_DB),
                        help=f"Путь к файлу базы шаблонов (JSON). По умолчанию: {DEFAULT_PATTERN_DB}")
    parser.add_argument("--min-similarity", type=float, default=MIN_SIMILARITY_DEFAULT,
                        help="Порог сходства для поиска шаблона (0-1)")
    parser.add_argument("--no-confirm", action="store_true",
                        help="Не запрашивать подтверждение перед объединением")
    parser.add_argument("--mock-model", action="store_true",
                        help="Имитировать ответ модели (для тестов без API ключа)")
    args = parser.parse_args()

    pattern_db_path = Path(args.pattern_db)

    from glob import glob
    files = sorted(glob(args.files))
    if not files:
        print(f"ERROR: нет файлов по маске: {args.files}", file=sys.stderr)
        sys.exit(1)

    # Валидация путей: все файлы должны быть внутри /media/temp
    for fp in files:
        if not is_allowed_path(Path(fp)):
            print(f"ERROR: Path not allowed (outside /media/temp): {fp}", file=sys.stderr)
            sys.exit(1)

    # Определяем выходной путь
    if args.output:
        output_path = Path(args.output)
    else:
        # Берём первый файл в порядке (пока未知 порядок, но возьмём первый из отсортированного списка, если шаблон/модель не сработали)
        # После определения порядка можно переименовать, но для простоты возьмём первый файл из отсортированного списка имён
        first_file = Path(files[0])
        output_path = first_file.parent / f"{first_file.stem}_merged.pdf"
    # Проверка выходного пути
    if not is_allowed_path(output_path):
        print(f"ERROR: Output path not allowed (outside /media/temp): {output_path}", file=sys.stderr)
        sys.exit(1)

    # Проверка существования файлов и расширения .pdf
    for fp in files:
        p = Path(fp)
        if not p.is_file():
            print(f"ERROR: File not found or not a regular file: {fp}", file=sys.stderr)
            sys.exit(1)
        if p.suffix.lower() != ".pdf":
            print(f"ERROR: Not a PDF file: {fp}", file=sys.stderr)
            sys.exit(1)

    print(f"Файлов: {len(files)}")
    signatures: List[List[str]] = []
    for fp in files:
        sig = get_document_signature(fp, num_words=300)
        if not sig:
            print(f"WARNING: пустая сигнатура для {Path(fp).name}")
        signatures.append(sig)
        print(f"  {Path(fp).name}: сигнатура {len(sig)} слов (первые: {', '.join(sig[:15])})")

    order: Optional[List[int]] = None
    patterns: List[Dict[str, Any]] = []
    if args.use_patterns:
        patterns = load_patterns(pattern_db_path)
        print(f"База шаблонов: {len(patterns)} записей")
        order = find_matching_pattern(signatures, patterns, args.min_similarity)
        if order:
            print(f"Найдён подходящий шаблон (сходство >= {args.min_similarity}). Порядок: {order}")
        else:
            print("Подходящий шаблон не найден. Запрашиваем порядок у модели...")

    if order is None:
        docs_info = [(fp, sig) for fp, sig in zip(files, signatures)]
        order = ask_model_for_order(docs_info, mock=args.mock_model)
        if order is None:
            print("ERROR: не удалось получить порядок от модели", file=sys.stderr)
            sys.exit(1)

    if set(order) != set(range(len(files))):
        print(f"ERROR: модель вернула некорректный порядок: {order}", file=sys.stderr)
        sys.exit(1)

    # Если output не был задан, теперь формируем на основе первого документа в порядке
    if not args.output:
        first_idx = order[0]
        first_file = Path(files[first_idx])
        output_path = first_file.parent / f"{first_file.stem}_merged.pdf"
        # Повторно проверим allowed (должно быть true, так как тот же каталог)
        if not is_allowed_path(output_path):
            print(f"ERROR: Generated output path not allowed: {output_path}", file=sys.stderr)
            sys.exit(1)

    print("Предлагаемый порядок объединения:")
    for pos, idx in enumerate(order):
        print(f"  {pos+1}. {Path(files[idx]).name}")

    if not args.no_confirm:
        resp = input("Подтвердить объединение? (y/N): ").strip().lower()
        if resp != 'y':
            print("Отменено пользователем.")
            sys.exit(0)

    sorted_files = [files[i] for i in order]
    merge_pdfs(sorted_files, str(output_path))

    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "signatures": [sig for sig in signatures],
        "order": order
    }
    patterns.append(entry)
    save_patterns(pattern_db_path, patterns)
    print(f"Шаблон сохранён в: {pattern_db_path}")
    print(f"Результат: {output_path}")

if __name__ == "__main__":
    main()