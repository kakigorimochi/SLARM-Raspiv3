import simpleaudio as sa

while True:
    wave_obj = sa.WaveObject.from_wave_file("w_50kph.wav")
    play_obj = wave_obj.play()
    play_obj.wait_done()
