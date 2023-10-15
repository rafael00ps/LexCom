import requests
import html2text
import re
import difflib
import os

def remove_spaces_and_gt_at_beginning_of_paragraphs(text):
    lines = text.split("\n")
    cleaned_lines = [line.lstrip(" >") for line in lines]
    return "\n".join(cleaned_lines)


def adjust_titles_chapters_sections_and_subsections(text):

    def replace_parte(match):
        return "# " + match.group(1) + " " + match.group(2) + "\n"

    def replace_title(match):
        title_text = ' '.join(match.group(2).split()).replace('- -', '-')
        return "## " + match.group(1) + " - " + title_text
    
    def replace_chapter(match):
        chapter_title = ' '.join(match.group(4).split()).replace('- -', '-').replace('- ', '-')
        return "### " + match.group(1) + (match.group(3) or "") + " - " + chapter_title
        
    def replace_section(match):
        section_title = ' '.join(match.group(2).split())
        return "#### " + match.group(1) + " - " + section_title

    def replace_subsection(match):
        return "##### " + match.group(1) + " - " + match.group(2)

    parte_pattern = re.compile(r"(PARTE)\s([^\n]+)")
    title_pattern = re.compile(r"(TÍTULO [IVXLC]+)((?:\s*\([^\)]+\))*\s*(?:[^\n]+(?:\n[^\n]+)*))")
    chapter_pattern = re.compile(r"(CAPÍTULO [IVXLC]+)(\s*(-[A-Z]))?((?:\s*\([^\)]+\))*\s*(?:[^\n]+(?:\n[^\n]+)*))")
    section_pattern = re.compile(r"(SEÇÃO [IVXLC]+)((?:\s*\([^\)]+\))*\s*(?:[^\n]+(?:\n[^\n]+)*))")
    subsection_pattern = re.compile(r"(Subseção [IVXLC]+)\n\n([^\n]+)")
    
    adjusted_text = parte_pattern.sub(replace_parte, text)
    adjusted_text = title_pattern.sub(replace_title, adjusted_text)
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
        r'\(Vide ADI .+?\)',
        r'\(Redação dada .+?\)',
        r'\(Incluído pela .+?\)',        
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

def remove_multiple_linebreaks(text):
    return re.sub(r'\n{3,}', '\n{2,}', text)


def fix_section_v(text):
    section_v_pattern = r"Seção V\n\n\n\nDo Tribunal Superior do Trabalho, dos Tribunais Regionais\n\ndo Trabalho e dos Juízes do Trabalho"
    section_v_replacement = "### Seção V - Do Tribunal Superior do Trabalho, dos Tribunais Regionais do Trabalho e dos Juízes do Trabalho"
    
    return re.sub(section_v_pattern, section_v_replacement, text)


#def remove_trailing_empty_lines(text):
#    return re.sub(r'\n+\Z', '', text)



def get_markdown_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
    response = requests.get(url, headers=headers)
    content = response.text

    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    h.ignore_tables = True
    h.ignore_anchors = True
    h.body_width = 0

    markdown_text = h.handle(content)

    markdown_text = remove_spaces_and_gt_at_beginning_of_paragraphs(markdown_text)

    # Removendo trechos indesejados "~~~~ "
    markdown_text = markdown_text.replace("~~~~ ", "")

    # Removendo trechos indesejados "~~~ "
    markdown_text = markdown_text.replace("~~", "")

    # Removendo trechos indesejados "_"
    markdown_text = markdown_text.replace("_", "")

    markdown_text = markdown_text.replace("\n)", "")


    # Removendo trechos indesejados "_"
    markdown_text = markdown_text.replace("\\", "")


    # Removendo trechos que começam com "**"
    markdown_text = remove_double_asterisks(markdown_text)

    markdown_text = remove_hashtags(markdown_text)

    # Removendo espaços no final dos parágrafos
    markdown_text = remove_spaces_at_end_of_paragraphs(markdown_text)

    # Removendo referências indesejadas
    markdown_text = remove_references(markdown_text)

    # Removendo vírgulas e espaços extras
    markdown_text = remove_extra_commas_and_spaces(markdown_text)

    markdown_text = remove_spaces_and_gt_at_beginning_of_paragraphs(markdown_text)

    # Ajustando os títulos, capítulos, seções e subseções
    markdown_text = adjust_titles_chapters_sections_and_subsections(markdown_text)

    # Corrigindo a Seção V específica
    markdown_text = fix_section_v(markdown_text)

    # Removendo múltiplas quebras de linha seguidas
    markdown_text = remove_multiple_linebreaks(markdown_text)

    markdown_text = markdown_text.replace("{2,}", "\n")

    markdown_text = markdown_text.replace("", "-")

    return markdown_text



def read_paragraphs(file):
    with open(file, 'r') as f:
        content = f.read()
        paragraphs = content.split('\n\n')
    return paragraphs

def write_paragraphs(file, paragraphs):
    with open(file, 'w') as f:
        content = '\n\n'.join(paragraphs)
        f.write(content)

def remover_marcacoes(texto):

    # Remover apenas os sinais "==", "*" e "**" e manter o conteúdo entre eles
    texto = re.sub(r'(={2}|\*{1,2})([^=]+)(={2}|\*{1,2})', r'\2', texto)

    # Remover expressões entre "<!--SR:!" e "-->"
    texto = re.sub(r'<!--SR:![^>]+-->\n', '', texto)

    # Remover expressões entre "<!--SR:!" e "-->"
    texto = re.sub(r'<!--SR:![^>]+-->', '', texto)

    # Remover textos seguidos de números entre "[^" e "]:", e o texto até a quebra de linha
    #padrao = r'\[\^\d+\]:.*\n?'
    #texto = re.sub(padrao, '', texto)

    # Encontrar todas as ocorrências da expressão com quebras de linha
    padrao = r'\[\^\d+\]:.*\n?'
    ocorrencias = re.finditer(padrao, texto)

    # Contar o número de vezes que a expressão é encontrada
    global total_ocorrencias
    total_ocorrencias = 0
    for ocorrencia in ocorrencias:
        total_ocorrencias += 1

    print(f"Total de ocorrências da expressão: {total_ocorrencias}")

    # Remover números entre "[^" e "]"
    texto = re.sub(r'\[\^(\d+)](?!:)', '', texto)
    
    # Remover textos com "^" seguidos de 6 caracteres alfanuméricos
    texto = re.sub(r' \^[\w\d]{6}', '', texto)

    # Remover a expressão que inaugura o texto e que se situa entre "---"
#    texto = re.sub(r'---.*?---\n*(.*\S.*)', r'\1', texto, flags=re.DOTALL)

    # Encontrar todas as ocorrências da expressão com quebras de linha
    ocorrencias = re.finditer(r'(---\n)(.*?\n)(---)', texto, flags=re.DOTALL)

    # Contar o número de quebras de linha em cada ocorrência
    global total_quebras_de_linha
    total_quebras_de_linha = 0
    for ocorrencia in ocorrencias:
        # Adiciona 2 para considerar as quebras de linha antes e depois de cada '---'
        quebras_de_linha = ocorrencia.group(2).count('\n') + 3
        total_quebras_de_linha += quebras_de_linha

    print(f"Total de quebras de linha: {total_quebras_de_linha}")

    return texto



def compare_and_update_files(markdown_text, file_b, skip_lines=None, skip_lines_end=None):
    paragraphs_a = markdown_text.split('\n\n')  # Atualize esta linha para ler 'markdown_text' em vez de 'file_a'
    paragraphs_b = read_paragraphs(file_b)
    str1 = '\n\n'.join(paragraphs_a)
    str2 = '\n\n'.join(paragraphs_b)

    str2_limpio = remover_marcacoes(str2)

    if skip_lines is None:
        skip_lines = total_quebras_de_linha

    if skip_lines_end is None:
        skip_lines_end = total_ocorrencias + 1

    matcher = difflib.SequenceMatcher()
    # Removendo a parte que ignora as linhas finais de str2_limpio
    matcher.set_seqs(str1.splitlines(keepends=True), str2_limpio.splitlines(keepends=True)[skip_lines:])

    updated_str_b = ''.join(str2.splitlines(keepends=True)[:skip_lines])
    last_match_b = 0

    for match in matcher.get_matching_blocks():
        i, j, n = match

        # Add non-matching paragraphs from A before the current match
        updated_str_b += ''.join(str1.splitlines(keepends=True)[last_match_b:i])

        # Add matching paragraphs from B
        updated_str_b += ''.join(str2.splitlines(keepends=True)[j + skip_lines:j + n + skip_lines])

        last_match_b = i + n

    # Add any remaining non-matching paragraphs from A
    updated_str_b += ''.join(str1.splitlines(keepends=True)[last_match_b:])

    # Adicionando o trecho final de str2 ao resultado
    updated_str_b += ''.join(str2.splitlines(keepends=True)[-skip_lines_end:])

    write_paragraphs(file_b, updated_str_b.split('\n\n'))



# Lista de URLs e arquivos para processar
urls = ['https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm']
files_list = ['/Users/rafael/Alma/Quaternum/Legislação/Decreto-Lei nº 2.848, de 7 de Dezembro de 1940.md']

# Iterando através das URLs e das listas de arquivos correspondentes
for url, file_b in zip(urls, files_list):
    markdown_text = get_markdown_from_url(url)
    compare_and_update_files(markdown_text, file_b)