class ImportSDFUseCase:
    def __init__(self, repo, parser) -> None:
        self._repo = repo
        self._parser = parser

    def execute(self, file_path: str) -> None:
        """Parses the file and saves data in batches."""
        pass
