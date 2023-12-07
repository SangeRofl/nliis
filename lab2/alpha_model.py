from lang_recog_model import LangRecognModel, Lang


class AlphaModel(LangRecognModel):
    def __init__(self):
        self.french_diacritics = ['é', 'è', 'à', 'ù', 'ç', 'â', 'ê', 'î', 'ô', 'ë', 'ï', 'ü']

    def recognize_language(self, text: str):
        for ch in text:
            if ch in self.french_diacritics:
                return Lang.fr
        return Lang.en
