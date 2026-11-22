from pathlib import Path
import math
import pickle
import Orange
import json

# PAS 3
def carregar_model(ruta):
    with open(ruta, "rb") as fitxer:
        model = pickle.load(fitxer)
    return model


# PAS 4
def mostrar_variables(model):
    for variable in model.original_domain.attributes:
        if variable.is_discrete:
            print(f"- {variable.name}: opcions vàlides -> {', '.join(variable.values)}")
        else:
            print(f"- {variable.name}: numèrica")


# PAS 7
def predir_preu_fitxer(model, ruta):
    domini = Orange.data.Domain(model.original_domain.attributes)
    taula = Orange.data.Table.from_file(str(ruta)).transform(domini)

    prediccions = model(taula)
    return [round(float(p), 2) for p in prediccions]

# PAS 5
def predir_preu(model, dictio):
    domini = Orange.data.Domain(model.original_domain.attributes)
    fila = [dictio[var.name] for var in domini.attributes]
    taula = Orange.data.Table.from_list(domini, [fila])
    prediccio = model(taula)
    return float(prediccio[0])


# PAS 8
def demanar_float(missatge):
    while True:
        entrada = input(missatge).strip().replace(",", ".")
        try:
            valor = float(entrada)
        except ValueError:
            print("Introdueix un nombre vàlid.")
            continue

        if not math.isfinite(valor) or valor <= 0:
            print("El valor ha de ser més gran que zero.")
            continue

        return valor


def demanar_portatil(model):
    dictio = {}
    for variable in model.original_domain.attributes:
        nom = variable.name
        etiqueta = nom.replace("_", " ")
        if isinstance(variable, Orange.data.DiscreteVariable):
            opcions = variable.values
            while True:
                entrada = input(f"Introdueix {etiqueta} ({'/'.join(opcions)}): ").strip()
                valor = None

                for opcio in opcions:
                    if entrada.casefold() == opcio.casefold():
                        valor = opcio
                        break

                if valor is None:
                    print(f"Valor no vàlid. Opcions: {', '.join(opcions)}.")
                    continue
                break
        else:
            valor = demanar_float(f"Introdueix {etiqueta}: ")

        dictio[nom] = valor

    return dictio

# PAS 9
def valorar(preu_botiga, preu_predit, mae):
    if preu_botiga < preu_predit - mae:
        return "ganga"
    elif preu_botiga > preu_predit + mae:
        return "car"
    else:
        return "preu raonable"


# PAS 6
if __name__ == "__main__":
    carpeta = Path(__file__).parent
    MAE = 74.6

    # # PAS 3
    ruta = carpeta / "ModelRegression.pkcls"
    model = carregar_model(ruta)

    # PAS 4
    print("Aquestes són les variables del model:")
    mostrar_variables(model)

    # # PAS 7
    # # print(f'\n Predir')
    # # print(predir_preu_fitxer(model, carpeta / "portatils_prediccio.csv"))

    # # PAS 8
    # portatil = demanar_portatil(model)
    # preu_botiga = demanar_float("Indica el preu del portàtil que et vols comprar: ")

    # # PAS 5
    # preu_predit = predir_preu(model, portatil)

    # # PAS 9
    # diferencia = preu_botiga - preu_predit
    # veredicte = valorar(preu_botiga, preu_predit, MAE)

    # print(f"\nPreu predit pel model: {preu_predit:.2f} €")
    # print(f"Diferència respecte a la botiga: {diferencia:+.2f} €")
    # print(f"Veredicte: {veredicte}")
    
    # PAS 10
    ruta_json = carpeta / "consultes.json"
    llista_consultes = []
    if ruta_json.exists():
        try:
            with open(ruta_json, "r", encoding="utf-8") as fitxer_json:
                dades = json.load(fitxer_json)
                if isinstance(dades, list):
                    llista_consultes = dades
        except (json.JSONDecodeError, OSError):
            print("Avís: no s'ha pogut llegir consultes.json, s'inicia un historial nou.")
            llista_consultes = []
    
    while True:
        portatil = demanar_portatil(model)
        preu_botiga = demanar_float("Indica el preu del portàtil que et vols comprar: ")
        preu_predit = predir_preu(model, portatil)

        diferencia = preu_botiga - preu_predit
        veredicte = valorar(preu_botiga, preu_predit, MAE)

        print(f"\nPreu predit pel model: {preu_predit:.2f} €")
        print(f"Diferència respecte a la botiga: {diferencia:+.2f} €")
        print(f"Veredicte: {veredicte}")

        llista_consultes.append({
            "portatil": portatil,
            "preu_botiga": preu_botiga,
            "preu_predit": round(preu_predit, 2),
            "veredicte": veredicte,
        })

        while True:
            una_altra = input("\nVols fer una altra consulta? (Sí/No): ").strip().casefold()
            if una_altra in ("si", "sí", "s"):
                continuar = True
                break
            if una_altra in ("no", "n"):
                continuar = False
                break
            print("Resposta no vàlida. Escriu Sí o No.")

        if not continuar:
            break
        
    try:
        with open(ruta_json, "w", encoding="utf-8") as fitxer_json:
            json.dump(llista_consultes, fitxer_json, indent=2, ensure_ascii=False)
    except OSError as error:
        print(f"Error en desar consultes.json: {error}")
     