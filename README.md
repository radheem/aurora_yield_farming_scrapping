# aurora_yield_farming_scrapping
This repo scrapes the APR for NEAR WETH from [vfat](https://vfat.tools/aurora/auroraswap/)<br>
Steps to run API:<br>
1. Make sure you have python, chrome and Selenium setup.
2. run python3 app.py -config ./config.json

In the config.json you can specify:<br>
1. refresh_time: the duration after with the bot refreshes the page
2. contract_address: the contract address to read data for (this might not always work but it works for NEAR-WETH so far)
