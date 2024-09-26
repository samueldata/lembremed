/*
problemas ao reinicializar o xampp
https://stackoverflow.com/questions/60864367/1030-got-error-176-read-page-with-wrong-checksum-from-storage-engine-aria
https://stackoverflow.com/questions/18022809/how-can-i-solve-error-mysql-shutdown-unexpectedly
*/


/*=======================*/
/*Criando a base de dados*/

DROP DATABASE IF EXISTS lembremed;
CREATE DATABASE lembremed;
USE lembremed;

/*===============*/
/*Criando usuario*/

CREATE USER 'lembremed'@'localhost' IDENTIFIED BY 'g14UNIVESP';
GRANT ALL PRIVILEGES ON lembremed.* to 'lembremed'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;


/*

git clone https://github.com/samueldata/lembremed


#Entrar na raiz do projeto


#Windows
del lembremed\migrations\00*

#Unix
rm lembremed/migrations/00*

python manage.py makemigrations

> configurar o usuario do banco em lembremed_proj/settings.py

python manage.py migrate

python manage.py populate_db

# Comando para realocar os arquivos de imagem, css e javascript
python manage.py collectstatic

python manage.py createsuperuser


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