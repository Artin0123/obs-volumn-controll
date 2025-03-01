import obspython as S  # studio
from types import SimpleNamespace
from ctypes import *
from ctypes.util import find_library

obsffi = CDLL("obs")  # windows

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
G.animation_lock = False  # 新增動畫鎖
G.animation_duration = 1000  # 動畫持續時間 (毫秒)
G.animation_timer = 0  # 動畫計時器
G.animation_phase = "up"  # 動畫階段：上升或下降
G.animation_step = 0  # 動畫步驟計數
G.animation_total_steps = 10  # 每個階段的步驟總數 (10步)
G.animation_step_distance = 1  # 每步移動的像素數 (1px)
G.animation_step_interval = 50  # 每步的間隔 (50毫秒，即0.05秒)
G.start_delay = 3
G.duration = 0
G.noise = -60.0
G.tick = 50
G.tick_mili = G.tick * 0.001
G.source_name = "擷取音訊輸入"
G.volmeter = "not yet initialized volmeter instance"
G.vt_source_name = "vtuber"
G.mouth_image_source_name = "mouth"
G.scene_Name = "Julti"
G.threshold = -30.0


def setVisibility(sceneName, sourceName, visible, doPrint=False):
    if doPrint:
        print(
            "set %s's %s visibility to %s"
            % (sceneName, sourceName, "True" if visible else "False")
        )
    source = S.obs_get_source_by_name(sourceName)
    scene = S.obs_get_scene_by_name(sceneName)
    scene_item = S.obs_scene_find_source(scene, sourceName)
    if scene_item:
        S.obs_sceneitem_set_visible(scene_item, visible)
    S.obs_scene_release(scene)
    S.obs_source_release(source)


def getPosition(sceneName, sourceName):
    """獲取物件的位置"""
    source = S.obs_get_source_by_name(sourceName)
    scene = S.obs_get_scene_by_name(sceneName)
    scene_item = S.obs_scene_find_source(scene, sourceName)
    pos = S.vec2()
    if scene_item:
        S.obs_sceneitem_get_pos(scene_item, pos)
    S.obs_scene_release(scene)
    S.obs_source_release(source)
    return (pos.x, pos.y)


def setPosition(sceneName, sourceName, x, y, doPrint=False):
    """設定物件的位置"""
    if doPrint:
        print("set %s's %s position to (%d, %d)" % (sceneName, sourceName, x, y))
    source = S.obs_get_source_by_name(sourceName)
    scene = S.obs_get_scene_by_name(sceneName)
    scene_item = S.obs_scene_find_source(scene, sourceName)
    if scene_item:
        pos = S.vec2()
        pos.x = x
        pos.y = y
        S.obs_sceneitem_set_pos(scene_item, pos)
    S.obs_scene_release(scene)
    S.obs_source_release(source)


def animate_jump():
    """開始角色跳躍的動畫"""
    # 獲取當前位置
    G.original_vt_pos = getPosition(G.scene_Name, G.vt_source_name)
    G.original_mouth_pos = getPosition(G.scene_Name, G.mouth_image_source_name)

    # 設定動畫鎖和計時器
    G.animation_lock = True
    G.animation_timer = G.animation_step_interval
    G.animation_phase = "up"
    G.animation_step = 0

    # 設定嘴巴可見
    setVisibility(G.scene_Name, G.mouth_image_source_name, True)


def update_jump_animation():
    """更新跳躍動畫狀態"""
    if G.animation_phase == "up":
        # 上升階段
        vt_pos = getPosition(G.scene_Name, G.vt_source_name)
        mouth_pos = getPosition(G.scene_Name, G.mouth_image_source_name)

        # 向上移動1px
        setPosition(
            G.scene_Name,
            G.vt_source_name,
            vt_pos[0],
            vt_pos[1] - G.animation_step_distance,
        )
        setPosition(
            G.scene_Name,
            G.mouth_image_source_name,
            mouth_pos[0],
            mouth_pos[1] - G.animation_step_distance,
        )

        # 更新步驟計數
        G.animation_step += 1

        # 檢查是否需要切換到下降階段
        if G.animation_step >= G.animation_total_steps:
            G.animation_phase = "wait"  # 改為等待階段
            G.animation_step = 0
    elif G.animation_phase == "wait":
        # 等待階段 - 檢查音量是否低於閾值
        if G.noise < G.threshold:
            # 音量低於閾值，開始下降
            G.animation_phase = "down"
    else:
        # 下降階段
        vt_pos = getPosition(G.scene_Name, G.vt_source_name)
        mouth_pos = getPosition(G.scene_Name, G.mouth_image_source_name)

        # 向下移動1px
        setPosition(
            G.scene_Name,
            G.vt_source_name,
            vt_pos[0],
            vt_pos[1] + G.animation_step_distance,
        )
        setPosition(
            G.scene_Name,
            G.mouth_image_source_name,
            mouth_pos[0],
            mouth_pos[1] + G.animation_step_distance,
        )

        # 更新步驟計數
        G.animation_step += 1

        # 檢查是否動畫已完成
        if G.animation_step >= G.animation_total_steps:
            G.animation_lock = False
            G.animation_phase = "up"
            G.animation_step = 0


def check_mouth_visibility(volume):
    if volume >= G.threshold or G.animation_lock:
        # 如果音量超過閾值或者動畫鎖定中，顯示嘴巴
        setVisibility(G.scene_Name, G.mouth_image_source_name, True)
        # 只有音量超過閾值且沒有動畫鎖時，才觸發跳躍動畫
        if volume >= G.threshold and not G.animation_lock:
            animate_jump()
    else:
        # 只有當音量低於閾值且動畫鎖已釋放時，才隱藏嘴巴
        setVisibility(G.scene_Name, G.mouth_image_source_name, False)


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

        # 處理動畫計時器
        if G.animation_lock:
            G.animation_timer -= G.tick
            if G.animation_timer <= 0:
                # 執行動畫的下一步
                update_jump_animation()
                # 重置計時器，如果是等待階段則不延遲，立即檢查下一幀
                if G.animation_phase == "wait":
                    G.animation_timer = 0  # 等待階段持續檢查音量
                else:
                    G.animation_timer = G.animation_step_interval
    else:
        G.duration += G.tick_mili


def script_load(settings):
    S.timer_add(event_loop, G.tick)


def script_unload():
    g_obs_volmeter_remove_callback(G.volmeter, volmeter_callback, None)
    g_obs_volmeter_destroy(G.volmeter)
    G.lock = False
    G.animation_lock = False
    G.duration = 0
    G.start_delay = 3
    G.noise = -60.0
    print("Removed volmeter & volmeter_callback")
