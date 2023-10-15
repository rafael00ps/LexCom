import re
import difflib
import requests
import html2text
import csv
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


DIRETORIO = '/Users/rafael/Alma/Direito/Legislação/Lei nº 8.078, de 11 de Setembro de 1990.md'
TABELA = '/Users/rafael/Library/Mobile Documents/com~apple~CloudDocs/Code/Lexcom/CDCT.md'


header = """---
Aliases: CDC, Código de Defesa do Consumidor
Tags: Legislação
Publicação: 1990-09-12
Retificação: 2007-01-10
obsidianUIMode: preview
---

"""



def remove_expressions(line):
    line = line.replace('==', '')
    line = line.replace('**', '')
    line = line.replace('*', '')
    line = re.sub(r'<!--SR:!.+?-->', '', line)  # Remove tudo entre <!--SR:! e -->
    line = re.sub(r'\^\w{6}', '', line)  # Remove '^' seguido de 6 caracteres alfanuméricos
    line = re.sub(r'\[\^\d+\]', '', line)  # Remove números entre "[^" e "]"
    return line.strip()

with open(DIRETORIO, 'r', encoding='utf-8') as file:
    lines = file.readlines()


def merge_sr_lines(lines):
    """Merging lines that start with <!--SR: with the previous line."""
    merged_lines = []
    skip_next = False
    for i in range(len(lines)):
        if skip_next:
            skip_next = False
            continue
        if i < len(lines) - 1 and lines[i+1].startswith('<!--SR:'):
            merged_line = lines[i].strip() + " " + lines[i+1].strip()
            merged_lines.append(merged_line)
            skip_next = True
        else:
            merged_lines.append(lines[i].strip())
    return merged_lines

with open(DIRETORIO, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Adjusting lines by merging those with <!--SR: to the previous one.
lines = merge_sr_lines(lines)

with open('CDCT.md', 'w', encoding='utf-8') as file:
    file.write('| Original | Comentado |\n')
    file.write('|----------|-----------|\n')
    
    footer_lines = []

    for line in lines:
        if re.search(r'\[\^\d+\]:', line):
            footer_lines.append(line)
            continue

        if any(expr in line for expr in ['==', '*', '**', '<!--SR:!', '^']) or re.search(r'\^\w{6}', line):
            modified_line = remove_expressions(line)
            file.write(f'| {modified_line} | {line.strip()} |\n')

    for line in footer_lines:
        file.write(f'|  | {line.strip()} |\n')


def remove_spaces_and_gt_at_beginning_of_paragraphs(text):
    lines = text.split("\n")
    cleaned_lines = [line.lstrip(" >") for line in lines]
    return "\n".join(cleaned_lines)

def adjust_titles_chapters_sections_and_subsections(text):


    def replace_title(match):
        title_text = ' '.join(match.group(2).split()).replace('- -', '-')
        return "# " + match.group(1) + " - " + title_text
    
    def replace_chapter(match):
        chapter_title = ' '.join(match.group(4).split()).replace('- -', '-').replace('- ', '-')
        return "## " + match.group(1) + (match.group(3) or "") + " - " + chapter_title
        
    def replace_section(match):
        section_title = ' '.join(match.group(2).split())
        return "### " + match.group(1) + " - " + section_title

    def replace_subsection(match):
        return "#### " + match.group(1) + " - " + match.group(2)

    title_pattern = re.compile(r"(TÍTULO [IVXLC]+)((?:\s*\([^\)]+\))*\s*(?:[^\n]+(?:\n[^\n]+)*))")
    chapter_pattern = re.compile(r"(CAPÍTULO [IVXLC]+)(\s*(-[A-Z]))?((?:\s*\([^\)]+\))*\s*(?:[^\n]+(?:\n[^\n]+)*))", re.IGNORECASE)
    section_pattern = re.compile(r"(SEÇÃO [IVXLC]+)((?:\s*\([^\)]+\))*\s*(?:[^\n]+(?:\n[^\n]+)*))", re.IGNORECASE)
    subsection_pattern = re.compile(r"(Subseção [IVXLC]+)\n\n([^\n]+)")
    
    adjusted_text = title_pattern.sub(replace_title, text)
    adjusted_text = chapter_pattern.sub(replace_chapter, adjusted_text)
    adjusted_text = section_pattern.sub(replace_section, adjusted_text)
    adjusted_text = subsection_pattern.sub(replace_subsection, adjusted_text)
    
    return adjusted_text


def remove_double_asterisks(text):
    return text.replace("**", "")

def remove_hashtags(text):
    return text.replace("#", "")

def remove_spaces_at_end_of_paragraphs(text):
    lines = text.split("\n")
    cleaned_lines = [line.rstrip() for line in lines]
    return "\n".join(cleaned_lines)

def remove_references(text):
    reference_patterns = [
        r'\(Vide Lei nº .+?\)',
        r'\(Vide DLG .+?\)',
        r'\(Vide Decreto .+?\)',
        r'\(Vide ADIN .+?\)',
        r'\(Redação dada .+?\)',
        r'\(Incluído pela .+?\)',
        r'\(Incluída pela .+?\)',        
    ]
    
    for pattern in reference_patterns:
        text = re.sub(pattern, "", text)
    
    return text

def remove_extra_commas_and_spaces(text):
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = re.sub(r'\s*,\s*,\s*', ', ', line)  # Remove sequências de vírgulas e espaços
        line = re.sub(r' {2,}', ' ', line)  # Remove espaços em branco consecutivos
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

def fix_section_v(text):
    section_v_pattern = r"Seção V\n\n\n\nDo Tribunal Superior do Trabalho, dos Tribunais Regionais\n\ndo Trabalho e dos Juízes do Trabalho"
    section_v_replacement = "### Seção V - Do Tribunal Superior do Trabalho, dos Tribunais Regionais do Trabalho e dos Juízes do Trabalho"
    
    return re.sub(section_v_pattern, section_v_replacement, text)

def get_markdown_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
    response = requests.get(url, headers=headers, verify=False)
    content = response.text

    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    h.ignore_tables = True
    h.ignore_anchors = True
    h.body_width = 0

    markdown_text = h.handle(content)
    markdown_text = remove_spaces_and_gt_at_beginning_of_paragraphs(markdown_text)
    markdown_text = markdown_text.replace("~~~~ ", "")
    markdown_text = markdown_text.replace("\\", "")
    markdown_text = markdown_text.replace("_", "")
    markdown_text = markdown_text.replace("", "-")
    markdown_text = remove_double_asterisks(markdown_text)
    markdown_text = remove_hashtags(markdown_text)
    markdown_text = remove_references(markdown_text)
    markdown_text = remove_extra_commas_and_spaces(markdown_text)
    markdown_text = remove_spaces_and_gt_at_beginning_of_paragraphs(markdown_text)
    markdown_text = adjust_titles_chapters_sections_and_subsections(markdown_text)
    markdown_text = fix_section_v(markdown_text)
    markdown_text = remove_multiple_linebreaks(markdown_text)
    markdown_text = markdown_text.replace("{2,}", "\n")
    markdown_text = remove_spaces_at_end_of_paragraphs(markdown_text)
    return markdown_text

def remove_multiple_linebreaks(text):
    return re.sub(r'\n{3,}', '\n\n', text)

def read_paragraphs(file):
    with open(file, 'r') as f:
        content = f.read()
        paragraphs = content.split('\n\n')
    return paragraphs

def write_paragraphs(file, paragraphs):
    with open(file, 'w') as f:
        content = '\n\n'.join(paragraphs)
        f.write(content)

def compare_and_update_files(markdown_text, file_b):
    paragraphs_a = markdown_text.split('\n\n')
    paragraphs_b = read_paragraphs(file_b)

    matcher = difflib.SequenceMatcher()
    matcher.set_seqs(paragraphs_b, paragraphs_a)

    opcodes = matcher.get_opcodes()

    new_paragraphs_b = []
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'equal' or tag == 'replace':
            new_paragraphs_b.extend(paragraphs_a[j1:j2])
        elif tag == 'insert':
            new_paragraphs_b.extend(paragraphs_a[j1:j2])

    updated_str_b = '\n\n'.join(new_paragraphs_b)

    write_paragraphs(file_b, updated_str_b.split('\n\n'))

urls = ['http://www.planalto.gov.br/ccivil_03/Leis/L8078compilado.htm']
files_list = [DIRETORIO]

for url, file_b in zip(urls, files_list):
    markdown_text = get_markdown_from_url(url)
    compare_and_update_files(markdown_text, file_b)

def ler_tabela():
    substituicoes = {}
    anexos = []
    with open(TABELA, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='|')
        for row in reader:
            original = row[' Original '].strip()
            comentado = row[' Comentado '].strip()
            if original and comentado:
                substituicoes[original] = comentado
            elif comentado:
                anexos.append(comentado)
    return substituicoes, anexos

def aplicar_substituicoes_e_anexos(conteudo, substituicoes, anexos):
    for original, comentado in substituicoes.items():
        pattern = re.escape(original)
        conteudo = re.sub(pattern, comentado, conteudo)
    for anexo in anexos:
        conteudo += '\n' + anexo


    # Adicionando quebra de linha antes de <!--SR:
    conteudo = re.sub(r'<!--SR:', '\n<!--SR:', conteudo)


    return conteudo

with open(DIRETORIO, 'r', encoding='utf-8') as file:
    conteudo = file.read()

substituicoes, anexos = ler_tabela()
conteudo_modificado = aplicar_substituicoes_e_anexos(conteudo, substituicoes, anexos)

with open(DIRETORIO, 'w', encoding='utf-8') as file:
    file.write(header + conteudo_modificado)

