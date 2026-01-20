from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from src.interface.cli import cli


def test_cli_import_verilog_calls_usecase():
    """
    Verify that 'import-verilog' command correctly invokes ImportVerilogUseCase.
    """
    runner = CliRunner()
    mock_usecase = MagicMock()

    with runner.isolated_filesystem():
        Path("design.v").touch()

        with patch("src.interface.cli.ImportVerilogUseCase") as mock_class:
            mock_class.return_value = mock_usecase

            # Act
            result = runner.invoke(
                cli, ["import-verilog", "design.v", "--db", "graph.db"]
            )

            # Assert
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "Importing Verilog" in result.output

            mock_usecase.execute.assert_called_once()
            args, _ = mock_usecase.execute.call_args
            assert args[0].name == "design.v"


def test_cli_import_sdf_calls_usecase():
    """
    Verify that 'import-sdf' command correctly invokes ImportSDFUseCase.
    """
    runner = CliRunner()
    mock_usecase = MagicMock()

    with runner.isolated_filesystem():
        Path("delay.sdf").touch()

        with patch("src.interface.cli.ImportSDFUseCase") as mock_class:
            mock_class.return_value = mock_usecase

            # Act
            result = runner.invoke(cli, ["import-sdf", "delay.sdf", "--db", "graph.db"])

            # Assert
            assert result.exit_code == 0, f"Command failed: {result.output}"
            assert "Importing SDF" in result.output

            mock_usecase.execute.assert_called_once()
            args, _ = mock_usecase.execute.call_args
            assert args[0].name == "delay.sdf"
