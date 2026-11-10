@echo off
REM Gera o BattleWish.exe (fica na pasta "dist").
REM Precisa ter: pip install pygame pyinstaller
cd /d "%~dp0"
python -m PyInstaller --onefile --windowed --name BattleWish --icon "%~dp0battlewish.ico" ^
  --add-data "%~dp0battlewish_icone.png;." --add-data "%~dp0frogbit_abertura_tira.png;." --add-data "%~dp0frogbit_jingle.wav;." --add-data "%~dp0frogbit_selo_2x.png;." ^
  --workpath build --specpath build --noconfirm ^
  luta.py
echo.
echo Pronto! O jogo esta em: %~dp0dist\BattleWish.exe
pause
