from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

Window.clearcolor = (1, 1, 1, 1)
Window.softinput_mode = "resize"

JAUNE = (1, 0.80, 0, 1)
NOIR = (0, 0, 0, 1)
BLANC = (1, 1, 1, 1)
GRIS = (0.45, 0.45, 0.45, 1)
GRIS_CLAIR = (0.88, 0.88, 0.88, 1)
ROUGE = (0.8, 0.1, 0.1, 1)
VERT = (0.07, 0.38, 0.20, 1)
VERT_CLAIR = (0.91, 0.96, 0.92, 1)

ETAPES = [
    ("longueur", "Longueur de la parcelle", "en mètres (m)"),
    ("largeur", "Largeur de la parcelle", "en mètres (m)"),
    ("esp_lignes", "Espacement entre les lignes", "en centimètres (cm)"),
    ("esp_plants", "Espacement entre les plants", "en centimètres (cm)"),
    ("testees", "Nombre de graines testées", "nombre entier"),
    ("germees", "Nombre de graines germées", "nombre entier"),
    ("pmg", "Poids de 1 000 graines (PMG)", "en grammes (g)"),
]


def fmt(nombre):
    return f"{nombre:,.0f}".replace(",", " ")


def texte(contenu, taille, couleur, gras=False, hauteur=None, align="center"):
    lab = Label(text=contenu, font_size=taille, color=couleur,
                bold=gras, halign=align, valign="middle")
    lab.bind(size=lambda i, s: setattr(i, "text_size", s))
    if hauteur:
        lab.size_hint_y = None
        lab.height = dp(hauteur)
    return lab


class Carte(BoxLayout):
    def __init__(self, couleur, rayon=14, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(*couleur)
            self.rect = RoundedRectangle(radius=[dp(rayon)])
        self.bind(pos=self.maj, size=self.maj)

    def maj(self, *a):
        self.rect.pos = self.pos
        self.rect.size = self.size


class Bouton(Button):
    def __init__(self, couleur_fond, couleur_texte=NOIR, **kw):
        super().__init__(**kw)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = couleur_texte
        self.bold = True
        with self.canvas.before:
            Color(*couleur_fond)
            self.rect = RoundedRectangle(radius=[dp(14)])
        self.bind(pos=self.maj, size=self.maj)

    def maj(self, *a):
        self.rect.pos = self.pos
        self.rect.size = self.size


def ligne(libelle, valeur, fond=VERT_CLAIR, couleur_valeur=VERT):
    c = Carte(fond, orientation="horizontal", size_hint_y=None,
              height=dp(58), padding=[dp(14), 0], spacing=dp(8))
    g = texte(libelle, "15sp", NOIR, align="left")
    g.size_hint_x = 0.55
    d = texte(valeur, "19sp", couleur_valeur, gras=True, align="right")
    d.size_hint_x = 0.45
    c.add_widget(g)
    c.add_widget(d)
    return c


def zone_defilante(widgets):
    zone = ScrollView(bar_width=dp(3))
    boite = BoxLayout(orientation="vertical", spacing=dp(8),
                      size_hint_y=None, padding=[0, dp(4)])
    boite.bind(minimum_height=boite.setter("height"))
    for w in widgets:
        boite.add_widget(w)
    zone.add_widget(boite)
    return zone


class AgroDensity(App):
    def build(self):
        self.valeurs = {}
        self.etape = 0
        self.racine = BoxLayout(orientation="vertical",
                                padding=dp(16), spacing=dp(10))
        self.afficher_etape()
        return self.racine

    # ---------- CALCULS ----------
    def resultats(self, n):
        v = {k: float(self.valeurs[k])
             for k, _, _ in ETAPES[:n] if k in self.valeurs}
        res = []
        total = 0
        if "largeur" in v:
            res.append(("Superficie",
                        f"{v['longueur'] * v['largeur']:.2f} m²"))
        if "esp_plants" in v:
            nbl = int(v["largeur"] * 100 / v["esp_lignes"])
            npl = int(v["longueur"] * 100 / v["esp_plants"])
            total = nbl * npl
            res.append(("Nombre de lignes", fmt(nbl)))
            res.append(("Plants par ligne", fmt(npl)))
            res.append(("Total de plants", fmt(total)))
        if "germees" in v:
            taux = v["germees"] / v["testees"] * 100
            semences = total / (taux / 100)
            res.append(("Taux de germination", f"{taux:.2f} %"))
            res.append(("Semences nécessaires", fmt(semences)))
            if "pmg" in v:
                g = semences * v["pmg"] / 1000
                res.append(("Poids des semences", f"{g:.2f} g"))
                res.append(("Poids en kilos", f"{g / 1000:.3f} kg"))
        return res

    def entete(self):
        h = Carte(VERT, orientation="vertical", size_hint_y=None,
                  height=dp(60), padding=dp(6))
        h.add_widget(texte("AGRO DENSITY", "24sp", BLANC, gras=True))
        return h

    # ---------- ÉCRAN D'UNE QUESTION ----------
    def afficher_etape(self):
        self.racine.clear_widgets()
        cle, titre, unite = ETAPES[self.etape]

        self.racine.add_widget(self.entete())

        # barre de progression
        barre = BoxLayout(size_hint_y=None, height=dp(8))
        part = (self.etape + 1) / len(ETAPES)
        plein = Carte(JAUNE, rayon=4, size_hint_x=part)
        vide = Carte(GRIS_CLAIR, rayon=4, size_hint_x=max(1 - part, 0.001))
        barre.add_widget(plein)
        barre.add_widget(vide)
        self.racine.add_widget(barre)

        self.racine.add_widget(texte(
            f"Étape {self.etape + 1} sur {len(ETAPES)}",
            "14sp", GRIS, hauteur=22))
        self.racine.add_widget(texte(titre, "21sp", NOIR,
                                     gras=True, hauteur=56))
        self.racine.add_widget(texte(unite, "15sp", GRIS, hauteur=22))

        # case noire (cadre) + intérieur blanc
        cadre = Carte(NOIR, rayon=12, size_hint_y=None,
                      height=dp(70), padding=dp(3))
        self.champ = TextInput(
            multiline=False, input_filter="float",
            text=self.valeurs.get(cle, ""),
            font_size="22sp", padding=[dp(14), dp(18)],
            background_normal="", background_active="",
            background_color=BLANC,
            foreground_color=NOIR, cursor_color=NOIR)
        self.champ.bind(on_text_validate=self.suivant)
        cadre.add_widget(self.champ)
        self.racine.add_widget(cadre)

        self.erreur = texte("", "14sp", ROUGE, hauteur=22)
        self.racine.add_widget(self.erreur)

        # boutons
        rangee = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(10))
        if self.etape > 0:
            retour = Bouton(GRIS_CLAIR, NOIR, text="Retour",
                            font_size="16sp", size_hint_x=0.3)
            retour.bind(on_release=self.retour)
            rangee.add_widget(retour)
        suiv = Bouton(JAUNE, NOIR, text="SUIVANT", font_size="19sp")
        suiv.bind(on_release=self.suivant)
        rangee.add_widget(suiv)
        self.racine.add_widget(rangee)

        # calculs déjà faits
        res = self.resultats(self.etape)
        if res:
            cartes = [texte("Calculs déjà faits", "14sp", GRIS, hauteur=22)]
            cartes += [ligne(a, b) for a, b in res]
        else:
            cartes = [texte("Les calculs apparaîtront ici.",
                            "14sp", GRIS, hauteur=30)]
        self.racine.add_widget(zone_defilante(cartes))

        Clock.schedule_once(
            lambda dt: setattr(self.champ, "focus", True), 0.3)

    # ---------- BOUTONS ----------
    def suivant(self, *args):
        cle = ETAPES[self.etape][0]
        brut = self.champ.text.replace(",", ".").strip()
        try:
            val = float(brut)
        except ValueError:
            self.erreur.text = "Écris un nombre."
            return
        if val <= 0:
            self.erreur.text = "Le nombre doit être supérieur à 0."
            return
        if cle == "germees" and val > float(self.valeurs["testees"]):
            self.erreur.text = "Les graines germées dépassent les graines testées."
            return

        self.valeurs[cle] = brut
        if self.etape < len(ETAPES) - 1:
            self.etape += 1
            self.afficher_etape()
        else:
            self.afficher_final()

    def retour(self, *args):
        self.etape -= 1
        self.afficher_etape()

    def recommencer(self, *args):
        self.valeurs = {}
        self.etape = 0
        self.afficher_etape()

    # ---------- ÉCRAN FINAL ----------
    def afficher_final(self):
        self.racine.clear_widgets()
        self.racine.add_widget(self.entete())
        self.racine.add_widget(texte("RÉSULTATS FINAUX", "20sp", NOIR,
                                     gras=True, hauteur=44))

        res = self.resultats(len(ETAPES))
        cartes = []
        for i, (a, b) in enumerate(res):
            if a.startswith("Poids"):
                cartes.append(ligne(a, b, fond=JAUNE, couleur_valeur=NOIR))
            else:
                cartes.append(ligne(a, b))
        self.racine.add_widget(zone_defilante(cartes))

        b = Bouton(VERT, BLANC, text="RECOMMENCER", font_size="19sp",
                   size_hint_y=None, height=dp(54))
        b.bind(on_release=self.recommencer)
        self.racine.add_widget(b)


AgroDensity().run()