CREATE USER 'dtd_slave'@'%' IDENTIFIED BY 'dtd_slave';
GRANT ALL PRIVILEGES ON dtd.* TO 'dtd_slave'@'%';

FLUSH PRIVILEGES;