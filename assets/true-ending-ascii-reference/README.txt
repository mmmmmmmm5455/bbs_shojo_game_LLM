True ending ASCII art — design reference
-----------------------------------------

These PNGs are screenshots of the hand-authored ASCII portraits (not error logs).
They are kept so artists and programmers can compare the in-game monospace render
to the original intent.

In-code frame order (signal decay):
  ENDING_ASCII_FRAME_1  ->  dense @ / % border (heaviest)
  ENDING_ASCII_FRAME_2  ->  sparse @@ vertical “ghost”
  ENDING_ASCII_FRAME_3  ->  .@@ dotted / waveform frame
  ENDING_ASCII_FRAME_4  ->  mid-density @@ figure

PNG filenames (chronological capture) are for visual reference only; align art in main_advanced_v2.py (module constants).

Runtime strings live in: src/main_advanced_v2.py (ENDING_ASCII_FRAME_1 … 4 and _r_ascii_block)
