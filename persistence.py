import winreg as reg
import os

python_path = r"C:\Path\to\python.exe"  # Exemple : C:\Python39\python.exe

script_dir = r"C:\Users\UX535\PycharmProjects\c2-scanner"  # Dossier contenant agent.py
script_name = "agent.py"

command = f'cmd.exe /c "cd /d {script_dir} && {python_path} {script_name}"'

key = reg.HKEY_CURRENT_USER
key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
try:
    reg_key = reg.OpenKey(key, key_path, 0, reg.KEY_WRITE)
    reg.SetValueEx(reg_key, "MonScriptAgent", 0, reg.REG_SZ, command)
    reg.CloseKey(reg_key)
    print("Script ajouté au démarrage de Windows.")
except Exception as e:
    print(f"Erreur lors de l'ajout au registre: {e}")
