
import urllib3
from bs4 import BeautifulSoup


url_term = ["M","I", "MI","MIE", "MIM", "MM", "IM", "IE", "IG"]
coresp = {1:"M",2:"I", 3:"MI",8:"MIE", 6:"MIM", 4:"MM", 5:"IM", 9:"IE", 7:"IG"}

full_url = "https://www.cs.ubbcluj.ro/files/orar/2021-2/tabelar/"



def get_orar(ent):
    """Ia orarul tuturor grupelor de pe aceeasi linie de studiu.
    
    ent: linia de studiu"""
    
    manager = urllib3.PoolManager()
    
    req = manager.request("GET", full_url+ent+".html")
    supa_perisoare = BeautifulSoup(req.data, 'html.parser')
    
    tabele = supa_perisoare.find_all('table')
    
    tabele_conv = []
    for tabel in tabele:
        tabel = tabel.find_all("tr")
        
        un_orar = []
        for action in tabel:
            action = action.find_all("td")
            un_orar.append(list(a.get_text() for a in action) ) 
            
        
        tabele_conv.append(un_orar)
    
    grupe = supa_perisoare.find_all('h1')
    grupe = list(a.get_text() for a in grupe[1:])
    
    result = {}
    for grupa, tabel in zip(grupe, tabele_conv):
        
        un_orar = []
        for action in tabel:
            if len(action) == 8:
                un_orar.append({"Ziua":action[0], "Orele":action[1], "Frecventa": action[2], "Sala":action[3], "Formatia":action[4], "Tipul":action[5], "Disciplina":action[6], "Cadrul didactic":action[7]})
            
        result[grupa] = un_orar
    
    return result
    

def get_orar_grupa(gru):
    
    linia = coresp[int(gru[0])]+gru[1]
    orare = get_orar(linia)
    for grupa in orare.keys():
        if grupa.split()[1] == gru:
            return orare[grupa]  
        
        
    
    
    