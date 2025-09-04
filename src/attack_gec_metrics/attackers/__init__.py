from .base import AttackerBase
from .llm_sent import AttackerForLLMSent
from .impara import AttackerForIMPARA
from .scribendi import AttackerForScribendi
from .some import AttackerForSOME

classes = [
    AttackerForIMPARA,
    AttackerForScribendi,
    AttackerForSOME,
    AttackerForLLMSent
]
__all__ = [c.__name__ for c in classes]
id2class = {
    c.__name__.lower().replace('attackerfor', ''): c for c in classes
}

def get_attacker_ids():
    return list(id2class.keys())

def get_attacker(name=None):
    if name not in get_attacker_ids():
        raise ValueError(f'The name {name} is invalid. Candidates are {get_attacker_ids()}.')
    return id2class[name]