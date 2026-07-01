import discord
from discord.ext import tasks
import requests
import os
from flask import Flask
from threading import Thread

# --- SERVIDOR PARA O RENDER NÃO DORMIR ---
app = Flask('')
@app.route('/')
def home():
    return "Bot Online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CONFIGURAÇÕES ---
TOKEN = os.getenv("DISCORD_TOKEN")
ID_CANAL = int(os.getenv("ID_CANAL"))
API_URL = "https://weao.xyz/api/status/exploits"
HEADERS = {"User-Agent": "WEAO-3PService"}

class StatusBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.historico = {}

    async def setup_hook(self):
        self.verificar_mudancas.start()

    @tasks.loop(minutes=5)
    async def verificar_mudancas(self):
        canal = self.get_channel(ID_CANAL)
        if not canal: return
        try:
            response = requests.get(API_URL, headers=HEADERS)
            if response.status_code == 200:
                dados = response.json()
                for item in dados:
                    nome = item.get("title")
                    status_bool = item.get("updateStatus")
                    if nome not in self.historico:
                        self.historico[nome] = status_bool
                        continue
                    if self.historico[nome] != status_bool:
                        self.historico[nome] = status_bool
                        cor = discord.Color.green() if status_bool else discord.Color.red()
                        status_texto = "🟢 ATUALIZADO" if status_bool else "🔴 PATCHED"
                        embed = discord.Embed(title="📢 MUDANÇA DE STATUS!", description=f"O executor **{nome}** mudou para **{status_texto}**!", color=cor)
                        await canal.send(embed=embed)
        except Exception as e:
            print(f"Erro: {e}")

    @verificar_mudancas.before_loop
    async def before_verificar(self):
        await self.wait_until_ready()

if __name__ == "__main__":
    keep_alive() # Inicia o servidor web
    bot = StatusBot()
    bot.run(TOKEN)
