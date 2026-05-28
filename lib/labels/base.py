# label_types/base.py
from abc import ABC, abstractmethod
import re

class LabelMeta(type):
    """Metaclasse que registra automaticamente todas as subclasses de LabelBase."""
    registry = []

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if name != 'LabelBase':   # não registra a classe abstrata
            LabelMeta.registry.append(cls)
        return cls

class LabelBase(metaclass=LabelMeta):
    """Classe base abstrata para todos os modelos de etiqueta."""

    def __init__(self, raw_code: str):
        self.raw_code = raw_code
        self.fields = {}       # armazena campos ^FD extraídos
        self.quantity = 1      # quantidade padrão
        self.parse()           # análise inicial do ZPL
        
    def get_display_name(self) -> str:
        """Nome amigável para exibição na UI."""
        return self.__class__.__name__

    def get_print_data(self, quantity: int = None):
        """Retorna o ZPL pronto para impressão (pode ser customizado)."""
        return self.raw_code

    @abstractmethod
    def parse(self):
        """Extrai os campos mapeados de um código ZPL."""
        ...

    @classmethod
    @abstractmethod
    def identify(cls, raw_code: str) -> bool:
        """
        Verifica se o código ZPL pertence a este tipo de etiqueta.
        Deve ser sobrescrito por cada subclasse com uma regra específica.
        """
        ...
