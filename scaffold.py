import subprocess
import os

os.chdir(r"C:\Users\aakas\Hospital")

subprocess.run("npx.cmd create-vite@latest frontend --template vue", shell=True)

os.chdir(r"C:\Users\aakas\Hospital\frontend")
subprocess.run("npm install axios vue-router bootstrap bootstrap-icons chart.js vue-chartjs pinia", shell=True)

print("Scaffold complete!")
