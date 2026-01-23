@echo off
setlocal

echo ==================================================
echo Demo 2: DummyJSON price -> Rule -> Alert
echo ==================================================
echo This demo will:
echo  1) Fetch price from DummyJSON (product id=16 "Apple")
echo  2) Create user (assumes new DB -> user_id=1)
echo  3) Create tracked item (marketplace=dummyjson, external_id=16)
echo  4) Create PRICE_BELOW rule using DummyJSON price + 0.01
echo  5) Run orchestrator cycle
echo  6) Fetch alerts
echo ==================================================
echo.

echo [STEP 1] Fetch external price from DummyJSON (id=16)...
for /f "usebackq delims=" %%P in (`powershell -NoProfile -Command ^
  "$p=Invoke-RestMethod 'https://dummyjson.com/products/16'; [double]$p.price"`) do set "DUMMY_PRICE=%%P"

for /f "usebackq delims=" %%T in (`powershell -NoProfile -Command ^
  "$price=[double]'%DUMMY_PRICE%'; '{0:F2}' -f ($price + 0.01)"`) do set "TARGET=%%T"

echo DummyJSON price: %DUMMY_PRICE%
echo Rule target    : %TARGET%
echo.

echo --------------------------------------------------
echo [STEP 2] Create user (name=Nikolay)
echo --------------------------------------------------
curl -s -X POST http://localhost:8001/users ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Nikolay\"}"
echo.
echo.

echo --------------------------------------------------
echo [STEP 3] Create tracked item (marketplace=dummyjson, external_id=16)
echo --------------------------------------------------
curl -s -X POST http://localhost:8001/tracked-items ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":1,\"marketplace\":\"dummyjson\",\"external_id\":\"16\"}"
echo.
echo.

echo --------------------------------------------------
echo [STEP 4] Create rule PRICE_BELOW (target from DummyJSON)
echo --------------------------------------------------
curl -s -X POST http://localhost:8001/rules ^
  -H "Content-Type: application/json" ^
  -d "{\"tracked_item_id\":1,\"rule_type\":\"PRICE_BELOW\",\"params\":{\"target\":%TARGET%}}"
echo.
echo.

echo --------------------------------------------------
echo [STEP 5] Run orchestrator cycle (user_id=1)
echo --------------------------------------------------
curl -s -X POST http://localhost:8000/run-cycle ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":1}"
echo.
echo.

echo --------------------------------------------------
echo [STEP 6] Fetch alerts (user_id=1)
echo --------------------------------------------------
curl -s http://localhost:8001/users/1/alerts
echo.
echo.

echo ==================================================
echo Demo 2 finished.
echo ==================================================
pause
