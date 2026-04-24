from .github import GithubExtractor
from .lesswrong import LessWrongExtractor
from .search_pivot import SearchPivotExtractor
from .instagram import InstagramStealthExtractor
from .pivots import BreachEmulatorExtractor, IdentityPivotExtractor
# Map of available extractors
EXTRACTORS = [
    GithubExtractor,
    LessWrongExtractor,
    SearchPivotExtractor,
    InstagramStealthExtractor,
    BreachEmulatorExtractor,
    IdentityPivotExtractor
]
