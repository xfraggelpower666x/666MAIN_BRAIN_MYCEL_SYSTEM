import runpy, sys
module=runpy.run_path(sys.argv[1])
module['tools']()
print('MP3_READY')
