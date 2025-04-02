import mysql.connector
import matplotlib.pyplot as plt
import io
import base64


table_name = 'x'
date_column = 'x'
start_year = x
end_year = x


config = {
    'host': 'x',
    'user': 'x',
    'password': 'x',
    'database': 'x'
}

try:

    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    # Obter o número exato de registros no período desejado
    query_count = f"""
    SELECT COUNT(*) 
    FROM {table_name}
    WHERE {date_column} BETWEEN '{start_year}-01-01 00:00:00' AND '{end_year}-12-31 23:59:59';
    """
    cursor.execute(query_count)
    total_registros_periodo = cursor.fetchone()[0]

    #Obter estatísticas da tabela a partir do information_schema
    query_info = """
    SELECT 
      (data_length + index_length) AS total_bytes,
      table_rows
    FROM information_schema.tables
    WHERE table_schema = %s
      AND table_name = %s;
    """
    cursor.execute(query_info, (config['database'], table_name))
    result = cursor.fetchone()
    total_bytes = result[0]
    total_linhas_est = result[1]

    cursor.close()
    cnx.close()

    #Calcular o tamanho médio por registro (utilizando as estatísticas atualizadas)
    if total_linhas_est and total_linhas_est > 0:
        tamanho_medio_linha = total_bytes / total_linhas_est
    else:
        tamanho_medio_linha = 0

    #Estimar o tamanho total dos registros do período (em bytes)
    tamanho_estimado_bytes = tamanho_medio_linha * total_registros_periodo

    # Converter os valores para gigabytes (1 GB = 1024^3 bytes)
    bytes_to_gb = 1024 * 1024 * 1024
    total_size_gb = total_bytes / bytes_to_gb
    estimated_freed_gb = tamanho_estimado_bytes / bytes_to_gb
    estimated_remaining_gb = total_size_gb - estimated_freed_gb


    labels = ['Tamanho Atual (GB)', 'Após Expurgo (Estimado)']
    values = [total_size_gb, estimated_remaining_gb]

    plt.figure(figsize=(8, 6))
    barras = plt.bar(labels, values, color=['blue', 'green'])
    plt.title('Comparação de Tamanho da Tabela')
    plt.ylabel('Tamanho (GB)')
    for bar in barras:
        altura = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, altura, f'{altura:.2f}', ha='center', va='bottom')
    plt.tight_layout()


    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    grafico_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()

    #Gerar o relatório em HTML com a descrição do método usado
    html_relatorio = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Relatório de Expurgo - {table_name}</title>
    </head>
    <body>
        <h1>Relatório de Expurgo - {table_name}</h1>
        <p><strong>Período:</strong> {start_year} a {end_year}</p>
        <h2>Método de Estimativa</h2>
        <p>
            Este relatório utiliza o COUNT(*) para obter o número exato de registros no período especificado. 
            Em seguida, utiliza as estatísticas atualizadas da tabela (obtidas do information_schema após a execução manual do ANALYZE TABLE) para calcular o tamanho total da tabela e o número estimado de linhas.
            O <strong>tamanho médio por registro</strong> é calculado como:
        </p>
        <p style="text-align: center;"><em>Tamanho Médio = (Total de Bytes da Tabela) / (Total de Linhas Estimado)</em></p>
        <p>
            O espaço estimado a ser liberado é calculado multiplicando-se o tamanho médio pelo número exato de registros do período. 
            Os valores são convertidos para gigabytes. 
            <strong>Observação:</strong> Estes valores são estimativas e podem ser menores ou maiores devido a overhead de armazenamento, índices e variações nos dados.
        </p>
        <h2>Métricas</h2>
        <table border="1" cellspacing="0" cellpadding="5">
            <tr>
                <th>Métrica</th>
                <th>Valor</th>
            </tr>
            <tr>
                <td>Total de registros no período ({start_year}-{end_year})</td>
                <td>{total_registros_periodo}</td>
            </tr>
            <tr>
                <td>Total de registros na tabela (estimado)</td>
                <td>{total_linhas_est}</td>
            </tr>
            <tr>
                <td>Tamanho total da tabela</td>
                <td>{total_size_gb:.2f} GB</td>
            </tr>
            <tr>
                <td>Tamanho médio por registro (estimado)</td>
                <td>{tamanho_medio_linha:.2f} bytes</td>
            </tr>
            <tr>
                <td>Espaço estimado a liberar (registros do período)</td>
                <td>{estimated_freed_gb:.2f} GB</td>
            </tr>
            <tr>
                <td>Tamanho estimado após expurgo</td>
                <td>{estimated_remaining_gb:.2f} GB</td>
            </tr>
        </table>
        <h2>Gráfico Comparativo</h2>
        <img src="data:image/png;base64,{grafico_base64}" alt="Gráfico de Tamanho da Tabela">
    </body>
    </html>
    """

    # Salvar o relatório em um arquivo HTML
    with open(f"{table_name}_relatorio.html", "w", encoding="utf-8") as f:
        f.write(html_relatorio)

    print(f"Relatório gerado com sucesso: {table_name}_relatorio.html")

except mysql.connector.Error as err:
    print(f"Erro: {err}")
