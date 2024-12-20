import webbrowser
import exaroton
import exaroton.types
import rumps

with open('exaroton.keys') as f:
    exa = exaroton.Exaroton(f.read())

class ExarotonBar(rumps.App):

    def __init__(self):
        super().__init__(name="")

        self.servers = exa.get_servers()

        # TODO: a selector for multiple servers!
        self.server = self.servers[0]
        for pool in exa.get_credit_pools():
            ss = exa.get_credit_pool_servers(pool.id)
            if any(s.id == self.server.id for s in ss):
                break
        else:
            self.pool = None
        self.pool = pool

        self.players = rumps.MenuItem('Players')
        self.menu.add(self.players)

        self.timer = rumps.MenuItem('Timer')
        self.menu.add(self.timer)
    
    @rumps.timer(10)
    def update(self, state=None):
        self.server = exa.get_server(self.server.id)

        p = self.server.players.count
        pmax = self.server.players.max
        self.players.title = f'{p}/{pmax}'

        gigabytes = exa.get_server_ram(self.server.id)
        self.pool = exa.get_credit_pool(self.pool.id)
        hours = self.pool.credits / gigabytes
        d, h = divmod(hours, 24)
        self.timer.title = f'{int(d)}d{int(h)}h credits'

        # import darkdetect
        # theme = darkdetect.theme().lower()
        theme = 'dark'
        
        self.icon = f'icons/{theme}/{self.server.status}.png'

    @rumps.clicked('Console')
    def console(self, state=None):
        webbrowser.open_new_tab('https://exaroton.com/console/')
    
    @rumps.clicked('Worlds')
    def console(self, state=None):
        webbrowser.open_new_tab('https://exaroton.com/worlds/')

if __name__ == "__main__":
    ExarotonBar().run()