
from enum import Enum

class LanguageEnum(Enum):
    PYTHON = "python"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    GO = "go"

LANGUAGE_TO_SUFFIX = {
    LanguageEnum.PYTHON: ("py",),
    LanguageEnum.JAVA: ("java",),
    LanguageEnum.CPP: ("cpp", "cc", "hpp"),
    LanguageEnum.C: ("c", "h"),
    LanguageEnum.GO: ("go",),
}
