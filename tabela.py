import re

def remove_expressions(line):
    line = line.replace('==', '')
    line = line.replace('**', '')
    line = line.replace('*', '')
    line = re.sub(r'<!--SR:!.+?-->', '', line)  # Remove tudo entre <!--SR:! e -->
    line = re.sub(r'\^\w{6}', '', line)  # Remove '^' seguido de 6 caracteres alfanuméricos
    line = re.sub(r'\[\^\d+\]', '', line)  # Remove números entre "[^" e "]"
    return line.strip()

# Lê o arquivo 'Constituição da República Federativa do Brasil de 1988 - Lei Seca.md'
with open('Constituição da República Federativa do Brasil de 1988 - Lei Seca.md', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Abre o arquivo 'D.md' para escrita
with open('D.md', 'w', encoding='utf-8') as file:
    # Escreve os cabeçalhos da tabela com "Original" vindo antes de "Comentado"
    file.write('| Original | Comentado |\n')
    file.write('|----------|-----------|\n')
    
    footer_lines = []

    for line in lines:
        # Captura linhas com textos seguidos de números entre "[^" e "]:"
        if re.search(r'\[\^\d+\]:', line):
            footer_lines.append(line)
            continue

        if any(expr in line for expr in ['==', '*', '**', '<!--SR:!', '^']) or re.search(r'\^\w{6}', line):
            modified_line = remove_expressions(line)
            file.write(f'| {modified_line} | {line.strip()} |\n')

    # Adiciona as linhas capturadas anteriormente ao final da tabela, com o campo "Original" em branco
    for line in footer_lines:
        file.write(f'|  | {line.strip()} |\n')

print("Processamento concluído!")
