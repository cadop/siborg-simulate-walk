from omni.anim.people.scripts.commands.goto import GoTo


class CustomGo(GoTo):
    def __init__(self, character, command, navigation_manager):
        super().__init__(character, command, navigation_manager)

    def update_path(self, new_command):
        ''' update the path on the goto command by generating a new one
        check that the current position was broadcast
        
        Note: This is NOT related to the navigation_manager update_path
        '''
        self.navigation_manager.generate_goto_path(new_command)
