/*
problemas ao reinicializar o xampp
https://stackoverflow.com/questions/60864367/1030-got-error-176-read-page-with-wrong-checksum-from-storage-engine-aria
https://stackoverflow.com/questions/18022809/how-can-i-solve-error-mysql-shutdown-unexpectedly
*/

/*

#Preparando o ambiente
mkdir projeto_lembremed
cd projeto_lembremed
mkdir ambiente01
	#Windows
	python -m venv .\ambiente01
	ambiente01\Scripts\activate
	#Unix
	python -m venv ./ambiente01
	source ambiente01/bin/activate
pip install Django mysqlclient python-telegram-bot requests
*/

/*=======================*/
/*Criando a base de dados*/

DROP DATABASE IF EXISTS lembremed;
CREATE DATABASE lembremed;
USE lembremed;

/*===============*/
/*Criando usuario*/

DROP USER IF EXISTS 'lembremed'@'localhost';
CREATE USER 'lembremed'@'localhost' IDENTIFIED BY 'g14UNIVESP';
ALTER USER 'lembremed'@'localhost' IDENTIFIED WITH mysql_native_password BY 'g14UNIVESP'; 
GRANT ALL PRIVILEGES ON lembremed.* TO 'lembremed'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;


/*

#Clonando o projeto
git clone https://github.com/samueldata/lembremed


#Entrar na raiz do projeto
cd lembremed

#Apagando os migrations anteriores
	#Windows
	del lembremed\migrations\00*
	#Unix
	rm lembremed/migrations/00*

#Criando os migrations
python manage.py makemigrations

#Pre-configurado, alterar se desejar
> configurar o usuario do banco em lembremed_proj/settings.py

#Rodando os migrations
python manage.py migrate

#Importando a lista de medicamentos pro banco
python manage.py populate_db

# Comando para realocar os arquivos de imagem, css e javascript
python manage.py collectstatic

#Criando o usuario administrativo
python manage.py createsuperuser
>lembremed
>lembremed@lembremed.com
>g14UNIVESP

# Colocar o servidor para rodar
python manage.py runserver





## No alwaysdata.net
> habilitar o login com senha no ssh
> criar o usuario do banco de dados mysql
> criar o banco de dados <usuario>_db, dando todas as permissoes ao usuario recem criado
> entrar no ssh, entrar na pasta /home/<usuario>/www
git clone https://github.com/samueldata/lembremed
cd lembremed
python -m venv env
source env/bin/activate
pip install Django
pip install mysqlclient
sed -i "s|^ALLOWED_HOSTS = .*|ALLOWED_HOSTS = [\'*']|" lembremed_proj/settings.py
> configurar o usuario do banco em lembremed_proj/settings.py
> o host era mysql-<usuario>.alwaysdata.net
nano lembremed_proj/settings.py

> configuracoes do site python wsgi
Application path*
[/home/lembremed/]:www/lembremed/lembremed_proj/wsgi.py
Working directory
[/home/lembremed/]:www/lembremed
Python version
3.11
virtualenv directory
[/home/lembremed/]:www/lembremed/env


*/