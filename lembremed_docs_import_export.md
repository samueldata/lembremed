## Importação e Exportação de Dados

O sistema LembreMed oferece recursos completos para importação e exportação de dados, permitindo a interoperabilidade e backup de informações essenciais.

### Exportação de Dados

A funcionalidade de exportação permite extrair todos os dados de administrações de medicamentos e informações relacionadas em formato CSV padronizado. Este recurso é especialmente útil para:

- Backup de dados
- Análise estatística externa
- Geração de relatórios personalizados
- Compartilhamento de dados com outros sistemas

#### Como exportar dados:

1. Acesse a página de **Relatórios**
2. Clique no botão "Exportar Dados" no canto superior direito
3. Escolha entre:
   - **Exportar todos os dados**: Exporta todas as administrações e dados relacionados
   - **Exportar com filtros**: Permite selecionar um período específico para exportação

O arquivo CSV gerado segue o mesmo formato utilizado na importação, garantindo compatibilidade para restauração de dados quando necessário.

#### Via linha de comando:

Também é possível exportar dados via linha de comando, usando o comando de gerenciamento personalizado:

```bash
python manage.py exportar_administracoes caminho_do_arquivo.csv [cnpj_instituicao] [--periodo_inicio YYYY-MM-DD] [--periodo_fim YYYY-MM-DD]
```

### Importação de Dados

O sistema permite a importação de dados em massa através de arquivos CSV padronizados, facilitando:

- Migração de dados de outros sistemas
- Restauração de backups
- Carga inicial de dados para testes ou implantação

#### Via linha de comando:

A importação é realizada através do comando de gerenciamento:

```bash
python manage.py importar_administracoes caminho_do_arquivo.csv cnpj_instituicao
```

#### Formato do CSV:

O arquivo CSV deve seguir um formato específico, contendo colunas para todos os dados necessários:
- Dados do morador (nome, CPF, data de nascimento)
- Dados do medicamento (nome, concentração, uso contínuo)
- Dados da administração (data/hora prevista, data/hora real)
- Dados do profissional responsável
- Informações de estoque e horários

Para exemplos de arquivos no formato correto, consulte os arquivos de exemplo incluídos no projeto (`lembremed_template_import_export.csv`).
