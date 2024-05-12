/*
problemas ao reinicializar o xampp
https://stackoverflow.com/questions/60864367/1030-got-error-176-read-page-with-wrong-checksum-from-storage-engine-aria
https://stackoverflow.com/questions/18022809/how-can-i-solve-error-mysql-shutdown-unexpectedly
*/


/*=======================*/
/*Criando a base de dados*/

DROP DATABASE lembremed;
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

python manage.py migrate

python manage.py populate_db

python manage.py collectstatic

python manage.py createsuperuser

python manage.py runserver






*/