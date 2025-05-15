# scripts
random scripts i use myself

### downloader
- downloads every second line/link in a specified file
- downloader-tvg-name.py is the same script but renames the output to the "tvg-name" in the line before (for m3u files)
### filter
- filters out every line containing a specific string in a specified file + the following line and saves them
### mcnames
- generates and checks minecraft names
### mwb-reset
- resets guids used for trial expiration checks and reinstalls malwarebytes
- one-liner: `curl -o %TEMP%\mwb-reset.bat https://z-n.cc/scripts/mwb-reset.bat & %TEMP%\mwb-reset.bat`
### renamer
- renames all files in the current directory to their modification timestamp ("%d.%m.%Y - %H-%M")
### stacker
- stacks all gifs in the current directory until the specified height is reached (used for steam profile customization)
