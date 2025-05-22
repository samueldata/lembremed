<h1 align="center"> Grupo 14 - UNIVESP Projeto Integrador</h1>

<p align="center">
  <img src="https://img.shields.io/badge/PI%20I-Conclu%C3%ADdo%20com%20sucesso-2ecc71?style=for-the-badge&logo=checkmarx&logoColor=white" alt="Projeto Integrador I concluído"/>
  <img src="https://img.shields.io/badge/PI%20II-Conclu%C3%ADdo%20com%20sucesso-2ecc71?style=for-the-badge&logo=checkmarx&logoColor=white" alt="Projeto Integrador II concluído"/>
  <br>
  <img src="https://img.shields.io/badge/PI%20III-Em%20desenvolvimento-3498db?style=for-the-badge&logo=progress&logoColor=white" alt="Projeto Integrador III em desenvolvimento"/>
</p>



<p align="center">
  <p align="center">
    <img src="https://img.shields.io/badge/Stack-FFD600?style=for-the-badge&logo=stackshare&logoColor=black" alt="Stack"/>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
    <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django"/>
    <img src="https://img.shields.io/badge/SQL-CC0066?style=for-the-badge&logo=postgresql&logoColor=white" alt="SQL"/>
    <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5"/>
    <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3"/>
    <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript"/>
  </p>

  <p align="center">
    <img src="https://img.shields.io/github/stars/samueldata/lembremed?style=for-the-badge&logo=github" alt="GitHub Stars"/>
  </p>

# LembreMEd

Calculadora web de duração de medicamentos voltada para Instituições de Longa Permanência para Idosos (ILPIs).


## Índice

1. [Descrição do Projeto](#descrição-do-projeto)
2. [Funcionalidades e Demonstração da Aplicação](#funcionalidades-e-demonstração-da-aplicação)
3. [Novas funcionalidades](#novas-funcionalidades)
4. [Tecnologias Utilizadas](#tecnologias-utilizadas)
5. [Pessoas Contribuidoras](#pessoas-contribuidoras)

## Descrição do Projeto

 A aplicação combina conhecimentos em Tecnologia da Informação e Ciência de Dados, utilizando noções de framework web (Django), versionamento de código e banco de dados. O projeto segue a metodologia proposta por Mascarenhas (2018) e Lakatos e Marconi (2003), com ênfase em pesquisa qualitativa, pesquisa aplicada e pesquisa-ação.

A aplicação da metodologia Design Thinking garante o desenvolvimento centrado no usuário, com foco na compreensão das necessidades das ILPIs e na criação de soluções inovadoras. A arquitetura da aplicação e a escolha das tecnologias utilizadas foram elaboradas para garantir eficiência, robustez e escalabilidade da solução.

Seu desenvolvimento busca representar um avanço na gestão de medicamentos nas ILPIs, colaborando para a qualidade de vida e segurança de seus pacientes, além de apoiar na efetivação dos direitos desse segmento populacional, que possui necessidades específicas quanto à administração de medicamentos.

## Funcionalidades e Demonstração da Aplicação

 Principais funcionalidades do projeto:

1. Cadastro de Profissionais
- Descrição: Permite o registro de profissionais da saúde que trabalham na ILPI.
- Detalhes:
  - Nome completo
  - CPF 
  - Identificação profissional (COREN, etc.)
    
2. Cadastro de Instituições
- Descrição: Funcionalidade para cadastrar as clínicas e instituições de cuidados para idosos.
- Detalhes:
  - Nome da instituição
  
3. Cadastro de Moradores
- Descrição: Registro dos moradores que recebem cuidados na clínica.
- Detalhes:
  - Nome completo
  - Data de nascimento
  - CPF
  - Informações de contato de referência

4. Cadastro de Medicamentos por Morador
- Descrição: Cada morador pode ter seus medicamentos registrados individualmente.
- Detalhes:
  - Nome do medicamento
  - Concentração
  - Frequência de administração
  - Horários de administração
      
5. Controle de Estoque de Medicamentos por Morador
- Descrição: Monitora a quantidade de medicamentos disponível para cada morador.
- Detalhes:
  - Quantidade inicial
  - Quantidade atual
  - Alertas para reposição
    
6. Administração da Dose com Hora da Última Administração
- Descrição: Registra a administração de doses de medicamentos, garantindo que a medicação seja dada na hora certa.
- Detalhes:
  - Registro da hora da última dose administrada
  - Responsável pela administração

7. Relatórios e Exportação de Dados
- Descrição: Dashboard visual com métricas importantes e função de exportação de dados.
- Detalhes:
  - Gráficos de medicamentos por morador
  - Gráficos de estoque de medicamentos
  - Administrações por período
  - Administrações por profissional
  - Exportação de dados em formato CSV (compatível com importação)
  - Filtragem por período para exportação

<p align="center">
  <a href="https://github.com/britocps"><img src="https://github.com/samueldata/lembremed/assets/163072898/a0a9c7f0-6515-4e85-ba65-5b36f2bd4ca8" width="516" height="300" ></a><br><sub> Tela Inicial</sub>
</div>

<p align="center">
  <a href="https://github.com/britocps"><img src="https://github.com/samueldata/lembremed/assets/163072898/27ff20f5-6232-4141-8943-43abe7274608" width="516" height="200" ></a><br><sub> Tela Cadastro de ILPIS</sub>
</div>

<p align="center">
  <a href="https://github.com/britocps"><img src="https://github.com/samueldata/lembremed/assets/163072898/e72dc00e-b412-4264-b4d6-ff7c0fada2b3" width="516" height="200" ></a><br><sub> Tela Cadastro de Moradores</sub>
</div>

<p align="center">
  <a href="https://github.com/britocps"><img src="https://github.com/samueldata/lembremed/assets/163072898/94f7e75b-8b35-4bd5-9b97-703d3de5b60c" width="516" height="200" ></a><br><sub> Tela Cadastro de Profissionais</sub>
</div>

<p align="center">
  <a href="https://github.com/britocps"><img src="https://github.com/samueldata/lembremed/assets/163072898/432cea78-f1e3-47d0-af71-413c13ac207d" width="516" height="200" ></a><br><sub> Tela Cadastro e Administração de Medicamentos por morador</sub>
</div>

## Novas funcionalidades

<p align="center">

  - API de notificação
  - Melhorar responsividade  
  - Tela nova de login
  - Exportação de dados para CSV
  - Dashboard de relatórios aprimorado
  - Importação/exportação de dados históricos

 <p align="center">
  <a href="https://github.com/britocps"><img src="https://github.com/user-attachments/assets/b4ab253a-5907-4e6a-a4e0-0ab1b641ed9b" width="516" height="200" ></a><br><sub> Notificação de estoque baixo E-mail</sub>
</div>

  <p align="center">
  <a href="https://github.com/britocps"><img src="https://github.com/user-attachments/assets/5e4c36e9-9b4e-4481-89b0-2d4a92c3b46f" width="516" height="200" ></a><br><sub> Tela nova de login</sub>
</div>


## Tecnologias Utilizadas

<p align="center">
 
As tecnologias utilizadas no desenvolvimento do projeto incluem:


<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg" alt="Git" width="40" height="40"/> **Git**: Utilizado como sistema de controle de versão para o gerenciamento do código-fonte. 

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
**Django**: Um framework web em Python que facilita a construção de aplicativos web robustos e escaláveis. 

<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-plain.svg" alt="PostgreSQL" width="40" height="40"/>**SQL**: Linguagem padrão para manipulação de bancos de dados relacionais, sendo utilizada para consultas e interações com o banco de dados. 

<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg" alt="HTML5" width="40" height="40"/> **HTML**: Linguagem de marcação utilizada para criar a estrutura básica de páginas web. 

<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg" alt="CSS3" width="40" height="40"/>**CSS**: Utilizado para estilizar e definir o layout das páginas web, tornando-as mais atraentes e usáveis. 

<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg" alt="JavaScript" width="40" height="40"/> **JavaScript**: Linguagem de programação utilizada para adicionar interatividade e dinamismo às páginas web. 

Essas tecnologias foram selecionadas com o objetivo de garantir eficiência, segurança e uma experiência de usuário agradável durante a interação com a aplicação.

</p>

## Pessoas Contribuidoras

👨‍💻 Eduardo Pires de Brito

👩‍💻 Giovana Bianchessi da Cunha

👨‍💻 Christian Roberto Couto Furquim

👨‍💻 Edgard Hiromi Kamimura

👩‍💻 Carolina Luchetta

👩‍💻 Graciela Oliveira

👩‍💻 Amanda Bertolini Queçada

👨‍💻 Samuel Leite da Silva

# Autores

**Conheça os incríveis desenvolvedores que contribuíram para este projeto:**


<div style="display: flex; justify-content: center;">
<table>
  <tr>
    <td align="center">
      <a href="https://github.com/britocps"><img src="https://github.com/samueldata/lembremed/assets/163072898/2f9676fc-55be-437c-88a5-54b096eef5da" width="115" height="140"><br><sub>Eduardo Brito</sub></a>
    </td>
    <td align="center">
      <a href="https://github.com/giovanabcunha"><img src="https://github.com/samueldata/lembremed/assets/163072898/214fad6f-59b6-4fd7-88ca-a50c21860aa2" width="115" height="140"><br><sub>Giovana Cunha</sub></a>
    </td>
    <td align="center">
      <a href="https://github.com/crfurquim"><img src="https://github.com/samueldata/lembremed/assets/163072898/f81a3bb7-c664-484c-b01e-9d84906a5eb6" width="115" height="140"><br><sub>Christian Furquim</sub></a>
    </td>
    <td align="center">
      <a href="https://github.com/Edkamimura"><img src="https://github.com/samueldata/lembremed/assets/163072898/c67ea93e-7815-41d6-b60a-4b9c94a80924" width="115" height="140"><br><sub>Edgard Kamimura</sub></a>
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="https://github.com/CarolinaLuchetta"><img src="https://github.com/samueldata/lembremed/assets/163072898/dab9e17e-7160-4760-8791-59dfded7debb" width="115" height="140"><br><sub>Carolina Luchetta</sub></a>
    </td>
    <td align="center">
      <a href="https://github.com/graciela-oliveira"><img src="https://github.com/samueldata/lembremed/assets/163072898/157ea53b-a436-4fa4-b6e8-870992057d58" width="115" height="140"><br><sub>Graciela Oliveira</sub></a>
    </td>
    <td align="center">
      <a href="https://github.com/qbamanda"><img src="https://github.com/samueldata/lembremed/assets/163072898/bdbff197-5b1e-4c0d-b08e-5d0f64d2642f" width="115" height="140"><br><sub>Amanda Queçada</sub></a>
    </td>
    <td align="center">
      <a href="https://github.com/samueldata"><img src="https://github.com/samueldata/lembremed/assets/163072898/5e027315-3fc9-40f1-b7aa-3d5ad94405e5" width="115" height="140"><br><sub>Samuel Leite</sub></a>
    </td>
  </tr>
</table>

## Documentação Adicional

- [Guia de Importação e Exportação de Dados](docs_importacao_exportacao.md)

## Licença

Este projeto está licenciado sob a licença MIT - consulte o arquivo LICENSE para obter detalhes.
</div>





