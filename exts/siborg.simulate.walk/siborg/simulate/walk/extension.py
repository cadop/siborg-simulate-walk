import omni.ext
import omni.ui as ui
import omni.usd

import os

import omni.kit.commands
from pxr import Sdf

class SiborgSimulateWalkExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        print("[siborg.simulate.walk] siborg simulate walk startup")

        self._window = ui.Window("Walk to Goal Behavior", width=300, height=100)

        self.stage = omni.usd.get_context().get_stage()

        with self._window.frame:
            with ui.VStack():

                def add_walk_to_prim():
                    # Could also Create/Get/Set Attribute
                    # self._person_prim.SetCustomDataByKey("target_goal", (0,0,0,0))

                    # Get the selections from the stage
                    self._usd_context = omni.usd.get_context()
                    self._selection = self._usd_context.get_selection()
                    selected_paths = self._selection.get_selected_prim_paths()
                    # Get them as prims
                    prims = [self.stage.GetPrimAtPath(x) for x in selected_paths]
                    
                    dir_path = os.path.dirname(os.path.realpath(__file__))
                    behavior_script = os.path.join(dir_path, 'cust_behavior.py')

                    for prim_path in selected_paths:
                        add_animation_graph(prim_path)

                    for prim in prims:
                        add_behavior_script(prim, behavior_script)

                ui.Button("Add Walk", clicked_fn=add_walk_to_prim)

    def on_shutdown(self):
        print("[siborg.simulate.walk] siborg simulate walk shutdown")

def add_animation_graph(prim_path):
    omni.kit.commands.execute('ApplyAnimationGraphAPICommand',
        paths=[Sdf.Path(prim_path)],
        animation_graph_path=Sdf.Path('/World/Biped_Setup/CharacterAnimation/AnimationGraph'))

def add_behavior_script(prim, script):
    omni.kit.commands.execute('ApplyScriptingAPICommand', paths=[Sdf.Path(prim.GetPath())])
    omni.kit.commands.execute('RefreshScriptingPropertyWindowCommand')

    attr = prim.GetAttribute("omni:scripting:scripts")
    val = attr.Get()
    if val:
        scripts = list(val)
        scripts.append(scripts)
        attr.Set(scripts)
    else:
        attr.Set([script])
