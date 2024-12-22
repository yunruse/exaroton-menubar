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

        self.pool = None
        for pool in exa.get_credit_pools():
            ss = exa.get_credit_pool_servers(pool.id)
            if any(s.id == self.server.id for s in ss):
                self.pool = pool

        self.players = rumps.MenuItem('Players')
        self.menu.add(self.players)

        self.timer = rumps.MenuItem('Credits', self.credits)
        self.menu.add(self.timer)

        self.usage = rumps.MenuItem('Usage')
        self.menu.add(self.usage)


    def set_icons(self):
        if hasattr(self, 'set_icons_done'):
            return
        self.set_icons_done = True

        for name, icon in (
            ('Start', 'Starting'),
            ('Restart', 'Restarting'),
            ('Stop', 'Stopping'),
        ):
            self._menu[name].set_icon(f'icons/dark/{icon}.png', (16, 16))

        def callback_generator(url):
            def callback(self, bar=None):
                webbrowser.open_new_tab(f'https://exaroton.com/{url}')
            return callback
        
        for name in (
            'Server',
            'Console',
            'Log',
            'Players',
            'Software',
            'Plugins',
            'Files',
            'Worlds',
            'Backups',
            'Access',
            'Transactions',
        ):
            menu = rumps.MenuItem(
                name,
                callback_generator(name.lower()),
                icon=f'icons/dark/{name}.png',
                dimensions=(16, 16))
            self.menu.insert_before('Quit', menu)

        self.menu.insert_before('Server', rumps.separator)
        self.menu.insert_before('Quit', rumps.separator)

    @rumps.timer(5)
    def update(self, bar=None):
        self.set_icons()
        self.server = exa.get_server(self.server.id)

        start: rumps.MenuItem = self._menu['Start']
        restart: rumps.MenuItem = self._menu['Restart']
        stop: rumps.MenuItem = self._menu['Stop']

        if self.server.status == 'Online':
            p = self.server.players.count
            pmax = self.server.players.max
            self.players.title = f'{p}/{pmax}'

            self.players.show()
            start.hide()
            restart.show()
            stop.show()
        else:
            self.players.hide()
            start.show()
            restart.hide()
            stop.hide()

        # import darkdetect
        # theme = darkdetect.theme().lower()
        theme = 'dark'
        
        self.icon = f'icons/{theme}/{self.server.status}.png'
    
    @rumps.timer(60)
    def update_stats(self, bar=None):
        gigabytes = exa.get_server_ram(self.server.id)
        if self.pool:
            credits = exa.get_credit_pool(self.pool.id).credits
        else:
            credits = exa.get_account().credits

        d, h = divmod(credits/ gigabytes, 24)
        self.timer.title = f'{int(d)}d{int(h)}h credits'

        def bytesize(num: int):
            for u in ' kMGTP':
                if num < 1024:
                    return f'{num:.1f} {u}iB'.replace(' i', '')
                num /= 1024

        req = exa._make_request(f"servers/{self.server.id}/files/info/").get('data', {}).get('size')
        self.usage.title = f'{bytesize(req)} used'
    
    def credits(self, bar=None):
        if self.pool:
            webbrowser.open_new_tab(f'https://exaroton.com/pools/{self.pool.id}')
        else:
            webbrowser.open_new_tab(f'https://exaroton.com/credits')

    @rumps.clicked('Start')
    def start_server(self, bar=None):
        print(exa._make_request(f"servers/{self.server.id}/start", "post"))
        self.update()

    @rumps.clicked('Restart')
    def restart_server(self, bar=None):
        print(exa._make_request(f"servers/{self.server.id}/restart", "post"))
        self.update()

    @rumps.clicked('Stop')
    def stop_server(self, bar=None):
        print(exa._make_request(f"servers/{self.server.id}/stop", "post"))
        self.update()

if __name__ == "__main__":
    ExarotonBar().run()