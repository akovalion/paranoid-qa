# vhs tape: renders assets/demo.gif from the replay script.
# Run from the repo root: vhs demo/gif/demo.tape
Output assets/demo.gif

Set Shell bash
Set FontSize 17
Set Width 1180
Set Height 860
Set Padding 18
Set TypingSpeed 10ms
Set Theme "Catppuccin Mocha"

Hide
Type "bash demo/gif/play.sh"
Enter
Sleep 600ms
Show
Sleep 17s
