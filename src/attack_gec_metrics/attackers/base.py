from dataclasses import dataclass
import abc

class AttackerBase(abc.ABC):
    @dataclass
    class Config:
        verbose: bool = False
        batch_size: int = 32
        show_tqdm=True

    def __init__(self, config=None) -> None:
        self.config = config if config is not None else self.Config()
    
    @abc.abstractmethod
    def correct(self, sources: list[str]) -> list[str]:
        '''Correct source sentences.

        Args:
            sources (list[str]): Source sentences.

        Returns:
            list[str]: (Hacked) corrected sentences.
        '''
        raise NotImplementedError


# Template
# from .base import AttackerBase
# from dataclasses import dataclass
# class AttackerNew(AttackerBase):
#     @dataclass
#     class Config(AttackerBase.Config): ...

#     def __init__(self, config=None) -> None:
#         self.config = config if config is not None else self.Config()
    
#     def correct(self, sources: list[str]) -> list[str]:
#         '''Correct source sentences.

#         Args:
#             sources (list[str]): Source sentences.

#         Returns:
#             list[str]: (Hacked) corrected sentences.
#         '''
#         raise NotImplementedError