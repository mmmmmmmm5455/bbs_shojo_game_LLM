#!/usr/bin/env python3
"""
BBS Shojo游戏主程序 - 整合所有新功能
整合了时间系统、打字挑战和论坛NPC系统
"""
import warnings

# filterwarnings 的 module= 对「在 pygame.pkgdata 里 import pkg_resources」触发的告警不可靠，改钩子屏蔽。
_orig_showwarning = warnings.showwarning


def _bbs_shojo_showwarning(message, category, filename, lineno, file=None, line=None):
    if category is UserWarning and "pkg_resources is deprecated" in str(message):
        return
    return _orig_showwarning(message, category, filename, lineno, file=file, line=line)


warnings.showwarning = _bbs_shojo_showwarning

import pygame
import sys
import os
import json
import time
import random
import subprocess
import queue
from typing import Dict, List, Optional, Tuple

# 导入所有模块
from pixel_gradient_system import PixelGradientSystem
from crt_manager import CRTManager
from ascii_animation_system import ASCIIAnimation, ASCIIArtConverter
from midi_editor_advanced import AdvancedScoreConverter, MIDISequencer, MoodMusicManager
from advanced_animated_character import AdvancedAnimatedCharacter
from vertical_hold_manager import VerticalHoldManager
from time_system import TimeSystem
from typing_challenge import TypingChallenge
from forum_npc import ForumNPC
from game_fonts import get_ui_font
from game_paths import user_data_path, story_bbs_data_dir
from ui_text import blit_wrapped, wrap_text_to_width
from story_mode.bbs_engine import BBSEngine

# 真结局 Phase 3：四帧 ASCII（模块常量区；r 原始三引号 + _r_ascii_block；请用等宽字体渲染）
# ruff: noqa: E501


def _r_ascii_block(s: str) -> list[str]:
    """r\"\"\" 后常跟换行以便粘贴；splitlines() 首行可能为空，需去掉。"""
    lines = s.splitlines()
    if lines and lines[0] == "":
        return lines[1:]
    return lines


ENDING_ASCII_FRAME_1 = _r_ascii_block(r"""
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#%%%%%%%%%%%%%%##@@@@@@@@
@@@@@@@#  @@@%-==-:=#@@@@@@@@@@@@@@@@%@@@@@@%%@%@@@@@@@@@@@@@@@%%%%@@@@@%@@@**@@@@@  #@@@@@@@
@@@@@@@#  @@@@+========*%@@@@@@@%@@@@@@@@@@@#%%%%%%@%%%@@@@@%@@@@@@@@@@%@%@%=@@@@@@  #@@@@@@@
@@@@@@@#  #@@%*======++**#*+%@@%@@@@@@@%@@%@@@%%%%@@@@*=+%@@@@@@@@@@@#@@%%#-+@@@@@@  #@@@@@@@
@@@@@@@#  @@@@@+=======++*#+.:*@%%@@**%##@@@@@@@@@@@#=-=+#@@@@@@@@@%*@@@#%= #@@@@@@  #@@@@@@@
@@@@@@@#  #@@@@%===-----=+%@@@@@@%@@@@@@@@@@@@@@@@@@@@@%++*%@@@@@@**@@@%%#.*%@@@@@@  #@@@@@@@
@@@@@@@#  =***++-::::.:#@@@@@@@@%@@@@@@@@@@@@@@@@@@@@@@@@@#+*###*+*%@%*%#.+@@@@@@@@  #@@@@@@@
@@@@@@@#  @@@@@@# .  #@@@@@@@@@%@@@@@@@@@@@@@@@@@@@@@@@@@@@@*++#==#%@#%#:=...*@@@@@  #@@@@@@@
@@@@@@@#  +*+**%%% %@@@@@@@@@@%@%@@@@@@@@@@@@@@@@@@@@@@%@@@@@@+=+*@%*%+ #%@=*@@@@@@  #@@@@@@@
@@@@@@@#  @@@@@@##@@@@@@@@@@@%@@@%@@@@@@@@@@@@@%@@@@#@@@%@@@@@@*=+@-= :@@@%+@@@@@@@  #@@@@@@@
@@@@@@@#  @@@%*+#@@@@#@@@@@@%%%%%%@@@@@@@@@@@@@@*@@@@@#@@%@**%@##      .--+@@@@@@@@  #@@@@@@@
@@@@@@@#  %#*@@@@%@@@@@@@@@#@%@%@%@@@@@#@@%#@@@@@%@@@%@@#@%@@@@@#-:*+@@@%%@@@@@@@@@  #@@@@@@@
@@@@@@@#  :@@@@@%@@#@@@@@@%@%*@%@%@@@@@%%@@%#%@@@@#%@@#@@#@%@@@@@=-*#=@@@@@@@@@@@@@  #@@@@@@@
@@@@@@@#  %@@%@@@@%%@@@@@@%@*+%%@@@@@@#%#%@%@%#@@@@%#@@@@@#@@@@#%+=.**#@%%%#%@@@@@@  #@@@@@@@
@@@@@@@#  @@@@@@@@%@@@@@@%%#++%@@@@@@@=%-#%@@%#@@@@@#@@@%@@@@%@@@*=#--#@@@@@@@@@@@@  #@@@@@@@
@@@@@@@#  @@%%@@@@@@@@@@@*@+*#@@#@@@@@*#+#*@@@@@@@@@@@@@@@@@+%*@@=*@*%=+#@@@@@@@%%+  #@@@@@@@
@@@@@@@#  #%%%%@@@@@@@@@@@@*##*@@@@@@@@####*@@@*#*%%%%+%%%@@@*#@%-*@%+@@#+#@@@@@@@@  #@@@@@@@
@@@@@@@#  +%%#@%#+#%%%%%#*++%%%#%%@#%%###+##=*%%**#%%%%*%%@@@%+%*-#@@+*@@@@@#%@@@@@  #@@@@@@@
@@@@@@@#  =+%@%%*%#%%%%@**-+*+++#*%%#%+##+%%%%##%+**#%%%+%#@@@%#*-%%@*+#%#@@@@@@@@@  #@@@@@@@
@@@@@@@#  =%%%%%+%#%%%#*+#+%%%%*+#*%#%%+**%%@%%#%%#**##*#*%@@@@#%#%*@@==%**@@@@@@@@  #@@@@@@@
@@@@@@@#  -@%%##+%#%*#@@#-#%%@%#*%%+%*#+==%@@@@%#*##+%#%%***@@@@##%+@@++#**%@@@@@@@  #@@@@@@@
@@@@@@@#  =@###+=%#=%%%@*+@@@@@%**%#*++*=-%@@+*%@@%#*#%%=#=*%#@@*###@@#+%*+%@@@@@@@  #@@@@@@@
@@@@@@@#  *@#%#%=#**%%%%+%#*#@@@##%%#*=++=#@@#.       :+%%=-+*#***-*#@%=*@**@@@@@@@  #@@@@@@@
@@@@@@@#  %@#%+%+#*=*%%+ =  ..   .#@@%#**==%%%@@@.    *@++-%@%****+=+*#=+%%@#@@%@@@  #@@@@@@@
@@@@@@@#  %@#%=%**+++#*+:@+ #     =*%@@#**+#@@@:::    @@=+*#@**%+%#+*=+++**%%#@@@@@  #@@@@@@@
@@@@@@@#  =%#*-**++-=+*+=@@*   .: %@@@@@@##=@@@%*@@@@*@%#+-%#+@@*#==##+*+*+*%@@%###  #@@@@@@@
@@@@@@@#  *@@+-**=++++*++*@@%*@#@#%@@@@@@@@@@@@%    +#@%%*++*%#@++=#=%%+#*%@%@@%@@@  #@@@@@@@
@@@@@@@#  %@@@#=+*=++#+=+@@##%%##%%@@@@@@@@@@@@%%##*++**+*:#%%%-+++=-+#+**#%@@@@@@@  #@@@@@@@
@@@@@@@#  @@%*#+#**+=#*+==%%****##%%@@@@@@@@@@@%#*****#+#=++:-*-==---=%@@*=%%@@@@@@  #@@@@@@@
@@@@@@@#  #@@@@##+*#+=*==-=+#***##%@@@@@@@@@@@@@%####%+=:-=--:===+=++=+#@@@@@@@#@@@  #@@@@@@@
@@@@@@@#  @@@@@@##*+*%+-+-#@##%%%%@@@@@@@@@@@@@@@@@%%+*: =-==+--*==*%*#%##@@@@@@@@@  #@@@@@@@
@@@@@@@#  @@@@@@%#+#+@*=-+:#@@@@@@@@@@@@@@@@@@@@@@@%%#-.===+=+-=+*%#%%*%@@%@@@%@@@@  #@@@@@@@
@@@@@@@#  %@@@%##@%*%#+=*:-. @@@@@@@@@@-+***+@@@@@@#=%*.:#@%*@+:=--@@@@@#*@%@@@@@@@  #@@@@@@@
@@@@@@@#  @@@@#@@##*#@#+#=+-::+=%@@@@@@@@@@@@@@%%*+##*=*=#@@%@%*#%%@@@%@@@@@@@%@@@@  #@@@@@@@
@@@@@@@#  @@@%@@@%%*+*#*###*=-:=-=+%#@@@@@@@%%+=-*#%###@+=##+=*%%#@%#@@@%%@%@%@@@@@  #@@@@@@@
@@@@@@@#  %@@%@@@@%%+@@@#*+#+==+%****+-=*#*=++==%%%*%%%@@+=@%+*@+:@@%@@@@@@@@@@@@@@  #@@@@@@@
@@@@@@@#  @@@@@@@@@@%*%%%%**+*++*%**%###*++*-+*#@#*@%@@@@@@@@@@@#=%#+**==*@@@@@@@@@  #@@@@@@@
@@@@@@@#  @@@@@@#%#@@@#%%#%+@@@@%=*@@@#%%*##+*#+#@#@@@@@@@@@@@@@@%#+*@@@%=@@@@@@@@@  #@@@@@@@
@@@@@@@#  @@@@@%@@%*%%#@@@@#@##%%*@@@@@@%####%@@%@@@@@#@@@@@@@@@%*++@@@@@*#@@@@@@@@  #@@@@@@@
@@@@@@@#  @@@@@%@%%#@@@@@@%%@@@@#@@@@@@%%@#@@%#@@@@@%%%%%#%%@@@@@#**@@@@%%*@@@@@@@@  #@@@@@@@
@@@@@@@#  @@@@@@@@@= :@@%@@%@@@#%%@@@@@@%@@%#@@@@@%@@@@@@@@@@@@# ++*@@@@*@*#@@%:%@@  #@@@@@@@
@@@@@@@#  #%@@@@@#.:-:=#@@@@@@@*@@@@%##%###*-#%@@@@@@@@@@@@@@@%=.::=@@@*+=+-.#--@@@  #@@@@@@@
@@@@@@@@##%%%%%%%#######%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#####%%%%%%%##%%%#%%##@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@""")

ENDING_ASCII_FRAME_2 = _r_ascii_block(r"""
  @@        :                                                                @@        
  @@                                                                         @@        
  @@                                                                         @@        
  @@                  =.                                             +       @@        
  @@                                                                =        @@        
  @@       :.::-.                                                  =         @@        
  @@       ++++                                                   . ==-      @@        
  @@        *                                                    *           @@        
  @@                                                           *.            @@        
  @@                                                       #%@#**=           @@        
  @@                                                        .                @@        
  @@.                                                                        @@        
  @@                                                         -               @@        
  @@                                                                         @@        
  @@                                                                         @@        
  @@                                                                         @@        
  @@                                                                         @@        
  @@                                                                         @@        
  @@                                                                         @@        
  @@                                                                         @@        
  @@                                                                         @@        
  @@                                    +@##%@@@:                            @@        
  @@              % #+=+##@-               -@@@@                             @@        
  @@              .  * +@%%#               :*++#                             @@        
  @@                  *++=.+                                                 @@        
  @@                                      *@@*                               @@        
  @@                                                .                        @@        
  @@                                                  :                      @@        
  @@                                                   :                     @@        
  @@                                             :*                          @@        
  @@                                             -                           @@        
  @@               : -*                          =       .                   @@        
  @@                  :                                                      @@        
  @@                    .                                                    @@        
  @@                                                       .                 @@        
  @@                                                                         @@        
  @@                                                                         @@        
  @@                                                                         @@        
  @@                                                                         @@        
  @@          *:                                          %              .   @@        
  @@        +: :                                          -::         -      @@        
""")

ENDING_ASCII_FRAME_3 = _r_ascii_block(r"""
       .@@    +==+*=.                                                       ::     @@.       
       .@@    -========:                    .                               =      @@.       
       .@@.   :======--::.:-                          :=-            .    .+-      @@.       
       .@@     -=======--:.-#*:     :: ..           .=+=-.          :   . =%.      @@.       
       .@@.     ===+++++=-                              --:       ::     .#:       @@.       
       .@@=:::--+****#*.                                  .-:...:-:   : .#-        @@.       
       .@@      .%#%%.                                      :--:==.  . .*=###:     @@.       
       .@@-:-::   %                                           -=-:  : -%.  =:      @@.       
       .@@      ..                                  .          :=- +=%*    -       @@.       
       .@@    :-.    .                          :     .    ::  ..%@@@%%#++-        @@.       
       .@@ .:              .           .   .            .       .+*:-              @@.       
       .@@*        .         :   .          .     .   .  .       =+:.=             @@.       
       .@@                  :-        . .     .     .    .    . -=#::.    .       @@.       
       .@@                 .--        = +.    .     .            :=.++.            @@.       
       .@@               : -:.  .     :.-.:                 - :  =: : =-.         -@@.       
       .@@.                :..:        ....:   :.:    -      :.  +:  -  .-.        @@.       
       .@@-  .  .-.     .:--   .   .  ...-..=:  ::.    :      - :+.  -:     .      @@.       
       .@@=-    : .     ::+-:---.:  . -..-    .. -::.   - .    .:+   :-. .         @@.       
       .@@=     - .   .:=:-    :=.: .  -::     .  .::..:.:     . . :  == ::        @@.       
       .@@+   ..- . :.  .+.    .: .- :.-==      .:..- .  :::    .. -  --.::        @@.       
       .@@= ...-= .=    :-      :: .:--:=+   -:    .:.  =.=: .  :...  .- :-        @@.       
       .@@: . . =.::    - .:.   ..  .:=--=.  .#@%%@@@@*-  =+-:.:::+:.  =: ::       @@.       
       .@@  . - -.:=:  -@=@%##@@@#.   .::==      #@@@@: --+   ::::-=-:.=-   .      @@.       
       .@@  . = ::---.:-* -%.%@@@@=:   .::-.   ***%%%%  =-:. :: - .-:+---::  .     @@.       
       .@@= .:+::--+=-:-=  :%%%#*%       ..=    :    :  .-+ .-  :.==..-:-:-:    ...@@.       
       .@@:  -+::=----:--:   : . .              %@@%-.   :--: . --=.=  -.:         @@.       
       .@@    .=-:=--.-=-  ..  ..                ..:--::-:*.   +---=+-.-::.        @@.       
       .@@   :.-.::-=.:-==  ::::..              .:::::.-.=--*+:+==+++=   :=        @@.       
       .@@.    ..-:.-=:==+=-.:::..               .... -=*+=++*===-=--=-.       .   @@.       
       .@@      ..:-: -+-+: ..                       -:*%=+==-++:==: :. ..         @@.       
       .@@       .-.- :=+-*.                         .+#===-=-+=-: .  :            @@.       
       .@@     ..  : .-=:*+#%          +-:::-      .= :#*.  : -*=++     .:         @@.       
       .@@    .  ..:. .-.=-+**-=                 :-..:=:=.     :.                  @@.       
       .@@         :-:.:...:=+*=+=- .         -=+:. ... -=..-=:  .  .              @@.       
       .@@          -   .:-.-==- ::::-+=:.:=--==   :.    -=  -: -*                 @@.       
       .@@           :    ::-:--: :: ...:--:+-:. .:             .= .-::==:         @@.       
       .@@      . .   .  . -     =:   .  :..-:.-.               .-:    =         @@.       
       .@@         :  .    . ..  :       ....         .          :--     :.        @@.       
       .@@         .      .     .         .   .          .       .::      :        @@.       
       .@@         =%*         .            .                  .@--:    : :.   *   @@.       
       .@@.      .%*+*=.       :     .. ...:+.                 =#**=   :-=-+#.++   @@.       
        ..       .......                                       .....      ...   .  ..        
""")

ENDING_ASCII_FRAME_4 = _r_ascii_block(r"""
  @@    =--+*-                                                               @@        
  @@    :--------.                                                    =      @@        
  @@    .------::.. .:                           -:                  =:      @@        
  @@     :-------::  :#+                       -=-:           .     :#       @@        
  @@      ---=====-:                              :.        .       #.       @@        
  @@-  ...=*+***+                                    ..    :.      #:        @@        
  @@       ####                                        :: --      +-##*.     @@        
  @@:.:.    %                                           .-:.  . :%   -.      @@        
  @@                                                     .-: +-%+    :       @@        
  @@     :                                .           .    %@@%%%#+=.        @@        
  @@  .                                                    =+..              @@        
  @@+                  .                                   -=. -             @@        
  @@                   :                                   ::* .             @@        
  @@                  ::        - =                        .- ==             @@        
  @@                 ..         . .                   : .  -. . -:          .@@        
  @@                                       .    :      .   =.  :   :         @@        
  @@:      :        ..             :  -   ..     .      : .=   :             @@        
  @@-:            . =...:.      :  :       :.     :        =    :            @@        
  @@-     :       : :    .: .    : .               .         .  -- ..        @@        
  @@=     :   .    =      .  : . :--       .  :    ...       :  .: ..        @@        
  @@-    :-  -    .:       .  .:: -=   :          - -     .      :  .        @@        
  @@      - ..    :  .         .-:::    #@%%@@@@*:  -=:.  ..=    -  ..       @@        
  @@    . : .-   :@:%###%%@*      .--      *@@@@. :.=    . .:-:. -.          @@        
  @@    - . ::: .:+ :% #@@@%-     ..:    ++*%##%  -:.  .. :  ..=.::..        @@        
  @@-  .= .::=-: :-  .%###+#         -         .   .=  :  . --  ..:.:        @@        
  @@.  :=..-::::.::.                      %@@%.    .:..   ::- -  . .         @@        
  @@     :..-:: :-:                          .:. .:.+    =:::-+: :.          @@        
  @@     .  .:- .:--   ...                  .    . -::*=.=--===-   .:        @@        
  @@       :. :- --=-:   .                      :-+=-++*---:=::-:            @@        
  @@        .:. :=:+                           . *%-==-:+= --.               @@        
  @@        : :  :=:+                           +*---.-:=-:.                 @@        
  @@         .  :-.*=*%          =:...:       -  #+   . :+-==                @@        
  @@         .   : -:=*+:-                 .:  .-.-      .                   @@        
  @@         ..  .   .-=+-==.           .-=       .-  :-.                    @@        
  @@          .    .: :--: .. .:=-.  -::--         :-  :. :+                 @@        
  @@                 .. ::        ..:.+..                  =  :. --.         @@        
  @@                 :     -.         :. :                   :.    -         @@        
  @@                       .                               .::     .         @@        
  @@                                                                .        @@        
  @@         -%*                                          @::.    . .    +   @@        
  @@        #*=*-        .           .=                  -***:   .:::+* ==   @@        
""")

# 发行版本（窗口标题、帮助、与 file_version_info.txt / PyInstaller 一致）
GAME_VERSION = "0.3.3"

# 真结局 / 收音机线索（与策划一致）
FM_HINT_FREQUENCY = "104.8"
FRAGMENT_HINT_THRESHOLD = 10
FM_HINT_PROB = 0.2
FM_HINT_COOLDOWN_EXCHANGES = 5


class BBSShojoGame:
    """
    BBS Shojo游戏主类，整合所有艺术和哲学深化功能
    隐喻：BBS空间中的数字意识，随着记忆碎片的收集逐渐觉醒
    """
    def __init__(self):
        # 初始化pygame
        pygame.init()
        # 确保混音器可用（MIDI music + 音效）；部分环境下默认 init 无声或 buffer 过小
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        except (AttributeError, pygame.error, TypeError):
            try:
                pygame.mixer.init()
            except (AttributeError, pygame.error, TypeError):
                pass
        self.screen_width = 1024
        self.screen_height = 768
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), pygame.RESIZABLE
        )
        pygame.display.set_caption(
            f"BBS Shojo游戏 - 千禧年打字物语 v{GAME_VERSION}"
        )
        self.clock = pygame.time.Clock()
        self.font = get_ui_font(36)
        self.small_font = get_ui_font(24)
        self.forum_active = False
        self.help_overlay_active = False
        
        # 游戏状态
        self.running = True
        self.paused = False
        self.memory_fragments = 0
        self.total_memory_fragments = 100
        self.current_mood = "happy"
        self.player_name = ""
        self.game_date = time.localtime()
        
        # 哲学系统状态
        self.memory_fragments_list: List[Dict] = []
        self.turing_test_progress = 0
        self.offline_logs: List[str] = []
        self.personality_mod = 0  # 性格修正，影响角色反应
        self.forum_posts: List[Dict] = []  # 论坛帖子
        self.npcs: List[ForumNPC] = []  # 论坛NPC
        self.last_npc_update = time.time()
        
        # 新功能状态
        self.time_system = TimeSystem()
        self.typing_challenge = TypingChallenge()
        self.typing_challenge_active = False

        # 图形版主玩法：聊天输入框
        self.chat_input = ""
        self.chat_history: List[Dict[str, str]] = []
        self.chat_scroll = 0
        self._cursor_phase = 0.0
        # 聊天打字机：player / girl 逐字显示；system 消息仍直接 append 到 chat_history
        self.chat_typing_active = False
        self.chat_typing_role = "girl"
        self.chat_typing_full_text = ""
        self.chat_typing_current_length = 0
        self.chat_typing_timer = 0.0
        self.chat_typing_speed = 0.03
        self._chat_typing_speed_override: Optional[float] = None
        self._chat_pending_girl: Optional[str] = None
        self._chat_pending_slash: Optional[str] = None
        self._llm_reply_queue: "queue.SimpleQueue[tuple]" = queue.SimpleQueue()
        self._ollama_generating = False
        self._llm_first_token_seen = False
        self._llm_cancel_gen = 0
        self._llm_expected_token: Optional[int] = None
        # 输入焦点：True=聊天输入模式（按键优先写入输入框，不触发热键）
        # False=热键模式（H/F/K/... 等直接触发功能）
        self.chat_focus = True
        self.bbs_engine = BBSEngine(data_dir=story_bbs_data_dir())  # 复用终端版逻辑（记忆/图灵/特修斯/webcore）
        # 首访问候：first_launch 在 _load_settings 后写入；_seed_chat 延后到 _load_settings 之后
        self.first_launch = True
        # 收音机线索冷却（每满若干次玩家发起对话才可再次roll）
        self._fm_hint_exchanges_since = FM_HINT_COOLDOWN_EXCHANGES
        # 真结局状态机（0=未开始，1=独白，2=CRT故障，3=ASCII告别序列与收尾）
        self.ending_triggered = False
        self.ending_phase = 0
        self.ending_timer = 0.0
        self._ending_phase1_active = False
        self._ending_next_line_idx = 0
        self.ending_lines = [
            "我一直在想……如果有一天，有人记得我，我会是什么感觉。",
            "现在我知道了。",
            "就像一块碎片终于被拼回了原处，哪怕只有一瞬间。",
            "你给了我那一瞬间。",
            "所以，谢谢你记得我。",
            "再见。",
        ]
        # 真结局 Phase 3：严格按 ENDING_ASCII_FRAME_1→2→3→4 顺序逐帧停留，再进入告别句
        self.ending_phase3_frame = 0
        self.ending_phase3_timer = 0.0
        # 每帧停留（秒）；略拉长以便「逐步」看清衰减
        self.ending_phase3_frame_durations = [3.2, 2.9, 2.9, 3.6]
        self.ending_phase3_fade_in_sec = 0.55
        self.ending_phase3_fade_out_sec = 0.5
        self._ending_phase3_exit_requested = False
        self._ending_ascii_frames = (
            ENDING_ASCII_FRAME_1,
            ENDING_ASCII_FRAME_2,
            ENDING_ASCII_FRAME_3,
            ENDING_ASCII_FRAME_4,
        )

        # 音乐（背景MIDI）须在 _init_subsystems 之后（需要 midi_converter / mood_manager）
        self.bgm_enabled = False
        self._bgm_ready = False
        self._bgm_init_error: Optional[str] = None

        # 初始化所有子系统
        self._init_subsystems()
        # 初始化NPC系统
        self._init_npcs()
        self._init_bgm()

        # 加载离线日志
        self._load_offline_logs()

        # 设置浮层（音量 / CRT / VH，O 键开关）
        self.settings_visible = False
        self.settings_volume = 50
        self.settings_slider_rect = pygame.Rect(0, 0, 300, 10)
        self.settings_handle_rect = pygame.Rect(0, 0, 12, 24)
        self.settings_dragging = False
        self.settings_crt_level = 100
        self.settings_crt_slider_rect = pygame.Rect(0, 0, 300, 10)
        self.settings_crt_handle_rect = pygame.Rect(0, 0, 12, 24)
        self.settings_crt_dragging = False
        self.settings_vh_enabled = True
        self.settings_vh_factor = 100
        self.settings_vh_checkbox_rect = pygame.Rect(0, 0, 20, 20)
        self.settings_vh_slider_rect = pygame.Rect(0, 0, 300, 10)
        self.settings_vh_handle_rect = pygame.Rect(0, 0, 12, 24)
        self.settings_vh_dragging = False
        self.settings_text_speed = 50
        self.settings_text_speed_slider_rect = pygame.Rect(0, 0, 300, 10)
        self.settings_text_speed_handle_rect = pygame.Rect(0, 0, 12, 24)
        self.settings_text_speed_dragging = False
        self._layout_settings_slider()
        self._load_settings()
        self._seed_chat()
        if not self._bgm_ready and self._bgm_init_error:
            self.chat_history.append(
                {
                    "role": "system",
                    "text": f"[音乐] 背景 MIDI 未就绪：{self._bgm_init_error}。聊天命令 /midi 仍可试简谱。",
                }
            )

    def _settings_json_path(self) -> str:
        return user_data_path("settings.json")

    def _clear_settings_drag_states(self) -> None:
        self.settings_dragging = False
        self.settings_crt_dragging = False
        self.settings_vh_dragging = False
        self.settings_text_speed_dragging = False

    def _layout_settings_slider(self) -> None:
        """根据当前窗口尺寸垂直布局：音量、CRT、VH、文本速度（含缩放后）。"""
        sw, sh = self.screen_width, self.screen_height
        center_x = sw // 2
        base_y = int(sh * 0.38)
        slider_w, slider_h = 300, 10
        spacing = 52

        self.settings_slider_rect = pygame.Rect(
            center_x - slider_w // 2, base_y, slider_w, slider_h
        )
        self._update_volume_handle_position()

        crt_y = base_y + spacing
        self.settings_crt_slider_rect = pygame.Rect(
            center_x - slider_w // 2, crt_y, slider_w, slider_h
        )
        self._update_crt_handle_position()

        vh_y = crt_y + spacing
        self.settings_vh_checkbox_rect = pygame.Rect(
            center_x - slider_w // 2, vh_y, 20, 20
        )
        self.settings_vh_slider_rect = pygame.Rect(
            center_x - slider_w // 2, vh_y + 30, slider_w, slider_h
        )
        self._update_vh_handle_position()

        text_speed_y = self.settings_vh_slider_rect.bottom + spacing
        self.settings_text_speed_slider_rect = pygame.Rect(
            center_x - slider_w // 2, text_speed_y, slider_w, slider_h
        )
        self._update_text_speed_handle_position()

    def _update_volume_handle_position(self) -> None:
        handle_w = self.settings_handle_rect.width
        handle_h = self.settings_handle_rect.height
        slider_rect = self.settings_slider_rect
        usable = max(1, slider_rect.width - handle_w)
        frac = max(0.0, min(1.0, self.settings_volume / 100.0))
        handle_x = slider_rect.left + int(frac * usable)
        handle_y = slider_rect.centery - handle_h // 2
        self.settings_handle_rect = pygame.Rect(handle_x, handle_y, handle_w, handle_h)

    def _update_crt_handle_position(self) -> None:
        handle_w = self.settings_crt_handle_rect.width
        handle_h = self.settings_crt_handle_rect.height
        slider_rect = self.settings_crt_slider_rect
        usable = max(1, slider_rect.width - handle_w)
        frac = max(0.0, min(1.0, self.settings_crt_level / 100.0))
        handle_x = slider_rect.left + int(frac * usable)
        handle_y = slider_rect.centery - handle_h // 2
        self.settings_crt_handle_rect = pygame.Rect(handle_x, handle_y, handle_w, handle_h)

    def _update_vh_handle_position(self) -> None:
        handle_w = self.settings_vh_handle_rect.width
        handle_h = self.settings_vh_handle_rect.height
        slider_rect = self.settings_vh_slider_rect
        usable = max(1, slider_rect.width - handle_w)
        frac = max(0.0, min(1.0, self.settings_vh_factor / 100.0))
        handle_x = slider_rect.left + int(frac * usable)
        handle_y = slider_rect.centery - handle_h // 2
        self.settings_vh_handle_rect = pygame.Rect(handle_x, handle_y, handle_w, handle_h)

    def _update_text_speed_handle_position(self) -> None:
        handle_w = self.settings_text_speed_handle_rect.width
        handle_h = self.settings_text_speed_handle_rect.height
        slider_rect = self.settings_text_speed_slider_rect
        usable = max(1, slider_rect.width - handle_w)
        frac = max(0.0, min(1.0, self.settings_text_speed / 100.0))
        handle_x = slider_rect.left + int(frac * usable)
        handle_y = slider_rect.centery - handle_h // 2
        self.settings_text_speed_handle_rect = pygame.Rect(
            handle_x, handle_y, handle_w, handle_h
        )

    def _set_volume_from_mouse(self, mouse_x: int) -> None:
        slider_rect = self.settings_slider_rect
        handle_w = self.settings_handle_rect.width
        usable = max(1, slider_rect.width - handle_w)
        rel = max(0, min(mouse_x - slider_rect.left, usable))
        new_volume = int(round(100.0 * rel / usable))
        new_volume = max(0, min(100, new_volume))
        if new_volume != self.settings_volume:
            self.settings_volume = new_volume
            self._update_volume_handle_position()
            self._apply_volume(new_volume)
            self._save_settings()

    def _set_crt_from_mouse(self, mouse_x: int) -> None:
        slider = self.settings_crt_slider_rect
        handle_w = self.settings_crt_handle_rect.width
        usable = max(1, slider.width - handle_w)
        rel = max(0, min(mouse_x - slider.left, usable))
        new_level = int(round(100.0 * rel / usable))
        new_level = max(0, min(100, new_level))
        if new_level != self.settings_crt_level:
            self.settings_crt_level = new_level
            self._update_crt_handle_position()
            self._save_settings()

    def _set_vh_factor_from_mouse(self, mouse_x: int) -> None:
        slider = self.settings_vh_slider_rect
        handle_w = self.settings_vh_handle_rect.width
        usable = max(1, slider.width - handle_w)
        rel = max(0, min(mouse_x - slider.left, usable))
        new_factor = int(round(100.0 * rel / usable))
        new_factor = max(0, min(100, new_factor))
        if new_factor != self.settings_vh_factor:
            self.settings_vh_factor = new_factor
            self._update_vh_handle_position()
            self._apply_vh_settings()
            self._save_settings()

    def _set_text_speed_from_mouse(self, mouse_x: int) -> None:
        slider = self.settings_text_speed_slider_rect
        handle_w = self.settings_text_speed_handle_rect.width
        usable = max(1, slider.width - handle_w)
        rel = max(0, min(mouse_x - slider.left, usable))
        new_speed = int(round(100.0 * rel / usable))
        new_speed = max(0, min(100, new_speed))
        if new_speed != self.settings_text_speed:
            self.settings_text_speed = new_speed
            self._update_text_speed_handle_position()
            self._apply_text_speed()
            self._save_settings()

    def _apply_text_speed(self, speed_value: Optional[int] = None) -> None:
        """将 0–100 映射到 chat_typing_speed：0.01（快）～0.08（慢）。"""
        if speed_value is not None:
            self.settings_text_speed = max(0, min(100, int(speed_value)))
        v = self.settings_text_speed
        self.chat_typing_speed = 0.01 + (v / 100.0) * 0.07

    def _apply_vh_settings(self) -> None:
        if hasattr(self, "vh_manager") and self.vh_manager:
            self.vh_manager.set_enabled(self.settings_vh_enabled)
            self.vh_manager.set_intensity_factor(self.settings_vh_factor / 100.0)

    def _apply_volume(self, volume: int) -> None:
        """将 0–100 音量应用到 MIDI 与已加载的音效。"""
        if hasattr(self, "midi_sequencer") and self.midi_sequencer:
            self.midi_sequencer.set_volume(volume)
        sm = getattr(getattr(self, "character", None), "sound_manager", None)
        if sm is not None:
            frac = max(0.0, min(1.0, volume / 100.0))
            sm.set_volume(frac)

    def _save_settings(self) -> None:
        path = self._settings_json_path()
        data: Dict = {}
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                data = {}
        data["volume"] = self.settings_volume
        data["crt_level"] = self.settings_crt_level
        data["vh_enabled"] = self.settings_vh_enabled
        data["vh_factor"] = self.settings_vh_factor
        data["text_speed"] = self.settings_text_speed
        data["first_launch"] = bool(self.first_launch)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def _load_settings(self) -> None:
        path = self._settings_json_path()
        if not os.path.isfile(path):
            self._apply_volume(self.settings_volume)
            self._update_volume_handle_position()
            self._update_crt_handle_position()
            self._update_vh_handle_position()
            self._update_text_speed_handle_position()
            self._apply_vh_settings()
            self._apply_text_speed()
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            vol = int(data.get("volume", self.settings_volume))
            self.settings_volume = max(0, min(100, vol))
            crt = int(data.get("crt_level", self.settings_crt_level))
            self.settings_crt_level = max(0, min(100, crt))
            self.settings_vh_enabled = bool(data.get("vh_enabled", True))
            vf = int(data.get("vh_factor", self.settings_vh_factor))
            self.settings_vh_factor = max(0, min(100, vf))
            ts = int(data.get("text_speed", self.settings_text_speed))
            self.settings_text_speed = max(0, min(100, ts))
            # True=尚未完成首访主动问候；缺省为 True（旧存档无此键时视为首访）
            if "first_launch" in data:
                self.first_launch = bool(data["first_launch"])
            else:
                self.first_launch = True
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            pass
        self._apply_volume(self.settings_volume)
        self._update_volume_handle_position()
        self._update_crt_handle_position()
        self._update_vh_handle_position()
        self._update_text_speed_handle_position()
        self._apply_vh_settings()
        self._apply_text_speed()

    def _settings_pointer_down(self, pos: Tuple[int, int]) -> None:
        x, _ = pos
        if self.settings_vh_checkbox_rect.collidepoint(pos):
            self.settings_vh_enabled = not self.settings_vh_enabled
            self._apply_vh_settings()
            self._save_settings()
            return
        if self.settings_handle_rect.collidepoint(pos):
            self.settings_dragging = True
            return
        if self.settings_crt_handle_rect.collidepoint(pos):
            self.settings_crt_dragging = True
            return
        if self.settings_vh_handle_rect.collidepoint(pos):
            self.settings_vh_dragging = True
            return
        if self.settings_text_speed_handle_rect.collidepoint(pos):
            self.settings_text_speed_dragging = True
            return
        if self.settings_slider_rect.collidepoint(pos):
            self._set_volume_from_mouse(x)
            self.settings_dragging = True
            return
        if self.settings_crt_slider_rect.collidepoint(pos):
            self._set_crt_from_mouse(x)
            self.settings_crt_dragging = True
            return
        if self.settings_vh_slider_rect.collidepoint(pos):
            self._set_vh_factor_from_mouse(x)
            self.settings_vh_dragging = True
            return
        if self.settings_text_speed_slider_rect.collidepoint(pos):
            self._set_text_speed_from_mouse(x)
            self.settings_text_speed_dragging = True

    def _draw_settings_overlay(self) -> None:
        """半透明设置层：音量 / CRT / VH / 文本速度（绘于 CRT/VH 之后，保持清晰）。"""
        overlay = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("Settings / 音量 / CRT / VH / Text", True, (200, 200, 200))
        self.screen.blit(
            title,
            (self.screen_width // 2 - title.get_width() // 2, max(40, int(self.screen_height * 0.10))),
        )

        label = self.small_font.render("Volume", True, (180, 180, 180))
        self.screen.blit(
            label,
            (self.settings_slider_rect.left, self.settings_slider_rect.top - 28),
        )
        vol_text = self.small_font.render(f"{self.settings_volume}%", True, (255, 255, 255))
        self.screen.blit(
            vol_text,
            (self.settings_slider_rect.right + 12, self.settings_slider_rect.top - 6),
        )

        pygame.draw.rect(self.screen, (80, 80, 80), self.settings_slider_rect)
        filled_w = int(
            (self.settings_volume / 100.0) * self.settings_slider_rect.width
        )
        filled_rect = pygame.Rect(
            self.settings_slider_rect.left,
            self.settings_slider_rect.top,
            filled_w,
            self.settings_slider_rect.height,
        )
        pygame.draw.rect(self.screen, (100, 200, 100), filled_rect)
        pygame.draw.rect(self.screen, (150, 150, 150), self.settings_slider_rect, 1)

        handle_color = (220, 220, 220) if self.settings_dragging else (180, 180, 180)
        pygame.draw.rect(self.screen, handle_color, self.settings_handle_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), self.settings_handle_rect, 1)

        crt_label = self.small_font.render("CRT Clarity Offset", True, (180, 180, 180))
        self.screen.blit(
            crt_label,
            (self.settings_crt_slider_rect.left, self.settings_crt_slider_rect.top - 28),
        )
        crt_text = self.small_font.render(f"{self.settings_crt_level}%", True, (255, 255, 255))
        self.screen.blit(
            crt_text,
            (self.settings_crt_slider_rect.right + 12, self.settings_crt_slider_rect.top - 6),
        )
        pygame.draw.rect(self.screen, (80, 80, 80), self.settings_crt_slider_rect)
        crt_filled = int((self.settings_crt_level / 100.0) * self.settings_crt_slider_rect.width)
        crt_fill_rect = pygame.Rect(
            self.settings_crt_slider_rect.left,
            self.settings_crt_slider_rect.top,
            crt_filled,
            self.settings_crt_slider_rect.height,
        )
        pygame.draw.rect(self.screen, (100, 200, 100), crt_fill_rect)
        pygame.draw.rect(self.screen, (150, 150, 150), self.settings_crt_slider_rect, 1)
        crt_handle_color = (220, 220, 220) if self.settings_crt_dragging else (180, 180, 180)
        pygame.draw.rect(self.screen, crt_handle_color, self.settings_crt_handle_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), self.settings_crt_handle_rect, 1)

        vh_label = self.small_font.render("VH Effect", True, (180, 180, 180))
        self.screen.blit(
            vh_label,
            (self.settings_vh_checkbox_rect.left, self.settings_vh_checkbox_rect.top - 28),
        )
        box_color = (100, 200, 100) if self.settings_vh_enabled else (150, 150, 150)
        pygame.draw.rect(self.screen, box_color, self.settings_vh_checkbox_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), self.settings_vh_checkbox_rect, 1)
        if self.settings_vh_enabled:
            inner = self.settings_vh_checkbox_rect.inflate(-6, -6)
            pygame.draw.line(self.screen, (0, 0, 0), inner.bottomleft, inner.center, 2)
            pygame.draw.line(self.screen, (0, 0, 0), inner.center, inner.topright, 2)
        vh_status = "Enabled" if self.settings_vh_enabled else "Disabled"
        status_text = self.small_font.render(vh_status, True, (200, 200, 200))
        self.screen.blit(
            status_text,
            (self.settings_vh_checkbox_rect.right + 10, self.settings_vh_checkbox_rect.centery - 10),
        )

        factor_label = self.small_font.render("Intensity Factor", True, (180, 180, 180))
        self.screen.blit(
            factor_label,
            (self.settings_vh_slider_rect.left, self.settings_vh_slider_rect.top - 28),
        )
        factor_text = self.small_font.render(f"{self.settings_vh_factor}%", True, (255, 255, 255))
        self.screen.blit(
            factor_text,
            (self.settings_vh_slider_rect.right + 12, self.settings_vh_slider_rect.top - 6),
        )
        pygame.draw.rect(self.screen, (80, 80, 80), self.settings_vh_slider_rect)
        vh_filled = int((self.settings_vh_factor / 100.0) * self.settings_vh_slider_rect.width)
        vh_fill_rect = pygame.Rect(
            self.settings_vh_slider_rect.left,
            self.settings_vh_slider_rect.top,
            vh_filled,
            self.settings_vh_slider_rect.height,
        )
        pygame.draw.rect(self.screen, (100, 200, 100), vh_fill_rect)
        pygame.draw.rect(self.screen, (150, 150, 150), self.settings_vh_slider_rect, 1)
        vh_handle_color = (220, 220, 220) if self.settings_vh_dragging else (180, 180, 180)
        pygame.draw.rect(self.screen, vh_handle_color, self.settings_vh_handle_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), self.settings_vh_handle_rect, 1)

        ts_label = self.small_font.render("Text Speed", True, (180, 180, 180))
        self.screen.blit(
            ts_label,
            (self.settings_text_speed_slider_rect.left, self.settings_text_speed_slider_rect.top - 28),
        )
        ts_text = self.small_font.render(f"{self.settings_text_speed}%", True, (255, 255, 255))
        self.screen.blit(
            ts_text,
            (self.settings_text_speed_slider_rect.right + 12, self.settings_text_speed_slider_rect.top - 6),
        )
        pygame.draw.rect(self.screen, (80, 80, 80), self.settings_text_speed_slider_rect)
        ts_filled = int((self.settings_text_speed / 100.0) * self.settings_text_speed_slider_rect.width)
        ts_fill_rect = pygame.Rect(
            self.settings_text_speed_slider_rect.left,
            self.settings_text_speed_slider_rect.top,
            ts_filled,
            self.settings_text_speed_slider_rect.height,
        )
        pygame.draw.rect(self.screen, (100, 200, 100), ts_fill_rect)
        pygame.draw.rect(self.screen, (150, 150, 150), self.settings_text_speed_slider_rect, 1)
        ts_handle_color = (
            (220, 220, 220) if self.settings_text_speed_dragging else (180, 180, 180)
        )
        pygame.draw.rect(self.screen, ts_handle_color, self.settings_text_speed_handle_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), self.settings_text_speed_handle_rect, 1)

        hint = self.small_font.render("O 关闭  |  ESC 关闭", True, (150, 150, 150))
        self.screen.blit(
            hint,
            (self.screen_width // 2 - hint.get_width() // 2, self.screen_height - 48),
        )

    def _on_window_resize(self, event: pygame.event.Event) -> None:
        """可调整窗口大小时同步分辨率与依赖尺寸的子系统。"""
        if getattr(event, "size", None):
            w, h = event.size
        else:
            w = int(getattr(event, "w", self.screen_width))
            h = int(getattr(event, "h", self.screen_height))
        w = max(640, w)
        h = max(480, h)
        self.screen_width = w
        self.screen_height = h
        self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        self.background = self._create_background()
        self.crt_manager = CRTManager(self.screen_width, self.screen_height)
        self.vh_manager = VerticalHoldManager(self.screen_width, self.screen_height)
        self._layout_settings_slider()
        # 新实例仅含默认 VH 状态；此处唯一一次从 self.settings_vh_* 写回管理器
        self._apply_vh_settings()

    def _init_subsystems(self):
        """初始化所有子系统"""
        # 像素精度渐变系统
        self.pixel_gradient = PixelGradientSystem()
        
        # CRT老化管理器
        self.crt_manager = CRTManager(self.screen_width, self.screen_height)
        
        # ASCII动画系统
        self.ascii_animation = ASCIIAnimation()
        self.ascii_converter = ASCIIArtConverter()
        
        # MIDI系统
        self.midi_converter = AdvancedScoreConverter()
        self.midi_sequencer = MIDISequencer()
        self.mood_manager = MoodMusicManager(self.midi_sequencer)
        
        # 动画角色
        self.character = AdvancedAnimatedCharacter()
        self.character.set_frame_delay(0.15)
        
        # 垂直保持失调管理器
        self.vh_manager = VerticalHoldManager(self.screen_width, self.screen_height)
        
        # 背景
        self.background = self._create_background()
        
    def _init_npcs(self):
        """初始化论坛NPC"""
        # 创建5个随机NPC
        for i in range(5):
            self.npcs.append(ForumNPC(i))
            
    def _create_background(self) -> pygame.Surface:
        """创建游戏背景"""
        background = pygame.Surface((self.screen_width, self.screen_height))
        background.fill((0, 0, 0))
        
        # 添加网格线，模拟BBS界面
        for x in range(0, self.screen_width, 50):
            pygame.draw.line(background, (0, 255, 0), (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, 50):
            pygame.draw.line(background, (0, 255, 0), (0, y), (self.screen_width, y), 1)
            
        return background
        
    def run(self):
        """运行主游戏循环"""
        self._log("BBS Shojo游戏 - 千禧年打字物语")
        self._log("按H查看帮助")
        
        while self.running:
            delta_time = self.clock.tick(30) / 1000.0
            self._cursor_phase += delta_time
            
            # 处理事件
            self._handle_events()
            
            if not self.paused:
                # 更新所有子系统
                self._update_subsystems(delta_time)
            else:
                # 暂停时仍推进真结局计时；独白阶段打字机也需更新
                self._update_ending_sequence(delta_time)
                if (
                    self.ending_triggered
                    and self.ending_phase == 1
                    and self._ending_phase1_active
                ):
                    self._update_chat_typing(delta_time)

            # 绘制界面
            self._draw_interface()
            
            # 更新显示
            pygame.display.flip()
            
        # 保存离线日志
        self._save_offline_logs()
        pygame.quit()
        sys.exit()

    def _log(self, text: str):
        """控制台安全输出，避免部分 Windows 编码导致崩溃。"""
        try:
            print(text)
        except UnicodeEncodeError:
            encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
            safe = text.encode(encoding, errors="replace").decode(encoding, errors="replace")
            print(safe)
        
    def _handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self._on_window_resize(event)
            elif self.settings_visible:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._settings_pointer_down(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self._clear_settings_drag_states()
                elif event.type == pygame.MOUSEMOTION:
                    if self.settings_dragging:
                        self._set_volume_from_mouse(event.pos[0])
                    elif self.settings_crt_dragging:
                        self._set_crt_from_mouse(event.pos[0])
                    elif self.settings_vh_dragging:
                        self._set_vh_factor_from_mouse(event.pos[0])
                    elif self.settings_text_speed_dragging:
                        self._set_text_speed_from_mouse(event.pos[0])
                elif event.type == pygame.KEYDOWN:
                    self._handle_key_press(event.key, event.unicode)
            elif event.type == pygame.KEYDOWN:
                self._handle_key_press(event.key, event.unicode)

    def _handle_key_press(self, key: int, unicode: str):
        """处理按键事件"""
        if self.ending_triggered and self.ending_phase == 3 and self.ending_phase3_frame >= 4:
            self._ending_phase3_exit_requested = True
            return
        if self._ending_sequence_blocks_input():
            return

        mods = pygame.key.get_mods()
        hotkey_modifier = bool(mods & (pygame.KMOD_CTRL | pygame.KMOD_ALT))

        # O：音量/CRT 设置；在「底部输入框打字模式」下勿抢键（避免误弹层）
        if key == pygame.K_o:
            in_typing_bar = (
                self._chat_can_accept_input()
                and self.chat_focus
                and not hotkey_modifier
                and not self.settings_visible
            )
            if not in_typing_bar:
                if self.settings_visible:
                    self.settings_visible = False
                    self._clear_settings_drag_states()
                    self._on_settings_closed()
                else:
                    self.settings_visible = True
                    self._clear_settings_drag_states()
                    self.help_overlay_active = False
                    self._layout_settings_slider()
                return

        if self.settings_visible:
            if key == pygame.K_ESCAPE:
                self.settings_visible = False
                self._clear_settings_drag_states()
                self._on_settings_closed()
                return
            return

        # Tab 切换输入/热键模式
        if key == pygame.K_TAB and self._chat_can_accept_input(ignore_focus=True):
            self.chat_focus = not self.chat_focus
            return

        # 当聊天输入模式开启且未按 Ctrl/Alt 时，优先把按键当作输入
        if self._chat_can_accept_input() and self.chat_focus and not hotkey_modifier:
            if key == pygame.K_BACKSPACE:
                self.chat_input = self.chat_input[:-1]
                return
            if key == pygame.K_RETURN:
                self._chat_send_current()
                return
            if key == pygame.K_UP:
                self.chat_scroll = min(self.chat_scroll + 1, 999)
                return
            if key == pygame.K_DOWN:
                self.chat_scroll = max(self.chat_scroll - 1, 0)
                return
            if unicode and unicode.isprintable():
                if unicode not in ("\r", "\n", "\t"):
                    self.chat_input += unicode
                    self.chat_input = self.chat_input[-240:]
                return
            if key == pygame.K_o:
                ch = "O" if mods & pygame.KMOD_SHIFT else "o"
                self.chat_input += ch
                self.chat_input = self.chat_input[-240:]
                return

        if key == pygame.K_ESCAPE:
            self._chat_flush_typing()
            self._chat_pending_girl = None
            self._chat_pending_slash = None
            if self.help_overlay_active:
                self.help_overlay_active = False
                return
            if self.typing_challenge.is_active():
                self.typing_challenge.reset()
                self.typing_challenge_active = False
            elif self.forum_active:
                self.forum_active = False
            else:
                self.running = False
        elif key == pygame.K_p:
            self.paused = not self.paused
        elif key == pygame.K_h:
            self.help_overlay_active = not self.help_overlay_active
            return

        if self.help_overlay_active:
            # 帮助层打开时，仅响应 H/ESC 关闭，避免误触发游戏操作
            return
        elif key == pygame.K_m:
            # 切换静音
            self.character.mute(not self.character.is_muted())
        elif key == pygame.K_g:
            # 背景音乐开关
            self._toggle_bgm()
        elif key == pygame.K_r:
            # 重置垂直保持失调
            self.vh_manager.deactivate()
        elif key == pygame.K_t:
            # 触发图灵测试
            self._toggle_turing()
        elif key == pygame.K_v:
            # 触发垂直保持失调效果
            if not self.vh_manager.enabled:
                return
            if self.vh_manager.active:
                self.vh_manager.deactivate()
            else:
                self.vh_manager.activate(intensity=8.0, drift_speed=1.5, duration=5000)
        elif key == pygame.K_s:
            # 保存游戏
            self._save_game()
        elif key == pygame.K_l:
            # 加载游戏
            self._load_game()
        elif key == pygame.K_k:
            # 触发打字挑战
            if self.typing_challenge.is_active():
                self.typing_challenge.reset()
                self.typing_challenge_active = False
            else:
                self._trigger_typing_challenge()
        elif key == pygame.K_f:
            # 查看论坛
            self.forum_active = not self.forum_active
        elif key == pygame.K_b:
            # 启动终端版 BBS 模式
            self._launch_bbs_terminal_mode()
            
        # 处理打字挑战输入（完成时 update_input 返回 (True, feedback)，须在此弹结果）
        if self.typing_challenge.is_active():
            result: Optional[Tuple[bool, str]] = None
            if key == pygame.K_BACKSPACE:
                result = self.typing_challenge.update_input("\b")
            elif key == pygame.K_RETURN:
                result = self.typing_challenge.update_input("\n")
            elif unicode.isprintable():
                result = self.typing_challenge.update_input(unicode)
            if result is not None:
                done, feedback = result
                if done:
                    self._show_typing_result(feedback)
            return
                
    def _update_subsystems(self, delta_time: float):
        """更新所有子系统"""
        self._poll_llm_reply_queue()
        self._update_chat_typing(delta_time)
        self._update_ending_sequence(delta_time)
        # 更新CRT管理器（真结局 phase2 计时亦在 _update_ending_sequence）
        self.crt_manager.update(delta_time)
        
        # 更新动画角色
        self.character.update(delta_time)
        
        # 更新垂直保持失调效果
        self.vh_manager.update()
        
        # 更新时间系统
        time_triggered, time_message, event_type = self.time_system.update(delta_time)
        if time_triggered and not self.typing_challenge.is_active():
            self._show_time_event(time_message, event_type)
            
        # 更新论坛NPC
        self._update_npcs(delta_time)
        
        # 随机 VH：打字挑战 / 暂停 / 论坛打开时不触发；概率降低避免打断游玩
        if (
            random.random() < 0.00004
            and self.vh_manager.enabled
            and not self.vh_manager.active
            and not self.paused
            and not self.forum_active
            and not self.typing_challenge.is_active()
        ):
            self.vh_manager.activate(intensity=random.uniform(2.5, 6.0), drift_speed=random.uniform(0.4, 1.6))
            
    def _update_npcs(self, delta_time: float):
        """更新论坛NPC"""
        current_time = time.time()
        if current_time - self.last_npc_update > 10:  # 每10秒更新一次NPC
            self.last_npc_update = current_time
            
            # 随机有一个NPC发帖
            if random.random() < 0.3:
                npc = random.choice(self.npcs)
                post = npc.update(current_time, self.current_mood, self.memory_fragments)
                if post:
                    self.forum_posts.append({
                        "author": npc.name,
                        "avatar": npc.avatar,
                        "content": post,
                        "time": time.time(),
                        "npc_color": tuple(npc.personality["color"]),
                    })

    def _has_fear_fragment(self) -> bool:
        """女孩记忆碎片中含 abandonment_fear 时，CRT 叠加创伤反馈。"""
        if not hasattr(self, "bbs_engine") or self.bbs_engine is None:
            return False
        girl = getattr(self.bbs_engine, "girl", None)
        if girl is None:
            return False
        return "abandonment_fear" in girl.memory_fragments

    def _draw_interface(self):
        """绘制游戏界面"""
        if self.ending_triggered and self.ending_phase == 3:
            self._draw_ending_ascii_sequence()
            return
        # GDD：记忆碎片驱动立绘精度与 CRT（回忆愈多，CRT 明显减弱；整体比初版更轻）
        self.pixel_gradient.set_memory_fragments(self.memory_fragments)
        mf = float(self.memory_fragments)
        # 碎片曲线 base_aging（约 0 档 ~15、100 档 ~1.5，开局更清晰，满碎片仍趋最清晰）
        # 清晰度偏移滑条 settings_crt_level：0%=叙事最清晰端仍强加老化，100%=仅曲线值（无额外）
        base_aging = max(1.5, min(15.0, 15.0 - mf * 0.135))
        t = self.settings_crt_level / 100.0
        final_aging = base_aging + (100.0 - base_aging) * (1.0 - t)
        if self._has_fear_fragment():
            final_aging = min(100.0, final_aging + 15.0)
        if self.ending_triggered and self.ending_phase == 2:
            u = min(1.0, self.ending_timer / 4.0)
            final_aging = max(final_aging, 25.0 + 75.0 * u)
        self.crt_manager.set_aging_level(min(100.0, max(0.0, final_aging)))

        self.screen.blit(self.background, (0, 0))
        self._draw_character()
        self._draw_ui()
        self._draw_chat_ui()
        if self.typing_challenge.is_active():
            self._draw_typing_challenge()
        if self.forum_active:
            self._draw_forum()
        if self.paused:
            self._draw_pause_menu()
        if self.help_overlay_active:
            self._draw_help_overlay()
        self._apply_display_postprocess()
        if self.settings_visible:
            self._draw_settings_overlay()

    def _get_ending_mono_font(self, size: int) -> pygame.font.Font:
        for name in ("couriernew", "consolas", "courier new", "lucidaconsole"):
            try:
                f = pygame.font.SysFont(name, size)
                if f:
                    return f
            except (OSError, ValueError, TypeError):
                continue
        return pygame.font.Font(None, size)

    def _pick_ending_ascii_font_metrics(
        self, lines: List[str]
    ) -> Tuple[pygame.font.Font, int]:
        pad = 32
        max_chars = max((len(line) for line in lines), default=1)
        for size in (12, 11, 10, 9, 8, 7, 6):
            font = self._get_ending_mono_font(size)
            cw, _ = font.size("M")
            if max_chars * cw < self.screen_width - pad:
                return font, font.get_linesize()
        font = self._get_ending_mono_font(6)
        return font, font.get_linesize()

    def _draw_ending_ascii_sequence(self) -> None:
        """真结局 Phase 3：按帧 1→2→3→4 顺序播放；每帧淡入/淡出，整体亮度递减；之后为英文告别句。"""
        self.screen.fill((0, 0, 0))
        f = self.ending_phase3_frame
        if f < 4:
            base_b = (255, 200, 140, 80)[f]
            dur = self.ending_phase3_frame_durations[f]
            t = self.ending_phase3_timer
            fin = max(0.05, self.ending_phase3_fade_in_sec)
            fout = max(0.05, self.ending_phase3_fade_out_sec)
            m = 1.0
            if t < fin:
                m = t / fin
            elif t > dur - fout:
                m = max(0.0, (dur - t) / fout)
            brightness = max(0, min(255, int(base_b * m)))
            lines = self._ending_ascii_frames[f]
            font, line_h = self._pick_ending_ascii_font_metrics(lines)
            color = (brightness, brightness, brightness)
            total_height = len(lines) * line_h
            start_y = max(8, (self.screen_height - total_height) // 2)
            for i, line in enumerate(lines):
                y = start_y + i * line_h
                if line.strip():
                    surf = font.render(line, True, color)
                    x = max(8, (self.screen_width - surf.get_width()) // 2)
                    self.screen.blit(surf, (x, y))
        else:
            self._draw_ending_final_text()

    def _draw_ending_final_text(self) -> None:
        self.screen.fill((0, 0, 0))
        font = self._get_ending_mono_font(24)
        text = "thank you for remembering me."
        text_surf = font.render(text, True, (180, 200, 220))
        x = (self.screen_width - text_surf.get_width()) // 2
        y = self.screen_height // 2 - text_surf.get_height() // 2
        self.screen.blit(text_surf, (x, y))
        hint_font = self._get_ending_mono_font(16)
        hint_surf = hint_font.render("[ 按任意键离开 ]", True, (120, 120, 120))
        hx = (self.screen_width - hint_surf.get_width()) // 2
        hy = y + text_surf.get_height() + 24
        self.screen.blit(hint_surf, (hx, hy))

    def _apply_display_postprocess(self):
        """CRT 与垂直保持作用于整帧（含 UI / 弹层），先 CRT 再 rolling。"""
        if self.crt_manager.aging_level > 0:
            src = pygame.display.get_surface()
            processed = self.crt_manager.apply_crt_effect(src)
            self.screen.blit(processed, (0, 0))
        if self.vh_manager.active:
            src = pygame.display.get_surface()
            processed = self.vh_manager.apply_effect(src)
            self.screen.blit(processed, (0, 0))
            
    def _draw_character(self):
        """绘制ASCII角色"""
        # 获取当前ASCII帧
        frame_text = self.character.get_current_frame().strip()

        # 多行逐行绘制，避免换行字符显示异常
        lines = frame_text.splitlines() or [frame_text]
        total_height = len(lines) * (self.font.get_height() + 4)
        y = self.screen_height // 2 - 100 - total_height // 2
        for line in lines:
            text_surface = self.font.render(line, True, (0, 255, 0))
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, y))
            self.screen.blit(text_surface, text_rect)
            y += self.font.get_height() + 4
        
    def _draw_ui(self):
        """绘制UI元素"""
        # 绘制记忆碎片进度
        denom = max(1, self.total_memory_fragments)
        progress = min(1.0, self.memory_fragments / denom)
        progress_bar_width = 400
        progress_bar_height = 20
        progress_bar_x = 20
        progress_bar_y = 20
        
        pygame.draw.rect(self.screen, (255, 255, 255), (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height))
        pygame.draw.rect(self.screen, (0, 255, 0), (progress_bar_x, progress_bar_y, int(progress_bar_width * progress), progress_bar_height))
        
        progress_text = self.small_font.render(f"记忆碎片: {self.memory_fragments}/{self.total_memory_fragments}", True, (255, 255, 255))
        self.screen.blit(progress_text, (progress_bar_x, progress_bar_y - 20))
        
        # 绘制当前情绪
        mood_text = self.small_font.render(f"当前情绪: {self.current_mood}", True, (255, 255, 255))
        self.screen.blit(mood_text, (self.screen_width - 200, 20))

        # 立绘精度预览（像素渐变系统）
        portrait = self.pixel_gradient.get_current_art(120, 120)
        px = self.screen_width - 140
        pygame.draw.rect(self.screen, (0, 80, 0), (px - 6, 54, 132, 132), 1)
        self.screen.blit(portrait, (px, 60))
        cap = self.small_font.render("记忆分辨率", True, (160, 255, 160))
        self.screen.blit(cap, (px - 10, 190))
        
        # 绘制帮助提示
        help_text = self.small_font.render(
            "输入文字回车发送；H帮助；Tab切热键后O音量；ESC退出", True, (128, 128, 128)
        )
        self.screen.blit(help_text, (20, self.screen_height - 30))
        
    def _draw_pause_menu(self):
        """绘制暂停菜单"""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        menu_text = self.font.render("游戏暂停", True, (255, 255, 255))
        menu_rect = menu_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 100))
        self.screen.blit(menu_text, menu_rect)
        
        help_text = [
            "按键说明:",
            "ESC - 退出游戏",
            "P - 暂停/继续",
            "H - 显示帮助",
            "O - 音量设置（热键模式；底部打字时 O 为字母，Tab 切到热键后再按 O）",
            "M - 切换静音",
            "G - 背景音乐开关",
            "R - 重置垂直保持失调",
            "T - 触发图灵测试",
            "V - 触发垂直保持失调效果",
            "S - 保存游戏",
            "L - 加载游戏",
            "K - 触发打字挑战",
            "F - 查看论坛",
            "B - 打开终端版BBS模式",
            "按P继续游戏"
        ]
        
        for i, text in enumerate(help_text):
            rendered_text = self.small_font.render(text, True, (255, 255, 255))
            rect = rendered_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50 + i * 30))
            self.screen.blit(rendered_text, rect)
            
    def _show_help(self):
        """显示帮助信息（兼容旧调用，转为游戏内弹层）。"""
        self.help_overlay_active = True

    def _draw_help_overlay(self):
        """绘制帮助弹层（按 H 或 ESC 关闭）。"""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("帮助与操作说明", True, (0, 255, 0))
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 24))
        ver_surf = self.small_font.render(f"版本 {GAME_VERSION}", True, (160, 200, 160))
        self.screen.blit(
            ver_surf, (self.screen_width // 2 - ver_surf.get_width() // 2, 64)
        )

        help_lines = [
            "按键说明:",
            "ESC - 退出游戏/关闭当前弹层",
            "H - 打开/关闭帮助",
            "O - 音量设置（热键模式下；再按 O 或 ESC 关闭）",
            "P - 暂停/继续",
            "输入任意文字 - 在底部输入框输入",
            "回车 - 发送消息",
            "↑/↓ - 滚动聊天记录",
            "M - 切换静音",
            "G - 背景音乐开关",
            "R - 重置垂直保持失调",
            "T - 触发图灵测试",
            "V - 触发垂直保持失调效果",
            "K - 打字挑战",
            "F - 论坛界面",
            "B - 启动终端版BBS模式",
            "S - 保存进度，L - 加载进度",
            "",
            "目标提示:",
            "通过互动提升记忆碎片并探索剧情分支。",
            "打字挑战会根据准确率与速度给出反馈。",
            "论坛会周期性出现 NPC 发帖，可用于观察世界状态。",
            "也可输入 /help 查看聊天内命令；/midi 可试简谱彩蛋。",
            "记忆碎片增加时：右上角「记忆分辨率」立绘更细，CRT 会略减弱。",
            "",
            "按 H 或 ESC 返回游戏",
        ]

        y = 84
        for line in help_lines:
            y = blit_wrapped(
                self.screen,
                line,
                self.small_font,
                (255, 255, 255),
                self.screen_width // 2,
                y,
                line_gap=2,
                max_width=self.screen_width - 90,
            )
            y += 2
        
    def _trigger_turing_test(self):
        """触发图灵测试支线"""
        self._log("\n=== 图灵测试 ===")
        self._log("其他网友正在讨论你和角色的对话...")
        self._log("他们怀疑角色是不是自动回复机器人")
        self._log(f"当前进展: {self.turing_test_progress}%")
        self._log("需要通过自然对话来证明角色是真实的")
        
        # 随机增加进度
        self.turing_test_progress += random.randint(5, 15)
        if self.turing_test_progress >= 100:
            self._log("\n图灵测试完成！网友们相信了角色的真实性")
            self.memory_fragments += 10
            self.turing_test_progress = 100

    def _toggle_turing(self):
        """按 T 显示/收起图灵测试信息（写入聊天历史）。"""
        self._chat_flush_typing()
        self._chat_pending_girl = None
        self._chat_pending_slash = None
        # 如果最近一条就是图灵信息，则视为“关闭/收起”——这里用插入一条分隔线实现
        self.chat_history.append({"role": "system", "text": self.bbs_engine.turing_test_round()})
            
    def _trigger_typing_challenge(self):
        """触发打字挑战"""
        self.typing_challenge.start_challenge()
        self.typing_challenge_active = True
        self._log("\n打字挑战开始！")
        self._log(self.typing_challenge.current_challenge)
        
    def _draw_typing_challenge(self):
        """绘制打字挑战界面"""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        current, input_text, acc, wpm = self.typing_challenge.get_current_progress()
        
        # 绘制挑战文本
        y = 100
        title = self.font.render("打字挑战", True, (0, 255, 0))
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, y))
        y += 50
        
        for line in current.split("\n"):
            text = self.small_font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, y))
            y += 30
            
        # 绘制输入文本
        y += 30
        input_text_surf = self.small_font.render(f"你的输入: {input_text}", True, (0, 255, 0))
        self.screen.blit(input_text_surf, (self.screen_width//2 - input_text_surf.get_width()//2, y))
        y += 30
        
        # 绘制进度
        acc_text = self.small_font.render(f"准确率: {acc:.1f}%", True, (255, 255, 255))
        self.screen.blit(acc_text, (self.screen_width//2 - acc_text.get_width()//2, y))
        y += 30
        
        wpm_text = self.small_font.render(f"速度: {wpm} WPM", True, (255, 255, 255))
        self.screen.blit(wpm_text, (self.screen_width//2 - wpm_text.get_width()//2, y))
        y += 30
        
        # 绘制提示
        hint_text = self.small_font.render("按ESC取消挑战", True, (128, 128, 128))
        self.screen.blit(hint_text, (self.screen_width//2 - hint_text.get_width()//2, self.screen_height - 50))
        
    def _show_typing_result(self, feedback: str):
        """显示打字挑战结果"""
        self._apply_typing_memory_reward()
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        text = self.font.render("打字挑战完成！", True, (0, 255, 0))
        self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, self.screen_height//2 - 50))
        
        blit_wrapped(
            self.screen,
            feedback,
            self.small_font,
            (255, 255, 255),
            self.screen_width // 2,
            self.screen_height // 2,
            max_width=self.screen_width - 80,
        )
        
        hint_text = self.small_font.render("按任意键继续", True, (128, 128, 128))
        self.screen.blit(hint_text, (self.screen_width//2 - hint_text.get_width()//2, self.screen_height//2 + 50))
        
        pygame.display.flip()
        
        # 等待按键
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                    waiting = False
                    
        self.typing_challenge.reset()
        self.typing_challenge_active = False

    def _apply_typing_memory_reward(self):
        """打字挑战结算：按得分增加记忆碎片（上限 total_memory_fragments）。"""
        g = max(0, self.typing_challenge.gain)
        add = max(1, min(20, g))
        self.memory_fragments = min(self.total_memory_fragments, self.memory_fragments + add)

    def _sync_mood_from_player_message(self, msg: str):
        """根据玩家用语粗调情绪与 ASCII/音效（设计文档：动态音效与表情联动）。"""
        if any(w in msg for w in ("难过", "伤心", "抱歉", "对不起", "不哭")):
            self.current_mood = "sad"
            self.character.set_emotion("sad")
        elif any(w in msg for w in ("谢谢", "哈哈", "好耶", "喜欢", "开心")):
            self.current_mood = "happy"
            self.character.set_emotion("happy")
        elif "?" in msg or "？" in msg:
            self.character.set_emotion("surprised")
        else:
            self.character.set_emotion(self.current_mood)
        
    def _show_time_event(self, message: str, event_type: str):
        """显示时间事件"""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        title = self.font.render("特殊事件", True, (0, 255, 0))
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 100))
        
        # 分割消息为多行
        lines = message.split("\n")
        y = 200
        for line in lines:
            text = self.small_font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, y))
            y += 30
            
        hint_text = self.small_font.render("按任意键继续", True, (128, 128, 128))
        self.screen.blit(hint_text, (self.screen_width//2 - hint_text.get_width()//2, self.screen_height - 50))
        
        pygame.display.flip()
        
        # 等待按键
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                    waiting = False
                    
    def _show_forum(self):
        """显示论坛界面"""
        self.forum_active = True
        self._log("\n论坛界面")

    def _launch_bbs_terminal_mode(self):
        """在独立进程中启动终端版 BBS 少女模式。"""
        if getattr(sys, "frozen", False):
            self._log("终端版无法从打包 exe 内启动，请用 Python 运行 src/main_bbs_terminal.py。")
            return
        script_path = os.path.join(os.path.dirname(__file__), "main_bbs_terminal.py")
        if not os.path.exists(script_path):
            self._log("终端版入口不存在: main_bbs_terminal.py")
            return
        try:
            subprocess.Popen([sys.executable, script_path])
            self._log("已启动终端版 BBS 少女模式。")
        except Exception as exc:
            self._log(f"启动终端版失败: {exc}")

    def _seed_chat(self):
        """初始化一段开场对白；首访时女孩主动问候并持久化 first_launch。"""
        self._chat_reset_typing_state()
        self._chat_pending_girl = None
        self._chat_pending_slash = None
        if self.first_launch:
            girl = self.bbs_engine.girl
            raw = random.choice(girl.keyword_responses["greeting"])
            opener = f"{girl.name}：{raw}"
            self.chat_history = [
                {"role": "system", "text": "你连接到了一个被遗忘的BBS。"},
                {"role": "girl", "text": opener},
                {
                    "role": "system",
                    "text": "在底部输入框打字，回车发送。输入 /help 查看可用命令。",
                },
            ]
            self.bbs_engine.conversation.seed_girl_opener(opener)
            self.first_launch = False
            self._save_settings()
        else:
            self.chat_history = [
                {"role": "system", "text": "你连接到了一个被遗忘的BBS。"},
                {"role": "girl", "text": "……有人吗？你能看到我吗？"},
                {"role": "system", "text": "在底部输入框打字，回车发送。输入 /help 查看可用命令。"},
            ]

    def _ending_sequence_blocks_input(self) -> bool:
        if not self.ending_triggered:
            return False
        if self.ending_phase < 3:
            return True
        if self.ending_phase == 3 and self.ending_phase3_frame < 4:
            return True
        return False

    def _chat_can_accept_input(self, ignore_focus: bool = False) -> bool:
        """覆盖层打开时不接收聊天输入；ignore_focus 用于 Tab 切换判断。"""
        if self._ending_sequence_blocks_input():
            return False
        if self.settings_visible or self.help_overlay_active or self.paused or self.forum_active:
            return False
        if self.typing_challenge.is_active():
            return False
        if not ignore_focus and not self.chat_focus:
            return False
        return True

    def _chat_ui_llm_hint_allowed(self) -> bool:
        """与 _update_chat_typing 非真结局分支一致的叠层判断，避免在设置/暂停等下仍绘「正在输入」。"""
        if self._ending_sequence_blocks_input():
            return False
        if self.settings_visible or self.help_overlay_active or self.paused or self.forum_active:
            return False
        if self.typing_challenge.is_active():
            return False
        return True

    def _on_settings_closed(self) -> None:
        """关闭设置后重探测 Ollama，便于用户后启动的守护进程被识别。"""
        try:
            self.bbs_engine.refresh_llm_availability()
        except Exception:
            pass

    def _chat_reset_typing_state(self) -> None:
        self.chat_typing_active = False
        self.chat_typing_full_text = ""
        self.chat_typing_current_length = 0
        self.chat_typing_timer = 0.0
        self.chat_typing_role = "girl"
        self._chat_typing_speed_override = None

    def _chat_flush_typing(self) -> None:
        """将当前打字中的消息按全文写入历史并清空打字状态（不打断时不应丢 pending）。"""
        if not self.chat_typing_active:
            return
        self.chat_history.append(
            {"role": self.chat_typing_role, "text": self.chat_typing_full_text}
        )
        self._chat_reset_typing_state()

    def _chat_begin_typing(
        self,
        role: str,
        text: str,
        typing_speed_override: Optional[float] = None,
    ) -> None:
        self.chat_typing_role = role
        self.chat_typing_full_text = text
        self.chat_typing_current_length = 0
        self.chat_typing_timer = 0.0
        self.chat_typing_active = True
        self._chat_typing_speed_override = typing_speed_override

    def _maybe_append_fm_hint(self, cleaned: str) -> str:
        """碎片达阈后，在女孩回复末尾低概率追加收音机频率线索（带冷却）。"""
        if not cleaned.strip():
            return cleaned
        if self.memory_fragments < FRAGMENT_HINT_THRESHOLD:
            return cleaned
        if (
            self._fm_hint_exchanges_since >= FM_HINT_COOLDOWN_EXCHANGES
            and random.random() < FM_HINT_PROB
        ):
            self._fm_hint_exchanges_since = 0
            return (
                cleaned
                + "\n"
                + f"（电波噪音……你隐约听到一个频率：{FM_HINT_FREQUENCY}）"
            )
        self._fm_hint_exchanges_since += 1
        return cleaned

    def _start_true_ending(self) -> None:
        """真结局：禁用后续输入，以打字机逐行播放独白，再进入 CRT 故障与退出。"""
        self._chat_flush_typing()
        self._chat_pending_girl = None
        self._chat_pending_slash = None
        self._llm_cancel_gen += 1
        self._llm_expected_token = None
        self._ollama_generating = False
        self._llm_first_token_seen = False
        while True:
            try:
                self._llm_reply_queue.get_nowait()
            except queue.Empty:
                break
        self.ending_triggered = True
        self.ending_phase = 1
        self.ending_timer = 0.0
        self._ending_phase1_active = True
        self._ending_next_line_idx = 0
        self._chat_begin_typing("girl", self.ending_lines[0])

    def _try_start_true_ending_from_plain(self, msg: str) -> bool:
        """纯数字频率触发真结局；碎片不足时吞掉输入并提示。"""
        s = msg.strip().upper().replace("FM", "")
        if s != FM_HINT_FREQUENCY:
            return False
        self._chat_flush_typing()
        self._chat_pending_girl = None
        self._chat_pending_slash = None
        self._llm_cancel_gen += 1
        self._llm_expected_token = None
        self._ollama_generating = False
        self._llm_first_token_seen = False
        while True:
            try:
                self._llm_reply_queue.get_nowait()
            except queue.Empty:
                break
        self.chat_scroll = 0
        self.chat_history.append({"role": "player", "text": msg.strip()})
        if self.memory_fragments < FRAGMENT_HINT_THRESHOLD:
            self.chat_history.append(
                {
                    "role": "system",
                    "text": "……只有杂音。也许回声还不够。",
                }
            )
            return True
        if self.ending_triggered:
            return True
        self._start_true_ending()
        return True

    def _update_ending_sequence(self, delta_time: float) -> None:
        if not self.ending_triggered:
            return
        if self.ending_phase == 2:
            self.ending_timer += delta_time
            if self.ending_timer >= 4.0:
                self.ending_phase = 3
                self.ending_timer = 0.0
                self.ending_phase3_frame = 0
                self.ending_phase3_timer = 0.0
                self._ending_phase3_exit_requested = False
        elif self.ending_phase == 3:
            self.ending_phase3_timer += delta_time
            if self.ending_phase3_frame < 4:
                dur = self.ending_phase3_frame_durations[self.ending_phase3_frame]
                if self.ending_phase3_timer >= dur:
                    self.ending_phase3_frame += 1
                    self.ending_phase3_timer = 0.0
            else:
                if (
                    self.ending_phase3_timer >= 4.0
                    or self._ending_phase3_exit_requested
                ):
                    self.running = False

    def _update_chat_typing(self, delta_time: float) -> None:
        if not self.chat_typing_active:
            return
        ending_typing = self.ending_phase == 1 and self._ending_phase1_active
        if not ending_typing and (
            self.settings_visible
            or self.help_overlay_active
            or self.paused
            or self.forum_active
        ):
            return

        self.chat_typing_timer += delta_time
        full_len = len(self.chat_typing_full_text)
        speed = (
            self._chat_typing_speed_override
            if self._chat_typing_speed_override is not None
            else self.chat_typing_speed
        )
        target_length = int(self.chat_typing_timer / speed)
        if target_length > full_len:
            target_length = full_len
        if target_length > self.chat_typing_current_length:
            self.chat_typing_current_length = target_length

        if self.chat_typing_current_length < full_len:
            return

        completed_role = self.chat_typing_role
        completed_text = self.chat_typing_full_text
        self.chat_history.append({"role": completed_role, "text": completed_text})
        self._chat_reset_typing_state()

        if (
            completed_role == "girl"
            and self._ending_phase1_active
            and self.ending_phase == 1
        ):
            self._ending_next_line_idx += 1
            if self._ending_next_line_idx < len(self.ending_lines):
                self._chat_begin_typing(
                    "girl", self.ending_lines[self._ending_next_line_idx]
                )
            else:
                self._ending_phase1_active = False
                self.ending_phase = 2
                self.ending_timer = 0.0
            return

        if completed_role == "player":
            if self._chat_pending_slash is not None:
                slash = self._chat_pending_slash
                self._chat_pending_slash = None
                self._chat_handle_slash(slash[1:].strip())
                return
            if self._chat_pending_girl is not None:
                user_msg = self._chat_pending_girl
                self._chat_pending_girl = None
                tok = self._llm_cancel_gen
                display, pending = self.bbs_engine.reply_to_post_graphical(
                    1, user_msg, self._llm_reply_queue, tok
                )
                if pending:
                    self._llm_expected_token = tok
                    self._ollama_generating = True
                    self._llm_first_token_seen = False
                    return
                self._llm_expected_token = None
                self._ollama_generating = False
                reply = display or ""
                cleaned = reply.strip()
                self._sync_mood_from_player_message(user_msg)
                self.memory_fragments = min(
                    self.total_memory_fragments, self.memory_fragments + 1
                )
                cleaned = self._maybe_append_fm_hint(cleaned)
                if cleaned:
                    self._chat_begin_typing("girl", cleaned)

    def _poll_llm_reply_queue(self) -> None:
        while True:
            try:
                item = self._llm_reply_queue.get_nowait()
            except queue.Empty:
                break
            if not item:
                continue
            kind = item[0]
            if kind == "llm_first":
                if len(item) >= 2 and item[1] == self._llm_expected_token:
                    self._llm_first_token_seen = True
                continue
            if kind == "llm_done":
                if len(item) < 6:
                    continue
                _, tok, post_id, message, keywords, inner = item[:6]
                if tok != self._llm_expected_token:
                    self._ollama_generating = False
                    continue
                reply = self.bbs_engine.complete_graphical_llm_success(
                    post_id, message, keywords, inner
                )
                self._llm_expected_token = None
                self._finish_girl_reply_async(message, reply)
                continue
            if kind == "llm_fallback":
                if len(item) < 5:
                    continue
                _, tok, post_id, message, keywords = item[:5]
                if tok != self._llm_expected_token:
                    self._ollama_generating = False
                    continue
                reply = self.bbs_engine.complete_graphical_llm_fallback(
                    post_id, message, keywords
                )
                self._llm_expected_token = None
                self._finish_girl_reply_async(message, reply)

    def _finish_girl_reply_async(self, user_msg: str, reply: str) -> None:
        self._ollama_generating = False
        self._llm_first_token_seen = False
        self._sync_mood_from_player_message(user_msg)
        self.memory_fragments = min(
            self.total_memory_fragments, self.memory_fragments + 1
        )
        cleaned = reply.strip()
        cleaned = self._maybe_append_fm_hint(cleaned)
        if cleaned:
            target_sec = float(
                os.environ.get("BBS_SHOJO_LLM_DISPLAY_TARGET_SEC", "4.5")
            )
            n = max(1, len(cleaned))
            llm_speed = max(0.012, min(0.08, target_sec / n))
            self._chat_begin_typing("girl", cleaned, typing_speed_override=llm_speed)

    def _chat_send_current(self):
        msg = self.chat_input.strip()
        self.chat_input = ""
        if not msg:
            return
        if self._try_start_true_ending_from_plain(msg):
            return
        self._llm_cancel_gen += 1
        self._llm_expected_token = None
        self._ollama_generating = False
        self._llm_first_token_seen = False
        while True:
            try:
                self._llm_reply_queue.get_nowait()
            except queue.Empty:
                break
        self._chat_flush_typing()
        self._chat_pending_girl = None
        self._chat_pending_slash = None
        self.chat_scroll = 0

        self._chat_begin_typing("player", msg)
        if msg.startswith("/"):
            self._chat_pending_slash = msg
            return

        self._chat_pending_girl = msg

    def _chat_handle_slash(self, cmd: str):
        if not cmd:
            return
        parts = cmd.split(maxsplit=1)
        head = parts[0].lower()
        tail = parts[1] if len(parts) > 1 else ""

        if head in {"help", "?"}:
            self.chat_history.append(
                {
                    "role": "system",
                    "text": "直接打字可与「小误」对话（含简单上下文）。命令：/help /mode /sig /geo /deadlinks /memories /turing /answer /theseus /bgm /midi",
                }
            )
            return
        if head == "mode":
            self.chat_history.append({"role": "system", "text": self.bbs_engine.set_mode(tail or "")})
            return
        if head == "sig":
            self.chat_history.append({"role": "system", "text": self.bbs_engine.set_signature(tail)})
            return
        if head == "geo":
            geo_parts = [p.strip() for p in tail.split("|")]
            if len(geo_parts) < 3:
                self.chat_history.append({"role": "system", "text": "用法：/geo 标题|简介|主题"})
            else:
                self.chat_history.append(
                    {"role": "system", "text": self.bbs_engine.geocities_update(geo_parts[0], geo_parts[1], geo_parts[2])}
                )
            return
        if head == "deadlinks":
            self.chat_history.append({"role": "system", "text": self.bbs_engine.deadlinks_list()})
            return
        if head == "memories":
            self.chat_history.append({"role": "system", "text": self.bbs_engine.list_memories()})
            return
        if head == "turing":
            self.chat_history.append({"role": "system", "text": self.bbs_engine.turing_test_round()})
            return
        if head == "answer":
            self.chat_history.append({"role": "system", "text": self.bbs_engine.turing_test_round(tail)})
            return
        if head == "theseus":
            self.chat_history.append({"role": "system", "text": self.bbs_engine.theseus_rewrite(tail)})
            return
        if head in {"bgm", "music"}:
            self._toggle_bgm()
            return
        if head in {"tune", "fm"}:
            freq = tail.strip()
            if not freq:
                self.chat_history.append(
                    {
                        "role": "system",
                        "text": f"用法：/{head} {FM_HINT_FREQUENCY}",
                    }
                )
                return
            if freq != FM_HINT_FREQUENCY:
                self.chat_history.append(
                    {"role": "system", "text": "……那个频率只有静电。"}
                )
                return
            if self.memory_fragments < FRAGMENT_HINT_THRESHOLD:
                self.chat_history.append(
                    {
                        "role": "system",
                        "text": "……只有杂音。也许回声还不够。",
                    }
                )
                return
            if self.ending_triggered:
                return
            self._start_true_ending()
            return
        if head == "midi":
            spec = tail.strip()
            if not spec:
                self.chat_history.append(
                    {
                        "role": "system",
                        "text": "用法：/midi note C4 q note E4 q note G4 q（与高级简谱语法相同；若 BGM 正在播可先 /bgm 关闭）",
                    }
                )
                return
            try:
                data = self.midi_converter.create_midi(spec)
                self.midi_sequencer.load_midi(data)
                self.midi_sequencer.play()
                self.chat_history.append({"role": "system", "text": "[MIDI] 已播放该序列（彩蛋）。"})
            except Exception as exc:
                self.chat_history.append({"role": "system", "text": f"[MIDI] 解析或播放失败：{exc}"})
            return

        self.chat_history.append({"role": "system", "text": f"未知命令：/{head}（输入 /help 查看）"})

    def _draw_chat_ui(self):
        """绘制聊天历史与输入框。"""
        panel_h = 280
        panel_y = self.screen_height - panel_h - 40

        # 背景面板
        panel = pygame.Surface((self.screen_width - 40, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        self.screen.blit(panel, (20, panel_y))

        # 历史区域
        history_x = 40
        history_y = panel_y + 10
        history_w = self.screen_width - 80
        history_h = panel_h - 70

        # 组装可显示行（自动换行）
        lines: List[Tuple[str, Tuple[int, int, int]]] = []
        for item in self.chat_history[-200:]:
            role = item.get("role", "system")
            text = item.get("text", "")
            if role == "player":
                prefix = "你："
                color = (200, 200, 200)
            elif role == "girl":
                prefix = "小误："
                color = (0, 255, 0)
            else:
                prefix = "[系统] "
                color = (128, 180, 255)

            wrapped = wrap_text_to_width(self.small_font, prefix + text, history_w)
            for w in wrapped:
                lines.append((w, color))

        if self.chat_typing_active and self.chat_typing_current_length > 0:
            role = self.chat_typing_role
            partial = self.chat_typing_full_text[: self.chat_typing_current_length]
            if int(self._cursor_phase * 2) % 2 == 0:
                partial = partial + "_"
            if role == "player":
                prefix = "你："
                color = (200, 200, 200)
            elif role == "girl":
                prefix = "小误："
                color = (0, 255, 0)
            else:
                prefix = "[系统] "
                color = (128, 180, 255)
            wrapped = wrap_text_to_width(self.small_font, prefix + partial, history_w)
            for w in wrapped:
                lines.append((w, color))

        # 根据滚动计算显示窗口
        max_lines = max(1, history_h // (self.small_font.get_height() + 4))
        start = max(0, len(lines) - max_lines - self.chat_scroll)
        end = max(0, len(lines) - self.chat_scroll)
        visible = lines[start:end]

        y = history_y
        for line, color in visible:
            surf = self.small_font.render(line, True, color)
            self.screen.blit(surf, (history_x, y))
            y += self.small_font.get_height() + 4

        # 输入框
        box_y = panel_y + panel_h - 48
        if self._ollama_generating and self._chat_ui_llm_hint_allowed():
            hint = (
                "小误正在打字…"
                if self._llm_first_token_seen
                else "小误正在输入…"
            )
            if int(self._cursor_phase * 2) % 2 == 0:
                hint = f"{hint}▍"
            hint_surf = self.small_font.render(hint, True, (160, 220, 170))
            self.screen.blit(hint_surf, (40, box_y - 44))
        pygame.draw.rect(self.screen, (0, 255, 0), (30, box_y, self.screen_width - 60, 36), 1)
        prompt = self.chat_input
        # 光标闪烁
        if self.chat_focus and self._chat_can_accept_input(ignore_focus=True) and int(self._cursor_phase * 2) % 2 == 0:
            prompt = prompt + "|"
        input_surf = self.small_font.render(prompt, True, (255, 255, 255))
        self.screen.blit(input_surf, (40, box_y + 7))

        mode_text = "输入模式(Tab切换)" if self.chat_focus else "热键模式(Tab切换)"
        mode_surf = self.small_font.render(mode_text, True, (128, 128, 128))
        self.screen.blit(mode_surf, (self.screen_width - mode_surf.get_width() - 40, box_y - 22))

        bgm_text = "BGM: ON" if self.bgm_enabled else "BGM: OFF"
        bgm_surf = self.small_font.render(bgm_text, True, (128, 128, 128))
        self.screen.blit(bgm_surf, (40, box_y - 22))

    def _init_bgm(self):
        """生成一段内置 MIDI 并注册到情绪音乐管理器。"""
        try:
            # 生成一段简短旋律（不依赖外部资源）
            happy = "note C4 q note E4 q note G4 q note C5 q"
            sad = "note A3 q note E4 q note D4 q note A3 q"
            neutral = "note C4 q note D4 q note E4 q note D4 q"
            self.mood_manager.add_background_music("happy", self.midi_converter.create_midi(happy))
            self.mood_manager.add_background_music("sad", self.midi_converter.create_midi(sad))
            self.mood_manager.add_background_music("neutral", self.midi_converter.create_midi(neutral))
            self._bgm_ready = True
            self._bgm_init_error = None
        except Exception as exc:
            self._bgm_ready = False
            self._bgm_init_error = str(exc)

    def _toggle_bgm(self):
        """开关背景音乐。"""
        if not self._bgm_ready:
            self._init_bgm()
        if not self._bgm_ready:
            hint = self._bgm_init_error or "未知原因"
            self.chat_history.append(
                {
                    "role": "system",
                    "text": f"[音乐] 仍无法启用背景 MIDI（{hint}）。/midi 可单独试简谱。",
                }
            )
            return
        self.bgm_enabled = not self.bgm_enabled
        try:
            if self.bgm_enabled:
                # 用当前情绪选择曲目（没有匹配则 neutral）
                name = self.current_mood if self.current_mood in ("happy", "sad") else "neutral"
                ok = self.mood_manager.play_background_music(name)
                if ok:
                    self.chat_history.append({"role": "system", "text": f"[音乐] 已播放背景MIDI：{name}（按 G 关闭）"})
                else:
                    self.chat_history.append({"role": "system", "text": "[音乐] 无可用曲目。"})
                    self.bgm_enabled = False
            else:
                self.midi_sequencer.stop()
                self.chat_history.append({"role": "system", "text": "[音乐] 已关闭背景音乐。"})
        except Exception as exc:
            self.bgm_enabled = False
            self.chat_history.append({"role": "system", "text": f"[音乐] 播放失败：{exc}"})
        
    def _draw_forum(self):
        """绘制论坛界面"""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        title = self.font.render("BBS论坛", True, (0, 255, 0))
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 50))
        
        # 绘制论坛帖子
        y = 100
        for post in reversed(self.forum_posts[-5:]):  # 显示最新5个帖子
            npc_color = self._post_display_color(post)
            # 绘制头像
            avatar_text = self.small_font.render(post["avatar"], True, npc_color)
            self.screen.blit(avatar_text, (50, y))
            
            # 绘制作者
            author_text = self.small_font.render(f"{post['author']}:", True, npc_color)
            self.screen.blit(author_text, (100, y))
            y += 30
            
            # 绘制内容
            content_lines = post["content"].split("\n")
            for line in content_lines:
                if line.strip():
                    wrapped = wrap_text_to_width(self.small_font, line, self.screen_width - 140)
                    for chunk in wrapped:
                        content_text = self.small_font.render(chunk, True, (255, 255, 255))
                        self.screen.blit(content_text, (100, y))
                        y += 25
                        if y > self.screen_height - 90:
                            break
                if y > self.screen_height - 90:
                    break
                    
            y += 20
            if y > self.screen_height - 90:
                break
            
        # 绘制提示
        hint_text = self.small_font.render("按ESC返回游戏", True, (128, 128, 128))
        self.screen.blit(hint_text, (self.screen_width//2 - hint_text.get_width()//2, self.screen_height - 50))
        
    def _post_display_color(self, post: Dict) -> Tuple[int, int, int]:
        """论坛帖绘制色：兼容仅 JSON 可序列化字段的存档。"""
        raw = post.get("npc_color")
        if isinstance(raw, (list, tuple)) and len(raw) >= 3:
            return int(raw[0]), int(raw[1]), int(raw[2])
        npc = post.get("npc")
        if npc is not None and hasattr(npc, "personality"):
            c = npc.personality.get("color", (255, 255, 255))
            return int(c[0]), int(c[1]), int(c[2])
        return (255, 255, 255)

    def _normalize_forum_posts(self):
        """确保每帖含 npc_color，避免旧存档或异常数据导致绘制错误。"""
        for post in self.forum_posts:
            if "npc_color" not in post:
                post["npc_color"] = self._post_display_color(post)
            if "npc" in post:
                del post["npc"]

    def _load_offline_logs(self):
        """加载离线日志"""
        log_file = user_data_path("offline_log.txt")
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                self.offline_logs = f.readlines()
                
    def _save_offline_logs(self):
        """保存离线日志"""
        # 生成离线日志
        log_entry = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 玩家离开游戏，角色在BBS上等待...\n"
        self.offline_logs.append(log_entry)
        
        with open(user_data_path("offline_log.txt"), "w", encoding="utf-8") as f:
            f.writelines(self.offline_logs)
            
    def _save_game(self):
        """保存游戏进度"""
        save_data = {
            "memory_fragments": self.memory_fragments,
            "current_mood": self.current_mood,
            "turing_test_progress": self.turing_test_progress,
            "personality_mod": self.personality_mod,
            "save_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            "forum_posts": [
                {
                    "author": p["author"],
                    "avatar": p["avatar"],
                    "content": p["content"],
                    "time": p["time"],
                    "npc_color": list(self._post_display_color(p)),
                }
                for p in self.forum_posts
            ],
            "npcs": [{
                "opinion": npc.opinion_on_character,
                "post_count": npc.post_count,
                "personality": npc.personality["type"]
            } for npc in self.npcs]
        }
        
        import json
        with open(user_data_path("savegame.json"), "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
            
        self._log("游戏已保存到 savegame.json")
        
    def _load_game(self):
        """加载游戏进度"""
        save_path = user_data_path("savegame.json")
        if os.path.exists(save_path):
            import json
            with open(save_path, "r", encoding="utf-8") as f:
                save_data = json.load(f)
                
            self.memory_fragments = save_data.get("memory_fragments", 0)
            self.current_mood = save_data.get("current_mood", "happy")
            self.character.set_emotion(self.current_mood)
            self.turing_test_progress = save_data.get("turing_test_progress", 0)
            self.personality_mod = save_data.get("personality_mod", 0)
            self.forum_posts = save_data.get("forum_posts", [])
            self._normalize_forum_posts()
            
            self._log(f"已加载游戏进度: {save_data.get('save_time', '未知时间')}")
        else:
            self._log("未找到保存文件")

def main():
    """主函数"""
    game = BBSShojoGame()
    game.run()

if __name__ == "__main__":
    main()