# ShakeCities
A joint project between Nathan.Woodburn/ and crymzyn/  
ShakeCities is a geocities clone with an emphasis on Handshake domains.  
Create a free site on yourname.shakecities/. You control that site and can add whatever you want to it.  
Every domain comes enabled with HTTPS via DANE. We have support HIP02 aliases, so you can send HNS to yourname.shakecities/  




### Template testing

Replace `new` with your template name

```sh
cd <Git-REPONAME>
# Copy template
cp templates/city_template.html templates/city_new.html
# Edit template
# Test site with template
python3 -m pip install -r requirements.txt
python3 template.py city_new
```

Visit http://127.0.0.1:5000/ to view the template  
Here is a list of placeholders you can use [PLACEHOLDERS.md](PLACEHOLDERS.md)


### Deployment
```
version: '3'
services:
  main:
    image: git.woodburn.au/nathanwoodburn/shakecities:latest
    depends_on:
      - db
    volumes:
      - images:/data
    environment:
      DB_HOST: db
      DB_USER: main
      DB_PASSWORD: your-db-password
      DB_NAME: main
      CITY_DOMAIN: exampledomainnathan1
      REG_KEY: <your-varo-apikey>
      CITY_ALIAS: city.hnshosting.au # ICANN domain that points to the IP for the cities server
      MAIN_DOMAIN: cities.hnshosting.au
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
      MAIN_DOMAIN: cities.hnshosting.au
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
  images:
```