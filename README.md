# NASA-Hackathon Backend

## docker

- config MAP_KEY and DATABASE_URL in .env

```
cp .env .env.example
```

- run db and api

```
docker compose up
```

## local

- config MAP_KEY and DATABASE_URL in .env

```
cp .env .env.example
```

- install package

```
potery install
```

- run api server

```
poetry run uvicorn main:app --reload
```

- open [http://127.0.0.1:8000/docs#/](http://127.0.0.1:8000/docs#/) to test api
