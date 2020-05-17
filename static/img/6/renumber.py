import pathlib

THIS_DIRECTORY = pathlib.Path(__file__).parent
for i, filename in enumerate(sorted(THIS_DIRECTORY.glob('*.jpg'))):
  print(i, filename)
  filename.rename(f'marble{i+10:02d}.jpg')