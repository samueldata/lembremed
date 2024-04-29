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
