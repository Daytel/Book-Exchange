FROM mysql:8.2

ENV MYSQL_CHARACTER_SET_SERVER=utf8mb4
ENV MYSQL_COLLATION_SERVER=utf8mb4_unicode_ci
ENV MYSQL_DEFAULT_CHARACTER_SET=utf8mb4

ENV MYSQL_INITDB_SKIP_TZINFO=1
ENV LANG=C.UTF-8

# Копируем скрипты в специальную папку
COPY init-db.sql /docker-entrypoint-initdb.d/
COPY test_data.sql /docker-entrypoint-initdb.d/

EXPOSE 3306