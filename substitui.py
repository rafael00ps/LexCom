import csv
import re

# Função para ler a tabela do arquivo e retornar dois dicionários
def ler_tabela():
    substituicoes = {}
    anexos = []
    with open('D.md', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='|')
        for row in reader:
            original = row[' Original '].strip()  # Remove os espaços extras nos nomes das colunas
            comentado = row[' Comentado '].strip()
            if original and comentado:  # Substituições
                substituicoes[original] = comentado
            elif comentado:  # Anexos
                anexos.append(comentado)
    return substituicoes, anexos

# Função para aplicar as substituições no conteúdo do arquivo e anexar textos
def aplicar_substituicoes_e_anexos(conteudo, substituicoes, anexos):
    for original, comentado in substituicoes.items():
        pattern = re.escape(original)  # Escapa caracteres especiais no texto original
        conteudo = re.sub(pattern, comentado, conteudo)
    # Anexando os textos ao final
    for anexo in anexos:
        conteudo += '\n' + anexo
    return conteudo

# Lê o conteúdo do arquivo Constituição da República Federativa do Brasil de 1988 - Lei Seca.md
with open('Constituição da República Federativa do Brasil de 1988 - Lei Seca.md', 'r', encoding='utf-8') as file:
    conteudo = file.read()

# Obtém as substituições e os anexos da tabela
substituicoes, anexos = ler_tabela()

# Aplica as substituições e anexa os textos
conteudo_modificado = aplicar_substituicoes_e_anexos(conteudo, substituicoes, anexos)

# Salva o conteúdo modificado de volta no arquivo Constituição da República Federativa do Brasil de 1988 - Lei Seca.md
with open('Constituição da República Federativa do Brasil de 1988 - Lei Seca.md', 'w', encoding='utf-8') as file:
    file.write(conteudo_modificado)
