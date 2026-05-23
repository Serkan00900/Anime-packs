name: Run Modrinth Tracker Bot

on:
  schedule:
    - cron: '0 * * * *' # Runs every hour
  workflow_dispatch: # Allows manual button click

permissions:
  contents: write

jobs:
  run-bot:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout Repository Code
      uses: actions/checkout@v4

    - name: Set Up Python Environment
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install Dependencies
      run: pip install requests

    - name: Run Script and Check Updates
      env:
        DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
      run: python Discord/bot.py

    - name: Save Cache for Next Run
      uses: stefanzweifel/git-auto-commit-action@v5
      with:
        commit_message: "Update last posted pack cache [skip ci]"
        file_pattern: 'Discord/last_posted_project.txt'
