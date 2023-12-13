from cat.mad_hatter.decorators import tool, hook
import requests

# Tools are Python functions called by the LLM to execute actions. 
# They are made of two parts: the first one contains instructions that 
# explain the LLM when and how to call function; the second one 
# contains the actual code to execute.

progettiDict = {}
projects = []

@hook
def agent_prompt_prefix(prefix, cat):
    prefix = """Tu sei ACBot, la nostra guida all'interno della piattaforma HypeIoT (link: https://hyperiot.cloud). Sei molto gentile e super disponibile ad ogni richiesta."""
    token = f"JWT {cat.user_id}"
    r = requests.get("https://microservices-test.hyperiot.cloud/hyperiot/hprojects/all/cards", headers={'Authorization': token}, verify=False)
    for obj in r.json():
        print(obj)
        progettiDict[obj['name'].lower()] = obj['id']
        projects.append(obj['name'])
    return prefix

@tool
def link_github(arg, cat):
    """Link Github del progetto? Rispondere con https://github.com/HyperIoT-Labs"""
    return "https://github.com/HyperIoT-Labs"

@tool
def cosa_e(arg, cat):
    """Cosa è? L'input è dopo il ?"""
    if arg.lower() in ["hyperiot"]:
        return "HyperIoT è una piattaforma Open Source No-Code Cloud Native per la gestione di big data da qualsiasi rete IIoT disponibile su Github"
    elif arg.lower() in ["link", "github", "link github"]:
         return "link github https://github.com/HyperIoT-Labs"
    else:
        return "Non lo so"
    
@tool
def quali_sono_i_progetti_di_hyperiot(arg, cat):
    """Quali sono i progetti di Hyperiot? Rispondi con la lista dei progetti"""
    token = f"JWT {cat.user_id}"
    r = requests.get("https://microservices-test.hyperiot.cloud/hyperiot/hprojects/all/cards", headers={'Authorization': token}, verify=False)
    for obj in r.json():
        progettiDict[obj['name']] = obj['id']
        projects.append(obj['name'])
    res = "Ecco la lista dei progetti:\n"
    for p in projects:
        res = res + p + "\n"
    return  res

@tool
def quali_sono_i_device_del_progetto(arg, cat):
    """Quali sono i device del progetto? L'input è il nome del progetto"""
    token = f"JWT {cat.user_id}"
    projectId = progettiDict[arg.lower()]
    r = requests.get(f"http://microservices-test.hyperiot.cloud/hyperiot/hdevices/all/{projectId}", headers={'Authorization': token}, verify=False)
    return r.json()

@tool
def quali_sono_i_pacchetti_del_progetto(arg, cat):
    """Quali sono i pacchetti del progetto? L'input è il nome del progetto"""
    token = f"JWT {cat.user_id}"
    projectId = progettiDict[arg.lower()]
    r = requests.get(f"http://microservices-test.hyperiot.cloud/hyperiot/hpackets/all/{projectId}", headers={'Authorization': token}, verify=False)
    return r.json()
