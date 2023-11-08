# shakecities

```
version: '3'
services:
  main:
    image: git.woodburn.au/nathanwoodburn/shakecities:latest
    depends_on:
      - db
    environment:
      DB_HOST: db
      DB_USER: main
      DB_PASSWORD: your-db-password
      DB_NAME: main
      WORKERS: 2 # number of workers to run (should be 2 * number of cores)

  sites:
    image: git.woodburn.au/nathanwoodburn/shakecities-sites:latest
    depends_on:
      - db
    environment:
      DB_HOST: db
      DB_USER: main
      DB_PASSWORD: your-db-password
      DB_NAME: main
      WORKERS: 2 # number of workers to run (should be 2 * number of cores)

  db:
    image: linuxserver/mariadb:latest
    environment:
      MYSQL_ROOT_PASSWORD: your-root-password
      MYSQL_DATABASE: main
      MYSQL_USER: main
      MYSQL_PASSWORD: your-db-password
    volumes:
      - db_data:/var/lib/mysql
volumes:
  db_data:
```