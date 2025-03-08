import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timezone, timedelta
from discord.ext.commands import MissingPermissions


load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
API_KEY = os.getenv('COINMARKETCAP_API_KEY')
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
url_website = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info'

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': API_KEY,
}

positions = {}
        

utc_plus_2 = timezone(timedelta(hours=2))

def buy(ticker, suma):
    if ticker in positions:
        params = {
        'symbol' : ticker,
        'convert' : 'USD'
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return(f"😢 Eroare la cererea API pentru {ticker}.")

        data = response.json()

        if 'data' not in data or len(data['data']) == 0:
            return(f"😥 Nu am putut găsi prețul pentru {ticker}. Verifică simbolul criptomonedei.")

        pret = data['data'][ticker]['quote']['USD']['price']
        cantitate_moneda = suma / pret
        suma_initiala = positions[ticker]['pret'] * positions[ticker]['cantitate_moneda']
        suma_totala = suma + suma_initiala
        pret_mediu =  suma_totala /  (cantitate_moneda + positions[ticker]['cantitate_moneda'])
        positions[ticker]['pret'] = pret_mediu
        positions[ticker]['cantitate_moneda'] += cantitate_moneda
        return (
           f"📝 Ai adaugat {suma} USD la pozitia ta {ticker}. Pretul de cumparare este: {round(pret,2)}. \n"
           f"🪙 Numarul tau de monede este: {round(positions[ticker]['cantitate_moneda'],4)}.\n"
           f"💰 Pretul mediu este: {round(positions[ticker]['pret'],2)} USD."
        )
    else:
        params = {
        'symbol': ticker,
        'convert' : 'USD'
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return(f"😢 Eroare la cererea API pentru {ticker}.")

        data = response.json()

        if 'data' not in data or len(data['data']) == 0:
            return(f"😢 Nu am putut găsi prețul pentru {ticker}. Verifică simbolul criptomonedei.")

        pret = data['data'][ticker]['quote']['USD']['price']
        cantitate_moneda = suma / pret
        data_achizitie = datetime.now(utc_plus_2)
        positions[ticker] = {'cantitate_moneda': cantitate_moneda, 'pret': pret, 'data_achizitie' : data_achizitie}
        return(
            f"🪙 Poziția pentru {ticker} a fost adăugată cu {round(cantitate_moneda,4)} monede , la prețul de {round(pret,2)} USD. 💰"
        )

def check(ticker):
    if ticker not in positions:
        return(f"Moneda 🪙 {ticker} nu se afla in portofoliul tau. Daca vrei sa o adaugi foloseste comanda 💵 /buy. ")
    
    params = {
        'symbol': ticker,
        'convert': 'USD'
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return(f"😢 Eroare la cererea API pentru {ticker}.")


    data = response.json()
    if 'data' not in data or len(data['data']) == 0:
        return(f"😢 Nu am putut găsi prețul pentru {ticker}. Verifică simbolul criptomonedei.")

    pret_actual = data['data'][ticker]['quote']['USD']['price']
    valoare_pozitie = positions[ticker]['cantitate_moneda'] * pret_actual
    PnL_procentual = ((pret_actual - positions[ticker]['pret']) / positions[ticker]['pret']) * 100
    PnL = pret_actual * positions[ticker]['cantitate_moneda'] - positions[ticker]['pret'] * positions[ticker]['cantitate_moneda']
	
    if PnL < 0:
            mesaj = f"📉 PnL procentual este: {round(PnL_procentual,2)}%.\n📉 PnL este: {round(PnL,2)} USD. \n"
    elif PnL == 0:
            mesaj = f"📊 PnL procentual este: {round(PnL_procentual,2)}%.\n📊 PnL este: {round(PnL,2)} USD. \n"
    elif PnL > 0:
            mesaj = f"📈 PnL procentual este: {round(PnL_procentual,2)}%.\n📈 PnL este: {round(PnL,2)} USD.\n"
	
    # Extragem data de achiziție
    data_achizitie = positions[ticker]['data_achizitie']
    
    # Obținem data și ora curentă în UTC+2
    acum = datetime.now(utc_plus_2)
    
    # Calculăm diferența de timp
    diferenta_timp = acum - data_achizitie
    zile = diferenta_timp.days
    ore = diferenta_timp.seconds // 3600

    # Converim timpul într-un string
    timp_deschidere = f"⏳ Poziția este deschisă de {zile} zile și {ore} ore."

    # data_achizitie_str = positions[ticker].get('data_achizitie')  # Folosim .get() pentru a evita KeyError
    # if data_achizitie_str:
    #     try:
    #         # Conversia la UTC pentru data de achiziție
    #         data_achizitie = datetime.strptime(data_achizitie_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

    #         # Conversia datei de achiziție din UTC în UTC+02
    #         print(f"Data achiziției în UTC+02: {data_achizitie}")
            

    #         # Obținem data și ora curentă în UTC+02
    #         acum = datetime.now(utc_plus_2)  # Folosim UTC+02 aici
    #         print(f"Data și ora curentă în UTC+02: {acum}")

    #         diferenta_timp = acum - data_achizitie
    #         print(diferenta_timp)
    #         zile = diferenta_timp.days
    #         ore = diferenta_timp.seconds // 3600  # orele din diferența de timp (fără milisecunde)

    #         timp_deschidere = f"⏳ Poziția este deschisă de {zile} zile și {ore} ore."
    #     except ValueError:
    #         timp_deschidere = "⚠️ Eroare la conversia datei de achiziție."
    # else:
    #     timp_deschidere = "❌ Nu există informație despre data deschiderii poziției."

    return(
        f"💵 Pozitia ta {ticker} valoreaza: {round(valoare_pozitie,2)}. \n"
        f"💰 Numarul de monede este: {round(positions[ticker]['cantitate_moneda'],4)}. \n"
        f"{mesaj}"
        f"💲 Moneda a fost cumparata la pretul {round(positions[ticker]['pret'],2)} USD.💲 Pretul actual este {round(pret_actual,2)} USD. \n"
        f"{timp_deschidere}"
    )

def sell(ticker, suma):
    if ticker not in positions:
        return(f"❌ Nu ai o pozitie {ticker} deschisa.")
    
    if suma > positions[ticker]['cantitate_moneda'] * positions[ticker]['pret']:
        return(f"👎 Suma depaseste bugetul.")
    
    params = {
        'symbol' : ticker,
        'convert' : 'USD'
    }

    response = requests.get(url, params=params,headers=headers)

    if response.status_code != 200:
        return(f"😢 Eroare la cererea API pentru {ticker}.")

    data = response.json()

    if 'data' not in data or len(data['data']) == 0:
        return(f"😢 Nu am putut găsi prețul pentru {ticker}. Verifică simbolul criptomonedei.")
        
    
    pret = data['data'][ticker]['quote']['USD']['price']
    cantitate = suma / pret
    positions[ticker]['cantitate_moneda'] -= cantitate
    if positions[ticker]['cantitate_moneda'] == 0:
        positions[ticker].pop()
        return(f"💸 Ai vandut {round(cantitate,4)} {ticker} la {round(pret,2)} USD.❌ Aceasta pozitie a fost inchisa.")
    return(f"💸 Ai vandut {round(cantitate, 4)} {ticker} la {round(pret,2)}USD.")    

def buy_cantitate(ticker, cantitate):
    if ticker in positions:
        params = {
        'symbol' : ticker,
        'convert' : 'USD'
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return(f"😢 Eroare la cererea API pentru {ticker}.")

        data = response.json()

        if 'data' not in data or len(data['data']) == 0:
            return(f"😢 Nu am putut găsi prețul pentru {ticker}. Verifică simbolul criptomonedei.")

        pret = data['data'][ticker]['quote']['USD']['price']
        
        suma_ceruta = cantitate * pret
        suma_initiala = positions[ticker]['pret'] * positions[ticker]['cantitate_moneda']
        suma_totala = suma_ceruta + suma_initiala
        pret_mediu =  suma_totala /  (cantitate + positions[ticker]['cantitate_moneda'])
        positions[ticker]['pret'] = pret_mediu
        positions[ticker]['cantitate_moneda'] += cantitate
        return (
           f"📝 Ai adaugat {round(cantitate,4)} la pozitia ta {ticker}. Pretul de cumparare este: {round(pret,2)}.\n"
           f"🪙 Numarul tau de monede este: {round(positions[ticker]['cantitate_moneda'],4)}.\n"
           f"💰 Pretul mediu este: {round(positions[ticker]['pret'],2)} USD."
        )
    else:
        params = {
        'symbol': ticker,
        'convert' : 'USD'
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return(f"😢 Eroare la cererea API pentru {ticker}.")

        data = response.json()

        if 'data' not in data or len(data['data']) == 0:
            return(f"😢 Nu am putut găsi prețul pentru {ticker}. Verifică simbolul criptomonedei.")

        pret = data['data'][ticker]['quote']['USD']['price']
        data_achizitie = datetime.now(utc_plus_2)
        positions[ticker] = {'cantitate_moneda': cantitate, 'pret': pret, 'data_achizitie' : data_achizitie}
        return(
            f"📝 Poziția pentru {ticker} a fost adăugată cu {round(cantitate,4)} monede, la prețul de {round(pret,2)} USD."
        )

def sell_cantitate(ticker, cantitate):
    if ticker not in positions:
        return(f"❌ Nu ai o pozitie {ticker} deschisa.")
    
    if cantitate > positions[ticker]['cantitate_moneda']:
        return(f"❌🪙 Nu ai destule moneji.")
    
    params = {
        'symbol' : ticker,
        'convert' : 'USD'
    }

    response = requests.get(url, params=params,headers=headers)

    if response.status_code != 200:
        return(f"😢 Eroare la cererea API pentru {ticker}.")

    data = response.json()

    if 'data' not in data or len(data['data']) == 0:
        return(f"😢 Nu am putut găsi prețul pentru {ticker}. Verifică simbolul criptomonedei.")
        
    
    pret = data['data'][ticker]['quote']['USD']['price']
    positions[ticker]['cantitate_moneda'] -= cantitate
    if positions[ticker]['cantitate_moneda'] == 0:
        positions[ticker].pop()
        return(f"💸 Ai vandut {round(cantitate,4)} {ticker} la {round(pret,2)}USD.❌ Aceasta pozitie a fost inchisa")
    return(f"💸 Ai vandut {round(cantitate,4)} {ticker} la {round(pret,2)}USD.")

def PNL():
    if not positions:
        return("😟 Nu ai nicio pozitie deschisa!")
    pnl_total = 0
    for coin in positions:
        params = {
            'symbol' : coin,
            'convert' : 'USD'
        }  
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return(f"😢 Eroare la cererea API pentru {coin}.")

        data = response.json()

        if 'data' not in data or len(data['data']) == 0:
            return(f"😢 Nu am putut găsi prețul pentru {coin}. Verifică simbolul criptomonedei.")

        pret = data['data'][coin]['quote']['USD']['price']
        suma_portofel = positions[coin]['cantitate_moneda'] * positions[coin]['pret']
        suma_normala = pret * positions[coin]['cantitate_moneda']
        pnl = suma_normala - suma_portofel
        pnl_total += pnl
        
    suma_portofel = 0
    valoare_normala = 0
    for coin in positions:
        suma_portofel += positions[coin]['cantitate_moneda'] * positions[coin]['pret']
        params = {
            'symbol' : coin,
            'convert' : 'USD'
        }  
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return(f"😢 Eroare la cererea API pentru {coin}.")

        data = response.json()

        if 'data' not in data or len(data['data']) == 0:
            return(f"😢 Nu am putut găsi prețul pentru {coin}. Verifică simbolul criptomonedei.")

        pret = data['data'][coin]['quote']['USD']['price']
        valoare_normala += pret * positions[coin]['cantitate_moneda']
    
    pnl_procentual = (pnl_total / suma_portofel) * 100
    if pnl_procentual < 0:
        mesaj = (
            f"📉 Portofelul tau are o miscare de pret de {abs(round(pnl_total,2))} USD in jos. \n"
        	f"📉 Asta inseamna ca esti pe minus: {abs(round(pnl_procentual,2))}%.\n"
            f"💵 Portofelul tau valoreaza: {round(valoare_normala,2)} USD. \n"
            f"💰 Suma investita este de: {round(suma_portofel,2)} USD."
            f"🧑‍🍳 O sa lucrezi la MeC."
        )
    if pnl_procentual == 0:
        mesaj = (
            f"💵 Portofelul tau valoreaza: {round(valoare_normala,2)} USD. \n"
            f"💰 Suma investita este de: {round(suma_portofel,2)} USD. \n"
            "🟰 Esti break even la portofel. Foloseste comanda !check pentru a afla mai multe. \n"   
        )
    if pnl_procentual > 0:
        mesaj = (
            f"📈 Portofelul tau are o miscare de pret de {round(pnl_total,2)} USD in sus. \n"
        	f"📈 Asta inseamna ca esti pe plus: {round(pnl_procentual,2)}%. \n"
            f"💵 Portofelul tau valoreaza: {round(valoare_normala,2)} USD. \n"
            f"💰 Suma investita este de: {round(suma_portofel,2)} USD."
        	f"😎 Iti iei lambo."
        )
    
    return (
       f"{mesaj} {pnl_procentual}"
       
    )

def portofel():
    if not positions:
        return("Nu e bine") 
    valoare_portofoliu = 0
    mesaj = "pozitiile tale sunt: \n"
    for coin in positions:
        mesaj += ("Inca ceva")
        params = {
            'symbol' : coin,
            'convert' : 'USD'
        }
        response = requests.get(url, params = params,headers = headers)
        if response.status_code != 200:
            return("Aia e")
        data = response.json()
        if 'data' not in data or len(data['data']) == 0:
            return("Nu exista")
        pret = data['data'][coin]['quote']['USD']['price']
        valoare_portofoliu += pret * positions[coin]['cantitate_moneda']
    
    mesaj += f"Portofoliul valoreaza: {valoare_portofoliu}"
    return mesaj

def portofel():
    if not positions:
        return("❌ Nu ai nicio pozitie deschisa!")
    valoare_portofoliu = 0
    mesaj = "📝 Pozitiile tale deschise sunt: \n"
    for coin in positions:
        # Folosind positions[coin] pentru a accesa dicționarul corespunzător
        mesaj += f"🪙 {coin}: {round(positions[coin]['cantitate_moneda'],4)} monede, pret mediu: {round(positions[coin]['pret'],2)} USD. \n"
        params = {
        	'symbol' : coin,
        	'convert' : 'USD'
    	}

        response = requests.get(url, params=params,headers=headers)

        if response.status_code != 200:
        	return(f"😢 Eroare la cererea API pentru {ticker}.")

        data = response.json()

        if 'data' not in data or len(data['data']) == 0:
        	return(f"😢 Nu am putut găsi prețul pentru {ticker}. Verifică simbolul criptomonedei.")
        
        pret = data['data'][ticker]['quote']['USD']['price']
        valoare_portofoliu += pret * positions[coin]['cantitate_moneda']
        
    mesaj += f"💵 Portofoliul tau valoreaza: {round(valoare_portofoliu,2)} USD."
    return mesaj


def get_info(ticker):
    params = {
        'symbol' : ticker,
        'convert' : 'USD'
    }
    params2 = {'symbol' : ticker}
    #Pentru website
    response2 = requests.get(url_website, params=params2,headers=headers)

    if response2.status_code != 200:
        return(f"😢 Eroare la cererea API pentru {ticker}.")

    data2 = response2.json()

    if 'data' not in data2 or len(data2['data']) == 0:
        return(f"😢 Nu am putut găsi moneda {ticker}. Verifică simbolul criptomonedei.")
    #Pentru celelalte informatii

    response = requests.get(url, params=params,headers=headers)

    if response.status_code != 200:
        return(f"😢 Eroare la cererea API pentru {ticker}.")

    data = response.json()

    if 'data' not in data or len(data['data']) == 0:
        return(f"😢 Nu am putut găsi moneda {ticker}. Verifică simbolul criptomonedei.")
    moneda = data['data'][ticker]
    nume = moneda['name']
    market_cap = moneda['quote']['USD']['market_cap']
    rank = moneda['cmc_rank']
    website = data2['data'][ticker].get('urls', {}).get('website', ["N/A"])[0]  # Unele monede nu au site
    cmc_link = f"https://coinmarketcap.com/currencies/{nume.lower().replace(' ', '-')}"
    return (
        f"📊 **Project Name:** {nume}\n"
        f"💰 **Marketcap:** {round(market_cap / 1_000_000_000, 2)} B $\n"
        f"🏆 **Rank:** {rank}\n"
        f"🌐 **Website:** {website} \n \n"
        f"🔍 [Pentru mai multe informații apasă aici]({cmc_link})"
    )
    
    
@bot.command(name='buy')
@commands.has_permissions(administrator = True)
async def buy_command(ctx, ticker: str, suma: float):
    rezultat = buy(ticker.upper(), suma)
    await ctx.send(rezultat)


@bot.command(name='sell')
@commands.has_permissions(administrator = True)
async def sell_command(ctx, ticker: str, suma: float):
    rezultat = sell(ticker.upper(), suma)
    await ctx.send(rezultat)


@bot.command(name='check')
async def check_command(ctx, ticker: str):
    rezultat = check(ticker.upper())
    await ctx.send(rezultat)

@bot.command(name='buy_cantitate')
@commands.has_permissions(administrator = True)
async def buy_cantitate_command(ctx, ticker: str, suma: float):
    rezultat = buy_cantitate(ticker.upper(), suma)
    await ctx.send(rezultat)

@bot.command(name='sell_cantitate')
@commands.has_permissions(administrator = True)
async def sell_cantitate_command(ctx, ticker: str, suma: float):
    rezultat = sell_cantitate(ticker.upper(), suma)
    await ctx.send(rezultat)

@bot.command(name='sell_all')
@commands.has_permissions(administrator = True)
async def sell_all_command(ctx, ticker: str):
    rezultat = sell_all(ticker.upper())
    await ctx.send(rezultat)

@bot.command(name='pnl')
async def pnl_command(ctx):
    rezultat = PNL() 
    await ctx.send(rezultat)  

@bot.command(name='portofoliu')
async def portofoliu_command(ctx):
    mesaj = portofel()
    await ctx.send(mesaj)

@bot.command(name='clear')
@commands.has_permissions(administrator = True)
async def clear_positions(ctx):
    global positions
    positions.clear() 
    await ctx.send("Toate pozițiile din portofoliu au fost șterse!")


@bot.command(name='help_crypto')
async def help_crypto(ctx):
    mesaj = (
        "**Lista de comenzi disponibile:**\n"
        "!buy <ticker> <suma> - Cumpără criptomonede în valoare de suma specificată.\n \n"
        "!sell <ticker> <suma> - Vinde criptomonede în valoare de suma specificată.\n\n"
        "!check <ticker> - Verifică informațiile despre o criptomonedă din portofoliu. PnL, cantitatea, pretul mediu, durata de la deschiderea pozitiei.\n\n"
        "!buy_cantitate <ticker> <cantitate> - Cumpără o cantitate specifică de criptomonedă.\n\n"
        "!sell_cantitate <ticker> <cantitate> - Vinde o cantitate specifică de criptomonedă.\n\n"
        "!sell_all <ticker> - Vinde întreaga poziție a unei criptomonede. Comanda recomandata daca vrei sa inchizi o pozitie.\n\n"
        "!pnl - Afișează profitul și pierderea totală din portofoliu.\n\n"
        "!portofoliu - Afișează toate pozițiile deschise din portofoliu.\n\n"
        "!clear - Șterge toate pozițiile din portofoliu.\n\n"
        "!info <ticker> - Ofera informatii despre o moneda de CoinMarketCap. \n\n"
        "Toate comenzile de buy si sell, ca si comanda de clear nu pot fi accesate de roluri mai mici de colonel."
    )
    await ctx.send(mesaj)

@bot.command(name='info')
async def info_command(ctx, ticker: str):
    try:
        rezultat = get_info(ticker.upper())
        await ctx.send(rezultat)
    except Exception as e:
        await ctx.send(f"A apărut o eroare: {str(e)}")

    
# Gestionarea erorii pentru utilizatorii fără permisiuni
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("❌ Nu ai permisiunea necesară pentru a folosi această comandă!")


        
bot.run(TOKEN)


