# DRF-template

## Setup
### Development
1. remove `-sample` ending from `.env` files with `.dev` prefix
2. change email and email password in `.dev.env`
3. run `docker-compose up --build`

### Production
1. remove `-sample` ending from `.env` files with `.prod` prefix
2. update .env files and `docker-compose.prod.yml` if you want
3. run `docker-compose -f docker-compose.prod.yml up --build --env-file env_files/.prod.compose.env`
