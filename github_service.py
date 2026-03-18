import logging
from typing import Optional
from github import Auth, Github, GithubException, InputFileContent
from config import Config
from exceptions import GitHubAPIException

logger = logging.getLogger(__name__)


class GitHubService:
    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token or Config.GITHUB_TOKEN
        if not self.token:
            logger.error("Token do GitHub é obrigatório")
            raise ValueError("Token do GitHub é obrigatório")

        try:
            auth = Auth.Token(self.token)
            self.client = Github(auth=auth)
            self.client.get_user().login
            logger.debug("Serviço GitHub inicializado com sucesso")
        except GithubException as e:
            logger.error(f"Falha ao autenticar com GitHub: {e}")
            raise GitHubAPIException(f"Autenticação falhou: {str(e)}", e)

    def create_gist_with_comment(self, city: str, comment: str) -> dict:
        logger.info(f"Criando novo gist para: {city}")
        
        try:
            user = self.client.get_user()
            
            files = {
                f"clima_{city.replace(' ', '_')}.txt": InputFileContent(comment)
            }
            
            gist = user.create_gist(
                public=False,
                files=files,
                description=f"Comentário de clima para {city}"
            )
            
            logger.info(f"Gist criado com sucesso: {gist.id}")
            
            return {
                "id": gist.id,
                "url": gist.html_url,
                "description": gist.description,
                "created_at": gist.created_at,
                "comment": comment,
            }
        
        except GithubException as e:
            logger.error(f"Erro da API GitHub ao criar gist: {e}")
            raise GitHubAPIException(
                f"Falha ao criar gist: {str(e)}", e, {"city": city}
            )
