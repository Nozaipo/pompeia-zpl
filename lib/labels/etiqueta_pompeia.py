# label_types/etiqueta_pompeia.py
from .base import LabelBase
import re

class EtiquetaPompeia(LabelBase):
    fields_mapping = {
        "OC": r"\^MD10\^FO35,245\^FB250,1,0,C\^A0N,17,14\^FD ([0-9]+) CORE\^FS",
        "COR": r"\^FO35,265\^FB250,1,0,C\^A0N,18,15\^FD(\w+)\^FS",
        "TAMANHO": r" \^FO35,373\^FB250,1,0,C\^A0N,45,37\^FD (\d+)\^FS",
        "REF": r"\^FO35,285\^FB250,3,0,C\^A0N,13,15\^FD(\d+) - LOVE SECRET\^FS"
    }
    
    fields_label = ["OC", "COR", "TAMANHO", "REF"]

    fields_sequence = {
        "CHECKBOX": 0,
        "OC": 1,
        "COR": 2,
        "TAMANHO": 3,
        "REF": 4,
        "QUANTIDADE": 5
    }

    def __init__(self, raw_code):
        super().__init__(raw_code)

    def get_display_name(self) -> str:
        return "Etiqueta Pompeia"

    def parse(self):
        """Extrai os campos mapeados de um código ZPL."""
        for campo, regex in self.fields_mapping.items():
            m = re.search(regex, self.raw_code)
            self.fields[campo] = m.group(1) if m else ""
        return self.fields
        ...

    @classmethod
    def identify(cls, raw_code: str) -> bool:
        """
        Verifica se o código ZPL pertence a este tipo de etiqueta.
        Deve ser sobrescrito por cada subclasse com uma regra específica.
        """
        fields_finded = []
        for _, regex in cls.fields_mapping.items():
            m = re.search(regex, raw_code)
            if m:
                fields_finded.append(True)
            else:
                fields_finded.append(False)
        return all(fields_finded)
