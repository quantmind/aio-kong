from .components import Component


class Jwts(Component):
    def get_consumer(self, id):
        """
        This is a bit special.
        /jwts/<id> -> 404
        /jwts/<id>/consumer -> Consumer
        """
        url = f'{self.url}/{id}/consumer'
        return self.execute(url, wrap=self.cli.consumers.wrap)
