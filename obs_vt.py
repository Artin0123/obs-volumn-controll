import obspython as S  # studio
from types import SimpleNamespace
from ctypes import *
from ctypes.util import find_library

obsffi = CDLL("obs")  #windows

G = SimpleNamespace()

def wrap(funcname, restype, argtypes):
    """Simplify wrapping ctypes functions in obsffi"""
    func = getattr(obsffi, funcname)
    func.restype = restype
    func.argtypes = argtypes
    globals()["g_" + funcname] = func

class Source(Structure):
    pass

class Volmeter(Structure):
    pass

volmeter_callback_t = CFUNCTYPE(
    None, c_void_p, POINTER(c_float), POINTER(c_float), POINTER(c_float)
)

wrap("obs_get_source_by_name", POINTER(Source), argtypes=[c_char_p])
wrap("obs_source_release", None, argtypes=[POINTER(Source)])
wrap("obs_volmeter_create", POINTER(Volmeter), argtypes=[c_int])
wrap("obs_volmeter_destroy", None, argtypes=[POINTER(Volmeter)])
wrap(
    "obs_volmeter_add_callback",
    None,
    argtypes=[POINTER(Volmeter), volmeter_callback_t, c_void_p],
)
wrap(
    "obs_volmeter_remove_callback",
    None,
    argtypes=[POINTER(Volmeter), volmeter_callback_t, c_void_p],
)
wrap(
    "obs_volmeter_attach_source",
    c_bool,
    argtypes=[POINTER(Volmeter), POINTER(Source)],
)

@volmeter_callback_t
def volmeter_callback(data, mag, peak, input):
    G.noise = float(peak[0])

def output_to_file(volume):
    print(str(volume))

def check_mouth_visibility(volume):
    if volume >= G.threshold:
        setVisibility(G.scene_Name, G.mouth_image_source_name, True)
    else:
        setVisibility(G.scene_Name, G.mouth_image_source_name, False)

OBS_FADER_LOG = 2
G.lock = False
G.start_delay = 3
G.duration = 0
G.noise = -60.0
G.tick = 300
G.tick_mili = G.tick * 0.001
G.source_name = "擷取音訊輸出"
G.volmeter = "not yet initialized volmeter instance"
G.mouth_image_source_name = "mouth"
G.scene_Name = "Walling"
G.threshold = -30.0

def setVisibility(sceneName, sourceName, visible, doPrint=False):
    if doPrint:
        print('set %s\'s %s visibility to %s' % (sceneName, sourceName, 'True' if visible else 'False'))
    source = S.obs_get_source_by_name(sourceName)
    scene = S.obs_get_scene_by_name(sceneName)
    scene_item = S.obs_scene_find_source(scene, sourceName)
    if scene_item:
        S.obs_sceneitem_set_visible(scene_item, visible)
    S.obs_scene_release(scene)
    S.obs_source_release(source)

def event_loop():
    """wait n seconds, then execute callback with db volume level within interval"""
    if G.duration > G.start_delay:
        if not G.lock:
            # setting volmeter
            source = g_obs_get_source_by_name(G.source_name.encode("utf-8"))
            G.volmeter = g_obs_volmeter_create(OBS_FADER_LOG)
            g_obs_volmeter_add_callback(G.volmeter, volmeter_callback, None)
            if g_obs_volmeter_attach_source(G.volmeter, source):
                # Attached to source
                g_obs_source_release(source)
                G.lock = True
                return
        # output_to_file(G.noise)
        check_mouth_visibility(G.noise)
    else:
        G.duration += G.tick_mili

def script_load(settings):
    S.timer_add(event_loop, G.tick)

def script_unload():
    g_obs_volmeter_remove_callback(G.volmeter, volmeter_callback, None)
    g_obs_volmeter_destroy(G.volmeter)
    G.lock = False
    G.duration = 0
    G.start_delay = 3
    G.noise = -60.0
    print("Removed volmeter & volmeter_callback")
