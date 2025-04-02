import mysql.connector
import matplotlib.pyplot as plt
import io
import base64


config = {
    'host': 'x',
    'user': 'x',
    'password': 'x',
    'database': 'x'
}

try:

    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    query = """
    SELECT 
        table_name, 
        ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
    FROM information_schema.TABLES
    WHERE table_schema = %s
    ORDER BY (data_length + index_length) DESC
    LIMIT 10;
    """
    cursor.execute(query, (config['database'],))
    results = cursor.fetchall()

    cursor.close()
    cnx.close()

    tabelas = [row[0] for row in results]
    tamanhos = [row[1] for row in results]

    # Gera o gráfico de barras
    plt.figure(figsize=(12, 6))
    plt.bar(tabelas, tamanhos, color='steelblue')
    plt.xlabel('Tabelas')
    plt.ylabel('Tamanho (MB)')
    plt.title('Top 10 Tabelas - Tamanho no Banco de Dados')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()


    html_content = "<html><head><meta charset='utf-8'><title>Tamanho das Tabelas</title></head><body>"
    html_content += "<h1>Tamanho das Tabelas (em MB) - Top 10</h1>"
    html_content += "<table border='1' cellspacing='0' cellpadding='5'>"
    html_content += "<tr><th>Tabela</th><th>Tamanho (MB)</th></tr>"
    for t, s in zip(tabelas, tamanhos):
        html_content += f"<tr><td>{t}</td><td>{s}</td></tr>"
    html_content += "</table>"
    html_content += "<h2>Gráfico</h2>"
    html_content += f"<img src='data:image/png;base64,{image_base64}' alt='Gráfico de Tabelas'/>"
    html_content += "</body></html>"


    with open("maiores_tabelas.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Saída HTML gerada com sucesso: maiores_tabelas.html")

except mysql.connector.Error as err:
    print(f"Erro: {err}")
