
from __future__ import annotations

from pxr import Gf, UsdGeom, Usd, Sdf
import omni.usd

from omni.anim.people.scripts.character_behavior import CharacterBehavior
from .cust_go import CustomGo as GoTo


class CustomBehavior(CharacterBehavior):

    def __init__(self, prim_path: Sdf.Path):
        super().__init__(prim_path)

    def on_init(self):
        super().on_init()
        # This could be simply in renew_character_state, but this is easier to follow
        self.assign_goal()

    def assign_goal(self):
        # # Create an xform
        newpath = self.prim_path.AppendPath('Goal')
        # check if there is already a Goal (and if there is,
        # whoever added better have a transform)
        prim: Usd.Prim = self.stage.GetPrimAtPath(newpath)

        # Need to set all of these to make transforms work can't just use translate
        if not prim:
            xform_faster = UsdGeom.Xform.Define(self.stage, newpath)

            prim_trans = xform_faster.AddTranslateOp()
            prim_trans.Set(Gf.Vec3f(0.0, 0.0, 0.0))

            prim_rot = xform_faster.AddOrientOp()
            prim_rot.Set(Gf.Quatf(0.0, 0.0, 0.0, 1.0))

            prim_scale = xform_faster.AddScaleOp()
            prim_scale.Set(Gf.Vec3f(1.0, 1.0, 1.0))

        self.goal_prim = self.stage.GetPrimAtPath(newpath)

    def on_play(self):
        # Make sure we have a goal (incase someone deleted it after creating character)
        super().on_play()
        self.assign_goal()

    def get_command(self, command):
        if command[0] == "GoTo":
            return GoTo(self.character, command, self.navigation_manager)

        # We don't really need this right now, but just a reminder of other possible commands
        return super().get_command(command)

    # def read_commands_from_file(self):
    #     ''' Overwritten method to skip the file reading part '''
    #     # The command parser creates this format, so we just use it for now
    #     return [['GoTo', '0', '0', '0', '0']]


    def get_simulation_commands(self):
        ''' Overwritten method to skip the file reading part '''
        # The command parser creates this format, so we just use it for now
        return [['GoTo', '0', '0', '0', '0']]
    
    def on_update(self, current_time: float, delta_time: float):
        """
        Called on every update. Initializes character at start,
        publishes character positions and executes character commands.
        :param float current_time: current time in seconds.
        :param float delta_time: time elapsed since last update.
        """
        if self.character is None:
            if not self.init_character():
                return

        # Make sure we have an active goal
        if not self.goal_prim.IsValid():
            # This should only happen if goal prim was deleted during Play
            # The existing goal will still be in memory and animation continues there
            return

        if self.avoidanceOn:
            self.navigation_manager.publish_character_positions(delta_time, 0.5)

        if self.commands:

            if self.current_command:
                # First get where the character currently is
                # Get the current goal attribute
                goal_position = omni.usd.get_world_transform_matrix(self.goal_prim).ExtractTranslation()
                new_goal = (goal_position[0], goal_position[1], goal_position[2], 0)

                # Two options to try `query_navmesh_path` and `validate_navmesh_point`
                # For now, we pre-query the path to check if it will work, and if not, just skip trying to update
                cur_pos = self.navigation_manager.character_manager.get_character_current_pos(self.prim_path.pathString)
                test_path = self.navigation_manager.navigation_interface.query_navmesh_path(cur_pos, new_goal)

                # If there is no path, don't go there
                if test_path is None:
                    return

                self.current_command.update_path(new_goal)

            self.execute_command(self.commands, delta_time)


