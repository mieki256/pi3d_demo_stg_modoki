#!/usr/bin/python
# -*- mode: python; Encoding: utf-8; coding: utf-8 -*-
# Last updated: <2017/10/16 06:09:50 +0900>
u"""
pi3d draw model(obj + mtl) sample.

3Dモデル(obj + mtl)を描画してみるテスト。
スプライトも表示してシューティングゲームっぽい画面にしてみる。

WASD / Cursor key : move
ESC : exit

- Windows10 x64 + Python 2.7.12 32bit + pi3d 2.21
- Raspberry Pi Zero W + raspbian stretch + pi3d 2.21

Author : mieki256
License : CC0
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import math
import pi3d
import pygame


MY_FPS = 30
BG_MODLE_PATH = "models/tiny_city02.obj"
PLAYER_IMG_PATH = "imgs/airplane_01_64x64.png"
BULLET_IMG_PATH = "imgs/fire_01_64x64.png"


class KeyboardStatus(object):
    u"""Keyboard status."""

    # referenc :
    # pi3d/event/Keys.py
    # https://www.pygame.org/docs/ref/key.html
    keys_list = {
        "KEY_ESC": pygame.K_ESCAPE,
        "KEY_A": pygame.K_a, "KEY_B": pygame.K_b, "KEY_C": pygame.K_c,
        "KEY_D": pygame.K_d, "KEY_E": pygame.K_e, "KEY_F": pygame.K_f,
        "KEY_G": pygame.K_g, "KEY_H": pygame.K_h, "KEY_I": pygame.K_i,
        "KEY_J": pygame.K_j, "KEY_K": pygame.K_k, "KEY_L": pygame.K_l,
        "KEY_M": pygame.K_m, "KEY_N": pygame.K_n, "KEY_O": pygame.K_o,
        "KEY_P": pygame.K_p, "KEY_Q": pygame.K_q, "KEY_R": pygame.K_r,
        "KEY_S": pygame.K_s, "KEY_T": pygame.K_t, "KEY_U": pygame.K_u,
        "KEY_V": pygame.K_v, "KEY_W": pygame.K_w, "KEY_X": pygame.K_x,
        "KEY_Y": pygame.K_y, "KEY_Z": pygame.K_z,
        "KEY_0": pygame.K_0, "KEY_1": pygame.K_1, "KEY_2": pygame.K_2,
        "KEY_3": pygame.K_3, "KEY_4": pygame.K_4, "KEY_5": pygame.K_5,
        "KEY_6": pygame.K_6, "KEY_7": pygame.K_7, "KEY_8": pygame.K_8,
        "KEY_9": pygame.K_9,
        "KEY_UP": pygame.K_UP, "KEY_DOWN": pygame.K_DOWN,
        "KEY_LEFT": pygame.K_LEFT, "KEY_RIGHT": pygame.K_RIGHT,
        "KEY_SPACE": pygame.K_SPACE
    }

    class PygameKeyStatus(object):
        u"""Keyboard status with pygame."""

        def __init__(self):
            """Init."""
            pygame.init()

        def update(self):
            """Update."""
            pygame.event.pump()
            self.keys = pygame.key.get_pressed()
            pygame.event.clear()

        def key_pressed(self, key_str):
            """Get key press state.

            @param key_str key kind string
            @return True or False

            """
            return self.keys[KeyboardStatus.keys_list[key_str]]

        def close(self):
            """Close."""
            pygame.quit()

    class Pi3dInputKeyState(object):
        """Keyboard status width pi3d.InputEvents."""

        def __init__(self):
            """Init."""
            self.inputs = pi3d.InputEvents()

        def update(self):
            """Update."""
            self.inputs.do_input_events()

        def key_pressed(self, key_str):
            """Get key press state.

            @param key_str key kind string
            @return True or False

            """
            return (self.inputs.key_state(key_str) != 0)

        def close(self):
            """Close."""
            pass

    def __init__(self):
        """Init."""
        self.keyboard = pi3d.Keyboard()
        if pi3d.USE_PYGAME:
            self.state = KeyboardStatus.PygameKeyStatus()
        else:
            self.state = KeyboardStatus.Pi3dInputKeyState()

    def update(self):
        """Update."""
        self.pikey = self.keyboard.read()
        self.state.update()

    def key_pressed(self, key_str):
        """Key press check.

        @param key_str key kind
        @return True or False

        """
        return self.state.key_pressed(key_str)

    def esckey_pressed(self):
        """ESC key press check.

        @return True or False

        """
        return (self.pikey == 27 or self.key_pressed("KEY_ESC"))

    def close(self):
        u"""Close."""
        self.keyboard.close()
        self.state.close()


display = pi3d.Display.create(frames_per_second=MY_FPS)
# display = pi3d.Display.create(w=1280, h=720, frames_per_second=MY_FPS)
ffps = float(MY_FPS)

# ライトを設定. position, color, ambientを指定
light = pi3d.Light(lightpos=(10.0, -10.0, -5.0),
                   lightcol=(1.0, 1.0, 1.0),
                   lightamb=(0.3, 0.3, 0.3),
                   is_point=False)

# シェーダを生成
shader = pi3d.Shader("uv_light")
shader_flat = pi3d.Shader("uv_flat")

# カメラ生成
camera_bg = pi3d.Camera(at=(0, 0, 0), eye=(0.0, 16.0, -6.0))
camera_flat = pi3d.Camera(is_3d=True)

# 背景モデルデータを読み込み
my_model0 = pi3d.Model(camera=camera_bg, light=light,
                       file_string=BG_MODLE_PATH)
my_model1 = pi3d.Model(camera=camera_bg, light=light,
                       file_string=BG_MODLE_PATH)

# 背景モデルのシェーダを設定
my_model0.set_shader(shader)
my_model1.set_shader(shader)

# 背景モデル位置を初期化
bg_x, bg_y, bg_z = 0.0, 0.0, 20.0
my_model0.position(bg_x, bg_y, bg_z)
my_model1.position(bg_x, bg_y, bg_z - 20.0)

# 背景モデルを少し回転
# my_model0.rotateIncZ(10)
# my_model1.rotateIncZ(10)

# 手前に重ねるスプライト(自機)を生成
x, y, z = 0.0, 0.0, 1.0
tex = pi3d.Texture(PLAYER_IMG_PATH)
spr = pi3d.ImageSprite(tex, shader_flat, w=0.1, h=0.1, camera=camera_flat)
display.add_sprites(spr)
spr.position(x, y, z)

# 手前に重ねるスプライト(弾)を生成
bullet_tex = pi3d.Texture(BULLET_IMG_PATH)
bullet_sprs = []
for i in range(8):
    bspr = pi3d.ImageSprite(bullet_tex, shader_flat,
                            w=0.1, h=0.1, camera=camera_flat)
    bspr.position(x, y, z)
    bspr.visible = False
    bullet_sprs.append(bspr)

inputs = KeyboardStatus()

# スプライトが画面外に移動しないように境界値を算出
y_limit = 0.45
x_limit = y_limit * float(display.width) / float(display.height)
y_limit -= 0.05
x_limit -= 0.05

frame_counter = 0

# メインループ
while display.loop_running():

    inputs.update()

    camera_bg.reset()
    camera_flat.reset()

    # BGモデルを描画
    my_model0.draw()
    my_model1.draw()

    # BGモデルを移動
    my_model0.position(bg_x, bg_y, bg_z)
    my_model1.position(bg_x, bg_y, bg_z - 20.0)
    bg_z -= (15.0 / ffps)
    if bg_z <= 0.0:
        bg_z += 20.0

    # 手前のスプライトの座標をキー入力で変更
    spd = (0.6 / ffps)
    ang = -1
    if inputs.key_pressed("KEY_A") or inputs.key_pressed("KEY_LEFT"):
        ang = 180
    elif inputs.key_pressed("KEY_D") or inputs.key_pressed("KEY_RIGHT"):
        ang = 0
    if inputs.key_pressed("KEY_W") or inputs.key_pressed("KEY_UP"):
        if ang == 0:
            ang = 45
        elif ang == 180:
            ang = 180 - 45
        else:
            ang = 90
    elif inputs.key_pressed("KEY_S") or inputs.key_pressed("KEY_DOWN"):
        if ang == 0:
            ang = 360 - 45
        elif ang == 180:
            ang = 180 + 45
        else:
            ang = 270
    if ang >= 0:
        rad = math.radians(ang)
        x += spd * math.cos(rad)
        y += spd * math.sin(rad)

    # 画面外に移動しないように座標を補正
    if y >= y_limit:
        y = y_limit
    elif y <= -y_limit:
        y = -y_limit
    if x >= x_limit:
        x = x_limit
    elif x <= -x_limit:
        x = -x_limit

    # スプライトの座標を設定
    spr.position(x, y, z)

    # 弾を発生
    if frame_counter % int(ffps / 7) == 0:
        for bspr in bullet_sprs:
            if not bspr.visible:
                bspr.visible = True
                bspr.position(x, y + 0.07, z)
                break

    # 弾を移動・描画
    bspd = (1.5 / ffps)
    for bspr in bullet_sprs:
        if bspr.visible:
            bspr.translateY(bspd)
            if bspr.y() >= y_limit + 0.1:
                bspr.visible = False
            else:
                bspr.draw()

    if inputs.esckey_pressed():
        inputs.close()
        display.destroy()
        break

    frame_counter += 1
