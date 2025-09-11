from solarpark.services.loopia import LoopiaEmailClient


def loopia_client() -> LoopiaEmailClient:
    return LoopiaEmailClient()
