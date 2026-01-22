@echo off

:: docker compose up --build
:: docker compose down
:: docker compose down -v

curl -X POST http://localhost:8001/users ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Nikolay\"}"

curl -X POST http://localhost:8001/tracked-items ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":1,\"marketplace\":\"ebay\",\"external_id\":\"EBAY-1\"}"

curl -X POST http://localhost:8001/rules ^
  -H "Content-Type: application/json" ^
  -d "{\"tracked_item_id\":1,\"rule_type\":\"PRICE_BELOW\",\"params\":{\"target\":900}}"

curl -X POST http://localhost:8000/run-cycle ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":1}"

curl http://localhost:8001/users/1/alerts


